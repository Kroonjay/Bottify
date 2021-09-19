
- [Concepts:](#concepts)
  - [Feeds](#feeds)
  - [Indicators](#indicators)
  - [Positions](#positions)
  - [Strategies](#strategies)
  - [Exchanges](#exchanges)
  - [Trades](#trades)
  - [Balances](#balances)
  - [Deposits](#deposits)
  - [Withdrawals](#withdrawals)
  - [Transfers](#transfers)
- [Tech Stack:](#tech-stack)
  - [Python Option](#python-option)
- [Trading Strategy Ideas](#trading-strategy-ideas)
  - [Cross-Exchange Arbitrage](#cross-exchange-arbitrage)
    - [Summary](#summary)
    - [Feeds](#feeds-1)
    - [Indicators](#indicators-1)
  - [Whale Movements](#whale-movements)
    - [Summary](#summary-1)
    - [Feeds](#feeds-2)
    - [Indicators](#indicators-2)
  - [Coinbase Listing Announcements](#coinbase-listing-announcements)
    - [Summary](#summary-2)
    - [Feeds](#feeds-3)
    - [Indicators](#indicators-3)
- [Network](#network)
  - [Mildly Overkill](#mildly-overkill)
  - [Super Overkill](#super-overkill)

<br>
<br>

# Concepts:
## Feeds
 - Source Data pulled from exchanges / third-party sources
 - 

## Indicators
 - Set of configurable parameters that will trigger changes in Positions based on feed inputs
 - User defined / editable
 - Should result in either OPEN, CLOSE decision for positions in strategy 

## Positions
 - Any orders placed on an exchange
 - Can be partial-fill, no-fill, closed
 - ideally NOT user editable, can create super-indicator as failsafe

## Strategies
 - Will open / close positions based on indicators
 - Allow for stop conditions like max P/L, etc.
 - Funds should be "locked" to a given strategy
   - *This isn't ideal but avoids potential issues with funds management when running multiple strategies*
 - Maximum Funds parameter to minimize losses in a disaster
 - Configure which Exchanges to use
 - User Editable

## Exchanges
 - Third Party platforms to buy/sell crypto
 - Also where crypto will be stored in v1
 - Should report balances, positions (orders), trades
 - Should report transfers via exchange deposits & Withdrawals
 - Identifier to determine proper API to use

## Trades
 - Any executed positions resulting in a balance delta
 - Permanent, cannot be cancelled/closed.
 - Will Modify Balances
 - System Enforced

## Balances
 - Current state of balances for all coins
 - System Enforced

## Deposits
 - Used to add crypto to system, increase balances
 - Supported Deposit Types
   -  Fiat to Exchange
   -  Personal Crypto to Exchange
   -  *v2*: Personal Crypto to Hot Wallet 
 - User Editable w/ Restrictions

## Withdrawals
 - Used to remove crypto from system, decrease balances
 - Exchange to Personal wallet & Exchange to Fiat withdrawal
 - User Editable w/ Restrictions

## Transfers
 - Used to transfer crypto between exchanges
 - Will alter balances due to tx/network fees
 
 - Transfer Types
   - Exchange to Exchange
   - *v2*: Exchange to Hot Wallet
- *Need to figure out how to support balance management between exchanges for cross-exchange arbitrage strategy*

<br>
<br>

# Tech Stack: 

## Python Option
- Hosted on AWS
- FastApi / Starlette with Uvicorn
    - Native Async, plays nicely w/ RabbitMQ, Elastisearch, hella fast
- Rabbitmq for task / worker management
- Elastisearch w/ Kibana for Feeds & Indicators
- Docker
- PostgreSQL for Balances, other persistent data


<br>
<br>

# Trading Strategy Ideas

## Cross-Exchange Arbitrage
 ### Summary
   - Look for price deltas between exchanges, make gainz 
    
### Feeds
   - Bittrex Orderbook
   - Coinbase Orderbook
   - Probably network/tx fees
### Indicators
 - For all coins, if price on Bittrex deviates from price on Coinbase (w/ threshold)
 - If that threshold is great enough to compensate for current tx/network fees
  - If we have funds on both exchanges: 
       - *Do we make money if we buy on the exchange with the lower price and sell on the exchange with the higher price, even if we don't transfer???* 
          - *still not totally sure...*

<br>

## Whale Movements

### Summary
- Monitor exchange wallet addresses for large deposits from cold wallets, assume they're selling
  - Easy via Block Explorer API
- Or, monitor WhaleAlerts twitter

### Feeds
- Whale Alerts Twitter
- Block Explorer API's for whale addresses
- Block Explorers for large amounts sent to exchange Addresses

### Indicators
- If X amount of any token is sent from a known cold address, assume price of that token will drop on that exchange
    - Look for "Running out the Order Book"
    - Look for cross-exchange arbitrage opportunities

<br>

## Coinbase Listing Announcements

### Summary
- Look for news of a coin listing on Coinbase, buy it on Bittrex

### Feeds
- Coinbase Socials, popular crypto news sites/socials

### Indicators
- If a token is announced for listing on Coinbase that's already listed on Bittrex, buy it on Bittrex

<br>
<br>


# Network
 ## Mildly Overkill
 - VPN server w/ public IP.  Probably Algo w/ Wireguard
- API Server blocks all public connections except VPN
- API server talks to DB, workers on Private vnet
- Bastion box is exposed to VPN only and allows access to private vnet

## Super Overkill
- 2 zone network w/ DMZ
- Would need to use Azure / AWS? 
- More protection for wallet servers (if required)
- Not worth the $$$ until we've got 6+ figs in the system

