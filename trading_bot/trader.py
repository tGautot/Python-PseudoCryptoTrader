import broker as brkr
import time
import yahoo_finance_scaper
from datetime import datetime

class Trader:

    def __init__(self, money, init_stocks):
        self.money = money
        self.stocks = init_stocks
        self.keepTrading = True    # This field can be changed by keyboard press 
        self.broker = brkr.Broker()
        self.is_in_trading_cycle = False

    def getStateString(self):
        return "Trader has ${} and owns the following stocks {}, for a total capital of {}".format(self.money, self.stocks, self.getCapital())

    def recordState(self):
        trader_data = open("txt_files/trade_history.txt", "a+")
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        trader_data.write("{}\n{}\n\n".format(dt_string, self.getStateString()))
        trader_data.close()

    def addStocks(self, stock_symbol, quantity):
        self.stocks[stock_symbol] = self.stocks.get(stock_symbol, 0.00) + quantity
    
    def removeStock(self, stock_symbol):
        del self.stocks[stock_symbol]

    def getOwnedStockQuantity(self, stock_symbol):
        return self.stocks.get(stock_symbol, 0.00)

    def getSocks(self):
        return self.stocks

    def updateMoney(self, diff):
        self.money += diff

    def buyStocks(self, list_stock_symbols): # All money will be used, equal amoun for each stock
        if self.money < 0.01 or len(list_stock_symbols) == 0:
            return

        money_per_stock = self.money/len(list_stock_symbols)

        if len(list(self.stocks.keys())) + len(list_stock_symbols) == 1:
            # if total amount of stock in portfolio after buy = 1
            money_per_stock = self.money/2

        for stock_symbol in list_stock_symbols:
            self.broker.handleBuy(self, stock_symbol, money_per_stock)

    def liquidateStocks(self):
        keys = list(self.stocks.keys())
        for key in keys:
            self.broker.handleSell(self, key)

    def getCapital(self): # money + owned crypto value
        total = self.money
        #print("Current stocks: {}".format(self.stocks))
        for key, entry in self.stocks.items():
            total += entry * yahoo_finance_scaper.getYahooStockPrice(key)
        return total

    def updateWatchList(self):
        self.watch_list = yahoo_finance_scaper.getYahooHighestChangingCryptos(5)

    def getCurrentWatchListStocksSnapshot(self):
        snapshot = {}
        for symbol in self.watch_list:
            price = yahoo_finance_scaper.getYahooStockPrice(symbol)
            snapshot[symbol] = price
        return snapshot

    def startTrading(self):
        self.cycles_on_current_watchlist_left = 0
        self.current_snapshot = {}
        while True:
            while self.cycles_on_current_watchlist_left > 0:
                self.recordTraderState()
                #print("Waiting for next cycle")
                time.sleep(60)
                self.is_in_trading_cycle = True
                snapshot = self.getCurrentWatchListStocksSnapshot()
                #print("Last snapshot: {}\ncrnt snapshot: {}".format(self.current_snapshot, snapshot))
                to_buy_this_round = []
                for symbol in self.watch_list:
                    self.liquidateStocks() # Always sell everything to makes sure money goes in all potentially viable cryptos
                    if symbol not in self.stocks and snapshot[symbol] > self.current_snapshot[symbol]:
                        # if we DONT own crypto and it's increasing
                        to_buy_this_round.append(symbol)
                    
                self.buyStocks(to_buy_this_round)
                self.current_snapshot = snapshot
                self.cycles_on_current_watchlist_left -= 1
                self.is_in_trading_cycle = False
                self.recordState()
            
            self.liquidateStocks()
            self.updateWatchList()
            self.current_snapshot = self.getCurrentWatchListStocksSnapshot()
            self.cycles_on_current_watchlist_left = 10
            #print("Updated watchlist")

    def recordTraderState(self):
        trader_data = open("txt_files/trader_data.txt", "w+")
        trader_data.write("{" + "\n\"money\": {},\n\"stocks\":{}\n".format(self. money, self.stocks).replace("'", '"') + "}")
        trader_data.close()

    def forceShutDown(self):
        self.liquidateStocks()
        self.recordTraderState()