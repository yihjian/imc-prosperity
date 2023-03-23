from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order, Trade

class Trader:
    def __init__(self):
        self.pearl_sell_side_position : int = 0
        self.pearl_buy_side_position : int = 0
        self.pearl_sell_side_limit : int = 10003
        self.pearl_buy_side_limit : int = 9997
        self.pearl_buy_side_orders : set = set()
        self.pearl_sell_side_orders : set = set()
        self.pearl_last_ts : int = -1

    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        self.update_my_position(state.own_trades)
        pearl_order : List[Order] = []
        for product in state.order_depths.keys():
            if product == "PEARLS":
                # simple market making
                # long under cutoff + short over cutoff on both sides
                pearl_order.extend(self.pearl_buyside(state.order_depths[product], state.timestamp))
                pearl_order.extend(self.pearl_sellside(state.order_depths[product], state.timestamp))
        print(f"pearal buy side position: {self.pearl_buy_side_position}")
        print(f"pearal sell side position: {self.pearl_sell_side_position}")
        return {"PEARLS": pearl_order}
    
    def update_my_position(self, own_trades: Dict[str, List[Trade]]):
        if ("PEARLS" in own_trades.keys()):    
            for t in own_trades["PEARLS"]:
                if (t.timestamp <= self.pearl_last_ts):
                    continue
                print(own_trades)
                self.pearl_last_ts = t.timestamp

                if (f"{int(t.price)}-{t.timestamp}" in self.pearl_buy_side_orders):
                    self.pearl_buy_side_orders.remove(f"{int(t.price)}-{t.timestamp}")
                    if (t.buyer == "SUBMISSION"):
                        self.pearl_buy_side_position += t.quantity
                    else:
                        self.pearl_buy_side_position -= t.quantity

                elif (f"{int(t.price)}-{t.timestamp}" in self.pearl_sell_side_orders):
                    self.pearl_sell_side_orders.remove(f"{int(t.price)}-{t.timestamp}")
                    if (t.buyer == "SUBMISSION"):
                        self.pearl_sell_side_position += t.quantity
                    else:
                        self.pearl_sell_side_position -= t.quantity


    def pearl_buyside(self, book: OrderDepth, time : int) -> List[Order]:
        orders: list[Order] = []

        if max(book.buy_orders.keys()) < self.pearl_buy_side_limit:
            # clear buy side short position if price is lower than limit
            if self.pearl_buy_side_position < 0:
                print(f"sending buy orders at {self.pearl_buy_side_limit} * {-self.pearl_buy_side_position}")
                orders.append(Order("PEARLS", max(book.buy_orders.keys()), -self.pearl_buy_side_position))
                self.pearl_buy_side_orders.add(f"{max(book.buy_orders.keys())}-{time}")
        else:
            # otherwise try to take out all buyside orders higher than limit
            for price, quantity in book.buy_orders.items():
                if price > self.pearl_buy_side_limit:
                    print(f"sending short orders at {price} * {-quantity}")
                    orders.append(Order("PEARLS", price, -quantity))
                    self.pearl_buy_side_orders.add(f"{price}-{time}")

        return orders
    
    def pearl_sellside(self, book: OrderDepth, time : int) -> List[Order]:
        orders: list[Order] = []

        if min(book.sell_orders.keys()) > self.pearl_sell_side_limit:
            # clear sell side long position if price is higher than limit
            if self.pearl_sell_side_position > 0:
                print(f"sending sell orders at {self.pearl_sell_side_limit} * {-self.pearl_sell_side_position}")
                orders.append(Order("PEARLS", min(book.sell_orders.keys()), -self.pearl_sell_side_position))
                self.pearl_sell_side_orders.add(f"{min(book.sell_orders.keys())}-{time}")
        else:
            # otherwise take out all sellside orders greater than limit
            for price, quantity in book.sell_orders.items():
                if price < self.pearl_sell_side_limit:
                    print(f"sending long orders at {price} * {-quantity}")
                    orders.append(Order("PEARLS", price, -quantity))
                    self.pearl_sell_side_orders.add(f"{price}-{time}")

        return orders