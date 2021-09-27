from enum import Enum


class CandleLength(Enum):
    Undefined = 0
    OneMinute = 1
    FiveMinutes = 5
    FifteenMinutes = 15
    OneHour = 60
    SixHours = 360
    OneDay = 1440
