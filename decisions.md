# Decisions

## 1. Asset Class

**Decision:** Stocks and having crypto as a second data source. 

**Rejected:** Doing crypto only using CoinGecko to get the data. 

**Reason:** Stocks are harder to implement and have real problems to solve. Crypto trades 24/7 unlike stocks that have market closures, splits, and overnight gaps. CoinGecko also gives only one year of history and I need at least two years. 

**Costs:** Have to handle market calendars and price gaps that crypto would have avoided.

**Date:** 2026-08-14 


## 2. Second Data Provider

**Decision:** Alpaca only. No second data provider.  

**Rejected:** Adding Binance as a second source to use for crypto. 

**Reason:** It would have cost four to six hours to implement and I didn't have that time. So I'd rather put those hours into the stocks side. Nothing the user will see is lost and the base class, shapes and exceptions still exist so the abstraction still stands.

**Costs:** I won't be able to show the provider swap working against a real second API. Only against a fake one during testing. Crypto is gone too, but the AssetClass enum is still there, so adding it later will mean only one new line and a new provider file.

**Date:** 2026-08-24 


## 3. Price Adjustment

**Decision:** Use Alpaca's `split` adjustment for historical bars. 

**Rejected:** `all` (splits, dividends and spin offs) and `raw` (no adjustment). 

**Reason:** `raw` will show splits as a fake 90% crash with a stock like Nvidia during June 2024 and it's in the available instruments. `all` fixes that but will shift historical prices for dividends so the stored price is not what the stock actually traded at. `split` keeps the price that the stock actually traded at on the day, and I want my stored prices to be real market prices.

**Costs:** Prices won't match charts on Yahoo or TradingView, which default to fully adjusted. In the long run this will mean returns will look slightly lower than  the true total returns because dividends aren't reflected.

**Date:** 2026-09-09 


## 4. Candle Uniqueness and Indexing

**Decision:** Put a unique constraint on `(instrument, interval, timestamp)` for candles. 

**Rejected:** Checking for duplicates in Python instead and having no index. 

**Reason:** Stops duplicate candles in the database, and my code wouldn't guarantee that. It also will build a B-tree index, and my main query is a range. One instrument and one interval, between two timestamps. A B-tree keeps keys sorted so Postgres jumps to the start of the range and reads forward instead of checking every row. The order isn't random. Instrument cuts it down to one stock first, then interval, then the timestamps are already sorted so it will continue reading along until it's past the end date. A hash map can't do that because hashing spreads the keys out on purpose, so there won't be a next one to read.

**Costs:** Inserts are slightly slower because the index will have to be updated. It only helps if the query knows the instrument. 

**Date:** 2026-09-14


## 5. Fill model 

**Decision:** Orders fill at the latest close plus costs, not replay.

**Rejected:** Checking the history candle by candle.

**Reason:** Replay would need a simulation clock, time tracking for each session, and open orders checked after every candle. This would take days to build for something visitors wouldn't notice. They just want to click Buy and see their order filled.
Using the latest stored closing price means trades happen at the real current market price, so the P&L they see is meaningful. Costs still apply, so trades are not free.

**Costs:** There is no intraday price movement, so the no lookahead rule does not apply and resting orders serve no purpose.

**Date:** 2026-09-19   


## 6. Cost model

**Decision:** Costs are based on basis points. 0 commission, 2bps spread with half applied, and 2bps slippage. All costs are charged to the trader.

**Rejected:** No trading costs or a fixed fee per trade.

**Reason:** Trading 212 does not charge commission on stocks and ETFs, so 0 is what the broker I’m modelling actually charges. Large US companies usually have spreads between 1 and 5bps, so I used 2bps as a middle value. Only half is applied because the trader only crosses half the spread. I set slippage at 2bps, which is within the typical 0 to 5bps range for retail orders. I used basis points rather than fixed amounts so costs scale with the share price. Costs always go against the trader, so buys fill slightly above the quoted price and sells slightly below.

**Costs:** Slippage does not change based on order size or candle volume. This means a large order costs the same per share as a small one, which is unrealistic. There is also no FX fee. See decision 7.

**Date:** 2026-09-19


## 7. Account currency 

**Decision:** The account uses USD.

**Rejected:** A GBP account with currency conversion, which would be more realistic for a UK user.

**Reason:** All instruments are US stocks priced in dollars. A GBP account would need a 0.15% FX fee on both sides of each trade and a GBP/USD exchange rate for every trade date. This would require another data source and provider to maintain, so I chose to leave it out.

**Costs:** This is unrealistic for UK users, as FX fees are actually the biggest cost for UK retail investors buying US stocks. Adding a currency field to Portfolio later would make it possible to support this without major changes.

**Date:** 2026-09-19


## 8. FIFO cost basis

**Decision:** Sells use the oldest shares first.

**Rejected:** Average cost and choosing specific shares to sell.

**Reason:** Average cost is simpler to code, but you lose track of which shares were sold and when they were bought. Choosing specific shares is what real brokers offer, but it would need extra UI. FIFO is a common default and always gives the same result for the same trades. This matters because trades are also hashed into the ledger.

**Costs:** Each Position has to store a list of purchases instead of one average price. When selling, I work through the oldest purchases first and split the last one if the quantity does not divide evenly. That is more code and more tests than average cost would need.

**Date:** 2026-09-19


## 9. Limit orders reject rather than rest 

**Decision:** A limit order that cannot be filled at the current price is rejected straight away.

**Rejected:** Keeping the order open until the price reaches the limit.

**Reason:** Keeping orders open would need the simulation clock from decision 5, which does not exist. Without time moving forward, an open order would never fill and would just sit there. Rejecting it is clearer about what the simulator can and cannot do. The limit is checked against the final price after costs, not the quoted price, because that is what the user actually pays.

**Costs:** This is not how real limit orders work, so users may expect their orders to stay open instead of being rejected. This can be revisited if replay is added later.

**Date:** 2026-09-20


## 10. Floats in the JSON API 

**Decision:** Decimals are converted to floats only when sending data through the JSON API.

**Rejected:** Sending decimals as strings and formatting them in JavaScript.

**Reason:** JSON does not support Decimal values. Everything inside the app uses Decimal, including the engine, database and hashing. They are only converted to floats when sent out for display. The chart library and `toFixed(2)` both need numbers. Incoming JSON uses `parse_float=Decimal` to make sure floats never enter the engine.

**Costs:** Displayed values may differ from the stored values by a very small rounding amount. Nothing is calculated from the float, it is only shown, so this does not affect any results.

**Date:** 2026-09-17


## 11. Hash-chained trade ledger

**Decision:** Every trade is added to a ledger table. Each row’s hash is made from the previous row’s hash plus the trade data. A verify endpoint checks the chain and reports the first row where something is wrong.

**Rejected:** Hashing each trade separately without linking them, or simply trusting the database.

**Reason:** Hashing trades separately can detect changes to a row, but not if a row is deleted. Linking the hashes catches both because changing one trade also makes every row after it invalid. Trade data must always be converted into the same format to keep the hashes consistent. This means sorting keys, removing extra spaces, storing prices as strings with 8 decimal places and using integer timestamps. A schema version is also included so the format can change later without affecting older records. I used SHA-256 because MD5 and SHA-1 both have practical collision attacks.

**Costs:** This can detect changes but cannot prevent them. Anyone with access to the database and the code could rebuild the entire chain, making it look valid again. Trades are only kept unchanged because I have not added a way to edit them, not because the database prevents it. Checking the chain also gets slower as more trades are added. 

**Date:** 2026-10-26    


## 12. Test database

**Decision:** Tests use an in memory SQLite database instead of Neon.

**Rejected:** Using a Neon test database.

**Reason:** Neon's connection pooler keeps old connections open, which stopped Django from deleting the test database between runs and caused the tests to fail. This is an exception to decision 4, which was about keeping decimal handling the same in development and production. The important decimal tests use SimpleTestCase and do not need a database anyway.

**Costs:** Database tests do not run against Postgres, so a bug specific to Postgres could go unnoticed locally and appear in production.

**Date:** 2026-10-20


## 13. Hosting region

**Decision:** Render is hosted in Frankfurt and Neon in London.

**Rejected:** Hosting both in the same region.

**Reason:** Frankfurt was the closest region available on my Render plan.

**Costs:** Every database query has to travel between regions, adding extra loading time to each page.

**Date:** 2026-08-24