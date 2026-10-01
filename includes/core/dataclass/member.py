from dataclasses import dataclass
from enum import IntEnum


class Gender(IntEnum):
    unspecified = 0
    male = 1
    female = 2
    nonbinary = 3
    other = 4