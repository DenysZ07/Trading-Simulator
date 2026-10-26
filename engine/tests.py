from django.test import SimpleTestCase
from .orders import Portfolio, Order, Side, Trade, Position, Lot, OrderType
from .exceptions import OrderRejected
from .execution import fill_order
from decimal import Decimal
from .pnl import unrealised_pnl, realised_pnl
from .ledger import START_OF_CHAIN, serialise_trade, chain_digest

class TradingTests(SimpleTestCase):

    def setUp(self):
        self.test_portfolio = Portfolio(Decimal("1000"))
        self.test_portfolio2 = Portfolio(Decimal("1000"))
        self.test_portfolio3 = Portfolio(Decimal("1000"))
        self.test_portfolio4 = Portfolio(Decimal("1000"))


    test_order_fail = Order("AAPL", Side.BUY, 10, OrderType.MARKET)
    test_order_pass = Order("AAPL", Side.BUY, 2, OrderType.MARKET)

    test_order_buy_1 = Order("MSFT", Side.BUY, 10, OrderType.MARKET)
    test_order_buy_2 = Order("MSFT", Side.BUY, 10, OrderType.MARKET)
    test_order_sell = Order("MSFT", Side.SELL, 15, OrderType.MARKET)

    test_limit_buy = Order("GOOGL", Side.BUY, 1, OrderType.LIMIT, Decimal("342.90"))


    def test_buy_order_filled(self):
        fill_order(self.test_portfolio, self.test_order_pass, Decimal("332.41"), 1700000000)
        self.assertEqual(self.test_portfolio.cash, Decimal("334.980554"))
        self.assertEqual(len(self.test_portfolio.trades), 1)


    def test_buy_order_rejected(self):
        with self.assertRaises(OrderRejected):
            fill_order(self.test_portfolio, self.test_order_fail, Decimal("332.41"), 1700000000)



    def test_rejection_leaves_portfolio_unchanged(self):
        with self.assertRaises(OrderRejected):
            fill_order(self.test_portfolio, self.test_order_fail, Decimal("332.41"), 1700000000)

        self.assertEqual(self.test_portfolio.cash, Decimal("1000"))
        self.assertEqual(len(self.test_portfolio.trades), 0)
        self.assertEqual(len(self.test_portfolio.positions), 0)


    def test_sell_oldest_lots_first(self):

        fill_order(self.test_portfolio2, self.test_order_buy_1, Decimal("40"), 1700000000)
        fill_order(self.test_portfolio2, self.test_order_buy_2, Decimal("50"), 1700000000)
        fill_order(self.test_portfolio2, self.test_order_sell, Decimal("50"), 1700000000)

        self.assertEqual(len(self.test_portfolio2.positions["MSFT"].lots), 1)
        self.assertEqual(self.test_portfolio2.positions["MSFT"].lots[0].quantity, 5)
        self.assertEqual(self.test_portfolio2.positions["MSFT"].lots[0].price, Decimal("50.0150"))



    def test_limit_order_fill(self):

        fill_order(self.test_portfolio3, self.test_limit_buy, Decimal("342.75"), 1700000000)

        self.assertEqual(self.test_portfolio3.cash, Decimal("657.147175"))
        self.assertEqual(len(self.test_portfolio3.trades), 1)

    
    def test_limit_order_rejection(self):

        with self.assertRaises(OrderRejected):
            fill_order(self.test_portfolio3, self.test_limit_buy, Decimal("342.87"), 1700000000)



    def test_realised_pnl(self):
        fill_order(self.test_portfolio4, self.test_order_buy_1, Decimal("40"), 1700000000)
        fill_order(self.test_portfolio4, self.test_order_buy_2, Decimal("50"), 1700000000)
        fill_order(self.test_portfolio4, self.test_order_sell, Decimal("50"), 1700000000)

        self.assertEqual(realised_pnl(self.test_portfolio4), Decimal("99.58"))


    def test_unrealised_pnl(self):
        fill_order(self.test_portfolio4, self.test_order_buy_1, Decimal("40"), 1700000000)
        fill_order(self.test_portfolio4, self.test_order_buy_2, Decimal("50"), 1700000000)
        fill_order(self.test_portfolio4, self.test_order_sell, Decimal("50"), 1700000000)

        prices = {"MSFT": Decimal("60")}

    
        self.assertEqual(unrealised_pnl(self.test_portfolio4, prices), Decimal("49.925"))


class LedgerTests(SimpleTestCase):

    def make_trade(self, fill_price):
        return Trade(
            symbol="AAPL",
            side=Side.BUY,
            quantity=10,
            fill_price=Decimal(fill_price),
            timestamp=1700000000,
            commission=Decimal("0"),
            slippage=Decimal("0.10"),
            spread=Decimal("0.05"),
        )

    def test_same_trade_gives_same_digest(self):
        first = chain_digest(START_OF_CHAIN, serialise_trade(self.make_trade("50.00")))
        second = chain_digest(START_OF_CHAIN, serialise_trade(self.make_trade("50.00")))

        self.assertEqual(first, second)

    def test_one_penny_change_scrambles_digest(self):
        first = chain_digest(START_OF_CHAIN, serialise_trade(self.make_trade("50.00")))
        second = chain_digest(START_OF_CHAIN, serialise_trade(self.make_trade("50.01")))

        self.assertNotEqual(first, second)

        matching = sum(1 for a,b in zip(first.hex(), second.hex()) if a == b)
        self.assertLess(matching, 32)
