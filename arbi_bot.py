from sxc_api_client import SxcApiClient
from sxc_api_client.constants import OrderTypes
from xeggex_api import XeggexClient
import time
import json
import datetime
from pathlib import Path
import logging

pairs = ["btc", "usdt"]

logging.basicConfig(filename='app.log', filemode='w', format='%(levelname)s %(asctime)s: %(message)s', level=logging.INFO, datefmt='%Y-%m-%d %H:%M:%S')

logging.info("Log initiated")


path = Path(".config.json")
config = path.is_file()
if config:
    print("Config found")
    with open(path, "r") as file:
        keys_dict = json.load(file)

else:
    print("config file not found, setting up config")
    print("Please enter your Southx API key")
    SOUTHX_API_KEY = input()
    print("Please enter your Southx Secret")
    SOUTHX_SECRET = input()
    print("Please enter your Xeggex API key")
    XEGGEX_API_KEY = input()
    print("Please enter your Xeggex Secret")
    XEGGEX_SECRET = input()
    keys_dict = {
        "southx_api": SOUTHX_API_KEY,
        "southx_secret": SOUTHX_SECRET,
        "xeggex_api": XEGGEX_API_KEY,
        "xeggex_secret": XEGGEX_SECRET
    }
    keys_json = json.dumps(keys_dict, indent=4)
    with open(path, "w") as file:
        file.write(keys_json)

print(f"Found keys: {keys_dict}")
southx_client = SxcApiClient(keys_dict["southx_api"], keys_dict["southx_secret"])
xeggex_client = XeggexClient(keys_dict["xeggex_api"], keys_dict["xeggex_secret"])




default_arb_amount = keys_dict["default_arb_amount"]

print(f"Default arb amount: {default_arb_amount}")



while True:
    for pair in pairs:
        timestamp = datetime.datetime.now()
        print(f"--------------yec/{pair}{timestamp.hour}:{timestamp.minute}:{timestamp.second}--------------")

        southx_orderbook = southx_client.list_order_book("YEC", pair.upper())

        bid_amount = southx_orderbook["BuyOrders"][0]["Amount"]
        bid_price = southx_orderbook["BuyOrders"][0]["Price"]
        fill_bid = bid_amount * bid_price
        ask_amount = southx_orderbook["SellOrders"][0]["Amount"]
        ask_price = southx_orderbook["SellOrders"][0]["Price"]
        fill_ask = ask_amount * ask_price

        southx_dict = {
            "BidAmount": bid_amount,
            "BidPrice": bid_price,
            "FillBid": fill_bid,
            "AskAmount": ask_amount,
            "AskPrice": ask_price,
            "FillAsk": fill_ask
        }

        southx_ask_buy = {pair: southx_dict}

        xeggex_ask_buy = xeggex_client.get_ask_bid("yec", pair)

        print(f"Southx ask and buy {southx_ask_buy}")
        print(f"Xeggex ask and buy {xeggex_ask_buy}")

        south_ask = southx_ask_buy[pair]["AskPrice"]
        south_bid = southx_ask_buy[pair]["BidPrice"]

        xegg_ask = xeggex_ask_buy[pair]["AskPrice"]
        xegg_bid = xeggex_ask_buy[pair]["BidPrice"]

        print(f"Ask prices: SouthX ask: {south_ask} Xeggex ask: {xegg_ask}")
        print(f"Bid prices: SouthX bid: {south_bid} Xeggex bid: {xegg_bid}")
        if south_bid > xegg_ask:
            print(southx_client.cancel_market_orders("yec", pair))
            xeggex_pair = f"YEC_{pair.upper()}"
            print(xeggex_client.cancel_orders(xeggex_pair, "sell"))

            print(f"Arb spotted on xeggex!")
            balances = xeggex_client.get_balances()
            avail_balance = 0
            for balance in balances:
                if balance["asset"] == pair.upper():
                    avail_balance = balance["available"]
                    break
            print(f"Xeggex balance: {avail_balance} {pair}")
            if float(avail_balance) > float(xeggex_ask_buy[pair]["FillAsk"]):
                print("Xeggex buy order:")
                ask_amount = xeggex_ask_buy[pair]["AskAmount"]
                xegg_order = xeggex_client.create_order(xeggex_pair, "buy", ask_amount, order_type="limit", price=xegg_ask)
                print(xegg_order)
                logging.info(f"Xeggex order: {xegg_order}")
                logging.info(f"Bought {ask_amount} YEC on Xeggex for {xegg_ask} {pair}")
                print("SouthX sell order:")
                south_order = southx_client.place_order("yec", pair, order_type="sell", amount=ask_amount, limit_price=south_bid)
                print(south_order)
                logging.info(f"SouthX_order: {south_order}")
                logging.info(f"Sold {ask_amount} YEC on SouthX for {south_bid} {pair}")
            else:
                print("Small Arb Xeggex buy order:")
                xegg_order = xeggex_client.create_order(xeggex_pair, "buy", default_arb_amount, order_type="limit", price=xegg_ask)
                logging.info(f"Bought {default_arb_amount} YEC on Xeggex for {xegg_ask} {pair}")
                print(xegg_order)
                logging.info(f"Xeggex order: {xegg_order}")
                print("Small Arb SouthX sell order:")
                south_order = southx_client.place_order("yec", pair, order_type="sell", amount=default_arb_amount, limit_price=south_bid)
                logging.info(f"Sold {default_arb_amount} YEC on SouthX for {south_bid} {pair}")
                print(south_order)
                logging.info(f"SouthX order: {south_order}")    
        elif xegg_bid > south_ask:
            xeggex_pair = f"YEC_{pair.upper()}"

            print(southx_client.cancel_market_orders("yec", pair))
            print(xeggex_client.cancel_orders(xeggex_pair, "buy"))
            print(f"Arb spotted on southx!")
            balances = southx_client.list_balances()
            avail_balance = 0
            for balance in balances:
                if balance["Currency"] == pair.upper():
                    avail_balance = balance["Available"]
                    break
            print(f"SouthX balance: {avail_balance} {pair}")
            if float(avail_balance) > float(southx_dict["FillAsk"]):
                print("SouthX buy order:")
                ask_amount = southx_dict["AskAmount"]
                south_order = southx_client.place_order("yec", pair, order_type="buy", amount=ask_amount, limit_price=south_ask)
                logging.info(f"Bought {ask_amount} YEC on SouthX for {south_ask} {pair}")
                print(south_order)
                logging.info(f"SouthX order: {south_order}")
                print("Xeggex sell Order:")
                xegg_order = xeggex_client.create_order(xeggex_pair, "sell", southx_dict["AskAmount"], price=xegg_bid)
                logging.info(f"Sold {ask_amount} YEC on Xeggex for {xegg_bid} {pair}")
                print(xegg_order)
                logging.info(f"Xeggex order: {xegg_order}")
            else:
                print("Small Arb SouthX buy order:")
                south_order = southx_client.place_order("yec", pair, order_type="buy", amount=default_arb_amount, limit_price=south_ask)
                logging.info(f"Bought {default_arb_amount} YEC on SouthX for {south_ask} {pair}")
                print(south_order)
                logging.info(f"SouthX order: {south_order}")
                print("Small Arb Xeggex sell Order:")
                xegg_order = xeggex_client.create_order(xeggex_pair, "sell", default_arb_amount, price=xegg_bid)
                logging.info(f"Sold {default_arb_amount} YEC on Xeggex for {xegg_bid} {pair}")
                print(xegg_order)
                logging.info(f"Xeggex order: {xegg_order}")
        else:
            print("No arb spotted!")
