# learn01 构建一个简单回测示例

> https://www.backtrader.com/docu/

## 1.数据源 Data Feed

backtrader中数据格式是`Data Feed`, 通常我们的数据是CSV, Pandas DataFrame, 数据库数据或者其他格式. 需要转换为`Data Feed`
格式.

---

在这里使用`AKShare`股票数据, 获取`历史行情数据-东财`

> https://akshare.akfamily.xyz/data/stock/stock.html#id23

```python
import akshare as ak
import backtrader as bt
import pandas as pd

# 获取股票数据, 这个数据是pandas DataFrame格式
df = ak.stock_zh_a_hist(
    symbol="600519",
    period="daily",
    start_date="20200101",
    end_date="20231231",
    adjust="qfq"  # 前复权
)
print(df)
# 转为backtrader所需的样式
# backtrader要求数据的列名为['date', 'open', 'high', 'low', 'close', 'volume', 'openinterest']


df.index = pd.to_datetime(df['日期'])
df = df[['开盘', '最高', '最低', '收盘', '成交量']]
# df.columns = ['open', 'high', 'low', 'close', 'volume']
print(df)

data = bt.feeds.PandasData(
    dataname=df,
    open='开盘',
    high='最高',
    low='最低',
    close='收盘',
    volume='成交量'
)
```

## 2. 策略 Strategy

策略是回测的核心, 定义交易逻辑和买卖规则.

```python
# 构建一个简单的均线策略
class MyStrategy(bt.Strategy):
    params = (
        ('period', 20),  # 均线周期
    )

    def __init__(self):
        # backtrader中有多种内置技术指标, 这里使用简单移动平均线
        self.ma = bt.indicators.MovingAverageSimple()

    # next方法是策略的核心, 每个bar都会调用一次
    def next(self):
        if self.datas[0].close[0] > self.ma[0]:
            # 如果当前价格高于20日均线，则买入
            self.order = self.buy(size=100)

        if self.datas[0].close[0] < self.ma[0]:
            # 如果当前价格低于20日均线，则卖出
            self.order = self.sell(size=100)
```

## 3. 大脑引擎 Cerebro

核心控制器, 协调所有组件的运行

```python
cerebro = bt.Cerebro()
cerebro.adddata(data)  # 添加数据
cerebro.addstrategy(MyStrategy)  # 添加策略
```

## 4. 经纪商 Broker

Broker中设置佣金与滑点, 现金与头寸

```python
cerebro.broker.setcash(1000000)  # 设置初始资金
cerebro.broker.setcommission(commission=0.001)  # 设置手续费
cerebro.broker.set_slippage_perc(perc=0.001)  # 设置滑点
```

## 5. 运行回测, 输出结果, 绘制图表

```python
results = cerebro.run()
print(f'回测结束资金: {cerebro.broker.getvalue():.2f} 元')
cerebro.plot()  # 绘制图表
```



