import csv
import datetime
import requests
import sqlite3

CREATE_INVESTMENTS_SQL = """
CREATE TABLE IF NOT EXISTS investments (
    coin_id TEXT NOT NULL,
    vs_currency TEXT NOT NULL,
    amount REAL,
    sell INT,
    date TIMESTAMP
);
"""

def get_coin_price(coin_id, vs_currency):
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies={vs_currency}'
    response = requests.get(url)
    if response.status_code == 200:
        price = response.json()[coin_id][vs_currency]
        print(f"The price of {coin_id} is ${price} in {vs_currency}.")
        return price
    else:
        raise Exception(f"Error fetching data: {response.status_code}")

def add_investment(coin_id, vs_currency, amount, sell):
    sql = "INSERT INTO investments VALUES (?, ?, ?, ?, ?);"
    values = (coin_id, vs_currency, amount, sell, datetime.datetime.now())
    cursor.execute(sql, values)
    database.commit()
    if sell:
        print(f"Added sell, {amount} of {coin_id} at {vs_currency}.")
    else:
        print(f"Added buy, {amount} of {coin_id} at {vs_currency}.")

def get_investment_value(coin_id, vs_currency):
    price = get_coin_price(coin_id, vs_currency)
    sql = """SELECT amount
    FROM investments
    WHERE coin_id = ? 
    AND vs_currency = ?
    AND sell=?;"""
    buy_result = cursor.execute(sql, (coin_id, vs_currency, False)).fetchall()
    sell_result = cursor.execute(sql, (coin_id, vs_currency, True)).fetchall()
    buy_amount = sum([row[0] for row in buy_result])
    sell_amount = sum([row[0] for row in sell_result])

    total_amount = buy_amount - sell_amount
    total_value = total_amount * price
    print(f"You own a total of {total_amount} {coin_id} worth ${total_value} at the current price of ${price} in {vs_currency.upper()}.")

def import_investments(csv_file):
    with open(csv_file, 'r') as file:
        rdr = csv.reader(file, delimiter=',')
        rows = list(rdr)
        sql = "INSERT INTO investments VALUES (?, ?, ?, ?, ?);"
        cursor.executemany(sql, rows)
        database.commit()

        print(f"Imported {len(rows)} investments from {csv_file}.")

def export_investments(csv_file=f'data/exported_investments_{datetime.datetime.now().strftime("%m-%d-%Y_%H-%M-%S")}.csv'):
    sql = "SELECT * FROM investments;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(rows)
        print(f"Exported {len(rows)} investments to {csv_file}.")

database = sqlite3.connect('portfolio.db')
cursor = database.cursor()
cursor.execute(CREATE_INVESTMENTS_SQL)

# Example usage
# get_coin_price('bitcoin', 'usd')
# add_investment('bitcoin', 'usd', 0.01, False)
# get_investment_value('bitcoin', 'usd')
# import_investments('data/demo-data.csv')
export_investments()
