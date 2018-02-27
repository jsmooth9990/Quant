from datetime import timedelta

class BasicTemplateOptionsAlgorithm(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2017, 5, 1)
        self.SetEndDate(2017, 8, 30)
        self.SetCash(30000)
        #for benchmark
        equity = self.AddEquity("GOOG", Resolution.Minute)
        
        option = self.AddOption("GOOG", Resolution.Minute)
        self.symbol = option.Symbol

        # set our strike/expiry filter for this option chain
        option.SetFilter(-7, 7, timedelta(30), timedelta(60))
        # use the underlying equity GOOG as the benchmark
        self.SetBenchmark(equity.Symbol)

    def OnData(self,slice):
        # option chain is a list of all put and call prices for a given maturity period
        optionchain = slice.OptionChains
        #search through the slice and find the option chain for "GOOG"
        for i in slice.OptionChains:
            if i.Key != self.symbol: continue
            chains = i.Value
            contract_list = [x for x in chains]
        # if there is no contracts in this optionchain, pass the instance
        if (slice.OptionChains.Count == 0) or (len(contract_list) == 0):
            return
         # if there is no securities in portfolio, trade the option. You only trade options once (YOTOO)
        if not self.Portfolio.Invested:
            self.TradeOptions(optionchain)

        # if the options expire, print out the undelying price
        if slice.Delistings.Count > 0:
            for x in slice.Delistings:
                if x.Key in [self.call_low.Symbol, self.call_high.Symbol]:
                    self.Log('underlying price at expiration date'+ str(self.call_low.UnderlyingLastPrice))

    def TradeOptions(self,optionchain):
        #list of all options for a given security
        for i in optionchain:
            if i.Key != self.symbol: continue
            chain = i.Value
            # sorted the optionchain by expiration date and choose the furthest date
            expiry = sorted(chain,key = lambda x: x.Expiry, reverse=True)[0].Expiry
            # filter the call options from the contracts expires on that date
            call = [i for i in chain if i.Expiry == expiry and i.Right == 0]
            # sorted the contracts according to their strike prices
            call_contracts = sorted(call,key = lambda x: x.Strike)
            if len(call_contracts) == 0: continue
            # call option contract with lower strike
            self.call_low = call_contracts[0]
            # call option contract with higher strike
            self.call_high = call_contracts[-1]
            self.Buy(self.call_low.Symbol, 1)
            self.Sell(self.call_high.Symbol ,1)
            self.Log('underlying price at time 0:'+ str(self.call_low.UnderlyingLastPrice))
