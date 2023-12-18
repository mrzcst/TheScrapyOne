import sqlite3

#  Starts DB and ends queries to create tables 
def initiate_database():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    # Main item table
    create_items_table = '''
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            buff_buy_price REAL,
            buff_sell_price REAL,
            buff_sell_num INTEGER,
            buff_buy_num INTEGER,
            buff_link TEXT,
            skinp_price REAL,
            skinp_num INTEGER,
            skinp_link TEXT,
            s2b_profit INTEGER,
            b2s_profit INTEGER
        );
        '''
    cursor.execute(create_items_table)

    # Bought items table
    create_bought_table = '''
        CREATE TABLE IF NOT EXISTS bought_items (
            name TEXT NOT NULL,
            paid_price REAL,
            bought_date DATE,
            tradeble_on DATE,
            minim_sell REAL,
            id INTEGER PRIMARY KEY
        );
        '''
    cursor.execute(create_bought_table)

    # Sold item table
    create_sold_table = '''
        CREATE TABLE IF NOT EXISTS sold_items (
            name TEXT NOT NULL,
            paid_price REAL,
            sold_price REAL,
            sold_site TEXT,
            sold_on DATE,
            profit REAL,
            id INTEGER PRIMARY KEY
        );
        '''
    cursor.execute(create_sold_table)

    # Investments table 
    create_investment_table = '''
        CREATE TABLE IF NOT EXISTS investments (
            name TEXT NOT NULL, 
            quantity INTEGER,
            date DATE,
            total_price REAL,
            price_per_item REAL, 
            price_now REAL, 
            profit REAL,
            item_id INTEGER,
            id INTEGER PRIMARY KEY
        );
        '''
    cursor.execute(create_investment_table)

    # Sid table
    create_sid_table = '''
        CREATE TABLE IF NOT EXISTS sid (
            session_id TEXT PRIMARY KEY,
            date DATE
        );
        '''
    cursor.execute(create_sid_table)

    conn.commit()
    cursor.close()
    conn.close()

# Insert query [items]
def insert_data(data:dict):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    clear_table = '''DELETE FROM items'''
    cursor.execute(clear_table)

    query = '''
    INSERT INTO items 
    VALUES (:item_id, :item_name, :buff_buy_price, :buff_sell_price, 
            :buff_sell_num, :buff_buy_num, :buff_link, 
            :skinp_price, :skinp_qnt, :skinp_link, :s2b_profit, :b2s_profit);
    '''
    for item in data:
        cursor.execute(query, item)

    conn.commit()
    cursor.close()
    conn.close()

# Insert query [bought_items]
def insert_bought_item(item:list):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = f'''
    INSERT INTO bought_items (
        name,
        paid_price, 
        bought_date, 
        tradeble_on,
        minim_sell
    )
    VALUES (?, ?, DATE('now'), DATE('now', '+8 days', '+{item[2]} days'), {item[3]});
    '''
    cursor.execute(query, item[0:2])
    conn.commit()
    cursor.close()
    conn.close()

# Insert query [sold_items]
def insert_sold_item(item:list):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query ='''
    INSERT INTO sold_items (
        name,
        paid_price, 
        sold_price, 
        sold_site,
        sold_on,
        profit
    )
    VALUES (?, ?, ?, ?, DATE('now'), ?);
    '''
    cursor.execute(query, item)

    conn.commit()
    cursor.close()
    conn.close()

# Insert query [investments]
def insert_investment(item:list):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query ='''
    INSERT INTO investments (
        name,
        quantity, 
        date, 
        total_price,
        price_per_item,
        price_now,
        profit,
        item_id
    )
    VALUES (?, ?, DATE('now'), ?, ?, ?, ?, ?);
    '''
    cursor.execute(query, item)

    conn.commit()
    cursor.close()
    conn.close()

# Insert query [SessionInfo]
def insert_sid(sid):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    clear_table = '''DELETE FROM sid'''
    cursor.execute(clear_table) 
    
    query = f'''
    INSERT INTO sid 
    VALUES ("{sid}", DATE('now'));
    '''
    cursor.execute(query)

    conn.commit()
    cursor.close()
    conn.close()

def get_extra_data():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()
    
    items_sold = cursor.execute('SELECT COUNT(*) FROM sold_items;').fetchone()
    skinp_sold = cursor.execute('SELECT COUNT(*) FROM sold_items WHERE sold_site = "Skinport";').fetchone()
    buff_sold = cursor.execute('SELECT COUNT(*) FROM sold_items WHERE sold_site = "Buff";').fetchone()
    profit = cursor.execute('SELECT SUM(profit) FROM sold_items').fetchone()
    
    cursor.close()
    conn.close()

    data = {
        'investment' : "To Be Added Later",
        'items_sold' : items_sold[0], 
        'skinp_sold' : skinp_sold[0],
        'buff_sold' : buff_sold[0],
        'profit' : profit[0]
    }
    return(data)

def get_b2s_data():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = '''
        SELECT 
            name, 
            buff_sell_price,
            skinp_price,
            skinp_num, 
            b2s_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            b2s_profit > 0 
            AND buff_sell_num > 0
        '''
    cursor.execute(query)
    response = cursor.fetchall()

    cursor.close()
    conn.close()
    return response

def get_s2b_data():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = '''
        SELECT 
            name, 
            skinp_price,
            buff_sell_price,
            buff_buy_num, 
            s2b_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            s2b_profit > 0 
            AND skinp_num > 0
        '''
    cursor.execute(query)
    response = cursor.fetchall()

    cursor.close()
    conn.close()
    return response

def get_bought_items():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = '''
        SELECT *
        FROM bought_items
        '''
    cursor.execute(query)
    response = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return response

def get_sold_items():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = '''
        SELECT *
        FROM sold_items
        '''
    cursor.execute(query)
    response = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return response

def get_investments():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = '''
        SELECT *
        FROM investments
        '''
    cursor.execute(query)
    response = cursor.fetchall()

    cursor.close()
    conn.close()
    return response

def get_session():
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = '''
        SELECT *
        FROM sid
        '''
    cursor.execute(query)
    response = cursor.fetchall()

    cursor.close()
    conn.close()

    return response

def delete_bought_item(item_id):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    item_id = (item_id,)

    query = '''
        DELETE FROM bought_items
        WHERE id=?;
        '''
    cursor.execute(query, item_id)

    conn.commit()
    cursor.close()
    conn.close()

def delete_investment(item_id):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    item_id = (item_id,)

    query = '''
        DELETE FROM investments
        WHERE id=?;
        '''
    cursor.execute(query, item_id)

    conn.commit()
    cursor.close()
    conn.close()

def update_investment_price(id, data):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query = f'''
        UPDATE investments
        SET price_now = ?, 
            profit = ?
        WHERE id = {id}
        '''
    cursor.execute(query, data)

    conn.commit()
    cursor.close()
    conn.close()

def search_items(table, search_w):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query_b2s = '''
        SELECT 
            name, 
            buff_buy_price,
            skinp_price,
            skinp_num, 
            b2s_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            b2s_profit > 0 
            AND buff_sell_num > 0
            AND name LIKE ?
        '''
    query_s2b = '''
        SELECT 
            name, 
            skinp_price,
            buff_sell_price,
            buff_buy_num, 
            s2b_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            s2b_profit > 0 
            AND skinp_num > 0
            AND name LIKE ?
        '''
    if table == "b2s":
        query = query_b2s
    else:
        query = query_s2b

    cursor.execute(query, ('%' + search_w + '%',))
    response = cursor.fetchall()

    cursor.close()
    conn.close()
    return response

def filter_by_profit(table, profit_min, profit_max):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query_b2s = f'''
        SELECT 
            name, 
            buff_buy_price,
            skinp_price,
            skinp_num, 
            b2s_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            buff_sell_num > 0
            AND b2s_profit >= {profit_min}
            AND b2s_profit <= {profit_max}
        '''
    query_s2b = f'''
        SELECT 
            name, 
            skinp_price,
            buff_sell_price,
            buff_buy_num, 
            s2b_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            skinp_num > 0
            AND s2b_profit >= {profit_min}
            AND s2b_profit <= {profit_max}
        '''
    if table == "b2s":
        query = query_b2s
    else:
        query = query_s2b

    cursor.execute(query)
    response = cursor.fetchall()

    cursor.close()
    conn.close()

    return response

def filter_by_price(table, price_min, price_max):
    conn = sqlite3.connect('app/data/TsoDB.db')
    cursor = conn.cursor()

    query_b2s = f'''
        SELECT 
            name, 
            buff_buy_price,
            skinp_price,
            skinp_num, 
            b2s_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            b2s_profit > 0
            AND buff_sell_num > 0
            AND buff_buy_price >= {price_min}
            AND buff_buy_price <= {price_max}
        '''
    query_s2b = f'''
        SELECT 
            name, 
            skinp_price,
            buff_sell_price,
            buff_buy_num, 
            s2b_profit, 
            buff_link, 
            skinp_link
        FROM items
        WHERE 
            s2b_profit > 0 
            AND skinp_num > 0
            AND skinp_price >= {price_min}
            AND skinp_price <= {price_max}
        '''
    if table == "b2s":
        query = query_b2s
    else:
        query = query_s2b

    cursor.execute(query)
    response = cursor.fetchall()

    cursor.close()
    conn.close()

    return response