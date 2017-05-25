def init(self):
    self.alpha = 0.08 # 8 процента
    self.holdPeriod = 12 * 24 # не менее 20
    self._tickSize = 'm5'
    self.currIndex = 0

    self.dataClose1h = []
    self.dataOpen1h = []
    self.dataHigh1h = []
    self.dataLow1h = []
    self.currIndex1h = 0

    self.rsi = 50
    self.rsiIndex = 0
    self.rsiAlpha = 0
    self.rsiUpEma = 0
    self.rsiDownEma = 0
    self.rsiTick = 0
    self.rsiIndicator = 0
    
    self.sma = 0
    self.smaArray = []
    
    self.stohastic_K_fast = []
    self.stohastic_K_full = []
    self.stohastic_D_full = []
    self.stohasticIndicator = 0
    self.stohasticTick = 0

    self.patternPogloshenie = 0

    self.BollingerUp = []
    self.BollingerDown = []
    self.BollingerMid = []
    self.BollingerIndicator = 0
    self.BollingerTick = 0

    self.MACD = 0
    self.MACD_gistogram = 0
    self.MACD_gistogram_prev = 0
    self.signal = 0
    self.MACD_ema_s = 0
    self.MACD_ema_l = 0
    self.MACD_s = 0
    self.MACD_l = 0
    self.MACD_a = 0
    self.MACD_indicator = 0


def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1., 0., window))
    weights /= weights.sum()
    ema = [values[i] * weights[i] for i in range(0, len(values))]
    return np.sum(ema)

def tick(self, data):
    self.currIndex += 1

    if self.currIndex % 12 == 0:
        self.currIndex1h += 1
        self.dataClose1h.append(data["close"][-1])
        self.dataOpen1h.append(data["open"][-12])
        self.dataHigh1h.append(np.max(data["high"][-12:]))
        self.dataLow1h.append(np.min(data["low"][-12:]))

        #-----------------------------rsi-----------------------------------
        tickWindow = 1
        era = 8
        self.rsiAlpha = 2 / (era + 1)

        if self.currIndex1h == 2:
            diff = self.dataClose1h[-1] - self.dataClose1h[-2]
            if diff > 0:
                self.rsiUpEma = diff
                self.rsiDownEma = 0
            else:
                self.rsiUpEma = 0
                self.rsiDownEma = -diff
        elif self.currIndex1h != 1:
            diff = data['close'][-1] - data['close'][-2]
            if diff > 0:
                self.rsiUpEma = self.rsiAlpha * diff + (1- self.rsiAlpha) * self.rsiUpEma
                self.rsiDownEma = 0
            else:
                self.rsiUpEma = 0
                self.rsiDownEma = self.rsiAlpha * (-diff) + (1- self.rsiAlpha) * self.rsiDownEma

        if self.currIndex1h > era:
            self.rsi = 100*(self.rsiUpEma/(self.rsiUpEma + self.rsiDownEma))

        if self.currIndex > era:
            if self.rsi > 70:
                self.rsiIndex = -1
            elif self.rsi < 30:
                self.rsiIndex = 1
            else:
                if self.rsiIndex == 1:
                    self.rsiIndicator = 1
                    self.rsiTick = tickWindow
                    self.rsiIndex = 0
                elif self.rsiIndex == -1:
                    self.rsiIndicator = -1
                    self.rsiTick = tickWindow
                    self.rsiIndex = 0

                if self.rsiTick > 0:
                    self.rsiTick -= 1
                else:
                    self.rsiIndicator = 0
        #-----------------------------rsi-----------------------------------
        
        #-----------------------------sma-----------------------------------
        #if self.currIndex > 1561:
        #    self.sma = np.average(data['close'][-1561:])
        #-----------------------------sma-----------------------------------
        
        #--------------------------stohastic(f_p, s_p, t_p)--------------------------------
        f_p = 2 
        s_p = 3 
        t_p = 3 
        
        tickWindow = 1

        self.stohastic_K_fast.append(100 * (self.dataClose1h[-1] - np.min(self.dataLow1h[-min(f_p, len(self.dataLow1h)):])) / (np.max(self.dataHigh1h[-min(f_p, len(self.dataHigh1h)):]) - np.min(self.dataLow1h[-min(f_p, len(self.dataLow1h)):])))
        self.stohastic_K_full.append(np.average(self.stohastic_K_fast[-min(s_p, len(self.stohastic_K_fast)):]))
        self.stohastic_D_full.append(np.average(self.stohastic_K_full[-min(t_p, len(self.stohastic_K_full)):]))
        
        if self.currIndex1h > f_p + s_p + t_p:
            if ((self.stohastic_K_full[-2] > self.stohastic_D_full[-2]) ^ (self.stohastic_K_full[-1] < self.stohastic_D_full[-1])) and (self.stohastic_K_full[-2] < 30 or self.stohastic_K_full[-1] < 30) and (self.stohastic_D_full[-2] < 30 or self.stohastic_D_full[-1] < 30):
                self.stohasticIndicator = 1
                self.stohasticTick = tickWindow
            elif ((self.stohastic_K_full[-2] > self.stohastic_D_full[-2]) ^ (self.stohastic_K_full[-1] < self.stohastic_D_full[-1])) and (self.stohastic_K_full[-2] > 70 or self.stohastic_K_full[-1] > 70) and (self.stohastic_D_full[-2] > 70 or self.stohastic_D_full[-1] > 70):
                self.stohasticIndicator = -1
                self.stohasticTick = tickWindow
            else:
                if self.stohasticTick > 0:
                    self.stohasticTick -= 1
                else:
                    self.stohasticIndicator = 0
        #--------------------------stohastic--------------------------------

        #--------------------------patternPogloshenie----------------------
        if self.currIndex1h > 2:
            if (self.dataOpen1h[-1] < self.dataClose1h[-1]) and (self.dataOpen1h[-2] > self.dataClose1h[-2]) and (self.dataClose1h[-2] > self.dataOpen1h[-1]) and (self.dataOpen1h[-2] < self.dataClose1h[-1]):
                self.patternPogloshenie = 1
            elif (self.dataOpen1h[-1] > self.dataClose1h[-1]) and (self.dataOpen1h[-2] < self.dataClose1h[-2]) and (self.dataClose1h[-2] < self.dataOpen1h[-1]) and (self.dataOpen1h[-2] > self.dataClose1h[-1]):
                self.patternPogloshenie = -1
            else:
                self.patternPogloshenie = 0
        #--------------------------patternPogloshenie----------------------


        #---------------------------------Bollinger---------------------------------
        era = 16
        tickWindow = 1
        k = 2

        mean = np.average(self.dataClose1h[-min(era, len(self.dataClose1h)):])
        std = np.std(self.dataClose1h[-min(era, len(self.dataClose1h)):])
        self.BollingerMid.append(mean)
        self.BollingerUp.append(mean + k * std)
        self.BollingerDown.append(mean - k * std)
        if self.currIndex > era:
            if (data["close"][-1] < self.BollingerDown[-1]):
                self.BollingerIndicator = 1
                self.BollingerTick = tickWindow
            elif (data["close"][-1] > self.BollingerUp[-1]):
                self.BollingerIndicator = -1
                self.BollingerTick = tickWindow
            else:
                if self.BollingerTick > 0:
                    self.BollingerTick -= 1
                else:
                    self.BollingerIndicator = 0
        #------------------------------------------------------------------

        #------------------------------------MACD-gistogram----------------
        self.MACD_s = 12
        self.MACD_l = 26
        self.MACD_a = 9


        if self.currIndex1h == 1:
            self.MACD_ema_s = self.dataClose1h[-1]
            self.MACD_ema_l = self.dataClose1h[-1]
            self.MACD = self.MACD_ema_s - self.MACD_ema_l
            self.signal = self.MACD_ema_s - self.MACD_ema_l
            self.MACD_gistogram = self.MACD - self.signal
        elif self.currIndex1h > 1:
            self.MACD_ema_s = self.MACD_s * self.dataClose1h[-1] + (1 - self.MACD_s) * self.MACD_ema_s
            self.MACD_ema_l = self.MACD_l * self.dataClose1h[-1] + (1 - self.MACD_l) * self.MACD_ema_l
            self.MACD = self.MACD_ema_s - self.MACD_ema_l
            self.signal = self.MACD_a * (self.MACD_ema_s - self.MACD_ema_l) + (1 - self.MACD_a) * self.signal
            self.MACD_gistogram_prev = self.MACD_gistogram
            self.MACD_gistogram = self.MACD - self.signal
            if self.MACD_gistogram > self.MACD_gistogram_prev:
                self.MACD_indicator = 1
            elif self.MACD_gistogram < self.MACD_gistogram_prev:
                self.MACD_indicator = -1
        #------------------------------------MACD-gistogram-----------------



    if (self.rsiIndicator == 1) and (self.BollingerIndicator == 1) and (self.MACD_indicator == 1):
        self.alpha = (self.BollingerMid[-1] - self.BollingerDown[-1]) / self.BollingerDown[-1]
        if self.alpha > 0.0004 and self.alpha/4 > 0.0004:
            order('buy', takeProfit=self.alpha, stopLoss=self.alpha, holdPeriod=self.holdPeriod)
    elif (self.rsiIndicator == -1) and (self.BollingerIndicator == -1) and (self.MACD_indicator == -1):
        self.alpha = (-self.BollingerMid[-1] + self.BollingerUp[-1]) / self.BollingerUp[-1]
        if self.alpha > 0.0004 and self.alpha/4 > 0.0004:
            order('sell', takeProfit=self.alpha, stopLoss=self.alpha, holdPeriod=self.holdPeriod)