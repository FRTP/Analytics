trix_9_day_prev = 100.0
trix_25_day_prev = 100.0
trix_9_hour_prev = 100.0
trix_25_hour_prev = 100.0

prev_info_9 = [0.0, 0.0, 0.0]
prev_info_25 = [0.0, 0.0, 0.0]

start = 0

def initialize(context):
    context.security = symbol('AAPL')

def trix(n, ema_prev, dma_prev, tma_prev, close, flag):
    global prev_info_9 
    global prev_info_25 

    alpha = 2.0/(n+1.0)
    ema = alpha * close + (1 - alpha) * ema_prev
    dma = alpha * ema + (1 - alpha) * dma_prev
    tma = alpha * dma + (1 - alpha) * tma_prev
    answer = (tma - tma_prev)/(tma_prev) * 100
    if (flag == 0):
        prev_info_9[0] = ema
        prev_info_9[1] = dma
        prev_info_9[2] = tma
    else:
        prev_info_25[0] = ema
        prev_info_25[1] = dma
        prev_info_25[2] = tma
    return answer

def handle_data(context, data):
    global start
    global trix_9_day_prev
    global trix_25_day_prev
    global trix_9_hour_prev
    global trix_25_hour_prev
    global prev_info_9
    global prev_info_25
    #if (start == 0):
     #   prev_info_9[0] = data.history(sid(24), 'close', 2, '1d')[0]
      #  prev_info_25[0] = data.history(sid(24), 'close', 2, '1d')[0]

    close_t_d = data.history(sid(24), 'close', 2, '1d')[-1]
    close_t_m = data.history(sid(24), 'close', 61, '1m')[-1]

    trix_9_day = trix(9, prev_info_9[0], prev_info_9[1], prev_info_9[2], close_t_d, 0)
    trix_25_day = trix(25, prev_info_25[0], prev_info_25[1], prev_info_25[2], close_t_d, 1)
    trix_9_hour = trix(9, prev_info_9[0], prev_info_9[1], prev_info_9[2], close_t_m, 0)
    trix_25_hour = trix(25, prev_info_25[0], prev_info_25[1], prev_info_25[2], close_t_m, 1)
    
    current_price = data[context.security].price
    
    amount = context.portfolio.positions[symbol('AAPL')].amount
    cash = context.portfolio.cash
    
    number_of_shares_buy = int(cash/current_price)
    number_of_shares_sell = amount
    #print trix_9_day_prev, trix_9_hour_prev, trix_25_day_prev, trix_25_hour_prev
    if (trix_9_day > trix_25_day and trix_9_day_prev > trix_25_day_prev) and (trix_9_hour_prev < trix_25_hour_prev and trix_9_hour > trix_25_hour) and cash > current_price:
        order(context.security, +number_of_shares_buy)
        log.info("Buying %s, amount: %d, cash: %d, price: %s" % (context.security.symbol, number_of_shares_buy, cash, current_price))
    elif (trix_9_day < trix_25_day and trix_9_day_prev < trix_25_day_prev) and (trix_9_hour_prev > trix_25_hour_prev and trix_9_hour < trix_25_hour) and amount>0:
        order(context.security, -number_of_shares_sell)
        log.info("Selling %s %d" % (context.security.symbol, number_of_shares_sell))
    trix_9_day_prev = trix_9_day
    trix_9_hour_prev = trix_9_hour
    trix_25_day_prev = trix_25_day
    trix_25_hour_prev = trix_25_hour
    record(stock_sum=amount) 