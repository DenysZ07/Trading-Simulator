from django.test import SimpleTestCase
from .orders import Portfolio, Order, Side, Trade, Position, Lot, OrderType
from .exceptions import OrderRejected
from .execution import fill_order
from decimal import Decimal

class TradingTests(SimpleTestCase):

    def setUp(self):
        self.test_portfolio = Portfolio(Decimal("1000"))


    test_order_fail = Order("AAPL", Side.BUY, 10, OrderType.MARKET)
    test_order_pass = Order("AAPL", Side.BUY, 2, OrderType.MARKET)


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

