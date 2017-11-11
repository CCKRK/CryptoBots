from __future__ import (absolute_import, division, print_function)
from __future__ import unicode_literals

import datetime
import argparse
import pandas as pd
#import backtrader as bt
#import backtrader.feeds as btfeeds
#import backtrader.indicators as btind
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from talib.abstract import *
import pinkfish as pf
import requests
import Wrappers
import time
client = Wrappers.PublicClient()
unit = 60*60*24
hour = datetime.timedelta(minutes=60)
now = datetime.datetime.now()
start = now - hour
print((now - start).seconds / unit)
print(now.isoformat())
print(start.isoformat())
product = "{}-{}".format("BTC", "USD")
data0 = [['date','low','high','open','close','volume']]
data0 = client.get_product_historic_rates(
                                    product,
                                    start=start.isoformat(),
                                    granularity=60*60*24)

ts = pd.DataFrame(data=data0, columns=['date','low','high','open','close','volume'])
ts['date'] = pd.to_datetime(ts['date'], unit='s')
ts = ts.sort_values(by=['date'])
ts = ts.set_index('date')
ts.index = pd.DatetimeIndex(ts.index)
capital = 10000
start = datetime.datetime(2017, 5, 13)
end = datetime.datetime(2017, 11, 11)

ts = pf.select_tradeperiod(ts, start, end, use_adj=False)

sma1 = SMA(ts, timeperiod=2)
ts['sma1'] = sma1

sma5 = SMA(ts, timeperiod=5)
ts['sma5'] = sma5

fig = plt.figure()
axes = fig.add_subplot(111,  ylabel='Price in $')

ts['close'].plot(ax=axes, label='close', color='k')
ts['sma1'].plot(ax=axes, label='sma1', color='r')
ts['sma5'].plot(ax=axes, label='sma5', color='b')
plt.legend(loc='best')

tlog = pf.TradeLog()
dbal = pf.DailyBal()

cash = capital
shares = 0
start_flag = True

t0 = time.time()

for i in range(len(ts.index)):
    date = ts.index[i]
    high = ts['high'][i]
    low = ts['low'][i]
    close = ts['close'][i]
    sma1 = ts['sma1'][i]
    sma5 = ts['sma5'][i]

    if pd.isnull(sma5) or ts.index[i] < start:
        continue
    elif start_flag:
        start_flag = False
        # set start and end
        start = ts.index[i]
        end = ts.index[-1]

    if tlog.num_open_trades() == 0:
        # buy?
        if sma1 > sma5 and ts['sma1'][i-1] <= ts['sma5'][i-1]:

            # calculate shares
            shares, cash = tlog.calc_shares(cash, close)

            # enter buy in trade log
            tlog.enter_trade(date, close, shares)
            print("{0} BUY  {1} {2} @ {3:.2f}".format(date, shares, 'BTC', close))

            # record daily balance
            dbal.append(date, high, low, close, shares, cash, pf.TradeState.OPEN)

        else:
            dbal.append(date, high, low, close, shares, cash, pf.TradeState.CASH)

    else:
        # sell?
        if (sma1 < sma5 and ts['sma1'][i-1] >= ts['sma5'][i-1]) or (i == len(ts.index) - 1):

            # enter sell in trade log
            idx = tlog.exit_trade(date, close)
            shares = tlog.get_log()['qty'][idx]
            print("{0} SELL {1} {2} @ {3:.2f}".format(date, shares, 'BTC', close))

            # record daily balance
            dbal.append(date, high, low, close, shares, cash, pf.TradeState.CLOSE)   
            
            # update cash
            cash = tlog.calc_cash(cash, close, shares)
    
        else:
            dbal.append(date, high, low, close, shares, cash, pf.TradeState.HOLD)

t1 = time.time()
total = t1-t0
print(total)
tlog = tlog.get_log()
tlog.tail(100)
dbal = dbal.get_log()

dbal.tail()
stats = pf.stats(ts, tlog, dbal, start, end, capital)
pf.print_full(stats)
benchmark = pf.Benchmark('SPY', capital, start, end)
benchmark.run()
benchmark.stats = benchmark.stats()
pf.print_full(benchmark.stats)
pf.plot_equity_curve(dbal)
pf.plot_trades(dbal)

metrics = ('annual_return_rate',
           'max_closed_out_drawdown',
           'drawdown_annualized_return',
           'drawdown_recovery',
           'best_month',
           'worst_month',
           'sharpe_ratio',
           'sortino_ratio',
           'monthly_std')
df = pf.plot_bar_graph(stats, *metrics)
plot.show()
df
plot.show()