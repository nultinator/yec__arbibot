from sxc_api_client import SxcApiClient
from sxc_api_client.constants import OrderTypes
from xeggex_api import XeggexClient
import time
import json
import datetime
from pathlib import Path
import logging

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
        "xeggex_secret": XEGGEX_SECRET,
        "default_arb_amount": 1 
    }
    keys_json = json.dumps(keys_dict, indent=4)
    with open(path, "w") as file:
        file.write(keys_json)

print(f"Found keys: {keys_dict}")
southx_client = SxcApiClient(keys_dict["southx_api"], keys_dict["southx_secret"])
xeggex_client = XeggexClient(keys_dict["xeggex_api"], keys_dict["xeggex_secret"])

default_arb_amount = keys_dict["default_arb_amount"]

print(f"Default arb amount: {default_arb_amount}")



southx_book_exists = False
while not southx_book_exists:
    try:
        southx_orderbook = southx_client.list_order_book("YEC", "BTC")
        southx_book_exists = True
    except:
        print("Failed API response")
    finally:
        time.sleep(1)


while True:
    timestamp = datetime.datetime.now()
    print(f"--------------{timestamp.hour}:{timestamp.minute}:{timestamp.second}--------------")


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

    southx_ask_buy = {"btc": southx_dict}

    xeggex_ask_buy = xeggex_client.get_ask_bid("yec", "btc")

    print(f"Southx ask and buy {southx_ask_buy}")
    print(f"Xeggex ask and buy {xeggex_ask_buy}")

    south_ask = southx_ask_buy["btc"]["AskPrice"]
    south_bid = southx_ask_buy["btc"]["BidPrice"]

    xegg_ask = xeggex_ask_buy["btc"]["AskPrice"]
    xegg_bid = xeggex_ask_buy["btc"]["BidPrice"]

    print(f"Ask prices: SouthX ask: {south_ask} Xeggex ask: {xegg_ask}")
    print(f"Bid prices: SouthX bid: {south_bid} Xeggex bid: {xegg_bid}")
    if south_bid > xegg_ask:
        print(f"Arb spotted on xeggex!")
        balances = xeggex_client.get_balances()
        for balance in balances:
            if balance["asset"] == "BTC":
                avail_balance = balance["available"]
                break
        print(f"Xeggex balance: {avail_balance} BTC")
        if float(avail_balance) > float(xeggex_ask_buy["btc"]["FillAsk"]):
            print("Xeggex buy order:")
            xegg_order = xeggex_client.create_order("YEC_BTC", "buy", xeggex_ask_buy["btc"]["AskAmount"], order_type="limit", price=xegg_ask)
            print(xegg_order)
            logging.info(f"Xeggex order: {xegg_order}")
            print("SouthX sell order:")
            south_order = southx_client.place_order("yec", "btc", order_type="sell", amount=xeggex_ask_buy["btc"]["AskAmount"], limit_price=south_bid)
            print(south_order)
            logging.info(f"SouthX_order: {south_order}")
        else:
            print("Small Arb Xeggex buy order:")
            xegg_order = xeggex_client.create_order("YEC_BTC", "buy", default_arb_amount, order_type="limit", price=xegg_ask)
            print(xegg_order)
            logging.info(f"Xeggex order: {xegg_order}")
            print("Small Arb SouthX sell order:")
            south_order = southx_client.place_order("yec", "btc", order_type="sell", amount=default_arb_amount, limit_price=south_bid)
            print(south_order)
            logging.info(f"SouthX order: {south_order}")    
    elif xegg_bid > south_ask:
        print(f"Arb spotted on southx!")
        balances = southx_client.list_balances()
        for balance in balances:
            if balance["Currency"] == "BTC":
                avail_balance = balance["Available"]
            break
        print(f"SouthX balance: {avail_balance} BTC")
        if float(avail_balance) > float(southx_dict["FillAsk"]):
            print("SouthX buy order:")
            south_order = southx_client.place_order("yec", "btc", order_type="buy", amount=southx_dict["AskAmount"], limit_price=south_ask)
            print(south_order)
            logging.info(f"SouthX order: {south_order}")
            print("Xeggex sell Order:")
            xegg_order = xeggex_client.create_order("YEC_BTC", "sell", southx_dict["AskAmount"], price=xegg_bid)
            print(xegg_order)
            logging.info(f"Xeggex order: {xegg_order}")
        else:
            print("Small Arb SouthX buy order:")
            south_order = southx_client.place_order("yec", "btc", order_type="buy", amount=default_arb_amount, limit_price=south_ask)
            print(south_order)
            logging.info(f"SouthX order: {south_order}")
            print("Small Arb Xeggex sell Order:")
            xegg_order = xeggex_client.create_order("YEC_BTC", "sell", default_arb_amount, price=xegg_bid)
            print(xegg_order)
            logging.info(f"Xeggex order: {xegg_order}")
    else:
        print("No arb spotted!")
        #logging.info("no arb spotted")