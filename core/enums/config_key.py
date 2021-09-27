from enum import Enum


class ConfigKey(Enum):
    FeedStuckAfterMinutes = "FeedStuckAfterMinutes"

    def __str__(self):
        return self.value
