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
pd.options.display.float_format = '{:0.2f}.'format
symbol='BTC-USD'
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


from __future__ import (absolute_import, division, print_function)
import gdax
import datetime
import argparse
import pandas as pd

now = datetime.datetime.now()
client = gdax.PublicClient()
# hack you suck
def five():
    return '5min'
def fifteen():
    return '15min'
def hour():
    return 'hour'
def day():
    return 'day'
def week():
    return 'week'
options = {300: five,
           900: fifteen,
           3600: hour,
           86400: day,
           2678400: week}
import requests


class PublicClient(object):
    """GDAX public client API.

    All requests default to the `product_id` specified at object
    creation if not otherwise specified.

    Attributes:
        url (Optional[str]): API URL. Defaults to GDAX API.

    """

    def __init__(self, api_url='https://api.gdax.com'):
        """Create GDAX API public client.

        Args:
            api_url (Optional[str]): API URL. Defaults to GDAX API.

        """
        self.url = api_url.rstrip('/')

    def get_product_historic_rates(self, product_id, start=None, end=None,
                                   granularity=None):
        """Historic rates for a product.

        Rates are returned in grouped buckets based on requested
        `granularity`. If start, end, and granularity aren't provided,
        the exchange will assume some (currently unknown) default values.

        Historical rate data may be incomplete. No data is published for
        intervals where there are no ticks.

        **Caution**: Historical rates should not be polled frequently.
        If you need real-time information, use the trade and book
        endpoints along with the websocket feed.

        The maximum number of data points for a single request is 200
        candles. If your selection of start/end time and granularity
        will result in more than 200 data points, your request will be
        rejected. If you wish to retrieve fine granularity data over a
        larger time range, you will need to make multiple requests with
        new start/end ranges.

        Args:
            product_id (str): Product
            start (Optional[str]): Start time in ISO 8601
            end (Optional[str]): End time in ISO 8601
            granularity (Optional[str]): Desired time slice in seconds

        Returns:
            list: Historic candle data. Example::
                [
                    [ time, low, high, open, close, volume ],
                    [ 1415398768, 0.32, 4.2, 0.35, 4.2, 12.3 ],
                    ...
                ]

        """
        params = {}
        if start is not None:
            params['start'] = start
        if end is not None:
            params['end'] = end
        if granularity is not None:
            params['granularity'] = granularity
        r = requests.get(self.url + '/products/{}/candles'
                         .format(product_id), params=params)
        # r.raise_for_status()
        return r.json()

def fetch_timeseries(symbol,dir_name='data',use_cache=True):
    args = parse_args()
    instrument = str(args.instrument)
    fromdate = str(args.fromdate)
    todate = str(args.todate)
    gran = int(args.seconds)
    candlesize = options[gran]
    if not os.path.exists(dir_name):
        os.makedirs(dir_name):
    timeseries_cache = os.path.join(dir_name, symbol+'csv')
    if os.path.isfile(timeseries_cache) and use_cache:
        pass
        else:
            data0 = client.get_product_historic_rates(symbol,start=fromdate,end=todate,granularity=86400)
            ts = pd.read_json(data0,typ='series',orient='records')
            ts.to_csv(timeseries_cache,encoding='utf-8')
    ts = pd.read_csv(timeseries_cache,index_col='Date',parse_dates=True)
    ts=_adj_column_names(ts)
    return(ts)
    # labels = ['Time','Low','High','Open','Close','Volume']
    frame = pd.DataFrame(data=data0, columns=['Time','Low','High','Open','Close','Volume'])
    
    frame['Time'] = pd.to_datetime(frame['Time'], unit='s')
    frame = frame.sort_values(by=['Time'])
    filename = str(args.instrument) + '_' + str(args.fromdate)+'_'+candlesize()
    frame = frame.set_index('Time')
    frame.to_csv(filename +'.csv')


def parse_args():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='Collect Sample Data')
    parser.add_argument('--fromdate', '-f', default='2014-01-01',
                        help=("Starting date in YYYY-MM-DD"))
    parser.add_argument('--todate', '-t', required=False, default=(str(now.year) + '-' + str(now.month)+ '-' + str(now.day)),
                        help=('Ending date similar form'))
    parser.add_argument('--instrument','-i', type=str, default='BTC-USD', help='Choose your instrument')
    parser.add_argument('--seconds','-s', default=60*60*24, help='granularity in sec - default day candles')
    return parser.parse_args()
if __name__ == '__main__':
    runprint()
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