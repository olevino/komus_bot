import random
import telebot
import time
import requests
import sqlite3
from copy import copy

TOKEN = '459597566:AAF3VonRFQSzgTsEJIgrFLf6xOOU-U5QWEY'
bot = telebot.TeleBot(TOKEN)



orders = {}
list_of_names = {}

cart = {}
last_message = {}
conn = sqlite3.connect('Chinook_Sqlite.sqlite')
cursor = conn.cursor()
cursor.execute('select QWE from QWE')
ORDERS = cursor.fetchone()[0]
cursor.execute('select ID from list_of_clients')
list_of_clients = list(map(lambda x: x[0], cursor.fetchall()))
cursor.execute('select ID from list_of_vip')
list_of_vip = list(map(lambda x: x[0], cursor.fetchall()))
cursor.execute('select ID from list_of_big_VIP')
list_of_Vip = list(map(lambda x: x[0], cursor.fetchall()))
cursor.execute('select EWQ from EWQ')
INVITE = cursor.fetchone()[0].strip()
cursor.execute('select ID, name from list_of_names')
results = cursor.fetchall()
for item in results:
    list_of_names[item[0]]=item[1]
for item in list_of_clients:
    orders[item]=[]
cursor.execute('select ID, MessageID from last_message')
results = cursor.fetchall()
for item in results:
    last_message[item[0]]=item[1]

cursor.execute('select Number, ClientID, Status from orders')
results = cursor.fetchall()
for i in range(len(results)):
    cursor.execute('select ID, Item_ID, Value, Flag_0, Name, Price_1, Price_2, Num from order_cart where Num = :qwe', {'qwe':results[i][0]})
    res = cursor.fetchall()
    results[i] = list(results[i])
    carts = {}
    for item in res:
        item = list(item)
        carts[item[1]] = [item[2], item[3:7]+[item[1]]]
    results[i] = [results[i][0]]+[carts]+results[i][1:]
    orders[results[i][2]]+=[results[i]]
cursor.execute('select ID, ID_Item, Value, Flag_0, Name, Price_1, Price_2 from cart')
results = cursor.fetchall()
for item in results:
    if(item[0] not in cart):
        cart[item[0]] = {}
    flag = (item[3], item[4], item[5], item[6], item[1])
    cart[item[0]][item[1]] = [item[2],flag]
conn.close()


AdminId = 262432234

@bot.message_handler(['gen_invite'])
def get_invite(message):
    global INVITE
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        standart(message)
        return
    a = [chr(c) for c in range(ord('a'),ord('z')+1)] + [chr(c) for c in range(ord('A'),ord('Z')+1)]+[str(c) for c in range(10)]
    s = ''.join([random.choice(a) for i in range(random.randrange(7,13))])
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from EWQ where EWQ = :INVITE', {'INVITE':INVITE})
    cursor.execute('insert into EWQ values (:s)', {'s':s})
    conn.commit()
    conn.close()
    INVITE = s
    bot.send_message(AdminId,'Новый Invite-код: '+INVITE)

def update_name(message):
    name = ''
    if message.from_user.username is None:
        name = str(message.from_user.first_name) + ' ' + str(message.from_user.last_name)
    else:
        name = str(message.from_user.username)
    if(message.chat.id in list_of_clients and (message.chat.id not in list_of_names or list_of_names[message.chat.id] != name) and name != 'olevino_komus_bot'):
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        if(message.chat.id in list_of_names):
            cursor.execute('delete from list_of_names where ID='+str(message.chat.id))
        cursor.execute('insert into list_of_names values (:id, :name)',{'id': str(message.chat.id), 'name': str(name)})
        conn.commit()
        cursor.execute('select ID, name from list_of_names')
        results = cursor.fetchall()
        for item in results:
            list_of_names[item[0]] = item[1]
        conn.close()

def delete_markup(id):
    if (last_message[id] != -1):
        now = telebot.types.InlineKeyboardMarkup()
        now.add(telebot.types.InlineKeyboardButton(text='Разделитель сообщений', callback_data='Нихуя'))
        try:
            bot.edit_message_reply_markup(id, last_message[id], None, now)
        except Exception as error:
            last_message[id]=-1
            conn = sqlite3.connect('Chinook_Sqlite.sqlite')
            cursor=conn.cursor()
            cursor.execute('delete from last_message where ID = :num', {'num':id})
            cursor.execute('insert into last_message values (:ID, :MessageID)', {'ID':id, 'MessageID':last_message[id]})
            conn.commit()
            conn.close()
        last_message[id]=-1
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor=conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num':id})
        cursor.execute('insert into last_message values (:ID, :MessageID)', {'ID':id, 'MessageID':last_message[id]})
        conn.commit()
        conn.close()


def opt(art):  # принимает артикул. Возвращает цену и количество.
    q = requests.Session()
    o = q.post('http://komus-opt.ru/auth/?login=yes&backurl=/',
               {'auth_ch': 1, 'AUTH_FORM': 'Y', 'TYPE': 'AUTH', 'USER_LOGIN': 'QWEQWE@bk.ru',
                'USER_PASSWORD': 'QWEWQE', 'Login': 'Войти'})
    response = q.get('http://komus-opt.ru/search/?q=' + art)
    p = response.text.find('var dataToGetID = [') + 19
    e = 0
    while (response.text[p] != ']'):
        if (response.text[p] in '0123456789'):
            e *= 10
            e += int(response.text[p])
        p += 1
    z = response.text.find('crc: ') + 6
    s = ''
    while (response.text[z] != '"'):
        s += response.text[z]
        z += 1
    r = q.post('http://komus-opt.ru/local/components/komusopt/catalog.v4.element/ajax.php',
               data={'action': 'getPrice', 'items[]': art, 'itemsID[]': e, 'crc': s},
               headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64...) Gecko/20100101 Firefox/57.0',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        'X-Requested-With': 'XMLHttpRequest'})
    y = r.text.find('|') + 1
    s = ''
    while (r.text[y:y + 2] != ' р'):
        if (r.text[y] not in ' ,'):
            s += r.text[y]
        elif (r.text[y] == ','):
            s += '.'
        y += 1
    response = q.get('http://komus-opt.ru/search/?q=' + art)
    p = response.text.find('input name="quantity"')
    if(p == -1):
        return [-1,-1]
    while (response.text[p:p + 7] != 'value="'):
        p += 1
    p = p + 7
    a = 0
    while (response.text[p] != '"'):
        a *= 10
        a += int(response.text[p])
        p += 1
    return [float(s), a]


def rozn(art, response):  # принимает артикул и страницу. Возвращает цену без скидки и цену со скидкой
    # p - Без скидки
    # s - Со скидкой
    if ('Товар отсутствует на складе' in response.text or 'Поставки прекращены' in response.text):
        return [-1, -1]
    s = response.text.find('i-fs30 i-fwb"> ') + 15
    p = s
    if ('i-td-thr i-fs22 i-fwb"> ' in response.text):
        p = response.text.find('i-td-thr i-fs22 i-fwb"> ') + 24
    a = 0
    while (response.text[p] != ','):
        if (response.text[p] in '0123456789'):
            a *= 10
            a += int(response.text[p])
        p += 1
    a += int(response.text[p + 1:p + 3]) / 100
    b = 0
    while (response.text[s] != ','):
        if (response.text[s] in '0123456789'):
            b *= 10
            b += int(response.text[s])
        s += 1
    b += int(response.text[s + 1:s + 3]) / 100
    return [str(a), str(b)]


def get_name_item(art, response):
    p = response.text.find('b-productName" itemprop="name">') + 31
    s = ''
    while (response.text[p] != '<'):
        s += response.text[p]
        p += 1
    return s


def hello(message):
    if (message.chat.id not in list_of_clients):
        start(message)
        return
    bot.send_message(message.chat.id,
                     "Я - бот, помогающий выбрать интересующий вас товар по низкой цене. Выберите интересующий вас товар на сайте http://komus.ru, а затем дайте мне его артикул. Я расскажу вам по какой цене вы можете его получить и помогу собрать ваш заказ.\n\nОбратите внимание, что мы специализируемся на канцелярских товарах, поэтому не удивляйтесь тому, что большая часть хозяйственных товаров с сайта может оказаться недоступной.\n\n По всем вопросам пишите тому, от кого вы получили Invite-код")


def standart(message):
    if (message.chat.id not in list_of_clients):
        start(message)
        return
    update_name(message)
    now = telebot.types.InlineKeyboardMarkup()
    now.add(telebot.types.InlineKeyboardButton(text='Узнать информацию о товаре',
                                               callback_data='Узнать информацию о товаре'))
    now.add(telebot.types.InlineKeyboardButton(text='Перейти в корзину', callback_data='Перейти в корзину'))
    now.add(telebot.types.InlineKeyboardButton(text='Мои заказы', callback_data='Мои заказы'))
    last_message[message.chat.id] = (bot.send_message(message.chat.id, 'Выберите действие:', reply_markup=now)).message_id
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)', {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
    conn.commit()
    conn.close()


@bot.callback_query_handler(func=lambda c: 'Мои заказы' in c.data)
def inline9(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    if (c.message.chat.id not in last_message):
        last_message[c.message.chat.id] = -1
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
        conn.commit()
        conn.close()
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    now = telebot.types.InlineKeyboardMarkup()
    now.add(telebot.types.InlineKeyboardButton(text='Активные заказы', callback_data='Активные заказы'))
    now.add(telebot.types.InlineKeyboardButton(text='Завершенные заказы', callback_data='Завершенные заказы'))
    now.add(
        telebot.types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='Вернуться в главное меню'))
    last_message[c.message.chat.id] = bot.send_message(c.message.chat.id, 'Выберите действие:', reply_markup=now).message_id
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()

@bot.callback_query_handler(func=lambda c: c.data == 'Узнать информацию о товаре')
def inline_0(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    bot.send_message(c.message.chat.id, 'Введите артикул товара или ссылку на него с сайта www.komus.ru')


@bot.callback_query_handler(func=lambda c: c.data == 'Перейти в корзину')
def inline_1(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    get_cart(c.message.chat.id, c.message.chat.id)


@bot.message_handler(commands=['code'])
def add_code(message):
    if (message.chat.id not in last_message):
        last_message[message.chat.id] = -1
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
        conn.commit()
        conn.close()
    delete_markup(message.chat.id)
    last_message[message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
    conn.commit()
    conn.close()
    if (len(message.text.split()) == 1):
        start(message)
        return
    global list_of_clients
    if (message.chat.id in list_of_clients):
        bot.send_message(message.chat.id, 'Вы уже авторизованы')
        standart(message)
        return
    code = message.text.split()[1]
    if (INVITE != code):
        bot.send_message(message.chat.id, 'Неверный Invite-код')
        start(message)
        return
    bot.send_message(message.chat.id, 'Поздравляем, Invite-код активирован.')
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('insert into list_of_clients values (' + str(message.chat.id)+')')
    conn.commit()
    cursor.execute('select ID from list_of_clients')
    list_of_clients = list(map(lambda x: x[0], cursor.fetchall()))
    conn.close()
    update_name(message)
    orders[message.chat.id] = []
    start(message)


@bot.message_handler(commands=['start'])
@bot.message_handler(commands=['help'])
def start(message):
    if (message.chat.id not in last_message):
        last_message[message.chat.id] = -1
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
        conn.commit()
        conn.close()
    delete_markup(message.chat.id)
    last_message[message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
    conn.commit()
    conn.close()
    if (message.chat.id not in list_of_clients):
        bot.send_message(message.chat.id,
                         'Чтобы получить доступ к боту, введите сообщение в формате "/code ######", где вместо решеток вставьте свой Invite-код.')
        return
    hello(message)
    standart(message)


@bot.message_handler(commands=['add_vip'])
def add_vip(message):
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        return
    if (len(message.text.split()) == 1):
        bot.send_message(message.chat.id,
                         'Введите команду в формате "/add_vip ######", где вместо решеток вставьте ID клиента.')
        return
    message.text = message.text.split()[1]
    global list_of_vip
    global list_of_Vip
    if (not message.text.isnumeric()):
        bot.send_message(message.chat.id, 'Некорректный ID клиента')
    elif (int(message.text) in list_of_vip):
        bot.send_message(message.chat.id, 'Данный клиент уже имеет vip-статус')
    else:
        flag = 0
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        if (int(message.text) in list_of_Vip):
            list_of_Vip.remove(int(message.text))
            bot.send_message(int(message.text), 'Вы потеряли VIP-статус')
            flag = 1
            bot.send_message(message.chat.id, 'Пользователь успешно потерял VIP-статус')
            cursor.execute('delete from list_of_big_VIP where ID = :num', {'num':int(message.text)})
        cursor.execute('insert into list_of_vip values (:ID)',{'ID':int(message.text)})
        conn.commit()
        conn.close()
        if (flag == 1):
            message.chat.id = int(message.text)
            delete_cart_call(message)
        else:
            standart(message)
        list_of_vip += [int(message.text)]
        bot.send_message(AdminId, 'Пользователь успешно получил vip-статус')
        bot.send_message(int(message.text), 'Вы получили vip-статус')


@bot.message_handler(commands=['add_VIP'])
def add_Vip(message):
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        return
    if (len(message.text.split()) == 1):
        bot.send_message(message.chat.id,
                         'Введите команду в формате "/add_VIP ######", где вместо решеток вставьте ID клиента.')
        return
    message.text = message.text.split()[1]
    global list_of_vip
    global list_of_Vip
    if (not message.text.isnumeric()):
        bot.send_message(message.chat.id, 'Некорректный ID клиента')
    elif (int(message.text) in list_of_Vip):
        bot.send_message(message.chat.id, 'Данный клиент уже имеет vip-статус')
    else:
        flag = 0
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        if (int(message.text) in list_of_vip):
            list_of_vip.remove(int(message.text))
            bot.send_message(int(message.text), 'Вы потеряли vip-статус')
            flag = 1
            bot.send_message(message.chat.id, 'Пользователь успешно потерял vip-статус')
            cursor.execute('delete from list_of_vip where ID = :num', {'num': int(message.text)})
        cursor.execute('insert into list_of_big_VIP values (:ID)', {'ID': int(message.text)})
        conn.commit()
        conn.close()
        list_of_Vip += [int(message.text)]
        bot.send_message(AdminId, 'Пользователь успешно получил VIP-статус')
        bot.send_message(int(message.text), 'Вы получили VIP-статус')
        if (flag == 1):
            message.chat.id = int(message.text)
            delete_cart_call(message)
        else:
            standart(message)

@bot.message_handler(commands=['remove_vip'])
def remove_all_vip(message):
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        return
    if (len(message.text.split()) == 1):
        bot.send_message(message.chat.id,
                         'Введите команду в формате "/remove_vip ######", где вместо решеток вставьте ID клиента.')
        return
    message.text = message.text.split()[1]
    global list_of_vip
    global list_of_Vip
    if (not message.text.isnumeric()):
        bot.send_message(message.chat.id, 'Некорректный ID клиента')
    elif (int(message.text) not in list_of_Vip and int(message.text) not in list_of_vip):
        bot.send_message(message.chat.id, 'Данный клиент не имеет vip- и VIP-статусов')
    else:
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        if (int(message.text) in list_of_vip):
            list_of_vip.remove(int(message.text))
            bot.send_message(message.chat.id, 'Пользователь успешно потерял vip-статус')
            bot.send_message(int(message.text), 'Вы потеряли vip-статус')
            cursor.execute('delete from list_of_vip where ID = :num', {'num': int(message.text)})
        if (int(message.text) in list_of_Vip):
            cursor.execute('delete from list_of_big_VIP where ID = :num', {'num': int(message.text)})
            list_of_Vip.remove(int(message.text))
            bot.send_message(message.chat.id, 'Пользователь успешно потерял VIP-статус')
            bot.send_message(int(message.text), 'Вы потеряли VIP-статус')
        conn.commit()
        conn.close()
        message.chat.id = int(message.text)
        delete_cart_call(message)

@bot.message_handler(commands=['get_my_id'])
def get_id(a):
    message = copy(a)
    if (message.chat.id not in last_message):
        last_message[message.chat.id] = -1
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
        conn.commit()
        conn.close()
    update_name(message)
    delete_markup(message.chat.id)
    last_message[message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, 'Ваш ID: ' + str(message.chat.id))
    standart(message)


def get_info(a, q=-1):
    message = copy(a)
    if (not message.text.isnumeric()):
        if (q != -1):
            bot.delete_message(q.chat.id, q.message_id)
        bot.send_message(message.chat.id, 'Некорректный артикул товара')
        standart(message)
        return
    response = requests.get('https://www.komus.ru/search?text=' + message.text)
    resp2 = requests.get('http://komus-opt.ru/search/?q=' + message.text)
    if (response.url == 'https://www.komus.ru/search?text=' + message.text):
        if (q != -1):
            bot.delete_message(q.chat.id, q.message_id)
        bot.send_message(message.chat.id,
                         'Несуществующий артикул товара. Если вы уверены в данном артикуле, напишите тому, кто дал вам Invite-код.')
        standart(message)
        return
    elif (resp2.url == 'http://komus-opt.ru/search/?q=' + message.text):
        if (q != -1):
            bot.delete_message(q.chat.id, q.message_id)
        bot.send_message(message.chat.id,
                         'К сожалению, данный товар доступен только в розничном магазине. Привезти его вам мы не сможем.')
        standart(message)
        return
    name = get_name_item(message.text, response)
    rozn_price = rozn(message.text, response)
    opt_price = opt(message.text)
    value = int(float(opt_price[1]))
    opt_price = float(opt_price[0])
    rozn_price_bez = float(rozn_price[0])
    rozn_price_with = float(rozn_price[1])
    rozn_price_res = 0
    if (opt_price == -1):
        if (q != -1):
            bot.delete_message(q.chat.id, q.message_id)
        bot.send_message(message.chat.id,
                         'К сожалению, данный товар доступен только в розничном магазине. Привезти его вам мы не сможем.')
        standart(message)
        return
    if (opt_price > rozn_price_with):
        if (q != -1):
            bot.delete_message(q.chat.id, q.message_id)
        bot.send_message(message.chat.id,
                         'Данный товар в розничном магазине стоит дешевле, чем в оптовом. Закажите его там.')
        standart(message)
        return
    if (rozn_price_bez == -1):
        rozn_price_res = -1
    elif ((float(rozn_price_bez) + float(opt_price)) / 2 > float(rozn_price_with)):
        rozn_price_res = str(rozn_price_with)
    else:
        rozn_price_res = str(rozn_price_bez)
    text = 'Товар: ' + name + '\n' + 'Артикул: ' + message.text + '\n' + 'Страница товара в розничном магазине: ' + response.url + '\n'
    qwe = 0
    if (float(rozn_price_res) == -1):
        if (message.chat.id in list_of_Vip):
            text += 'В розничном интернет-магазине товар сейчас отсутствует\n'
            text += 'Цена, по которой привезем вам: ' + str(round(float(opt_price), 2)) + ' руб.\n'
        else:
            text += 'В розничном интернет-магазине товар сейчас отсутствует\n'
            text += 'Цена, по которой привезем вам: ' + str(round(float(opt_price) * 1.3, 2)) + ' руб.\n'
    else:
        text += 'Цена в розничном магазине: ' + rozn_price_res + ' руб.\n'
        text += 'Цена, по которой привезем вам: '
        qwe = round(float(calc_price(opt_price, rozn_price_res, message.chat.id, rozn_price_with)), 2)
        text += str(qwe) + ' руб.\n'
    text += 'Заказывать пачками по ' + str(value) + ' шт.\n'
    if (float(rozn_price_res) == -1):
        if (message.chat.id in list_of_vip):
            text += 'Цена одной пачки: ' + str(float(opt_price) * int(float(value))) + ' руб.\n'
        else:
            text += 'Цена одной пачки: ' + str(round(float(opt_price) * 1.3, 2) * int(float(value))) + ' руб.\n'
    else:
        text += 'Цена одной пачки: ' + str(round(qwe * int(float(value)), 2)) + ' руб.\n'
    now = telebot.types.InlineKeyboardMarkup()
    now.add(telebot.types.InlineKeyboardButton(text='Добавить 1 пачку товара в корзину',
                                               callback_data='Добавить товар в корзину ' + message.text + ' 1 ' + str(
                                                   int(
                                                       value))))
    now.add(telebot.types.InlineKeyboardButton(text='Добавить 2 пачки товара в корзину',
                                               callback_data='Добавить товар в корзину ' + message.text + ' 2 ' + str(
                                                   int(
                                                       value))))
    now.add(telebot.types.InlineKeyboardButton(text='Добавить 5 пачек товара в корзину',
                                               callback_data='Добавить товар в корзину ' + message.text + ' 5 ' + str(
                                                   int(value))))
    now.add(telebot.types.InlineKeyboardButton(text='Добавить 10 пачек товара в корзину',
                                               callback_data='Добавить товар в корзину ' + message.text + ' 10 ' + str(
                                                   int(value))))
    now.add(
        telebot.types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='Вернуться в главное меню'))
    if (q != -1):
        bot.delete_message(q.chat.id, q.message_id)
    last_message[message.chat.id] = bot.send_message(message.chat.id, text, disable_web_page_preview=True,
                                                     reply_markup=now).message_id
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
    conn.commit()
    conn.close()


def calc_price(opt_price, rozn_price, id, rozn_price_with):
    if (id in list_of_Vip):
        return str(opt_price)
    elif (id in list_of_vip):
        return str((min(float(opt_price) * 1.3, (float(opt_price) + float(rozn_price)) / 2, float(rozn_price_with))))
    else:
        return str(min((float(opt_price) + float(rozn_price)) / 2, float(rozn_price_with)))


@bot.callback_query_handler(func=lambda c: c.data == 'Вернуться в главное меню')
def inline_3(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    standart(c.message)


@bot.callback_query_handler(func=lambda c: 'Добавить товар в корзину' in c.data)
def inline_2(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    art = c.data.split()[4]
    value = c.data.split()[-2]
    min_value = c.data.split()[-1]
    add_to_cart(c.message.chat.id, art, value, min_value)


def exists(art, id):
    response = requests.get('https://www.komus.ru/search?text=' + str(art))
    resp2 = requests.get('http://komus-opt.ru/search/?q=' + str(art))
    if (response.url == 'https://www.komus.ru/search?text=' + str(art)):
        return [2]
    elif (resp2.url == 'http://komus-opt.ru/search/?q=' + str(art)):
        return [3]
    q = opt(art)
    rozn_price = rozn(art, response)
    if (rozn_price[0] == -1):
        rozn_price_res = -1
    elif ((float(rozn_price[0]) + float(q[0])) / 2 > float(rozn_price[1])):
        rozn_price_res = str(rozn_price[1])
    else:
        rozn_price_res = str(rozn_price[0])
    return [1, get_name_item(art, response), round(float(calc_price(q[0], rozn_price_res, id, rozn_price[1])), 2), q[1],
            art]


def add_to_cart(id, art, value, min_value):
    q = bot.send_message(id, 'Ожидайте...')
    flag = exists(art, id)
    if (id not in cart):
        cart[id] = {}
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    if (art not in cart[id]):
        cart[id][art] = [0, flag]
        cursor.execute('insert into cart values (:ID, :ID_Item, :Value, :Flag_0, :Name, :Price_1, :Price_2)', {'ID':id, 'ID_Item':art, 'Value': 0, 'Flag_0':flag[0], 'Name':flag[1], 'Price_1':flag[2], 'Price_2':flag[3]})
    cart[id][art][1] = flag
    cursor.execute('delete from cart where ID = :ID AND ID_Item = :ID_Item', {'ID':id, 'ID_Item':art})
    cursor.execute('insert into cart values (:ID, :ID_Item, :Value, :Flag_0, :Name, :Price_1, :Price_2)',
                   {'ID': id, 'ID_Item': art, 'Value': cart[id][art][0]+int(float(value) * float(min_value)), 'Flag_0': flag[0], 'Name': flag[1], 'Price_1': flag[2],
                    'Price_2': flag[3]})
    conn.commit()
    conn.close()
    cart[id][art][0] += int(float(value) * float(min_value))
    text = str(int(float(value) * float(min_value)))
    text += ' единиц (' + str(
        int(float(value))) + ' пачек) товара добавлено в корзину.\nСтоимость добавленного товара: '
    text += str(round(float(value) * float(min_value) * float(flag[2]), 2))
    text += ' руб.\nСтоимость всех товаров в корзине: '
    text += str(get_sum_cart(id)) + ' руб.'
    now = telebot.types.InlineKeyboardMarkup()
    now.add(telebot.types.InlineKeyboardButton(text='Перейти в корзину', callback_data='Перейти в корзину'))
    now.add(
        telebot.types.InlineKeyboardButton(text='Вернуться в главное меню', callback_data='Вернуться в главное меню'))
    bot.delete_message(q.chat.id, q.message_id)
    last_message[id] = bot.send_message(id, text, reply_markup=now).message_id
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': id, 'MessageID': last_message[id]})
    conn.commit()
    conn.close()


def get_cart(id, mess):
    a = 0
    su = 0
    if (id not in cart):
        cart[id] = {}
    text = 'Ваша корзина:\n\n'
    for item in cart[id]:
        if (cart[id][item][0] != 0):
            a += 1
            text += 'Наименование товара: ' + str(cart[id][item][1][1]) + '\n'
            text += 'Артикул товара: ' + str(cart[id][item][1][4]) + '\n'
            text += 'Цена товара: ' + str(cart[id][item][1][2]) + ' руб.\n'
            text += 'Количество: ' + str(int(float(cart[id][item][0]))) + '\n'
            text += 'Стоимость: ' + str(round(float(cart[id][item][0]) * float(cart[id][item][1][2]), 2)) + ' руб.\n\n'
            su += round(float(cart[id][item][0]) * float(cart[id][item][1][2]), 2)
    text += 'Общая сумма: ' + str(round(float(su), 2)) + ' руб.'
    if (id == mess):
        if (a == 0):
            text = 'Ваша корзина пуста.\nСумма: 0.00 руб.'
        now = telebot.types.InlineKeyboardMarkup()
        if (a != 0):
            now.add(telebot.types.InlineKeyboardButton(text='Удалить товар из корзины',
                                                       callback_data='Удалить товар из корзины'))
            now.add(telebot.types.InlineKeyboardButton(text='Очистить корзину', callback_data='Очистить корзину'))
            now.add(telebot.types.InlineKeyboardButton(text='Подтвердить заказ', callback_data='Подтвердить заказ'))
        now.add(telebot.types.InlineKeyboardButton(text='Вернуться в главное меню',
                                                   callback_data='Вернуться в главное меню'))
        last_message[id] = bot.send_message(mess, text, reply_markup=now).message_id
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': id, 'MessageID': last_message[id]})
        conn.commit()
        conn.close()
    else:
        bot.send_message(mess, text)


@bot.callback_query_handler(func=lambda c: 'Очистить корзину' in c.data)
def clean_cart_all(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    if(c.data == 'Очистить корзину'):
        now = telebot.types.InlineKeyboardMarkup()
        now.add(telebot.types.InlineKeyboardButton(text='Да, полностью очистить корзину.',callback_data='Очистить корзину да'))
        now.add(telebot.types.InlineKeyboardButton(text='Нет, отменить очищение корзины.', callback_data='Очистить корзину нет'))
        last_message[c.message.chat.id] = bot.send_message(c.message.chat.id, 'Вы уверены?',reply_markup=now).message_id
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
        conn.commit()
        conn.close()
    elif(c.data.split()[2]=='да'):
        cart[c.message.chat.id] = {}
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from cart where ID=:ID',{'ID':c.message.chat.id})
        conn.commit()
        conn.close()
        bot.send_message(c.message.chat.id, 'Ваша корзина успешно очищена.\nСумма: 0.00 руб.')
        standart(c.message)
    else:
        bot.send_message(c.message.chat.id, 'Очищение корзины отменено.')
        standart(c.message)

def delete_cart_call(message):
    if (message.chat.id not in list_of_clients):
        start(message)
        return
    update_name(message)
    delete_markup(message.chat.id)
    last_message[message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
    cursor.execute('delete from cart where ID=:id',{'ID':id})
    conn.commit()
    conn.close()
    cart[message.chat.id] = {}
    bot.send_message(message.chat.id, 'Ваша корзина успешно очищена.\nСумма: 0.00 руб.')
    standart(message)

@bot.callback_query_handler(func=lambda c: 'Удалить товар из корзины' in c.data)
def clean_cart_item(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    if c.data == 'Удалить товар из корзины':
        now = telebot.types.InlineKeyboardMarkup()
        t = []
        for item in cart[c.message.chat.id]:
            if float(cart[c.message.chat.id][item][0]) != 0:
                t += [telebot.types.InlineKeyboardButton(text=str(cart[c.message.chat.id][item][1][4]),
                                                         callback_data='Удалить товар из корзины ' + str(
                                                             cart[c.message.chat.id][item][1][4]))]
                if (len(t) == 3):
                    now.add(*t)
                    t = []
        if t != []:
            now.add(*t)
        now.add(telebot.types.InlineKeyboardButton(text='Вернуться в корзину', callback_data='Перейти в корзину'))
        last_message[c.message.chat.id] = bot.send_message(c.message.chat.id,
                                                           'Выберите артикул товара, который нужно удалить из корзины:',
                                                           reply_markup=now).message_id
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
        conn.commit()
        conn.close()
    else:
        art = c.data.split()[4]
        if (art not in cart[c.message.chat.id]):
            bot.send_message(c.message.chat.id,
                             'Данного товара в корзине нет.\nСумма: ' + str(get_sum_cart(c.message.chat.id)) + ' руб.')
            standart(c.message)
        else:
            cart[c.message.chat.id].pop(art)
            bot.send_message(c.message.chat.id, 'Товар успешно удален из корзины.\nСумма: ' + str(
                get_sum_cart(c.message.chat.id)) + ' руб.')
            conn = sqlite3.connect('Chinook_Sqlite.sqlite')
            cursor = conn.cursor()
            cursor.execute('delete from cart where ID = :ID AND ID_Item = :ID_Item', {'ID':c.message.chat.id, 'ID_Item':art})
            conn.commit()
            conn.close()
            standart(c.message)


def get_sum_cart(id):
    su = 0
    a = 0
    if (id not in cart):
        cart[id] = {}
    text = ''
    for item in cart[id]:
        if (cart[id][item][0] != 0):
            a += 1
            su += round(float(cart[id][item][0]) * float(cart[id][item][1][2]), 2)
    if (a == 0):
        su = 0
    return round(float(su), 2)


@bot.callback_query_handler(func=lambda c: 'Подтвердить заказ' in c.data)
def confirm_order(c):
    if (c.message.chat.id not in list_of_clients):
        start(c.message)
        return
    update_name(c.message)
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    if (get_sum_cart(c.message.chat.id) == 0):
        bot.send_message(c.message.chat.id, 'Ваша корзина пуста. Пополните корзину перед подтверждением.')
        standart(c.message)
    elif c.data == 'Подтвердить заказ':
        now = telebot.types.InlineKeyboardMarkup()
        now.add(telebot.types.InlineKeyboardButton(text='Да, подтвердить заказ!', callback_data='Подтвердить заказ да'))
        now.add(telebot.types.InlineKeyboardButton(text='Нет, не подтверждать заказ',
                                                   callback_data='Подтвердить заказ нет'))
        last_message[c.message.chat.id] = bot.send_message(c.message.chat.id, 'Вы уверены?', reply_markup=now).message_id
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
        conn.commit()
        conn.close()
    elif c.data.split()[-1] == 'да':
        text = get_cart(c.message.chat.id, AdminId)
        global ORDERS
        bot.send_message(AdminId, 'Handle: ' + str(list_of_names[c.message.chat.id]) + '\n' + 'ID: ' + str(c.message.chat.id)+'\n'+'Номер заказа: №' + str(ORDERS))
        bot.send_message(c.message.chat.id, 'Ваш заказ подтвержден. В ближайшее время с вами свяжутся.')
        global orders
        if (c.message.chat.id not in orders):
            orders[c.message.chat.id] = []

        orders[c.message.chat.id] += [[ORDERS, copy(cart[c.message.chat.id]), c.message.chat.id, 0]]
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor=conn.cursor()
        cursor.execute('insert into orders values (:number, :id, 0)', {'number':ORDERS, 'id' : c.message.chat.id})
        for item in cart[c.message.chat.id]:
            cursor.execute('insert into order_cart values (:ID, :Item_ID, :Value, :Flag_0, :Name,:Price_1, :Price_2, :Num)', {'ID':c.message.chat.id, 'Item_ID':item, 'Value':cart[c.message.chat.id][item][0],'Flag_0':cart[c.message.chat.id][item][1][0], 'Name':cart[c.message.chat.id][item][1][1], 'Price_1':cart[c.message.chat.id][item][1][2], 'Price_2':cart[c.message.chat.id][item][1][3],'Num': ORDERS})
        cursor.execute('delete from QWE where QWE=:ORDERS',{'ORDERS':ORDERS})
        cursor.execute('insert into QWE values (:ORDERS)',{'ORDERS':ORDERS+1})
        ORDERS += 1
        cart[c.message.chat.id].clear()
        cursor.execute('delete from cart where ID=:ID', {'ID': c.message.chat.id})
        conn.commit()
        conn.close()
        standart(c.message)
    else:
        bot.send_message(c.message.chat.id, 'Подтверждение заказа отменено')
        standart(c.message)


@bot.message_handler(['broadcast'])
def broadcast(message):
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        standart(message)
        return
    if (len(message.text.split()) == 1):
        bot.send_message(message.chat.id,
                         'Введите команду в формате "/broadcast ######", где вместо решеток вставьте сообщение, которое отправится всем клиентам.')
        return
    p = message.text.find('broadcast')
    message.text = message.text[p + 10:]
    for item in list_of_clients:
        bot.send_message(item, message.text)
        standart(message)

@bot.message_handler(['broadcast_active'])
def broadcast(message):
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        standart(message)
        return
    if (len(message.text.split()) == 1):
        bot.send_message(message.chat.id,
                         'Введите команду в формате "/broadcast_active ######", где вместо решеток вставьте сообщение, которое отправится всем клиентам.')
        return
    p = message.text.find('broadcast_active')
    message.text = message.text[p + 17:]
    for item in list_of_clients:
        flag = 0
        if(item in orders):
            for order in orders[item]:
                if(order[3] != 4):
                    flag = 1
        if(flag):
            bot.send_message(item, message.text)
            standart(message)
            
@bot.message_handler(['show_all_orders'])
def show_all_orders(message):
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        standart(message)
        return
    for person in orders:
        k = -1
        for order in orders[person]:
            if(order[3]!=4):
                k += 1
                text = 'Номер заказа: ' + str(order[0]) + '\n'
                text += 'ID клиента: ' + str(order[2]) + '\n'
                text += 'Handle: ' + str(list_of_names[order[2]]) + '\n'
                if (order[3] == 0):
                    text += 'Статус заказа: Ожидает подтверждения.\n'
                elif order[3] == 1:
                    text += 'Статус заказа: Подтвержден. Ожидает доставки.\n'
                elif order[3] == 2:
                    text += 'Статус заказа: Доставлен. Ожидает получения.\n'
                elif order[3] == 3:
                    text += 'Статус заказа: Заказ получен. Завершён.\n'
                text += '\n'
                a = 0
                su = 0
                for item in order[1]:
                    if (order[1][item][0] != 0):
                        text += 'Наименование товара: ' + str(order[1][item][1][1]) + '\n'
                        text += 'Артикул товара: ' + str(order[1][item][1][4]) + '\n'
                        text += 'Цена товара: ' + str(order[1][item][1][2]) + ' руб.\n'
                        text += 'Количество: ' + str(int(float(order[1][item][0]))) + '\n'
                        text += 'Стоимость: ' + str(
                            round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)) + ' руб.\n\n'
                        su += round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)
                text += 'Общая сумма: ' + str(round(float(su), 2)) + ' руб.\n'
                if (order[3] != 3):
                    now = telebot.types.InlineKeyboardMarkup()
                    if (order[3] == 0):
                        now.add(telebot.types.InlineKeyboardButton(text='Подтвердить заказ', callback_data='Кек0 ' + str(person) + ' ' + str(k) + ' ' + str(order[0])))
                    elif order[3] == 1:
                        now.add(telebot.types.InlineKeyboardButton(text='Отметить заказ, как доставленный',
                                                                   callback_data=str(
                                                                       'Кек1 ' + str(
                                                                           person) + ' ' + str(k) + ' ' + str(order[0]))))
                    elif order[3] == 2:
                        now.add(telebot.types.InlineKeyboardButton(text='Отметить заказ, как полученный(завершенный)',
                                                                   callback_data=str(
                                                                       'Кек2 ' + str(
                                                                           person) + ' ' + str(k) + ' ' + str(order[0]))))
                    now.add(telebot.types.InlineKeyboardButton(text = 'Отменить заказ', callback_data=str('Кек3 ' +str(person) + ' '+str(k) + ' ' +str(order[0]))))
                    bot.send_message(AdminId, text, reply_markup=now)
                else:
                    bot.send_message(AdminId, text)


@bot.message_handler(['show_cur_orders'])
def show_cur_orders(message):
    if (message.chat.id != AdminId):
        bot.send_message(message.chat.id, 'У вас недостаточно прав. Забудьте об этой команде:)')
        standart(message)
        return
    for person in orders:
        k = -1
        for order in orders[person]:
            if(order[3]!=4):
                k += 1
                text = 'Номер заказа: №' + str(order[0]) + '\n'
                text += 'ID клиента: ' + str(order[2]) + '\n'
                text += 'Handle: ' + str(list_of_names[order[2]]) + '\n'
                if (order[3] == 0):
                    text += 'Статус заказа: Ожидает подтверждения.\n'
                elif order[3] == 1:
                    text += 'Статус заказа: Подтвержден. Ожидает доставки.\n'
                elif order[3] == 2:
                    text += 'Статус заказа: Доставлен. Ожидает получения.\n'
                elif order[3] == 3:
                    text += 'Статус заказа: Заказ получен. Завершён.\n'
                text += '\n'
                a = 0
                su = 0
                for item in order[1]:
                    if (order[1][item][0] != 0):
                        text += 'Наименование товара: ' + str(order[1][item][1][1]) + '\n'
                        text += 'Артикул товара: ' + str(order[1][item][1][4]) + '\n'
                        text += 'Цена товара: ' + str(order[1][item][1][2]) + ' руб.\n'
                        text += 'Количество: ' + str(int(float(order[1][item][0]))) + '\n'
                        text += 'Стоимость: ' + str(
                            round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)) + ' руб.\n\n'
                        su += round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)
                text += 'Общая сумма: ' + str(round(float(su), 2)) + ' руб.\n'
                if (order[3] != 3):
                    now = telebot.types.InlineKeyboardMarkup()
                    if (order[3] == 0):
                        now.add(telebot.types.InlineKeyboardButton(text='Подтвердить заказ',
                                                                   callback_data='Кек0 ' + str(
                                                                       person) + ' ' + str(k) + ' ' + str(order[0])))
                    elif order[3] == 1:
                        now.add(telebot.types.InlineKeyboardButton(text='Отметить заказ, как доставленный',
                                                                   callback_data='Кек1 ' + str(
                                                                       person) + ' ' + str(k) + ' ' + str(order[0])))
                    elif order[3] == 2:
                        now.add(telebot.types.InlineKeyboardButton(text='Отметить заказ, как полученный(завершенный)',
                                                                   callback_data='Кек2 ' + str(
                                                                       person) + ' ' + str(k) + ' ' + str(order[0])))
                    now.add(telebot.types.InlineKeyboardButton(text='Отменить заказ',
                                                               callback_data='Кек3 ' + str(person) + ' ' + str(
                                                                   k) + ' ' + str(order[0])))
                    bot.send_message(AdminId, text, reply_markup=now)


@bot.callback_query_handler(func=lambda c: 'Кек0' in c.data)
def inline4(c):
    id = int(c.data.split()[1])
    p = int(c.data.split()[2])
    num = int(c.data.split()[3])
    orders[id][p][3] = 1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor=conn.cursor()
    cursor.execute('delete from orders where Number = :num', {'num':orders[id][p][0]})
    cursor.execute('insert into orders values (:num, :id, 1)', {'num':orders[id][p][0], 'id':orders[id][p][2]})
    conn.commit()
    conn.close()
    delete_markup(id)
    bot.send_message(id, 'Ваша оплата по заказу №' + str(
        num) + ' была подтверждена. Ожидайте статуса "Доставлен". По вопросам сроков доставки свяжитесь с тем, кто дал вам Invite-код')
    c.message.chat.id = id
    standart(c.message)
    bot.send_message(AdminId, 'Заказ №' + str(num) + ' был успешно подтвержден.')


@bot.callback_query_handler(func=lambda c: 'Кек1' in c.data)
def inline5(c):
    id = int(c.data.split()[1])
    p = int(c.data.split()[2])
    num = int(c.data.split()[3])
    orders[id][p][3] = 2
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor=conn.cursor()
    cursor.execute('delete from orders where Number = :num', {'num':orders[id][p][0]})
    cursor.execute('insert into orders values (:num, :id, 2)', {'num':orders[id][p][0], 'id':orders[id][p][2]})
    conn.commit()
    conn.close()
    delete_markup(id)
    bot.send_message(id, 'Ваш заказ №' + str(
        num) + ' успешно доставлен. По вопросам получения заказа свяжитесь с тем, кто дал вам Invite-код')
    c.message.chat.id = id
    standart(c.message)
    bot.send_message(AdminId, 'Заказ №' + str(num) + ' был успешно доставлен.')


@bot.callback_query_handler(func=lambda c: 'Кек2' in c.data)
def inline6(c):
    id = int(c.data.split()[1])
    p = int(c.data.split()[2])
    num = int(c.data.split()[3])
    orders[id][p][3] = 3
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor=conn.cursor()
    cursor.execute('delete from orders where Number = :num', {'num':orders[id][p][0]})
    cursor.execute('insert into orders values (:num, :id, 3)', {'num':orders[id][p][0],  'id':orders[id][p][2]})
    conn.commit()
    conn.close()
    delete_markup(id)
    bot.send_message(id, 'Ваш заказ №' + str(num) + ' был получен. Спасибо за сотрудничество:)')
    c.message.chat.id = id
    standart(c.message)
    bot.send_message(AdminId, 'Заказ №' + str(num) + ' был успешно получен.')


@bot.callback_query_handler(func=lambda c: 'Кек3' in c.data)
def inline7(c):
    id = int(c.data.split()[1])
    p = int(c.data.split()[2])
    num = int(c.data.split()[3])
    orders[id][p][3] = 4
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor=conn.cursor()
    cursor.execute('delete from orders where Number = :num', {'num':orders[id][p][0]})
    cursor.execute('insert into orders values (:num, :id, 4)', {'num':orders[id][p][0], 'id':orders[id][p][2]})
    conn.commit()
    conn.close()
    delete_markup(id)
    bot.send_message(id, 'Ваш заказ №' + str(
        num) + ' был отменен. По всем вопросам свяжитесь с тем, кто дал вам Invite-код.')
    c.message.chat.id = id
    standart(c.message)
    bot.send_message(AdminId, 'Заказ №' + str(num) + ' был успешно отменен.')


@bot.callback_query_handler(func=lambda c: c.data == 'Активные заказы')
def open_orders(c):
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    update_name(c.message)
    if (orders[c.message.chat.id] == []):
        bot.send_message(c.message.chat.id, 'У вас нет активных заказов.')
        standart(c.message)
        return
    qw = 0
    for order in orders[c.message.chat.id]:
        if (order[3] < 3):
            qw += 1
            text = 'Номер заказа: №' + str(order[0]) + '\n'
            text += 'ID клиента: ' + str(order[2]) + '\n'
            text += 'Handle: ' + str(list_of_names[order[2]]) + '\n'
            if (order[3] == 0):
                text += 'Статус заказа: Ожидает подтверждения.\n'
            elif order[3] == 1:
                text += 'Статус заказа: Подтвержден. Ожидает доставки.\n'
            elif order[3] == 2:
                text += 'Статус заказа: Доставлен. Ожидает получения.\n'
            elif order[3] == 3:
                text += 'Статус заказа: Заказ получен. Завершён.\n'
            text += '\n'
            su = 0
            for item in order[1]:
                if (order[1][item][0] != 0):
                    text += 'Наименование товара: ' + str(order[1][item][1][1]) + '\n'
                    text += 'Артикул товара: ' + str(order[1][item][1][4]) + '\n'
                    text += 'Цена товара: ' + str(order[1][item][1][2]) + ' руб.\n'
                    text += 'Количество: ' + str(int(float(order[1][item][0]))) + '\n'
                    text += 'Стоимость: ' + str(
                        round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)) + ' руб.\n\n'
                    su += round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)
            text += 'Общая сумма: ' + str(round(float(su), 2)) + ' руб.\n'
            bot.send_message(c.message.chat.id, text)
    if (qw == 0):
        bot.send_message(c.message.chat.id, 'У вас нет активных заказов.')
    standart(c.message)


@bot.callback_query_handler(func=lambda c: c.data == 'Завершенные заказы')
def done_orders(c):
    delete_markup(c.message.chat.id)
    last_message[c.message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': c.message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': c.message.chat.id, 'MessageID': last_message[c.message.chat.id]})
    conn.commit()
    conn.close()
    update_name(c.message)
    if (orders[c.message.chat.id] == []):
        bot.send_message(c.message.chat.id, 'У вас нет активных заказов.')
        standart(c.message)
        return
    a = 0
    for order in orders[c.message.chat.id]:
        if (order[3] == 3):
            a += 1
            text = 'Номер заказа: №' + str(order[0]) + '\n'
            text += 'ID клиента: ' + str(order[2]) + '\n'
            text += 'Handle: ' + str(list_of_names[order[2]]) + '\n'
            if (order[3] == 0):
                text += 'Статус заказа: Ожидает подтверждения.\n'
            elif order[3] == 1:
                text += 'Статус заказа: Подтвержден. Ожидает доставки.\n'
            elif order[3] == 2:
                text += 'Статус заказа: Доставлен. Ожидает получения.\n'
            elif order[3] == 3:
                text += 'Статус заказа: Заказ получен. Завершён.\n'
            text += '\n'
            su = 0
            for item in order[1]:
                if (order[1][item][0] != 0):
                    text += 'Наименование товара: ' + str(order[1][item][1][1]) + '\n'
                    text += 'Артикул товара: ' + str(order[1][item][1][4]) + '\n'
                    text += 'Цена товара: ' + str(order[1][item][1][2]) + ' руб.\n'
                    text += 'Количество: ' + str(int(float(order[1][item][0]))) + '\n'
                    text += 'Стоимость: ' + str(
                        round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)) + ' руб.\n\n'
                    su += round(float(order[1][item][0]) * float(order[1][item][1][2]), 2)
            text += 'Общая сумма: ' + str(round(float(su), 2)) + ' руб.\n'
            bot.send_message(c.message.chat.id, text)
    if (a == 0):
        bot.send_message(c.message.chat.id, 'У вас нет завершенных заказов.')
    standart(c.message)


@bot.message_handler()
def default_handler(a):
    message = copy(a)
    if (message.chat.id not in list_of_clients):
        start(message)
        return
    update_name(message)
    if (message.chat.id not in last_message):
        last_message[message.chat.id] = -1
        conn = sqlite3.connect('Chinook_Sqlite.sqlite')
        cursor = conn.cursor()
        cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
        cursor.execute('insert into last_message values (:ID, :MessageID)',
                       {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
        conn.commit()
        conn.close()
    delete_markup(message.chat.id)
    last_message[message.chat.id] = -1
    conn = sqlite3.connect('Chinook_Sqlite.sqlite')
    cursor = conn.cursor()
    cursor.execute('delete from last_message where ID = :num', {'num': message.chat.id})
    cursor.execute('insert into last_message values (:ID, :MessageID)',
                   {'ID': message.chat.id, 'MessageID': last_message[message.chat.id]})
    conn.commit()
    conn.close()

    if (message.text.isnumeric()):
        q = bot.send_message(message.chat.id, 'Ожидайте...')
        get_info(message, q)
    elif 'www.komus.ru/katalog' in message.text:
        q = bot.send_message(message.chat.id, 'Ожидайте...')
        p = len(message.text) - 1
        while (p >= 0 and not message.text[p].isnumeric()):
            p -= 1
        s = ''
        while (p >= 0 and message.text[p].isnumeric()):
            s += message.text[p]
            p -= 1
        message.text = s[::-1]
        get_info(message, q)
    else:
        bot.send_message(message.chat.id, 'Неопознанная команда. Для справки -> /start')
        standart(message)
while True:
    try:
        bot.polling()
    except Exception as error:
        if('Read timed out' not in str(error)):
            bot.send_message(AdminId, str(error))
        time.sleep(10)
