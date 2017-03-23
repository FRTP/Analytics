import numpy as np
import matplotlib.pyplot as plt

listOrders = []
tp = 10  # take profit
sl = 5  # stop loss
hp = 10  # holding period
svechka_gap_minutes = 5
working_hours = 9  # длина рабочего дня


class ctxt:
    pass


close = np.load('close.npy')
ctxt = ctxt()


def calc_period(days=0, hours=0, minutes=0):
    per = days * working_hours * svechka_per_hour
    per += hours * svechka_per_hour + minutes / svechka_gap_minutes
    return per


def calc_alpha(days=0, hours=0, minutes=0):
    svechka_per_minute = svechka_per_hour / 60
    return 2 / (1 + calc_period(days, hours, minutes))


periods = {'9 hours': calc_period(hours=9)}

periods.update('25 hours', calc_period(hours=25))
periods.update('9 days', calc_period(9))
periods.update('25 days', calc_period(25))

ctxt.period = {'9 hours': calc_period(hours=9)}
ctxt.period.update('25 hours', calc_period(hours=25))
ctxt.period.update('9 days', calc_period(9))
ctxt.period.update('25 days', calc_period(25))

ctxt.ema = {'9 hours': close[periods['9 hours']]}
ctxt.ema.update('25 hours', close[periods['25 hours']])
ctxt.ema.update('9 days', close[periods['9 days']])
ctxt.ema.update('25 days', close[periods['25 days']])

ctxt.dma = ctxt.tma = ctxt.ema
ctxt.alpha = {'9 hours': calc_alpha(hours=9)}
ctxt.alpha.update('25 hours', calc_alpha(hours=25))
ctxt.alpha.update('9 days', calc_alpha(9))
ctxt.alpha.update('25 days', calc_alpha(25))

ctxt.counter = 1
ctxt.prevtrix = ctxt.trix = {'9 hours': 0.0}
for peri in ['25 hours', '9 days', '25 days']:
    ctxt.prevtrix.update(peri, 0.0)
    ctxt.prevtrix.update(peri, 0.0)

trix4 = trix3 = trix2 = trix1 = []


def order(operation, takeprofit, stoploss, holdingperiod):
    # operation - ‘buy' or ‘sell’
    # takeProfit и StopLoss в процентах
    # holdingPeriod - число элементов массива (ширина прямоугольника)
    listOrders.append((operation, takeprofit, stoploss, holdingperiod))


def calc_TRIX(per):
    ema = ctxt.alpha[per] * price + (1 - ctxt.alpha[per]) * ctxt.ema[per]
    dma = ctxt.alpha[per] * ema + (1 - ctxt.alpha[per]) * ctxt.dma[per]
    prevtma = ctxt.tma[per]
    tma = ctxt.alpha[per] * dma + (1 - ctxt.alpha[per]) * ctxt.tma[per]
    ctxt.trix[per] = ((tma - prevtma) / prevtma) * 100
    ctxt.ema[per] = ema
    ctxt.dma[per] = dma
    ctxt.tma[per] = tma


def inter_action_type(long_short):
    if long_short == 'long':
        ret = ['buylong', 'selllong']
    else:
        ret = ['sellshort', 'buyshort']
    if (ctxt.prevtrix['9 hours'] <= ctxt.prevtrix['25 hours']) and (
                ctxt.trix['9 hours'] >= ctxt.trix['25 hours']):
        return (ret[1])
    elif (ctxt.prevtrix['9 hours'] >= ctxt.prevtrix['25 hours']) and (
                ctxt.trix['9 hours'] <= ctxt.trix['25 hours']):
        return (ret[2])


def handle_data(price):
    # handle_data TRIX, use order function
    ctxt.prevtrix = ctxt.trix
    for per in ['9 hours', '25 hours', '9 days', '25 days']:
        if ctxt.counter > ctxt.period[per]:
            calc_TRIX(per, price)
        if ctxt.counter > ctxt.period['25 days']:
            trix1.append(ctxt.trix[0])
            trix2.append(ctxt.trix[1])
            trix3.append(ctxt.trix[2])
            trix4.append(ctxt.trix[3])

    ordered = 0

    # print(ctxt.prevtrix)
    # print(ctxt.trix)

    if ctxt.counter > ctxt.period['25 days']:
        if ctxt.trix['9 days'] > ctxt.trix['25 days']:
            order(inter_action_type(ctxt), tp, sl, hp)
            ordered = 1
        elif ctxt.trix['9 days'] < ctxt.trix['25 days']:
            order(inter_action_type(ctxt), tp, sl, hp)
            ordered = 1

    if ordered == 0:
        order('continue', 0, 0, 0)


pass


def algo_to_orders():
    for price in close:
        handle_data(price)
        # print(ctxt.trix)
        ctxt.counter += 1
    return listOrders


def calculate_finance_result():
    # Алгоритм на 2-х итераторах по данным и по списку заявок,
    # вспоминаем про   прямоугольник и то,
    #  что если мы сейчас не закрыли заявку в новую не входим:
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
