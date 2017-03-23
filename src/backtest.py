import numpy as np
import matplotlib.pyplot as plt

listOrders = []
tp = 10  # take profit
sl = 5  # stop loss
hp = 10  # holding period
svechka_gap_minutes = 5
svechka_per_hour = 60 / svechka_gap_minutes
working_hours = 9  # длина рабочего дня


class Context:
    pass


close = np.load('close.npy')
context = Context()


def calc_period(days=0, hours=0, minutes=0):
    return days * working_hours * svechka_per_hour + hours * svechka_per_hour + minutes / svechka_gap_minutes


def calc_alpha(days=0, hours=0, minutes=0):
    svechka_per_minute = svechka_per_hour / 60
    return 2 / (1 + calc_period(days, hours, minutes))


periods = {'9 hours': calc_period(hours=9), '25 hours': calc_period(hours=25), '9 days': calc_period(9),
           '25 days': calc_period(25)}

context.period = {'9 hours': calc_period(hours=9), '25 hours': calc_period(hours=25), '9 days': calc_period(9),
                  '25 days': calc_period(25)}
context.ema = {'9 hours': close[periods['9 hours']], '25 hours': close[periods['25 hours']],
               '9 days': close[periods['9 days']], '25 days': close[periods['25 days']]}
context.dma = context.tma = context.ema
context.alpha = {'9 hours': calc_alpha(hours=9), '25 hours': calc_alpha(hours=25), '9 days': calc_alpha(9),
                 '25 days': calc_alpha(25)}
context.counter = 1
context.trix = {'9 hours': 0.0, '25 hours': 0.0, '9 days': 0.0, '25 days': 0.0}
context.prevtrix = {'9 hours': 0.0, '25 hours': 0.0, '9 days': 0.0, '25 days': 0.0}
# (!) засунул инициации в функции

trix1 = []
trix2 = []
trix3 = []
trix4 = []


def order(operation, takeprofit, stoploss, holdingperiod):
    # operation - ‘buy' or ‘sell’
    # takeProfit и StopLoss в процентах
    # holdingPeriod - число элементов массива (ширина прямоугольника)
    listOrders.append((operation, takeprofit, stoploss, holdingperiod))


def calc_TRIX(per):
    context.ema[per] = context.alpha[per] * data + (1 - context.alpha[per]) * context.ema[per]
    context.dma[per] = context.alpha[per] * context.ema[per] + (1 - context.alpha[per]) * context.dma[per]
    prevtma = context.tma[per]
    context.tma[per] = context.alpha[per] * context.dma[per] + (1 - context.alpha[per]) * context.tma[per]
    context.trix[per] = ((context.tma[per] - prevtma) / prevtma) * 100


def inter_action_type(long_short):
    if long_short == 'long':
        ret = ['buylong', 'selllong']
    else:
        ret = ['sellshort', 'buyshort']
    if (context.prevtrix['9 hours'] <= context.prevtrix['25 hours']) and (
                context.trix['9 hours'] >= context.trix['25 hours']):
        return (ret[1])
    elif (context.prevtrix['9 hours'] >= context.prevtrix['25 hours']) and (
                context.trix['9 hours'] <= context.trix['25 hours']):
        return (ret[2])


def handle_data(data):
    # handle_data TRIX, use order function
    context.prevtrix = context.trix
    for per in ['9 hours', '25 hours', '9 days', '25 days']:
        if context.counter > context.period[per]:
            calc_TRIX(per)
        if context.counter > context.period['25 days']:
            trix1.append(context.trix[0])
            trix2.append(context.trix[1])
            trix3.append(context.trix[2])
            trix4.append(context.trix[3])

    ordered = 0

    # print(context.prevtrix)
    # print(context.trix)

    if context.counter > context.period['25 days']:
        if context.trix['9 days'] > context.trix['25 days']:
            order(inter_action_type(context), tp, sl, hp)
            ordered = 1
        elif context.trix['9 days'] < context.trix['25 days']:
            order(inter_action_type(context), tp, sl, hp)
            ordered = 1

    if ordered == 0:
        order('continue', 0, 0, 0)


pass


def algo_to_orders():
    for price in close:
        handle_data(price)
        # print(context.trix)
        context.counter += 1
    return listOrders


def calculate_finance_result():
    # Алгоритм на 2-х итераторах по данным и по списку заявок,
    # вспоминаем про   прямоугольник и то, что если мы сейчас не закрыли заявку в новую не входим:
    moment = 0
    inlong = 0
    inshort = 0
    enter_price = 0.0
    finance_result = 0.0
    for cur_ord in listOrders:
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
