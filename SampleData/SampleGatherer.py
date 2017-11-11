
# Gathers samples from GDAX when you spec
# -i inst -f start date -t end date -s candlesize in seconds
# don't forget theres a "200 candle max..."
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


def runprint():
    args = parse_args()
    instrument = str(args.instrument)
    fromdate = str(args.fromdate)
    todate = str(args.todate)
    gran = int(args.seconds)
    candlesize = options[gran]
    data0 = client.get_product_historic_rates(instrument, start=fromdate, end=todate, granularity=gran)
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