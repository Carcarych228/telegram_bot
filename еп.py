import telebot
from telebot import types
import json
import os
# from main import user_data

from datetime import datetime

def get_week_type():
    week_number = datetime.now().isocalendar().week
    return "четная" if week_number % 2 != 0 else "нечетная"



bot = telebot.TeleBot(os.environ.get"BOT_TOKEN")

ADMINS = [1917691975, 1385003597]

with open("shedule.json", "r", encoding="utf-8") as f:
    data = json.load(f)


user_state = {}
try:
    with open("homework.json", "r", encoding="utf-8") as f:
        homework = json.load(f)    # ← homework существует
except:
    homework = {}                 # ← домашка пустая, но СУЩЕСТВУЕТ
#---------------------------------------------------------------------------------------------------------------------
@bot.message_handler(commands=["myid"])
def get_my_id(message):
    bot.send_message(message.chat.id, f"Твой ID: {message.from_user.id}")

#---------------------------------------------------------------------------------------------------------------------


@bot.message_handler(commands=['start'])
def choose_group(message):
    user_state[message.chat.id] = {}

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("ПИнж-1-25")
    keyboard.add(btn)
    bot.send_message(message.chat.id, "Выбери свою группу: ", reply_markup=keyboard)



@bot.message_handler(func=lambda m: m.text == "ПИнж-1-25")
def choose_subgroup(message):
    user_state[message.chat.id]["group"] = "ПИнж-1-25"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("1")
    btn2 = types.KeyboardButton("2")
    keyboard.add(btn, btn2)
    bot.send_message(message.chat.id, "Выбери подгруппу: ", reply_markup=keyboard)
#-----------------------------------------------------------------------------------
@bot.message_handler(func=lambda m: m.text in ['1', '2'])
def choose_week_type(message):
    user_state[message.chat.id]["subgroup"] = message.text

    # ✅ автоматически определяем чётность
    week_type = get_week_type()
    user_state[message.chat.id]["week_type"] = week_type

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("Пн", "Вт", "Ср", "Чт", "Пт")

    bot.send_message(
        message.chat.id,
        f"📅 Сейчас {week_type} неделя\nВыбери день недели:",
        reply_markup=keyboard
    )

#------------------------------------------------------------------------------------
# @bot.message_handler(func=lambda m: m.text in ['нечетная', 'четная'])
# def choose_day(message):
#     user_state[message.chat.id]["week_type"] = message.text
#
#     keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
#     keyboard.add("Пн", "Вт", "Ср", "Чт", "Пт")
#     bot.send_message(message.chat.id, "Выбери день недели: ", reply_markup=keyboard)


@bot.message_handler(func=lambda m: m.text in ["Пн", "Вт", "Ср", "Чт", "Пт"])
def choose_day(message):

    user_state[message.chat.id]["day"] = message.text
    lessons = data[user_state[message.chat.id]["group"]][user_state[message.chat.id]["subgroup"]][user_state[message.chat.id]["week_type"]][user_state[message.chat.id]["day"]]

    emoji_map = {
        "физра": "🏃‍♂️",
        "русский": "📘",
        "математика": "📐",
        "информатика": "💻",
        "физика": "⚡",
        "экология": "🌿",
        "кырг. яз": "📚",
        "програм. на языке выс. ур.": "👨‍💻",
        "введение прог. инж.": "🛠",
        "лабораторная": "🧪",
        "лекция": "🎓",
        "практика": "📝"
    }
    text = ''

    for lesson in lessons:
        subj = lesson['предмет']
        emoji = emoji_map.get(subj, "📘")

        text += (
            f"{emoji} **{subj.title()}**\n"
            f"Тип: *{lesson['тип']}*\n"
            f"🏫 Аудитория: `{lesson['аудитория']}`\n"
            "----------------------\n"
        )
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="Добавить дз", callback_data="homework")
    keyboard.add(btn)

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data == "homework")
def choose_homework(call):
    user_id = call.from_user.id

    if user_id not in ADMINS:
        bot.answer_callback_query(call.id, "У вас нет прав")
        return

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton("1", callback_data="hw_sb_1"), types.InlineKeyboardButton("2", callback_data="hw_sb_2"))
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Выберите подгруппу", reply_markup=keyboard)

    # lessons = data[user_state[user_id]["group"]][user_state[user_id]["subgroup"]][user_state[user_id]["week_type"]][user_state[user_id]["day"]]
    # keyboard = types.InlineKeyboardMarkup()
    # for i, lesson in enumerate(lessons):
    #     subject = lesson["предмет"]
    #     keyboard.add(types.InlineKeyboardButton(text = subject, callback_data=f"lesson_{i}"))
    # bot.answer_callback_query(call.id)
    # bot.send_message(call.message.chat.id, "Выбери предмет: ", reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: call.data.startswith("hw_sb_"))
def choose_lesson_after_subgroup(call):
    user_id = call.from_user.id
    subgroup = call.data.split("_")[2]  # 1 или 2

    # сохраняем выбранную подгруппу для ДЗ
    user_state[user_id]["hw_subgroup"] = subgroup

    lessons = data[user_state[user_id]["group"]][subgroup][user_state[user_id]["week_type"]][user_state[user_id]["day"]]

    keyboard = types.InlineKeyboardMarkup()
    for i, lesson in enumerate(lessons):
        subject = lesson["предмет"]
        keyboard.add(types.InlineKeyboardButton(text=subject, callback_data=f"lesson_{i}"))

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Выбери предмет:", reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: call.data.startswith("lesson_"))
def enter_homework(call):
    user_id = call.from_user.id
    lesson_index = int(call.data.split("_")[1])

    # сохраняем выбранный урок
    lessons = data[user_state[user_id]["group"]][user_state[user_id]["hw_subgroup"]][user_state[user_id]["week_type"]][user_state[user_id]["day"]]

    selected_lesson = lessons[lesson_index]['предмет']
    user_state[user_id]["selected_lesson"] = selected_lesson
    user_state[user_id]["selected_subgroup_for_hw"] = user_state[user_id]["hw_subgroup"]

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id,f"Введите ДЗ по предмету: {selected_lesson}")


@bot.message_handler(commands=["hw"])
def hw_menu(message):
    days = ["Пн", "Вт", "Ср", "Чт", "Пт"]

    keyboard = types.InlineKeyboardMarkup()
    for d in days:
        keyboard.add(types.InlineKeyboardButton(text=d,callback_data=f"showday_{d}"))
    bot.send_message(message.chat.id,"📅 Выберите день недели:",reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: call.data.startswith("showday_"))
def show_homework_for_day(call):
    user_id = call.from_user.id
    day = call.data.split("_")[1]

    # 👉 ЗАЩИТА от KeyError
    if user_id not in user_state or \
       "group" not in user_state[user_id] or \
       "subgroup" not in user_state[user_id] or \
       "week_type" not in user_state[user_id]:

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Сначала выбери группу и подгруппу через /start")
        return

    group = user_state[user_id]["group"]
    subgroup = user_state[user_id]["subgroup"]
    week_type = user_state[user_id]["week_type"]

    if (group not in homework or
        subgroup not in homework[group] or
        week_type not in homework[group][subgroup] or
        day not in homework[group][subgroup][week_type]):

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "На этот день ДЗ нет 🙂")
        return

    text = f"📘 ДЗ на {day} ({week_type}, подгруппа {subgroup}):\n\n"

    for subject, hw in homework[group][subgroup][week_type][day].items():
        text += f"• <b>{subject}</b>: {hw}\n"

    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, text, parse_mode="HTML")


@bot.message_handler(func=lambda message: True)
def save_homework(message):
    user_id = message.from_user.id
    if "selected_subgroup_for_hw" not in user_state[user_id]:
        bot.send_message(message.chat.id, "⚠ Сначала выберите подгруппу для ДЗ")
        return

    if user_id not in ADMINS:
        return

    if user_id not in user_state or "selected_lesson" not in user_state[user_id]:
        return

    lesson = user_state[user_id]["selected_lesson"]
    text = message.text

    group = user_state[user_id]["group"]
    subgroup = user_state[user_id]["selected_subgroup_for_hw"]
    week_type = user_state[user_id]["week_type"]
    day = user_state[user_id]["day"]

    homework.setdefault(group, {})
    homework[group].setdefault(subgroup, {})
    homework[group][subgroup].setdefault(week_type, {})
    homework[group][subgroup][week_type].setdefault(day, {})  # ← ВАЖНО

    existed = lesson in homework[group][subgroup][week_type][day]

    # ✅ Проверяем: было ли уже ДЗ по этому предмету
    existed = lesson in homework[group][subgroup][week_type][day]

    # ✅ Сохраняем (старое автоматически затирается)
    homework[group][subgroup][week_type][day][lesson] = text

    with open("homework.json", "w", encoding="utf-8") as f:
        json.dump(homework, f, indent=4, ensure_ascii=False)

    # ✅ Сообщение пользователю
    if existed:
        bot.send_message(message.chat.id, f"♻ ДЗ по {lesson} обновлено!")
    else:
        bot.send_message(message.chat.id, f"✅ ДЗ по {lesson} сохранено!")

    del user_state[user_id]["selected_lesson"]
    del user_state[user_id]["hw_subgroup"]
    del user_state[user_id]["selected_subgroup_for_hw"]


bot.infinity_polling()
