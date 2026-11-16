import math
import random


class TemperatureSensor:
    def __init__(
        self,
        *,
        seed: int,
        start_temperature_c: float,
        ambient_temperature_c: float,
        fan_cooling_c_per_second: float,
        noise_stddev_c: float,
        thermal_time_constant_seconds: float,
    ) -> None:
        values = (
            start_temperature_c, ambient_temperature_c,
            fan_cooling_c_per_second, noise_stddev_c,
            thermal_time_constant_seconds,
        )
        if not all(math.isfinite(value) for value in values):
            raise ValueError("Sensor parameters must be finite")
        if fan_cooling_c_per_second < 0 or noise_stddev_c < 0:
            raise ValueError("Cooling and measurement noise cannot be negative")
        if thermal_time_constant_seconds <= 0:
            raise ValueError("Thermal time constant must be positive")
        self._temperature_c = start_temperature_c
        self._ambient_c = ambient_temperature_c
        self._cooling = fan_cooling_c_per_second
        self._noise = noise_stddev_c
        self._time_constant = thermal_time_constant_seconds
        self._random = random.Random(seed)

    def advance(self, elapsed_seconds: float, *, fan_on: bool) -> None:
        if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
            raise ValueError("Elapsed time must be finite and nonnegative")
        equilibrium = self._ambient_c
        if fan_on:
            equilibrium -= self._cooling * self._time_constant
        fraction = -math.expm1(-elapsed_seconds / self._time_constant)
        self._temperature_c += (equilibrium - self._temperature_c) * fraction

    def read_celsius(self) -> float:
        return round(self._temperature_c + self._random.gauss(0, self._noise), 2)
