from __future__ import (absolute_import, division, print_function)
import gdax
import datetime
import argparse
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds
client = gdax.PublicClient()
data0 = client.get_product_historic_rates('BTC-USD', start='2017-08-01', granularity=60*60*24)
frame = pd.DataFrame(data=data0,columns=['Time','Low','High','Open','Close','Volume'])
frame['Time'] = pd.to_datetime(frame['Time'], unit='s')
frame=frame.sort_values(by=['Time'])
frame = frame.set_index('Time') 


def __init__(self):
 self._addobserver(True, bt.observers.BuySell)


class Swinger(bt.Indicator):
 lines = ('swings', 'signal')
 params = (('period',7),)
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
    params = (('pfast', 1), ('pslow', 5),)
    def __init__(self):
        sma1, sma2 = bt.ind.SMA(period=self.p.pfast), bt.ind.SMA(period=self.p.pslow)
        self.signal_add(bt.SIGNAL_LONG, bt.ind.CrossOver(sma1, sma2))


def runstrat():
    args = parse_args()
    cerebro = bt.Cerebro()
    cerebro.addstrategy(St)
    cerebro.addstrategy(SmaCross)
    data = bt.feeds.PandasData(dataname=args.data)
    cerebro.resampledata(data,
                         timeframe=bt.TimeFrame.Ticks,
                         compression=args.compression)
    cerebro.addobserver(bt.observers.BuySell)
    cerebro.addobserver(bt.observers.Value)
    cerebro.run(stdstats=False)
    #if args.plot is not True:
    if args.plot:  # Plot if requested to
        cerebro.addobserver(bt.observers.BuySell)
        cerebro.addobserver(bt.observers.Value)
        cerebro.plot(style='line', plotbelow=False)
    cerebro.plot()

def parse_args():
 parser = argparse.ArgumentParser(
  formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  description='BidAsk to OHLC')
 parser.add_argument('--data', required=False, default=frame,help='Data file to be read in')
 parser.add_argument('--compression', required=False, default=2, type=int,help='How much to compress the bars')
 parser.add_argument('--plot', required=False, action='store_true', help='Plot the vars')
 return parser.parse_args()
'''  parser.add_argument('--smaperiod', required = False, action ='store',
                    type=int, default=30,
                    help=('Period of the moving average'))
 parser.add_argument('--exitperiod', required =False, action='store',
                    type=int,default=5,
                    help=('Period for the exit control SMA'))
 parser.add_argument('--signal', required = False, action='store',
                    default = MAINSIGNALS.keys()[0], choices=MAINSIGNALS,
                    help = ('Signal type to use for the main signal'))
 parser.add_argument('--exitsignal', required= False, action ='store',
                    default= None, choices = EXITSIGNALS,
                    help=('Signal type to use for the exit signal'))
 parser.add_argument('--fromdate',required=False,default=None,
                    help=("Ending date in YYYY-MM-DD"))
 parser.add_argument('--todate',required = False, default =None,
                    help=('Starting date similar form'))
 parser.add_argument('--cash',required=False,action='store',
                    type=float,default=50000, '''
'''                     help=('Cash to start with'))
 parser.add_argument('--plot','-p', nargs='?',required=False,
                    metavar='kwags',const=True,
                    help=('No')) '''
 ''' if pargs is not None:
     return parser.parse_args(pargs) '''
 #parser.add_argument('--plot','-p', nargs='?',required=False,
 #                   metavar='kwargs',const=True,
  #                  help=('Plot the read data applying any kwargs passed\n'
   ##                'For example:\n'
     #               '\n'
      #              ' --plot style = "Candle" \n'))
if __name__ == '__main__':
    runstrat()