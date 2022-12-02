import telebot
import mysql.connector
import re


class DataBase:
    __cls = None

    def __new__(cls, *args, **kwargs):
        if cls.__cls is None:
            cls.__cls = super().__new__(cls)
        return cls.__cls

    def __init__(self, host='s', user='s', password='s', database='s'):
        self.mydb = mysql.connector.connect(host=host,
                                            user=user,
                                            password=password,
                                            database=database)
        self.database = database
        self.cursor = self.mydb.cursor()
        self.cursor.execute('show tables')
        self.tables = tuple(i for i in map(lambda x: x[0], self.cursor.fetchall()))

    def phone_searcher(self, phone_number):
        for table in self.tables:
            self.cursor.execute(f"show columns from {self.database}.{table}")
            names = tuple(map(lambda x: x[0], self.cursor.fetchall()))
            if 'phone_number' in names:
                self.cursor.execute(f"select * from {table} where phone_number='{phone_number}'")
                yield from map(lambda x: tuple(zip(names, x)), self.cursor.fetchall())

    def name_searcher(self, fio):
        for table in self.tables:
            self.cursor.execute(f"show columns from {self.database}.{table}")
            names = tuple(map(lambda x: x[0], self.cursor.fetchall()))
            if 'fio' in names:
                self.cursor.execute(f"select * from {table} where fio='{fio}'")
                yield from map(lambda x: tuple(zip(names, x)), self.cursor.fetchall())

    def email_searcher(self, email):
        for table in self.tables:
            self.cursor.execute(f"show columns from {self.database}.{table}")
            names = tuple(map(lambda x: x[0], self.cursor.fetchall()))
            if 'email' in names:
                self.cursor.execute(f"select * from {table} where email='{email}'")
                yield from map(lambda x: tuple(zip(names, x)), self.cursor.fetchall())


bot = telebot.TeleBot('Token')
ex = DataBase()


@bot.message_handler(commands=['start'])
def start(message):
    mess = f'Привет, {message.from_user.username}'
    bot.send_message(message.chat.id, mess)


@bot.message_handler()
def get_all(message):
    if message.chat.id == 'int_my_id':
        if re.fullmatch(r'\d{11}', message.text):
            res = (i for i in ex.phone_searcher(message.text))
        elif re.findall(r'@', message.text):
            res = (i for i in ex.email_searcher(message.text))
        else:
            res = (i for i in ex.name_searcher(message.text))
        for j in res:
            fin = '\n'.join(map(lambda x: ': '.join(map(str, x)), j))
            bot.send_message(message.chat.id, fin)
        bot.send_message(message.chat.id, 'Finito !')
    else:
        bot.send_message(message.chat.id, 'No access')


while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
