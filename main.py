import asyncio
import os

from models import User, Habit
from database import SessionLocal, init_db
from helper import helper as hp
import constant

from dotenv import load_dotenv
from telebot.async_telebot import AsyncTeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from telebot.util import quick_markup

init_db()
session = SessionLocal()

load_dotenv(dotenv_path='.env')
print(os.getenv("BOT_TOKEN"))
bot = AsyncTeleBot(os.getenv("BOT_TOKEN"))

@bot.message_handler(commands=["start"])
async def start(message: Message):
    if not User.check_user(session, message.chat.id):
        print("User not found")
        user = User(
            first_name=message.chat.first_name,
            last_name=message.chat.last_name,
            id_telegram=message.chat.id
        )
        session.add(user)
        session.commit()
        await bot.send_message(message.chat.id, f"Hallo {message.chat.first_name}. \nIni adalah interaksi pertamamu dengan My Habit Tracker Bot!. \nSilahkan ketik /help untuk melihat perintah yang tersedia.")
    else:
        await bot.send_message(message.chat.id, "Hallo {}. \nSilahkan ketik /help untuk melihat perintah yang tersedia.".format(message.chat.first_name))

@bot.message_handler(commands=["help"])
async def help(message: Message):
    hp.update_stage(session, message.chat.id, constant.Stage.help)
    await bot.send_message(message.chat.id, "Apa yang kamu inginkan ?", reply_markup=quick_markup({
        'Add Habit': {'callback_data': 'habit_add'},
        'View Habit': {'callback_data': 'habit_view'},
        'Edit Habit': {'callback_data': 'habit_edit'},
        'Delete Habit': {'callback_data': 'habit_delete'},
        'Back': {'callback_data': 'whatever'}
    }, row_width=2))

@bot.callback_query_handler(func=lambda call: call.data == 'habit_add')
async def habit_add(call):
    hp.update_stage(session, call.message.chat.id, constant.Stage.add_habit)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    await bot.send_message(call.message.chat.id, "Kamu memilih Add Habit. Ketik nama habit yang ingin kamu tambahkan")

@bot.callback_query_handler(func=lambda call: call.data == 'habit_view')
async def habit_view(call):
    hp.update_stage(session, call.message.chat.id, constant.Stage.view_habit)
    await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    list_habit = Habit.get_habit(session, call.message.chat.id)
    count_habit =  Habit.count_habit(session, call.message.chat.id)

    if list_habit:
        markup = InlineKeyboardMarkup(row_width=1)
        for habit in list_habit[:5]:
            markup.add(InlineKeyboardButton(habit.name, callback_data=f"habit_view_{habit.id}"))
        if count_habit > 5:            
            # markup.add(InlineKeyboardButton("Prev", callback_data="habit_prev"), InlineKeyboardButton("Next", callback_data="habit_next"), row_width=2)
            markup.add(InlineKeyboardButton(
                "Next ➡️", callback_data="habit_nav_5"), row_width=1)
        await bot.send_message(call.message.chat.id, "List Habit:", reply_markup=markup)
    else:
        await bot.send_message(call.message.chat.id, "Tidak ada habit yang ditemukan.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('habit_nav_'))
async def habit_next(call):
    offset = int(call.data.split('_')[2])
    print(offset)
    list_habit = Habit.get_habit(session, call.message.chat.id, offset=offset)
    count_habit =  Habit.count_habit(session, call.message.chat.id)
    if list_habit:
        markup = InlineKeyboardMarkup(row_width=1)
        for habit in list_habit[:5]:
            markup.add(InlineKeyboardButton(habit.name, callback_data=f"habit_view_{habit.id}"))
        if offset == 0:
            markup.add(InlineKeyboardButton(
                "Next ➡️", callback_data=f"habit_nav_{offset+5}"), row_width=1)
        elif count_habit > offset + 5:
            markup.add(InlineKeyboardButton("⬅️ Prev", callback_data=f"habit_nav_{offset-5}"),
                InlineKeyboardButton(
                "Next ➡️", callback_data=f"habit_nav_{offset+5}"), row_width=2)
        else:
            markup.add(InlineKeyboardButton("⬅️ Prev", callback_data=f"habit_nav_{offset-5}"), row_width=1)
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    else:
        await bot.send_message(call.message.chat.id, "Tidak ada habit yang ditemukan.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('habit_view_'))
async def handle_habit_callback(call):
    habit_id = int(call.data.split('_')[2])
    habit = Habit.get_habit(session, call.message.chat.id, habit_id)
    if habit:
        view_markup = InlineKeyboardMarkup(row_width=2)
        view_markup.add(InlineKeyboardButton("Edit", callback_data=f"habit_edit_{habit[0].id}"), InlineKeyboardButton("Delete", callback_data=f"habit_delete_{habit[0].id}"))
        await bot.send_message(call.message.chat.id, f"Habit: {habit[0].name}\nDescription: {habit[0].description}", reply_markup=view_markup)
    else:
        await bot.send_message(call.message.chat.id, "Habit tidak ditemukan.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('habit_delete_'))
async def habit_delete(call):
    habit_id = int(call.data.split('_')[2])
    habit = Habit.get_habit(session, call.message.chat.id, habit_id)
    deleted_habit = Habit.delete_habit(session, call.message.chat.id, habit_id)
    if deleted_habit:
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        await bot.send_message(call.message.chat.id, f"{habit[0].name} berhasil dihapus.")
    else:
        await bot.send_message(call.message.chat.id, "Habit tidak ditemukan.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('habit_description_'))
async def habit_description(call):
    habit_id = int(call.data.split('_')[2])
    habit = Habit.get_habit(session, call.message.chat.id, habit_id)
    if habit[0]:
        hp.update_stage(session, call.message.chat.id, f"{constant.Stage.add_habit_description} {habit[0].id}")
        await bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        await bot.send_message(call.message.chat.id, f"Ketik deskripsi habit {habit[0].name}")
    else:
        await bot.send_message(call.message.chat.id, "Habit tidak ditemukan.")

@bot.message_handler(func=lambda message: True)
async def echo(message:Message):
    user:User = User.check_user(session, message.chat.id)
    if user.stage == constant.Stage.add_habit:
        habit = Habit.create_habit(session, id_telegram_user=user.id_telegram, name=message.text)
        if habit:
            hp.update_stage(session, message.chat.id, constant.Stage.start)
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(InlineKeyboardButton("View Habit", callback_data="habit_view"), InlineKeyboardButton(
                "Add Description", callback_data=f"habit_description_{habit.id}"))
            await bot.send_message(message.chat.id, f"Kamu berhasil menambahkan habit {message.text}", reply_markup=markup)
        else:
            await bot.send_message(message.chat.id, f"Kamu gagal menambahkan habit {message.text}")
    elif user.stage.startswith(constant.Stage.add_habit_description):
        habit_id = user.stage.split(' ')[3]
        habit = Habit.get_habit(session, user.id_telegram, habit_id)
        habit_name = habit[0].name
        # if habit:
        #     habit[0].description = message.text
        #     session.commit()
        #     hp.update_stage(session, message.chat.id, constant.Stage.start)
        #     await bot.send_message(message.chat.id, f"Deskripsi habit {habit[0].name} berhasil diubah.")
        # else:
        #     await bot.send_message(message.chat.id, "Habit tidak ditemukan.")
        habit = Habit.update_habit(session, user.id_telegram, habit_id, habit_name, message.text)
        if habit:
            hp.update_stage(session, message.chat.id, constant.Stage.start)
            await bot.send_message(message.chat.id, f"Deskripsi habit {habit_name} berhasil diubah.")
        else:
            await bot.send_message(message.chat.id, "Habit tidak ditemukan.")

asyncio.run(bot.polling())