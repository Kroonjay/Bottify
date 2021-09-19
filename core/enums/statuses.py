from enum import IntEnum


class BottifyStatus(IntEnum):
    Unset = 0
    New = 1  # Used for Alerts, initial status when created before the relevant response activities have been picked up by a worker
    Active = 2  # Used for a ton of things
    Busy = 3  # Used for Feeder, Indicators when their activities are actively being completed by a worker
    Complete = 4  # Used for Alerts & Orders, set when all relevant response activities are complete
    Settled = 5  # Used for Orders, set once all relevant budgets have been calculated from trades
    Error = 253
    UserDisabled = 254
    SourceDisabled = 255
    SourceDeleted = 256  # Used for permanent deletions by a source feed or exchange.  Created to handle Coinbase markets with "delisted" status
    AdminDisabled = 420
