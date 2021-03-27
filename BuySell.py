import sqlite3
conn = sqlite3.connect('Stock.db')

def buy(code,price,qty,action): #buy_code
    try:
        conn.execute(f'''INSERT INTO {code} VALUES({price*qty},{qty},'{action.upper()}');''')
    except:
        conn.execute(f'''CREATE TABLE {code} (PRICE FLOAT , QTY INT , ACTION VARCHAR(4));''')
        conn.execute(f'''INSERT INTO {code} VALUES({price * qty},{qty},'{action.upper()}');''')

    conn.commit()


def sell(code,price,qty,action): #sell_code
    if Total_Stock(code) >= qty:
        try:
            conn.execute(f'''INSERT INTO {code} VALUES({price * qty},{qty},'{action.upper()}');''')
        except:
            print("NO STOCKS")
    else:
        print('YOU DO NOT HAVE THAT MUCH STOCK QTY')
    conn.commit()


def Total_Stock(code):
    a = conn.execute(f'''SELECT SUM(QTY) FROM {code} WHERE ACTION = 'BUY' ''')
    b = conn.execute(f'''SELECT SUM(QTY) FROM {code} WHERE ACTION = 'SELL' ''')
    for i in a :
        positive = i[0]
    for i in b:
        negative = i[0]

    if negative == None:
        return positive
    else:
        return positive - negative
    conn.commit()

def average_price(code):

    if Total_Stock(code) == None:
        return 0

    elif Total_Stock(code) > 0 :
        a = conn.execute(f'''SELECT SUM(QTY) FROM {code} WHERE ACTION = 'BUY' ''')
        b = conn.execute(f'''SELECT SUM(PRICE) FROM {code} WHERE ACTION = 'BUY' ''')
        c = conn.execute(f'''SELECT SUM(QTY) FROM {code} WHERE ACTION = 'SELL' ''')
        d = conn.execute(f'''SELECT SUM(PRICE) FROM {code} WHERE ACTION = 'SELL' ''')

        for i in a:
            quanb = i[0]
        for i in b:
            amountb = i[0]
        for i in c:
            quans = i[0]
            if quans ==None:
                quans = 0
            else:
                pass
        for i in d:
            amounts = i[0]
            if amounts == None:
                amounts = 0
            else:
                pass
        if quanb == None or quanb == 0:
            return None
        elif quanb - quans > 0 :
            return (amountb-amounts)/(quanb - quans)

    else:
        print('NO STOCK')

    conn.commit()
