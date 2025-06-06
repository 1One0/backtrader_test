# learn0 获取数据

# AKShare
import akshare as ak

df = ak.stock_zh_a_hist(
        symbol="600519",
        period="daily",
        start_date="20200101",
        end_date="20211231",
        adjust="qfq"  # 前复权
)

print(df)

# BaoStock
import baostock as bs
import pandas as pd

lg = bs.login()
print('login respond error_code:' + lg.error_code)
print('login respond  error_msg:' + lg.error_msg)

rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,peTTM,pbMRQ,psTTM,pcfNcfTTM,isST",
    start_date='2020-01-01',
    end_date='2020-12-31',
    frequency="d",
    adjustflag="2"      # adjustflag: 复权类型，1：后复权  2：前复权  3：不复权  默认为3
)

bs.logout()

# baostock获取的数据是一个ResultData对象, 如果需要转换为DataFrame，可以使用以下方法
data_list = []
while (rs.error_code == '0') & rs.next():
    # 获取一条记录，将记录合并在一起
    data_list.append(rs.get_row_data())
df = pd.DataFrame(data_list, columns=rs.fields)

print(df)

# Yahoo Finance
import yfinance as yf
import os

proxy = '127.0.0.1:1082'
os.environ['http_proxy'] = proxy
os.environ['https_proxy'] = proxy

start_date = "2020-01-01"
end_date = "2020-12-31"

# 用 download 方法获取数据, 更稳定
df = yf.download("AAPL", start=start_date, end=end_date, interval="1d", progress=False)
print(df)
