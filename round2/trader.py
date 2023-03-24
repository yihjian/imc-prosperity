from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade
import pandas as pd

class Trader:
    def __init__(self):
        self.pearl_cutoff : int = 10000
        self.banana_prices : pd.DataFrame = pd.DataFrame(columns=['timestamp', 'price'])
        self.banana_signal : int = 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        pearl_order : List[Order] = []
        banana_order : List[Order] = []
        for product in state.order_depths.keys():
            if product == "PEARLS":
                pearl_order.extend(self.pearl_trader(state.order_depths['PEARLS']))
            if product == "BANANAS":
                banana_order.extend(self.banana_trader(state.order_depths['BANANAS'], state.timestamp))
        return {
            "PEARLS": pearl_order,
            "BANANAS": banana_order
        }
    
    def pearl_trader(self, book: OrderDepth) -> List[Order]:
        orders = []
        for price in book.buy_orders.keys():
            if price >= self.pearl_cutoff:
                orders.append(Order("PEARLS", price, -book.buy_orders[price]))
        for price in book.sell_orders.keys():
            if price <= self.pearl_cutoff:
                orders.append(Order("PEARLS", price, -book.sell_orders[price]))
        return orders
    
    def banana_trader(self, book: OrderDepth, time: int) -> List[Order]:
        orders = []

        # track banana price history
        midprice = (max(book.buy_orders.keys()) + min(book.sell_orders.keys())) / 2
        self.banana_prices = pd.concat([
            self.banana_prices,
            pd.DataFrame([[time, midprice]],columns=['timestamp', 'price'])
        ], ignore_index=True)

        # need 26 days for macd to be calculated
        if (self.banana_prices.shape[0] < 26):
            return orders
        
        # calculate macd and trading signal
        macd, signal = self.get_macd(12, 26, 9)
        self.get_signal(macd, signal)
        print("banana signal: ", self.banana_signal)
        # trade base on signal
        if self.banana_signal == 1:
            orders.append(Order("BANANAS", min(book.sell_orders.keys()), -book.sell_orders[min(book.sell_orders.keys())]))
        elif self.banana_signal == -1:
            orders.append(Order("BANANAS", max(book.buy_orders.keys()), -book.buy_orders[max(book.buy_orders.keys())]))

        return orders
    
    def get_macd(self, slow:int, fast:int, smooth:int):
        exp1 = self.banana_prices['price'].ewm(span = fast, adjust = False).mean()
        exp2 = self.banana_prices['price'].ewm(span = slow, adjust = False).mean()
        macd = pd.DataFrame(exp1 - exp2).rename(columns = {'price':'macd'})
        signal = pd.DataFrame(macd.ewm(span = smooth, adjust = False).mean()).rename(columns = {'macd':'signal'})
        return macd['macd'].to_numpy(), signal['signal'].to_numpy()
    
    def get_signal(self, macd, signal):
        for i in range(len(macd)):
            if macd[i] > signal[i]:
                if self.banana_signal != 1:
                    self.banana_signal = 1
                else:
                    self.banana_signal = 0
            elif macd[i] < signal[i]:
                if self.banana_signal != -1:
                    self.banana_signal = -1
                else:
                    self.banana_signal = 0
            else:
                self.banana_signal = 0
