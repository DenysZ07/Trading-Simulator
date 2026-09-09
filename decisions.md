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