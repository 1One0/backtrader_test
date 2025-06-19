# learn3 sizer

虽然在模拟交易时, 可以每笔都可以使用size来制定交易的数量, 但交易策略的考量中, 应以账户总额的百分比来作为每笔交易的金额. 这样对于不同价格的资产, 可以有更好的适应性.

在backtrader中, 可以通过Sizer来实现这个功能. Sizer可以根据账户总额和当前价格来计算每笔交易的数量, 同时还会自动考虑佣金因素.

## 内置Sizer

backtrader提供了几种内置的Sizer, 可以直接使用

### 1. FixedSize

每次交易都使用固定的数量.

```python
cerebro.addsizer(bt.sizers.FixedSize, stake=100)    # 每次交易100股
```

### 2. PercentSizer, PercentSizerInt

每次交易使用账户总资金的一定百分比. 区别在于前者允许非整数的交易数量, 而后者的交易数量向下取整.

```python
cerebro.addsizer(bt.sizers.PercentSizer, perc=20)  # 每次交易使用20%的现金
cerebro.addsizer(bt.sizers.PercentSizerInt, perc=20)  # 每次交易使用20%的现金, 交易数量向下取整
```

### 3. AllInSizer, AllInSizerInt

全仓交易, 等同于`PercentSizer(percents=100)`和`PercentSizerInt(percents=100)`.

```python
cerebro.addsizer(bt.sizers.AllInSizer)
cerebro.addsizer(bt.sizers.AllInSizerInt)
```

##

