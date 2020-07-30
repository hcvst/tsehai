from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER

class MainMenu:

    def main_menu(self, update, context):
        update.message.reply_text(
            f"What would you like to do?",
            reply_markup=ReplyKeyboardMarkup([
                ["🏅 See my medals"],
                [ "🏛️ I want to read", "📔 I want English lessons"]
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.STARTED

    def return_to_main_menu(self, update, context):
        update.message.reply_text("Sorry, I don't know how to help you with that.")
        return self.main_menu(update, context)