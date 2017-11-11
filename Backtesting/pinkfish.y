%matplotlib inline
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import datetime
from talib.abstract import *
import pinkfish as pf

# format price data
pd.options.display.float_format = '{:0.2f}'.format

# Double the DPI, so we are making 2x plots:
matplotlib.rcParams['savefig.dpi'] = 2 * matplotlib.rcParams['savefig.dpi']

symbol = '^GSPC'
#symbol = 'SPY'
#symbol = 'DIA'
#symbol = 'QQQ'
#symbol = 'IWM'
#symbol = 'TLT'
#symbol = 'GLD'
#symbol = 'AAPL'
#symbol = 'BBRY'
capital = 10000
start = datetime.datetime(2000, 1, 1)
end = datetime.datetime(2015, 5, 1)
ts = pf.fetch_timeseries(symbol)
ts.head()
ts = pf.select_tradeperiod(ts, start, end, use_adj=True)
ts.head()
sma50 = SMA(ts, timeperiod=50)
ts['sma50'] = sma50

sma200 = SMA(ts, timeperiod=200)
ts['sma200'] = sma200
fig = plt.figure()
axes = fig.add_subplot(111,  ylabel='Price in $')

ts['close'].plot(ax=axes, label='close', color='k')
ts['sma50'].plot(ax=axes, label='sma50', color='r')
ts['sma200'].plot(ax=axes, label='sma200', color='b')
plt.legend(loc='best')
tlog = pf.TradeLog()
dbal = pf.DailyBal()
cash = capital
shares = 0
start_flag = True

import time
t0 = time.time()


for i in range(len(ts.index)):

    date = ts.index[i]
    high = ts['high'][i]
    low = ts['low'][i]
    close = ts['close'][i]
    sma50 = ts['sma50'][i]
    sma200 = ts['sma200'][i]

    if pd.isnull(sma200) or ts.index[i] < start:
        continue
    elif start_flag:
        start_flag = False
        # set start and end
        start = ts.index[i]
        end = ts.index[-1]

    if tlog.num_open_trades() == 0:
        # buy?
        if sma50 > sma200 and ts['sma50'][i-1] <= ts['sma200'][i-1]:

            # calculate shares
            shares, cash = tlog.calc_shares(cash, close)

            # enter buy in trade log
            tlog.enter_trade(date, close, shares)
            print("{0} BUY  {1} {2} @ {3:.2f}".format(date, shares, symbol, close))

            # record daily balance
            dbal.append(date, high, low, close, shares, cash, pf.TradeState.OPEN)

        else:
            dbal.append(date, high, low, close, shares, cash, pf.TradeState.CASH)

    else:
        # sell?
        if (sma50 < sma200 and ts['sma50'][i-1] >= ts['sma200'][i-1]) or (i == len(ts.index) - 1):

            # enter sell in trade log
            idx = tlog.exit_trade(date, close)
            shares = tlog.get_log()['qty'][idx]
            print("{0} SELL {1} {2} @ {3:.2f}".format(date, shares, symbol, close))

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
benchmark = pf.Benchmark(symbol, capital, start, end)
benchmark.run()
benchmark.tlog, benchmark.dbal = benchmark.get_logs()
benchmark.stats = benchmark.stats()
pf.print_full(benchmark.stats)
pf.plot_equity_curve(dbal, benchmark=benchmark.dbal)
pf.plot_trades(dbal, benchmark=benchmark.dbal)
metrics = ('annual_return_rate',
           'max_closed_out_drawdown',
           'drawdown_annualized_return',
           'drawdown_recovery',
           'best_month',
           'worst_month',
           'sharpe_ratio',
           'sortino_ratio',
           'monthly_std')
df = pf.plot_bar_graph(stats, benchmark.stats, *metrics)
df