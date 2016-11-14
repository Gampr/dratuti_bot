# -*- coding: utf-8 -*-
import config
import telebot
import random

bot = telebot.TeleBot(config.token)

SEX = ["М", "Ж"]

START_MESSAGE = """Дратути! Я помогу тебе найти свою половинку;))
/help - помощь"""

HELP_MESSAGE = """
    help
"""

WANTED = {"М": "Сейчас вы будете искать парней, чтобы пообщаться",
          "Ж": "Сейчас вы будете искать девушек, чтобы пообщаться",
          "Неважно": "Сейчас вам не вaжно, кого искать"}

sex = {}
state = {}
who_to_find = {}
binded = {}

def change_state(f):
    def stated_f(chat_id):
        state[chat_id] = f.__name__
        return f(chat_id)
    return stated_f

#
# init
#
@change_state
def choose_sex(chat_id):
    sex_markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    sex_markup.row('М', 'Ж')
    bot.send_message(chat_id, "Выбери раз и навсегда, кто ты:", reply_markup=sex_markup)

@bot.message_handler(func=lambda message: not sex.get(message.chat.id), commands=["start"])
def start(message):
    bot.send_message(message.chat.id, START_MESSAGE)
    who_to_find[message.chat.id] = "Неважно"
    choose_sex(message.chat.id)

@bot.message_handler(func=lambda message: True, commands=["start", "help"])
def help(message):
    bot.send_message(message.chat.id, HELP_MESSAGE)

@bot.message_handler(func=lambda message: state.get(message.chat.id) == "choose_sex" and message.text in SEX, content_types=["text"])
def check_sex(message):
    sex[message.chat.id] = message.text
    # debug
    print(str(message.chat.id) + ", " + message.text)
    choose_action(message.chat.id)
# init

@change_state
def choose_action(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Искать', 'Кого искать')
    #markup.row('Настройки')
    bot.send_message(chat_id, "<i>" + WANTED[who_to_find[chat_id]] + "</i>", reply_markup=markup, parse_mode="HTML")

@change_state
def choose_who_to_find(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('М', 'Ж')
    markup.row('Неважно')
    bot.send_message(chat_id, "Кого будем искать?", reply_markup=markup)

def can_be_with(id1, id2):
    if not who_to_find[id1] in SEX:
        return True
    return sex[id2] == who_to_find[id1]

@change_state
def find(chat_id):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('/disconnect')
    bot.send_message(chat_id, "<b>... ищем ...</b>", reply_markup=markup, parse_mode="HTML")
    founded = [id for id in state.keys() if state[id] == "find" and can_be_with(chat_id, id) and can_be_with(id, chat_id) and id != chat_id]
    if founded:
        bind_id = random.choice(founded)
        binded[chat_id] = bind_id
        binded[bind_id] = chat_id
        state[chat_id] = "chatting"
        state[bind_id] = "chatting"
        bot.send_message(chat_id, "<b>... собеседник найден ...</b>", reply_markup=markup, parse_mode="HTML")
        bot.send_message(bind_id, "<b>... собеседник найден ...</b>", reply_markup=markup, parse_mode="HTML")

@bot.message_handler(func=lambda message: state.get(message.chat.id) == "choose_action", content_types=["text"])
def check_action(message):
    if message.text == "Искать":
        find(message.chat.id)

    if message.text == "Кого искать":
        choose_who_to_find(message.chat.id)

@bot.message_handler(func=lambda message: state.get(message.chat.id) == "choose_who_to_find", content_types=["text"])
def check_who_to_find(message):
    if message.text in WANTED.keys():
        who_to_find[message.chat.id] = message.text
        choose_action(message.chat.id)

@bot.message_handler(commands=["disconnect"])
def disconnect(message):
    if state.get(message.chat.id) == "chatting":
        bot.send_message(message.chat.id, "<b>... свзяь разорвана ...</b>", parse_mode="HTML")
        bot.send_message(binded[message.chat.id], "<b>... связь разорвана ...</b>", parse_mode="HTML")
        choose_action(message.chat.id)
        choose_action(binded[message.chat.id])
    if state.get(message.chat.id) == "find":
        bot.send_message(message.chat.id, "<b>... перестали искать ...</b>", parse_mode="HTML")
        choose_action(message.chat.id)

@bot.message_handler(func=lambda message: state.get(message.chat.id) == "chatting", content_types=["text"])
def chat(message):
    bot.send_message(binded[message.chat.id], "<b>Собеседник: </b>" + message.text, parse_mode = "HTML")

if __name__ == '__main__':
    bot.polling(none_stop=True)
