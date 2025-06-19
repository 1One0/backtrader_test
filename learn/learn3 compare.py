import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import backtrader as bt
import matplotlib.pyplot as plt
import baostock as bs

# 对于matplot绘图的中文字体和符号进行设置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 设置负号正常显示


# 1. 获取数据
def get_data(code: str, start_time='2020-01-01', end_time='2025-01-01'):
    lg = bs.login()
    print('login respond error_code:' + lg.error_code)
    print('login respond error_msg:' + lg.error_msg)

    # 获取贵州茅台(600519)的日线数据
    rs = bs.query_history_k_data_plus(
        code,
        "date,open,high,low,close,volume",  # 只获取需要的字段
        start_date=start_time,
        end_date=end_time,
        frequency="d",
        adjustflag="3"
    )

    bs.logout()

    # 将数据转换为DataFrame
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    df = pd.DataFrame(data_list, columns=rs.fields)

    # 数据预处理
    df['date'] = pd.to_datetime(df['date'])  # 转换为datetime类型
    df.set_index('date', inplace=True)  # 设置日期为索引
    df = df.astype(float)  # 将所有数据转换为float类型

    # 重命名列名以符合backtrader要求
    df = df[['open', 'high', 'low', 'close', 'volume']]  # 已经是我们需要的列名

    print(df.head())  # 打印前几行数据查看

    # 创建backtrader数据源
    data = bt.feeds.PandasData(
        dataname=df,
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

    start_time = '20170101'  # 回测开始时间
    end_time = '20170501'  # 回测结束时间
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
