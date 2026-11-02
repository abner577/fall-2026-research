from enum import StrEnum


class FanState(StrEnum):
    OFF = "off"
    ON = "on"


class Fan:
    def __init__(self) -> None:
        self._state = FanState.OFF

    @property
    def state(self) -> FanState:
        return self._state

    @property
    def is_on(self) -> bool:
        return self._state == FanState.ON

    def set_state(self, state: FanState) -> None:
        self._state = FanState(state)
