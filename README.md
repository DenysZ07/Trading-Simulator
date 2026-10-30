# Trading Simulator

A stock trading simulator built using real market data. 

You can place market and limit orders against two years of real daily prices for five US equities, track your positions and P&L, and verify the trade history has not been tampered with. There is no sign up, a portfolio is created for you on your first visit.

**Live:** https://trading-sim.com/

![Trading Simulator](docs/chart.png)

## What it does

- Stores daily price data for five US stocks, uses Alpaca as the data source and stored in Postgres
- Candlestick charts with the ability to switch between the stocks 
- Market and limit orders, with spread and slippage charged on every fill
- FIFO cost basis, so realised P&L can be traced back to the purchase it came from
- Every trade is written to a hash-chained ledger so editing or deleting a past trade will break the chain, and the verify button finds the exact row
- Market data is kept separate from the rest of the application, so the data source can be swapped without rewriting everything around it
- Uses `Decimal` for prices instead of floats to avoid rounding issues

## Not built yet

- Accounts and sign in. The portfolios are currently tied to a browser session.
- Intraday prices, so orders fill at the latest daily close.
- Resting limit orders, which are rejected rather than held open.


## Stack 

|||
|---|---|
| Backend | Django 6.1, Python 3.13 |
| Database | PostgreSQL (Neon) |
| Market data | Alpaca Market Data API |
| Charting | Lightweight Charts 5.2.1 |
| Hosting | Render, Cloudflare DNS |

## Hosting locally 

```bash
git clone https://github.com/DenysZ07/Trading-Simulator.git
cd Trading-Simulator

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env # then fill in your own values

python manage.py migrate
python manage.py backfill
python manage.py runserver
```

You will need an Alpaca API key. The free plan is enough to run the project. 

## Tests

```bash 
python manage.py test
```

The market data provider has a small set of tests that run against both Alpaca and a fake provider. This makes it easier to add or change the data source without having to rewrite the tests. 

## Design decisions

See [decisions.md](decisions.md)