from enum import IntEnum

# TODO Finish this fucking mess...Roles should only be used to identify a user_permission row in database with columns for each permission we need
class UserRole(IntEnum):
    # Roles between 0:9 Cannot Login to the Site
    Unset = 0
    UserDisabled = 1
    AdminDisabled = 2
    # Roles between 10-50 can Login but cannot Trade, Deposit, or Withdraw.

    # Roles under 50 Can't Trade
    BasicTrader = 50  # Basic Traders can create strategies for top 10 cryptos on a single exchange.  Does not have permissions for deposit, withdraw, or transfer operations

    # Can do anything and everything...within reason.
    God = 42069
