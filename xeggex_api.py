import requests
import json
import hmac
import hashlib
import time
import base64
from urllib.parse import urlencode

BASE_URL = "https://api.xeggex.com/api/v2"

"""
#get the current ask/bid price and size
def get_ask_bid(currency, ref_currency):
    ##create our dict to return
    return_map = {}
    #create a string of our url
    url = f"{BASE_URL}/market/getorderbookbysymbol/{currency}_{ref_currency}"
    #send the GET request and unwrap the result
    resp = requests.get(url)
    #create a json object from the result
    resp_json = resp.json()
    #xeggex returns this as a string, so we parse the string for f32
    current_bid_amount =  float(resp_json["bids"][0]["quantity"])
    #we retrieve this the same way as with Southx        
    current_bid_price = float(resp_json["bids"][0]["numberprice"])
    #once again, parse the string for f32
    current_ask_amount = float(resp_json["asks"][0]["quantity"])
    #same as Southx
    current_ask_price = float(resp_json["asks"][0]["numberprice"])
    #insert these pairs into the map
    map = {}
    map["BidAmount"] = current_bid_amount
    map["BidPrice"] = current_bid_price
    map["AskAmount"] = current_ask_amount
    map["AskPrice"] = current_ask_price
    #calculate the cost to fill ask and bid
    fill_bid = current_bid_amount * current_bid_price
    fill_ask = current_ask_amount * current_ask_price
    #insert the calculated amounts into the map
    map["FillBid"] = fill_bid
    map["FillAsk"] = fill_ask
    #insert the map into a larger map named after our reference currency
    return_map[ref_currency] = map
    return return_map
"""

#xeggex api client
class XeggexClient:
    def __init__(self, api_key, secret):
        self.api_key = api_key
        self.secret = secret
    def sign_data(self, url, payload, nonce):
        if payload is not None:
            payload_string = json.dumps(payload, separators=(',', ':'))
        else:
            payload_string = ""
        data = f"{self.api_key}{url}{payload_string}{nonce}"
        sig = hmac.new(self.secret.encode(), data.encode(), hashlib.sha256).hexdigest()
        return sig
    def create_order(self, symbol, side, quantity, price=None, order_type="limit", user_provided_id=None, strict_validate=False):
        url = f"{BASE_URL}/createorder"
        auth_string = f"{self.api_key}:{self.secret}"
        base64_auth_string = base64.b64encode(auth_string.encode()).decode()

        headers = {
            "Authorization": f"Basic {base64_auth_string}",
            #"Accept": "application/json",
            #"Content-Type": "application/json",
            #"X-API-KEY": self.api_key,                       
        }

        payload = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": str(float(quantity)),
            "price": str(float(price))
            #"strictValidate": False,
            #"timestamp": str(int(time.time()))
        }
        resp = requests.post(url, headers=headers, data=payload)
        return resp.text
    def get_balances(self):
        url = f"{BASE_URL}/balances"
        auth_string = f"{self.api_key}:{self.secret}"
        base64_auth_string = base64.b64encode(auth_string.encode()).decode()
        headers = {
            "Authorization": f"Basic {base64_auth_string}"
        }
        try:
            resp = requests.get(url, headers=headers)
            resp.raise_for_status()
            #print(resp.text)
            return resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}")
            return None
    #get the current ask/bid price and size
    def get_ask_bid(self, currency, ref_currency):
        ##create our dict to return
        return_map = {}
        #create a string of our url
        url = f"{BASE_URL}/market/getorderbookbysymbol/{currency}_{ref_currency}"
        #send the GET request and unwrap the result
        resp = requests.get(url)
        #create a json object from the result
        resp_json = resp.json()
        #xeggex returns this as a string, so we parse the string for f32
        current_bid_amount =  float(resp_json["bids"][0]["quantity"])
        #we retrieve this the same way as with Southx        
        current_bid_price = float(resp_json["bids"][0]["numberprice"])
        #once again, parse the string for f32
        current_ask_amount = float(resp_json["asks"][0]["quantity"])
        #same as Southx
        current_ask_price = float(resp_json["asks"][0]["numberprice"])
        #insert these pairs into the map
        map = {}
        map["BidAmount"] = current_bid_amount
        map["BidPrice"] = current_bid_price
        map["AskAmount"] = current_ask_amount
        map["AskPrice"] = current_ask_price
        #calculate the cost to fill ask and bid
        fill_bid = current_bid_amount * current_bid_price
        fill_ask = current_ask_amount * current_ask_price
        #insert the calculated amounts into the map
        map["FillBid"] = fill_bid
        map["FillAsk"] = fill_ask
        #insert the map into a larger map named after our reference currency
        return_map[ref_currency] = map
        return return_map