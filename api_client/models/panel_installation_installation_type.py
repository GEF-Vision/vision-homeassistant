from enum import IntEnum


class PanelInstallationInstallationType(IntEnum):
    VALUE_0 = 0
    VALUE_1 = 1
    VALUE_3 = 3
    VALUE_2 = 2
    VALUE_4 = 4
    VALUE_99 = 99

    def __str__(self) -> str:
        return str(self.value)