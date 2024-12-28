from telebot.types import InlineKeyboardButton

class Stage:
    help = 'Help'
    start = 'Start'
    add_habit = 'Add Habit'
    view_habit = 'View Habit'
    edit_habit = 'Edit Habit'
    delete_habit = 'Delete Habit'
    setting_habit = 'Set Habit'
    add_habit_description = 'Add Habit Description'

# class MarkupButton:
#     navigation = InlineKeyboardButton("Prev", callback_data="habit_prev"), InlineKeyboardButton("Next", callback_data="habit_next"), row_width=2
