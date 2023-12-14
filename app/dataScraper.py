import requests
import time
from app.sessionInfo import check_sid

def get_profit(x2y, sellPrice, buyPrice):
        if x2y == 'b2s':
            tax = 0.12 * sellPrice
            profit = (sellPrice - tax) - buyPrice
            percentage = (profit/buyPrice)*100
            return round(percentage)
        elif x2y == 's2b':
            tax = 0.025 * sellPrice
            profit = (sellPrice - tax) - buyPrice
            percentage = (profit/buyPrice)*100
            return round(percentage)
        else:
            return 

# Gets dataPool and calculates profit, updating the dict [To do better]
def update_profit(dataPool:list):
    profits = {}
    if not dataPool:
        return

    for item in dataPool:
        s2b_sell_price = float(item["buff_sell_price"])
        b2s_buy_price = float(item["buff_sell_price"])

        s2b_buy_price = float(item["skinp_price"])
        b2s_sell_price = float(item["skinp_price"])

        profits = {
                "s2b_profit": get_profit("s2b", s2b_sell_price, s2b_buy_price),
                "b2s_profit": get_profit("b2s", b2s_sell_price, b2s_buy_price)
            }
        item.update(profits)
    return dataPool

# Scrapes Buff and returns all the data [To do better error handling]
def get_data_buff():
    # Header creation
    sid = str(check_sid())
    session_key = 'session='+ sid +'; '
    headers = {"cookie": session_key, "Accept-Language": "en-US;q=0.8"}
    
    # Url to scrape
    url = "https://buff.163.com/api/market/goods"

    # Create querystring and get the number of pages
    try:
        qs = {"game":"csgo","page_num":"1","page_size":"80"}
        response = requests.request("GET", url, headers=headers, params=qs)
        pages = response.json()['data']['total_page']
        time.sleep(5)
    except Exception:
        return

    # Go through all pages and save the data in [buff_data]
    buff_data = []
    try:
        for page in range(1, pages + 1):
            qs = {"game":"csgo","page_num":f"{page}","page_size":"80"}
            response = requests.request("GET", url, headers=headers, params=qs)

            data = response.json()
            for item in data['data']['items']:
                buff_data.append(item)

            if page >= data['data']['total_page']:
               break
            print(page,"/",pages)
            time.sleep(5)
    except Exception:
        return
    return buff_data

# Scrapes Skinport and returns all the data 
def get_data_skinp():
    # Create querystring and url
    url = "https://api.skinport.com/v1/items"
    qs = {"app_id":"730","currency":"CNY"}
    # Request and return data
    try:
        response = requests.request("GET", url, params=qs)
        return response.json()
    except Exception:
        return

# Creates and returns the final item pool
def create_item_struct():
    # Get data
    buff_pool = get_data_buff()
    skinp_pool = get_data_skinp()

    # Create an array of objects by name
    buff_item = {}
    for item in buff_pool:
        name = item['name']
        
        if name == 'StatTrak\u2122 Swap Tool':
            continue

        buff_item[name] = {
            "item_id": item['id'],
            "item_name": name,
            "buff_buy_price": item['buy_max_price'],
	        "buff_buy_num": item['buy_num'],
	        "buff_sell_price": item['sell_min_price'],
	        "buff_sell_num": item['sell_num'],
            "buff_link": f"https://buff.163.com/goods/{item['id']}"
        } 
    
    # Creates the pool of intersected items 
    skinp_item = {}
    item_data = {}
    for item in skinp_pool:
        name = item['market_hash_name']

        if item['quantity'] == 0:
            price = item['suggested_price']
        else:
            price = item['min_price']

        skinp_item = {
	        "skinp_price": price,
	        "skinp_qnt": item['quantity'],
	        "skinp_link": item['item_page'],
        }

        if name in buff_item:
           item_data[name] = buff_item[name].copy()
           item_data[name].update(skinp_item)

    # Create a list of all updated objects
    items = []
    items.extend(item_data.values())
    item_pool = update_profit(items)
    return item_pool 

# Check last current selling price of an item (Buff)
def get_current_price(id):  
    url = "https://buff.163.com/api/market/goods/sell_order"
    querystring = {"game":"csgo","goods_id":f"{id}"}
    response = requests.request("GET", url, params=querystring)

    price = float(response.json()["data"]["items"][0]["price"])
    name = str(response.json()["data"]["goods_infos"][f"{id}"]["market_hash_name"])

    item = [name, price]
    return item