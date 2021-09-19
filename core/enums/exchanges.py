from enum import IntEnum


class Exchange(IntEnum):
    Reserved = 0
    # Values Between 0-100 Are reserved for real, production exchanges with real trading activity
    Bittrex = 1
    Coinbase = 2
    CoinbaseSandbox = 101  # Values Greater than 100 are used for Sandboxes, where no real funds are exchanged
