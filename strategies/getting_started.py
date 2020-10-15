import os
import sys
import backtrader as bt
from datetime import datetime


class TestStrategy(bt.Strategy):
    def __init__(self):
        self.order = None

    def log(self, txt):
        dt = self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):

        # self.log('Close, %.2f' % self.datas[0].close[0])
        if self.order:
            return

        if not self.position:
            # buy if there are two consecutive down days
            if self.datas[0].close[0] < self.datas[0].close[-1]:
                if self.datas[0].close[-1] < self.datas[0].close[-2]:
                    self.log('BUY CREATE: %.2f' % self.datas[0].close[0])
                    self.order = self.buy()
        else:
            if len(self) >= self.bar_executed + 5:
                self.log('SELL CREATE: %.2f' % self.datas[0].close[0])
                self.order = self.sell()


    def notify_order(self, order):
        if order.status in [order.Accepted, order.Submitted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED: %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED: %.2f' % order.executed.price)

            self.bar_executed = len(self)

        self.order = None


data = bt.feeds.YahooFinanceCSVData(
    dataname=os.path.join(sys.path[0], r'../data/K.csv'),
    fromdate=datetime(1990, 1, 1),
    todate=datetime(2020, 1, 1),
    adjclose=True
)

cerebro = bt.Cerebro()
start_cash = 1_000_000
cerebro.broker.set_cash(start_cash)
cerebro.adddata(data)
cerebro.addstrategy(TestStrategy)
cerebro.addsizer(bt.sizers.FixedSize, stake=10000)
cerebro.run()
print('p/l $%.2f' % (cerebro.broker.getvalue() - start_cash))