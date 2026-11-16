import argparse
import logging
import signal
import sys
import threading
import time
from datetime import UTC, datetime
from logging.handlers import RotatingFileHandler
from typing import Callable
from uuid import uuid4

from firmware.api_client import ApiError, DeviceApiClient, FanCommand, Reading
from firmware.fan import Fan, FanState
from firmware.settings import ConfigurationError, Settings, load_settings
from firmware.temperature_sensor import TemperatureSensor

logger = logging.getLogger(__name__)


class DeviceRuntime:
    def __init__(
        self, settings: Settings, client: DeviceApiClient, *,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._settings = settings
        self._client = client
        self._clock = clock
        self._fan = Fan()
        self._sensor = TemperatureSensor(
            seed=settings.sensor_seed,
            start_temperature_c=settings.start_temperature_c,
            ambient_temperature_c=settings.ambient_temperature_c,
            fan_cooling_c_per_second=settings.fan_cooling_c_per_second,
            noise_stddev_c=settings.noise_stddev_c,
            thermal_time_constant_seconds=settings.thermal_time_constant_seconds,
        )
        self._last_update = self._next_reading = self._next_command = clock()
        self._pending_reading: Reading | None = None
        self._pending_command: FanCommand | None = None

    def _advance_sensor(self) -> None:
        now = self._clock()
        self._sensor.advance(now - self._last_update, fan_on=self._fan.is_on)
        self._last_update = now

    def _send_reading(self) -> None:
        if self._pending_reading is None:
            self._pending_reading = Reading(
                reading_id=str(uuid4()),
                recorded_at=datetime.now(UTC).isoformat(timespec="milliseconds"),
                temperature_c=self._sensor.read_celsius(),
                fan_state=self._fan.state,
            )
        delay = self._settings.reading_interval_seconds
        try:
            self._client.submit_reading(self._pending_reading)
        except ApiError as error:
            if not error.retryable:
                raise
            delay = self._settings.reconnect_delay_seconds
            logger.warning("Reading delivery deferred: reason=%s status=%s", error.reason, error.status_code)
        else:
            logger.info("Reading delivered: temperature_c=%.2f fan=%s", self._pending_reading.temperature_c, self._pending_reading.fan_state)
            self._pending_reading = None
        self._next_reading = self._clock() + delay

    def _process_command(self) -> None:
        delay = self._settings.command_poll_interval_seconds
        try:
            if self._pending_command is None:
                command = self._client.poll_command()
                if command is not None:
                    self._advance_sensor()
                    self._fan.set_state(command.fan_state)
                    self._pending_command = command
                    logger.info("Fan command applied: command=%s state=%s", command.command_id, self._fan.state)
            if self._pending_command is not None:
                self._client.acknowledge_command(self._pending_command, self._fan.state)
                logger.info("Fan command acknowledged: command=%s", self._pending_command.command_id)
                self._pending_command = None
        except ApiError as error:
            if not error.retryable:
                raise
            delay = self._settings.reconnect_delay_seconds
            logger.warning("Command exchange deferred: reason=%s status=%s", error.reason, error.status_code)
        self._next_command = self._clock() + delay

    def step(self) -> float:
        self._advance_sensor()
        if self._clock() >= self._next_reading:
            self._send_reading()
        if self._clock() >= self._next_command:
            self._process_command()
        return min(self._next_reading, self._next_command)

    def stop(self) -> None:
        self._fan.set_state(FanState.OFF)


def configure_logging(settings: Settings) -> None:
    settings.log_file.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        settings.log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8",
    )
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(), file_handler], force=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the room monitor device client.")
    parser.add_argument("--check-config", action="store_true", help="Validate local settings without contacting the API.")
    args = parser.parse_args()
    try:
        settings = load_settings()
    except ConfigurationError as error:
        print(f"Invalid firmware configuration: {error}", file=sys.stderr)
        return 2
    except OSError:
        print("Cannot read firmware configuration. Check .env and certificate file permissions.", file=sys.stderr)
        return 2
    if args.check_config:
        print("Firmware configuration is valid; API connectivity and enrollment have not been checked.")
        return 0
    try:
        configure_logging(settings)
    except OSError:
        print("Cannot open FIRMWARE_LOG_FILE. Check the path and write permissions.", file=sys.stderr)
        return 2

    stop_event = threading.Event()

    def request_stop(signum: int, frame: object) -> None:
        stop_event.set()

    previous_handlers = {signum: signal.signal(signum, request_stop) for signum in (signal.SIGINT, signal.SIGTERM)}
    try:
        with DeviceApiClient(settings) as client:
            runtime = DeviceRuntime(settings, client)
            logger.info("Device started: device=%s", settings.device_id)
            try:
                while not stop_event.is_set():
                    deadline = runtime.step()
                    stop_event.wait(max(0, deadline - time.monotonic()))
            finally:
                runtime.stop()
                logger.info("Device stopped; fan state is off")
    except ApiError as error:
        logger.error("Device stopped after API rejection: reason=%s status=%s", error.reason, error.status_code)
        return 1
    finally:
        for signum, previous in previous_handlers.items():
            signal.signal(signum, previous)
        logging.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
