from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade

class Trader:
    def __init__(self):
        self.pearl_cutoff = 10000

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        pearl_order : List[Order] = []
        for product in state.order_depths.keys():
            if product == "PEARLS":
                pearl_order.extend(self.pearl_order(state.order_depths['PEARLS']))
        return {"PEARLS": pearl_order}
    
    def pearl_order(self, book: OrderDepth) -> List[Order]:
        orders = []
        for price in book.buy_orders.keys():
            if price > self.pearl_cutoff:
                orders.append(Order("PEARLS", price, -book.buy_orders[price]))
        for price in book.sell_orders.keys():
            if price < self.pearl_cutoff:
                orders.append(Order("PEARLS", price, -book.sell_orders[price]))
        return orders