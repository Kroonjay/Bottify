from enum import IntEnum


class CurrencyType(IntEnum):
    # Currency Types 1-99 Are Reserved for non-crypto
    Unset = 0
    FiatUSD = 1
    # Currencies 100-500 are for Cryptos
    Crypto = 100
