import sqlite3


def get_users():
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT Handle, ID, Status, Spam, Root FROM User")
    response = list(map(lambda x: x[0], cursor.fetchall()))
    conn.commit()
    conn.close()
    return response


def get_carts():
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT UserID, Art, Amount FROM Cart")
    response = list(map(lambda x: x[0], cursor.fetchall()))
    conn.commit()
    conn.close()
    return response


def get_items():
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT Art, OptPrice, SpecPrice, RoznPrice FROM Item")
    response = list(map(lambda x: x[0], cursor.fetchall()))
    conn.commit()
    conn.close()
    return response


def get_orders():
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("SELECT OrderID, UserID, Type, Art, Amount FROM Order")
    response = list(map(lambda x: x[0], cursor.fetchall()))
    conn.commit()
    conn.close()
    return response


def insert_user(handle, ID, root):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO User VALUES (:Handle, :ID, 0, 0, :Root)", {"Handle": handle, "ID": ID, "Root": root})
    conn.commit()
    conn.close()


def insert_cart(userID, art, amount):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Cart VALUES (:UserID, :Art, :Amount)", {"UserID": userID, "Art": art, "Amount": amount})
    conn.commit()
    conn.close()


def insert_item(art, opt_price, spec_price, rozn_price, min_amount):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Item VALUES (:Art, :OptPrice, :SpecPrice, :RoznPrice, :MinAmount)",
                   {"Art": art, "OptPrice": opt_price, "SpecPrice": spec_price, "RoznPrice": rozn_price,
                    "MinAmount": min_amount})
    conn.commit()
    conn.close()


def insert_order(orderID, userID, type, art, amount):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Order VALUES (:OrderID, :UserID, :Type, :Art, :Amount)",
                   {"OrderID": orderID, "UserID": userID, "Type": type, "Art": art, "Amount": amount})
    conn.commit()
    conn.close()


def delete_user(ID):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM User WHERE ID = :ID", {"ID": ID})
    conn.commit()
    conn.close()


def delete_cart(userID):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Cart WHERE UserID = :UserID", {"UserID": userID})
    conn.commit()
    conn.close()


def delete_item(art):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Item WHERE Art = :Art", {"Art": art})
    conn.commit()
    conn.close()


def delete_order(orderID):
    conn = sqlite3.connect("Komus_BD.sqlite")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Order WHERE OrderID = :OrderID", {"OrderID": orderID})
    conn.commit()
    conn.close()
