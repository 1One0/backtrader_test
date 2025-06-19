# learn00 get_data 获取数据

在正式使用backtrader之前, 第0步是需要先获取数据, 其他工作才能进行下去. 
并且获取数据并不仅限于供给backtrader使用, 也可以用于其他分析或省去翻N年前的K线数据的麻烦.

这里介绍几个获取数据的库, 和使用示例, 以供参考.

PS: A股市场推荐使用BaoStock, 数据为等比前复权数据, 并且提供5分钟级的数据.

## 普通前复权与等比前复权

例如一只股票股价一直为2元, 每年分红1元, 普通前复权的价格会在每年分红后将过往的价格除去分红的价格, 
也就是说2年之后最初的2元股价在前复权下会变为0元, 3年后最初的股价会变为-1元.

这直观反应了分红对于持有者的成本的影响, 但对于投资分析来说, 这个前复权价格不能代表当时的股票价值. 
比如上述例子中, 出现了负价格的股票, 那收益最大的策略应该是全仓这种负价格的股票, 而因为价格是负的, 永远没有"全仓"的上限, 左脚踩右脚直接无限收益了.

所以这普通前复权无法反应真实价值, 这里就需要引入等比复权的概念.

等比前复权的价格等效于**分红在除权日按除权后价格再投资**. 
还是上面的例子, 最开始购入1股, 1年后分红再投, 此时拥有2股, 2年后分红再投, 则拥有了4股, 同理3年后拥有8股. 
这样算得的前复权价格为0.25, 0.5, 1元, 这个数字才符合当时的股票价值, 也更符合投资分析的逻辑.

- 如何判断自己平时查看的数据是哪种前复权? 
  - 查看**600000 浦发银行**的前复权数据, 普通前复权数据在2006年之前的股价会变为负数, 而等比前复权的股价永远大于0.
  - 东方财富网, 同花顺等常用的A股数据平台提供的前复权数据都是普通前复权, 雪球和Wind这些更专业的平台提供的数据是等比前复权.

## 1. BaoStock

> http://baostock.com/

BaoStock是一个更专注于A股市场的平台, 它的优势在于可以获取5分钟级别的K线数据, 并且实测接口快于AKShare. 并且提供的前复权数据为等比复权数据.

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

## 2. AKShare

> https://akshare.akfamily.xyz/introduction.html

AKShare数据非常全面, 主要通过东方财富网的数据, 涵盖A股, B股, H股, 美股, 期货等市场的实时行情, 历史数据和财务指标.

- AKShare只提供日线, 周线和月线数据, 不提供更细的数据, 涉及日内交易的部分无法使用.

- AKShare的前复权是普通的前复权, 而不是等比前复权

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

## 3. Yahoo Finance

> https://github.com/ranaroussi/yfinance

Yahoo Finance提供全球金融市场的数据, 且历史数据完整(尤其美股市场), 提供分钟级别的数据.

- Yahoo Finance对于A股数据支持差, 并且在国内直连的稳定性差, 经常报错 'too many request', 使用代理的情况下依旧不能稳定获取数据, 故放弃使用, 这里仅作示例参考

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




