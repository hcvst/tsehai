from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Inline Buttons
# btn_to_the_library = InlineKeyboardButton(text="📚 To the Library", callback_data="123")

# Inline Keyboards
# ilkb_library = InlineKeyboardMarkup([[btn_to_the_library]])
reply_keyboard = [['Age', 'Favourite colour'],
                  ['Number of siblings', 'Something else...'],
                  ['Done']]
# keyboard = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)