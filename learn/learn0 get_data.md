# learn00 get_data 获取数据

在正式使用backtrader之前, 第0步是需要先获取数据, 其他工作才能进行下去. 
并且获取数据并不仅限于供给backtrader使用, 也可以用于其他分析或省去翻N年前的K线数据的麻烦.

这里介绍几个获取数据的库, 和使用示例, 以供参考.

## 1. AKShare

> https://akshare.akfamily.xyz/introduction.html

AKShare数据非常全面, 主要通过东方财富网的数据, 涵盖A股, B股, H股, 美股, 期货等市场的实时行情, 历史数据和财务指标.

- 但AKShare只提供日线, 周线和月线数据, 不提供更细的数据, 涉及日内交易的部分无法使用.

```python
import akshare as ak

df = ak.stock_zh_a_hist(
        symbol="600519",
        period="daily",
        start_date="20200101",
        end_date="20231231",
        adjust="qfq"  # 前复权
)

print(df)
```

## 2. BaoStock

> http://baostock.com/

BaoStock是一个更专注于A股市场的平台, 它的优势在于可以获取5分钟级别的K线数据, 并且实测接口快于AKShare.

```python
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
```

## 3. Yahoo Finance

> https://github.com/ranaroussi/yfinance

Yahoo Finance提供全球金融市场的数据, 且历史数据完整(尤其美股市场), 提供分钟级别的数据.

- Yahoo Finance对于A股数据支持较差, 并且在国内直连的稳定性差, 经常报错 'too many request', 使用代理的情况下依旧不能稳定获取数据, 故放弃使用, 这里仅作示例参考

```python
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
```
