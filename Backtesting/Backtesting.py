from __future__ import (absolute_import, division, print_function)
import gdax
import datetime
import argparse
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
from backtrader.analyzers import (SQN, AnnualReturn, TimeReturn, SharpeRatio,
                                  TradeAnalyzer)
client = gdax.PublicClient()
data0 = client.get_product_historic_rates('BTC-USD', start='2017-08-01', granularity=60*60*24)
frame = pd.DataFrame(data=data0, columns=['Time','Low','High','Open','Close','Volume'])
frame['Time'] = pd.to_datetime(frame['Time'], unit='s')
frame = frame.sort_values(by=['Time'])
frame = frame.set_index('Time')


class LongShortStrategy(bt.Strategy):
    params = dict(
        period=15,
        stake=1000,
        printout=False,
        csvcross=False,
        onlylong=False
    )

    def start(self):
        pass

    def stop(self):
        pass

    def log(self, txt, dt=None):
        if self.p.printout:
            dt = dt or self.data.datetime[0]
            dt = bt.num2date(dt)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # add observers for Buy/Sell plot
        # self._addobserver(True, bt.observers.BuySell)
        # control operation entries
        self.orderid = None
        # these initialize SMAs and crossovers
        sma = btind.MovAv.SMA(self.data, period=self.p.period)
        self.signal = btind.CrossOver(self.data.close, sma)
        self.signal.csv = self.p.csvcross

    def next(self):
        # cannot place new orders (against myself)
        if self.orderid:
            return
        # bull cross
        if self.signal > 0.0:
            if self.position:
                self.log('Close SHORT, %.2f' % self.data.close[0])
                self.close()
            self.log('LONG Create, %.2f' % self.data.close[0])
            self.buy(size=self.p.stake)
        # bear cross
        elif self.signal < 0.0:
            if self.position:
                self.log('Close LONG, %.2f' % self.data.close[0])
                self.close()
            self.log('SHORT Create %.2f' % self.data.close[0])
            self.sell(size=self.p.stake)
    # controls orderbook status

    def notify_order(self, order):
        # waiting for fill
        if order.status in [bt.Order.Submitted, bt.Order.Accepted]:
            return
        # filled
        if order.status == order.Completed:
            if order.isbuy():
                buytxt = 'BUY COMPLETE, %.2f' % order.executed.price
                self.log(buytxt, order.executed.dt)
            else:
                selltxt = 'SELL COMPLETE, %.2f' % order.executed.price
                self.log(selltxt, order.executed.dt)
        # Cancels/EXP/margin trades
        elif order.status in [order.Expired, order.Canceled, order.Margin]:
            self.log('%s ,' % order.Status[order.status])
            pass
        # allow orders to resume
        self.orderid = None

    def notify_trade(self, trade):
        if trade .isclosed:
            self.log('Trade Profit, Gross %.2f, NET %.2f' %
                     (trade.pnl, trade.pnlcomm))
        elif trade.justopened:
            self.log('TRADE OPENED, Size %2d' % trade.size)

class Swinger(bt.Indicator):
 lines = ('swings', 'signal')
 params = (('period', 7),)
 def __init__(self):
  self.swing_range = (self.p.period * 2) + 1
  self.addminperiod(self.swing_range)
  def next(self):
#Get the highs/lows for the period
   highs = self.data.high.get(size=self.swing_range)
   lows = self.data.low.get(size=self.swing_range)
#check the bar in the middle of the range and check if greater than rest
  if highs.pop(self.p.period) > max(highs):
   self.lines.swings[-self.p.period] = 1 #add new swing
   self.lines.signal[0] = 1 #give a signal
  elif lows.pop(self.p.period) < min(lows):
   self.lines.swings[-self.p.period] = -1 #add new swing
   self.lines.signal[0] = -1 #give a signal
  else:
   self.lines.swings[-self.p.period] = 0
   self.lines.signal[0] = 0


class SMACloseSignal(bt.Indicator):
    lines = ('signal',)
    params = (('period', 30),)
    def __init__(self):
        self.lines.signal = self.data - bt.indicators.SMA(period=self.p.period)


class SMAExitSignal(bt.Indicator):
    lines = ('signal',)
    params = (('p1', 5), ('p2', 10),)
    def __init__(self):
        sma1 = bt.indicators.SMA(period=self.p.p1)
        sma2 = bt.indicators.SMA(period=self.p.p2)
        self.lines.signal = sma1 - sma2


class St(bt.Strategy):
    params = (('sma', False), ('period', 3))
    def __init__(self):
        if self.p.sma:
            self.sma = btind.SMA(self.data, period=self.p.period)
    def next(self):
        print(','.join(str(x) for x in [
        self.data.datetime.datetime(),
        self.data.open[0], self.data.high[0], 
        self.data.high[0], self.data.close[0],
        self.data.volume[0]]))


class SmaCross(bt.SignalStrategy):
    params = (('pfast', 15), ('pslow', 30))
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.pfast),
        bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))


def runstrat():
    args = parse_args()
    cerebro = bt.Cerebro()
    # can I add strategies like this...
    #cerebro.addstrategy(St)
    #cerebro.addstrategy(SmaCross)
    # this is where I will grab dates from args.. need ors
    if args.fromdate is not None:
        fromdate = datetime.datetime.strptime(args.fromdate, '%Y-%m-%d')
        todate = datetime.datetime.strptime(args.todate, '%Y-%m-%d')
    else:
        #fromdate = frame.index[0]
        #todate = frame.index[len(frame)-1]
        fromdate = datetime.datetime(2016,12,14)
        todate = datetime.datetime(2017,11,11)
    
    data = bt.feeds.PandasData(dataname=args.data, fromdate=fromdate,
                               todate=todate)
    # data resampling
    #cerebro.resampledata(data,
    #                     timeframe=bt.TimeFrame.Ticks,
    #                     compression=args.compression)
    cerebro.adddata(data)
    #cerebro.addstrategy(St)
    #cerebro.addstrategy(SmaCross)
    cerebro.addstrategy(LongShortStrategy,
                        period=args.period,
                        csvcross=False,
                        stake=args.stake)
    # im adding observers here for plot, is it working
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)
    # some sort of tframes dict
    tframes = dict(
        days=bt.TimeFrame.Days,
        weeks=bt.TimeFrame.Weeks,
        months=bt.TimeFrame.Months,
        years=bt.TimeFrame.Years)
    # Analyzers
    cerebro.addanalyzer(SQN)
    if args.legacyannual:
        cerebro.addanalyzer(AnnualReturn)
        cerebro.addanalyzer(SharpeRatio, legacyannual=True)
    else:
        cerebro.addanalyzer(TimeReturn, timeframe=tframes[args.tframe])
        cerebro.addanalyzer(SharpeRatio, timeframe=tframes[args.tframe])
    cerebro.addanalyzer(TradeAnalyzer)
    cerebro.addwriter(bt.WriterFile, csv=args.writercsv, rounding=4)
    cerebro.run(stdstats=False)
    # if args.plot is not True:
    if args.plot:  # Plot if requested to
        cerebro.addobserver(bt.observers.BuySell)
        cerebro.addobserver(bt.observers.Value)
        #cerebro.plot(style='line', plotbelow=False)
    cerebro.plot()

def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='BidAsk to OHLC')
    parser.add_argument('--data', required=False, default=frame, help='Data file to be read in')
    parser.add_argument('--compression', required=False, default=1, type=int,help='How much to compress the bars')
    parser.add_argument('--plot', required=False, action='store_true', help='Plot the vars')
    parser.add_argument('--period', default=15, type=int,
                        help='Period to apply to the SMA. Default 15')
 # return parser.parse_args()
    parser.add_argument('--fromdate', '-f', required=False, default=None,
                        help=("Ending date in YYYY-MM-DD"))
    parser.add_argument('--todate', '-t', required=False, default=None,
                        help=('Starting date similar form'))
    parser.add_argument('--writercsv', '-wcsv', action='store_true',
                        help='Tell the writer to produce a csv stream')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--tframe', default='days', required=False,
                       choices=['days', 'weeks', 'months', 'years'],
                       help='Timeframe for the port return/Sharpe calcs')
    group.add_argument('--legacyannual', action='store_true',
                       help='User legacy annual return analyzer')
    parser.add_argument('--stake', default=1, type=int,
                        help='Stake to apply in each operation')
    parser.add_argument('--cash',required=False, action='store',
                        type=float, default=50000,
                        help=('Cash to start with'))
    return parser.parse_args()

if __name__ == '__main__':
    runstrat()