from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.components.switch import Switch


class English:
    def english_lessons(self, update,context):
        if not context.user_data.get(USER.GRADE):
            update.message.reply_text(
                f"Great!, What grade are you in?",
                reply_markup=ReplyKeyboardMarkup([
                    ["1️⃣","2️⃣"],
                    ["3️⃣", "4️⃣"],
                    ["5️⃣","6️⃣"],
                    [ "7️⃣", "8️⃣"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.GRADE
        else:
            update.message.reply_text("User Already selected a grade")
            return STATE.END

    def assign_grade(self, update, context):
        switcher = Switch()
        grade = switcher.grade(update.message.text)
        
        if grade >= 1 and grade <= 8:
            context.user_data[USER.GRADE] = grade
            print(context.user_data)
            return self.english_lessons(update, context)