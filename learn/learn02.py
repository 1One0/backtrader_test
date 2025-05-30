import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import backtrader as bt
import matplotlib.pyplot as plt
import akshare as ak

# 对于matplot绘图的中文字体和符号进行设置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 设置负号正常显示


# 1. 获取数据
def get_data(stock_code: str, start_time='20240101', end_time='20250101'):
    df = ak.stock_zh_a_hist(
        symbol=stock_code,
        period="daily",
        start_date=start_time,
        end_date=end_time,
        adjust="qfq"
    )
    # print(df)

    # 设置索引/列名, 转为backtrader所需的样式
    df.index = pd.to_datetime(df['日期'])
    df = df[['开盘', '最高', '最低', '收盘', '成交量']]
    # df.columns = ['open', 'high', 'low', 'close', 'volume']
    # print(df)

    data = bt.feeds.PandasData(
        dataname=df,
        open='开盘',
        high='最高',
        low='最低',
        close='收盘',
        volume='成交量'
    )

    return data


# 2. 构建策略
# 设置一个简单的20日均线策略
class MyStrategy(bt.Strategy):
    params = (
        ('period', 20),  # 均线周期
        ('period2', 60),  # 参数2
    )

    def __init__(self):
        self.order = None
        self.ma = bt.indicators.MovingAverageSimple()
        # SMA是backtrader通过元类注册的别名
        self.ma1 = bt.indicators.SMA(self.data0, period=self.params.period2)
        self.ma2 = bt.indicators.SMA(self.data1, period=self.params.period2)


        # 添加分析器
        self.analyzers.returns = bt.analyzers.Returns()
        self.analyzers.drawdown = bt.analyzers.DrawDown()

    def next(self):
        if not self.position:
            if self.data.close[0] > self.ma[0]:
                # 如果当前价格高于20日均线，则买入
                self.order = self.buy(size=100)
        else:
            if self.data.close[0] < self.ma[0]:
                # 如果当前价格低于20日均线，则卖出
                self.order = self.sell(size=100)


# 作为对比, 构建一个买入持有策略
class HoldStrategy(bt.Strategy):
    def __init__(self):
        self.order = None

    def start(self):
        price = self.data.close[0]
        commission = self.broker.getcommissioninfo(self.data).p

        # 计算最大可买数量（考虑佣金+最小交易单位）
        max_possible = self.broker.get_cash() / (price * (1 + commission.commission))
        size = int(max_possible * 0.99)

        self.buy(size=size)


if __name__ == '__main__':
    # 3. 设置策略
    cerebro = bt.Cerebro()  # 创建大脑

    start_time = '20250101'  # 回测开始时间
    end_time = '20250501'  # 回测结束时间
    stock_code = '600519'  # 股票代码
    data = get_data(stock_code, start_time, end_time)  # 获取数据
    data2 = get_data('600036', start_time, end_time)

    cerebro.adddata(data, 'maotai')  # 添加数据
    cerebro.adddata(data2, 'zhaohang')

    cerebro.addstrategy(MyStrategy)  # 添加策略
    print(cerebro.datas[0])
    print(cerebro.datas[1])

    # 4. 设置broker
    cash = 100000  # 初始资金
    cerebro.broker.setcash(cash)  # 设置初始资金
    cerebro.broker.setcommission(commission=0.001)  # 设置手续费

    # 5. 执行回测
    print(f'初始资金: {cerebro.broker.getvalue():.2f} 元, 回测时间: {start_time} 至 {end_time}')
    results = cerebro.run()
    print(f'回测结束资金: {cerebro.broker.getvalue():.2f} 元')
    strat = results[0]

    # 6. 绘制图表
    cerebro.plot(style='candlestick')
