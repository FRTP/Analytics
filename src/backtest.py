listOrders = []
tp = 10  # take profit
sl = 5  # stop loss
hp = 10  # holding period
svechka_per_hour = 60 / 5


class Context:
    pass


import numpy as np
import matplotlib.pyplot as plt

close = np.load('close.npy')
context = Context()
context.period = [9 * svechka_per_hour, 25 * svechka_per_hour, 9 * svechka_per_hour * 9, 25 * svechka_per_hour * 9]
context.ema = [close[context.period[0]], close[context.period[1]], close[context.period[2]], close[context.period[3]]]
context.dma = [close[context.period[0]], close[context.period[1]], close[context.period[2]], close[context.period[3]]]
context.tma = [close[context.period[0]], close[context.period[1]], close[context.period[2]], close[context.period[3]]]
context.alpha = [2 / (9 * svechka_per_hour + 1), 2 / (25 * svechka_per_hour + 1), 2 / (9 * svechka_per_hour * 9 + 1),
                 2 / (25 * svechka_per_hour * 9 + 1)]
context.counter = 1
context.trix = [0.0, 0.0, 0.0, 0.0]
context.prevtrix = [0.0, 0.0, 0.0, 0.0]

trix1 = []
trix2 = []
trix3 = []
trix4 = []


def order(operation, takeprofit, stoploss, holdingperiod):
    # operation - ‘buy' or ‘sell’
    # takeProfit и StopLoss в процентах
    # holdingPeriod - число элементов массива (ширина прямоугольника)
    listOrders.append((operation, takeprofit, stoploss, holdingperiod))


def handle_data(context, data):
    # handle_data TRIX, use order function
    context.prevtrix = context.trix
    for i in [0, 1, 2, 3]:
        if context.counter > context.period[i]:
            context.ema[i] = context.alpha[i] * data + (1 - context.alpha[i]) * context.ema[i]
            context.dma[i] = context.alpha[i] * context.ema[i] + (1 - context.alpha[i]) * context.dma[i]
            prevtma = context.tma[i]
            context.tma[i] = context.alpha[i] * context.dma[i] + (1 - context.alpha[i]) * context.tma[i]
            context.trix[i] = ((context.tma[i] - prevtma) / prevtma) * 100
        if context.counter > context.period[3]:
            trix1.append(context.trix[0])
            trix2.append(context.trix[1])
            trix3.append(context.trix[2])
            trix4.append(context.trix[3])

    ordered = 0

    # print(context.prevtrix)
    # print(context.trix)

    if context.counter > context.period[3]:
        if context.trix[2] > context.trix[3]:
            # print('I passed second.1 condition')
            if (context.prevtrix[0] <= context.prevtrix[1]) and (context.trix[0] >= context.trix[1]):
                print('buylong')
                order('buylong', tp, sl, hp)
                ordered = 1
            elif (context.prevtrix[0] >= context.prevtrix[1]) and (context.trix[0] <= context.trix[1]):
                print('selllong')
                order('selllong', tp, sl, hp)
                ordered = 1
        elif context.trix[2] < context.trix[3]:
            # print('I passed second.2 condition')
            if (context.prevtrix[0] >= context.prevtrix[1]) and (context.trix[0] <= context.trix[1]):
                print('buyshort')
                order('buyshort', tp, sl, hp)
                ordered = 1
            elif (context.prevtrix[0] <= context.prevtrix[1]) and (context.trix[0] >= context.trix[1]):
                print('sellshort')
                order('sellshort', tp, sl, hp)
                ordered = 1

    if ordered == 0:
        order('continue', 0, 0, 0)


pass


def algo_to_orders():
    for price in close:
        handle_data(context, price)
        # print(context.trix)
        context.counter += 1
    return listOrders


def calculate_finance_result():
    # Алгоритм на 2-х итераторах по данным и по списку заявок, вспоминаем про   прямоугольник и то, что если мы сейчас не закрыли заявку в новую не входим:
    moment = 0
    inlong = 0
    inshort = 0
    enter_price = 0.0
    finance_result = 0.0
    for cur_ord in listOrders:
        # print('moment ', moment)
        if inlong == 0 and inshort == 0:
            if cur_ord[0] == 'buylong':
                inlong = 1
                enter_price = close[moment]
            elif cur_ord[0] == 'buyshort':
                inshort = 1
                enter_price = close[moment]
        elif inlong > 0:
            inlong += 1
            if inlong > hp:
                finance_result += close[moment] - enter_price
                inlong = 0
            elif enter_price - close[moment] > sl:
                finance_result += close[moment] - enter_price
                inlong = 0
            elif close[moment] - enter_price >= tp:
                finance_result += close[moment] - enter_price
                inlong = 0
            elif cur_ord[0] == 'selllong':
                finance_result += close[moment] - enter_price
                inlong = 0
        elif inshort > 0:
            inshort += 1
            if inshort > hp:
                finance_result += enter_price - close[moment]
                inshort = 0
            elif enter_price - close[moment] >= tp:
                finance_result += enter_price - close[moment]
                inshort = 0
            elif close[moment] - enter_price > sl:
                finance_result += enter_price - close[moment]
                inshort = 0
            elif cur_ord[0] == 'sellshort':
                finance_result += enter_price - close[moment]
                inshort = 0

        moment += 1

    return finance_result


algo_to_orders()
print(calculate_finance_result())
x = range(len(trix1))
fig = plt.figure()
plt.plot(x, trix1, label=u'9h', color='green')
plt.plot(x, trix2, label=u'25h', color='red')
plt.plot(x, trix3, label=u'9d', color='yellow')
plt.plot(x, trix4, label=u'25d', color='cyan')
plt.show()
