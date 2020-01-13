from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import yahoo_finance_scaper
import trader
from datetime import datetime

ACTION_CODE_BUY  = 42
ACTION_CODE_SELL = 69 # Haha funny sex number

class Broker:

    def getStockPrice(self, stock_symbol):
        return yahoo_finance_scaper.getYahooStockPrice(stock_symbol)

    def recordTransaction(self, action_code, trader, symbol, quantity, money):
    
        if action_code == ACTION_CODE_SELL:
            action_string = "sold"
            money_action_string = "gained"
        elif action_code == ACTION_CODE_BUY:
            action_string = "bought"
            money_action_string = "paid"
        else:
            print("Invalid argument <action_code>, not recording")

        record_file = open("txt_files/trade_history.txt", "a+")
        
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        record = "Trader {} {} {} and {} ${}".format(action_string, str(quantity), symbol, money_action_string, str(money))

        record_content = dt_string + "\n" + record + "\n" + trader.getStateString() + "\n\n"
        print(record_content)
        record_file.write(record_content)

        record_file.close()

    def handleBuy(self, trader, stock_symbol, money_to_spend):
        unit_price = self.getStockPrice(stock_symbol)
        quantity_bought = money_to_spend/unit_price
        trader.addStocks(stock_symbol, quantity_bought)
        trader.updateMoney(-money_to_spend)
        #self.recordTransaction(ACTION_CODE_BUY, trader, stock_symbol, quantity_bought, money_to_spend)

    def handleSell(self, trader, stock_symbol):
        unit_price = self.getStockPrice(stock_symbol)
        quantity_to_sell = trader.getOwnedStockQuantity(stock_symbol)
        money_gained = unit_price*quantity_to_sell
        trader.removeStock(stock_symbol)
        trader.updateMoney(money_gained)
        #self.recordTransaction(ACTION_CODE_SELL, trader, stock_symbol, quantity_to_sell, money_gained)
        

if __name__ == '__main__':
    broker = Broker()
    #print(broker.getStockPrice('ETH'))
    trader = trader.Trader(8000, {})
    broker.handleBuy(trader, "BTC", 8000)
    broker.handleSell(trader, "BTC")