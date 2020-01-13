import time
import keyboard
import json
import trader as trdr
import sys
import threading

def forceTraderShutDown(trader):
    print("Shutting down trader: " + trader.getStateString())
    if trader.is_in_trading_cycle:
        print("Waiting for end of cycle")
        time.sleep(10)
    trader.forceShutDown()
    print("Trader has shut down")

    
def startTrading(trader):
    trader.startTrading()

if __name__ == "__main__":

    trader_data_file = open("txt_files/trader_data.txt", "r")
    trader_data = json.loads(trader_data_file.read())

    trader = trdr.Trader(trader_data["money"], trader_data["stocks"])

    traderThread = threading.Thread(target=startTrading, args=(trader,), daemon=True)
    traderThread.start()

    while True:
        print("Write 'status' to see the trader's current status")
        print("Write 'stop' to end trading asap")
        command = input(">>> ")
        command = command.lower()
        if command == "status":
            print(trader.getStateString())
        if command == "stop":
            forceTraderShutDown(trader)
            exit(0)


