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


def runprint():
    args = parse_args()
    instrument = str(args.instrument)
    fromdate = str(args.fromdate)
    todate = str(args.todate)
    gran = int(args.seconds)
    data0 = client.get_product_historic_rates('BTC-USD', start=fromdate, end=todate, granularity=gran)
    # labels = ['Time','Low','High','Open','Close','Volume']
    frame = pd.DataFrame(data=data0, columns=['Time','Low','High','Open','Close','Volume'])
    frame['Time'] = pd.to_datetime(frame['Time'], unit='s')
    frame = frame.sort_values(by=['Time'])
    # filename = args.instrument + '-' + frame['Time'][0]+'-'+frame['Time'][len(frame)-1]
    filename = str(args.instrument) + '-' + str(args.fromdate)
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