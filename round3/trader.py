from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade
import pandas as pd

class Trader:
    def __init__(self):
        self.pearl_cutoff : int = 10000
        self.banana_prices : pd.DataFrame = pd.DataFrame(columns=['timestamp', 'price'])
        self.banana_signal : int = 0
        self.positions : Dict[str, int] = {
            "PEARLS": 0,
            "BANANAS": 0,
            "BERRIES": 0
        }
        self.positions_last_update : Dict[str, int] = {
            "PEARLS": -1,
            "BANANAS": -1,
            "BERRIES": -1
        }

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        pearl_order : List[Order] = []
        banana_order : List[Order] = []
        mayberry_order : List[Order] = []
        self.update_poistions(state.own_trades)
        for product in state.order_depths.keys():
            if product == "PEARLS":
                pearl_order.extend(self.pearl_trader(state.order_depths['PEARLS']))
            # if product == "BANANAS":
            #     banana_order.extend(self.banana_trader(state.order_depths['BANANAS'], state.timestamp))
            if product == "BERRIES":
                mayberry_order.extend(self.mayberry_trader(state.order_depths['BERRIES'], state.timestamp))
        print(self.positions)
        return {
            "PEARLS": pearl_order,
            "BANANAS": banana_order,
            "BERRIES": mayberry_order
        }
    
    def update_poistions(self, own_trade : Dict[str, List[Trade]]):
        for product in own_trade.keys():
            if product not in self.positions.keys():
                self.positions[product] = 0
            if self.positions_last_update[product] == own_trade[product][-1].timestamp:
                continue
            self.positions_last_update[product] = own_trade[product][-1].timestamp
            for trade in own_trade[product]:
                if trade.buyer == "SUBMISSION":
                    self.positions[product] += trade.quantity
                elif trade.seller == "SUBMISSION":
                    self.positions[product] -= trade.quantity

    def pearl_trader(self, book: OrderDepth) -> List[Order]:
        '''
        Simple market making, buy/sell at 10000 cutoff
        '''
        orders = []
        for price in book.buy_orders.keys():
            if price >= self.pearl_cutoff:
                orders.append(Order("PEARLS", price, -book.buy_orders[price]))
        for price in book.sell_orders.keys():
            if price <= self.pearl_cutoff:
                orders.append(Order("PEARLS", price, -book.sell_orders[price]))
        return orders
    
    def mayberry_trader(self, book: OrderDepth, time: int) -> List[Order]:
        '''
        Simple Mayberry strategy, buy as much as possible before noon, sell as much as possible after noon
        '''
        orders = []
        if time < 500000:
            if self.positions['BERRIES'] < 250 and min(book.sell_orders.keys()) < 3900:
                orders.append(Order("BERRIES", min(book.sell_orders.keys()), -book.sell_orders[min(book.sell_orders.keys())]))
        else:
            if self.positions['BERRIES'] > -250 and max(book.buy_orders.keys()) > 3950:
                orders.append(Order("BERRIES", max(book.buy_orders.keys()), -book.buy_orders[max(book.buy_orders.keys())]))
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
