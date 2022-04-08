import json, telebot
from telebot import types;
#init storage
storage = {}
try:
    with open("database.json", "r") as dbfile:
        all_lines = dbfile.readlines()
        joined_lines = "".join(all_lines)
        storage = json.loads(joined_lines)
except:
    pass

bot = telebot.TeleBot('')

@bot.message_handler(content_types=['text'])
def start(message):
    if (message.text == '/start') or (message.text == '/reg') or (message.text == '/themes'):
        if message.text == '/start':
            bot.send_message(message.from_user.id, 'Привет! \n Это бот, написанный специально для НФибд-01-21, чтобы не возникло одинаковых тем для рефератов по истории. \n \n У него есть 3 команды:\n/start (чтобы получить это сообщение снова) \n/reg (записать свои данные) \n/themes (проверить уже занятые темы) \n Заполни данные коректно. Если захотите изменить тему, то используйте команду /reg повторно')
        if message.text =='/reg':
            user_id=str(message.from_user.id)
            storage[user_id]={"name": None, "surname": None, "stbil": 0, "tema": None}
            bot.send_message(message.from_user.id, "Каково твоё имя, путник?")
            bot.register_next_step_handler(message, get_name); #следующий шаг – функция get_name
        if message.text=="/themes":
            user_id=str(message.from_user.id)
            all_topics =  []
            for key, value in storage.items():
               all_topics.append(value["tema"])
            stra = '\n'.join(topic for topic in all_topics if not (topic is None))
            bot.send_message(message.from_user.id, 'Вот темы, которые заняты другими странниками:' + '\n\n' + stra)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю используй команду одну из 3х команд:\n /start \n /reg \n /themes')
def get_name(message): #получаем фамилию
    user_id=str(message.from_user.id)
    storage[user_id]["name"]=message.text
    bot.send_message(message.from_user.id, 'Интересное имя. Есть ли у тебя фамилия?')
    bot.register_next_step_handler(message, get_surname)

def get_surname(message):
    user_id=str(message.from_user.id)
    storage[user_id]["surname"]=message.text
    bot.send_message(message.from_user.id, 'О чем собираешься рассказывать?')
    bot.register_next_step_handler(message, get_tema)

def get_tema(message):
    user_id=str(message.from_user.id)
    storage[user_id]["tema"]=message.text
    bot.send_message(message.from_user.id, 'Назови номер твоего студбилета, '+storage[user_id]["name"])
    bot.register_next_step_handler(message, get_stbil)

def get_stbil(message):
    user_id=str(message.from_user.id)
    if storage[user_id]["stbil"] == 0: #проверяем что возраст изменился
        try:
             storage[user_id]["stbil"]=int(message.text) #проверяем, что студак введен корректно
        except Exception:
             bot.send_message(message.from_user.id, 'Цифрами, пиши. Умник нашелся')
             bot.register_next_step_handler(message, get_stbil)
             return
    keyboard = types.InlineKeyboardMarkup(); #наша клавиатура
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes_' + str(user_id))
    keyboard.add(key_yes); #добавляем кнопку в клавиатуру
    key_no= types.InlineKeyboardButton(text='Нет', callback_data='no_' + str(user_id))
    keyboard.add(key_no)
    question = 'Тебя зовут '+storage[user_id]["name"]+' '+storage[user_id]["surname"]+str(storage[user_id]["stbil"])+', и твоя тема для реферата по истории: '+storage[user_id]["tema"]+'?';
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)

def write_json():
    with open('database.json', 'w') as file:
        json_line =  json.dumps(storage, indent=4, ensure_ascii=False)
        file.write(json_line)
        
@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    answer = call.data.split('_')[0]
    user_id = call.data.split('_')[1]
    if answer == "yes": #call.data это callback_data, которую мы указали при объявлении кнопки
        print (storage)
        write_json()
        bot.send_message(call.message.chat.id, 'Хорошо, так и запишем \nЕсли хочешь проверить внеслась ли тема в список, то используй /themes \n:)')
    elif answer == "no":
        storage[user_id]={"name": None, "surname": None, "stbil": 0, "tema": None}
        bot.send_message(call.message.chat.id, "Попробуем еще раз")
        bot.send_message(call.message.chat.id, "Напиши своё имя")
        bot.register_next_step_handler(call.message, get_name)
        
'''def output(message):
    if message.text=="/themes":
        user.id=message.from_user.id
        bot.send_message(message.from_user.id, 'Вот темы которые заняты:')
        all_topics =  []
        for key, value in storage.items():
           all_topics.append(value["tema"]) 
        bot.send_message(message.from_user.id, all_topics)'''

bot.polling(none_stop=True, interval=0)
