from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

def getYahooFinanceStockUrl(stock_symbol):
    return "https://finance.yahoo.com/quote/" + stock_symbol + "-USD"

def getYahooStockPrice(stock_symbol):
    url = getYahooFinanceStockUrl(stock_symbol)
    resp = get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    closing(resp)
    spans = soup.find_all('span', attrs={"data-reactid": "14"}) #Seems to be 14 for the program
    return float(spans[0].text.replace(',', ''))

def getYahooHighestChangingCryptos(amount):
    url = "https://finance.yahoo.com/cryptocurrencies?count=100&offset=0"
    resp = get(url)
    soup = BeautifulSoup(resp.content, "html.parser")
    closing(resp)
    #quotes = soup.tbody #soup.find_all('a', attrs={"class":"Fw(600)"})
    cryptos = []

    for tr in soup.tbody:
        crypto_name = ""
        crypto_prcnt_change = 0
        skip = False

        for td in tr:
            if td.attrs['aria-label'] == "Symbol":
                full_name = td.a.text
                crypto_name = full_name[0:len(full_name) - 4]
            if td.attrs['aria-label'] == "% Change":
                pcrnt_text = td.span.text
                crypto_prcnt_change = float(pcrnt_text[0:len(pcrnt_text)-1])
            if td.attrs['aria-label'] == "Price (Intraday)":
                price_intraday = float(td.span.text.replace(',', ''))
                if price_intraday < 0.001:
                    skip = True


        if crypto_prcnt_change > 0.5 and skip == False:      
            cryptos.append((crypto_prcnt_change, crypto_name))
    
    cryptos.sort()
    cryptos.reverse()
    #print(cryptos)
    crypto_symbols = []
    
    i = 0
    for crypto in cryptos:
        crypto_symbols.append(crypto[1])
        i+=1
        if i == amount:
            break
    
    return crypto_symbols

if __name__ == "__main__":
    print(getYahooHighestChangingCryptos(5))