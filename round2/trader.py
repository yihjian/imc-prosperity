from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade

class Trader:
    def __init__(self):
        self.pearl_sell_side_position : int = 0
        self.pearl_buy_side_position : int = 0
        self.pearl_sell_side_limit : int = 10003
        self.pearl_buy_side_limit : int = 9997
        self.pearl_last_ts : int = 0

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        self.update_my_position(state.own_trades)
        pearl_order : List[Order] = []
        for product in state.order_depths.keys():
            if product == "PEARLS":
                # simple market making
                # long under cutoff + short over cutoff on both sides
                pearl_order.extend(self.pearl_buyside(state.order_depths[product]))
                pearl_order.extend(self.pearl_sellside(state.order_depths[product]))
        print(f"pearal buy side position: {self.pearl_buy_side_position}")
        print(f"pearal sell side position: {self.pearl_sell_side_position}")
        return {"PEARLS": pearl_order}
    
    def update_my_position(self, own_trades: Dict[str, List[Trade]]):
        if ("PEARLS" in own_trades.keys()):    
            for t in own_trades["PEARLS"]:
                if (t.timestamp <= self.pearl_last_ts):
                    continue
                self.pearl_last_ts = t.timestamp
                if t.price > 10000:
                    if t.buyer == "SUBMISSION":
                        self.pearl_buy_side_position += t.quantity
                    elif t.seller == "SUBMISSION":
                        self.pearl_buy_side_position -= t.quantity
                elif t.price < 10000:
                    if t.buyer == "SUBMISSION":
                        self.pearl_sell_side_position += t.quantity
                    elif t.seller == "SUBMISSION":
                        self.pearl_sell_side_position -= t.quantity


    def pearl_buyside(self, book: OrderDepth) -> List[Order]:
        orders: list[Order] = []

        if max(book.buy_orders.keys()) < self.pearl_buy_side_limit:
            # clear buy side short position if price is lower than limit
            if self.pearl_buy_side_position < 0:
                print(f"sending buy orders at {self.pearl_buy_side_limit} * {-self.pearl_buy_side_position}")
                orders.append(Order("PEARLS", max(book.buy_orders.keys()), -self.pearl_buy_side_position))
        else:
            # otherwise try to take out all buyside orders higher than limit
            for price, quantity in book.buy_orders.items():
                if price > self.pearl_buy_side_limit:
                    print(f"sending short orders at {price} * {-quantity}")
                    orders.append(Order("PEARLS", price, -quantity))

        return orders
    
    def pearl_sellside(self, book: OrderDepth) -> List[Order]:
        orders: list[Order] = []

        if min(book.sell_orders.keys()) > self.pearl_sell_side_limit:
            # clear sell side long position if price is higher than limit
            if self.pearl_sell_side_position > 0:
                print(f"sending sell orders at {self.pearl_sell_side_limit} * {-self.pearl_sell_side_position}")
                orders.append(Order("PEARLS", min(book.sell_orders.keys()), -self.pearl_sell_side_position))
        else:
            # otherwise take out all sellside orders greater than limit
            for price, quantity in book.sell_orders.items():
                if price < self.pearl_sell_side_limit:
                    print(f"sending long orders at {price} * {-quantity}")
                    orders.append(Order("PEARLS", price, -quantity))

        return orders