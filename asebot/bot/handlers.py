import logging

from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, ConversationHandler, Filters, MessageHandler

import asebot.bot.keyboards as keyboards
from asebot.constants import USER, STATE

logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    user = update.message.from_user
    if not context.user_data.get(USER.REPEAT_VISITOR):
        update.message.reply_text(f"Hi {user.first_name}. I am Tsehai! 👋")
        update.message.reply_text(f"It is very nice to meet you.")
        context.user_data[USER.REPEAT_VISITOR] = True
    else:
        update.message.reply_text(f"Hello {user.first_name}!")
        update.message.reply_text(f"Nice to see you again.")
    return main_menu(update, context)


def main_menu(update, context):
    update.message.reply_text(
        f"What would you like to do?",
        reply_markup=ReplyKeyboardMarkup([
            ["📚 Go to the library", "🏅 View my medals"]
        ], one_time_keyboard=True, resize_keyboard=True)
    )
    return STATE.STARTED


def library(update, context):

    update.message.reply_text(f"📚 The library 📚")


def medals(update, context):
    update.message.reply_text(
        f"🏅 Your medals\n"
        "\n"
        "🥇 Gold - 0\n"
        "🥈 Silver - 0\n"
        "🥉 Bronze - 0\n")


def return_to_main_menu(update, context):
    update.message.reply_text("Sorry, I don't know how to help you with that.")
    return main_menu(update, context)


def prompt_to_start_over(update, context):
    update.message.reply_text(
        "Sorry, I don't know how to help with that yet.\n"
        "You can start over by pressing /start.",
        reply_markup=ReplyKeyboardMarkup([
            ["/start"]
        ], one_time_keyboard=True, resize_keyboard=True))


fallback = MessageHandler(Filters.regex(r'.*'), prompt_to_start_over)

root_conversation = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        STATE.STARTED: [
            MessageHandler(Filters.regex(r'📚'), library),
            MessageHandler(Filters.regex(r'medals'), medals),
        ]
    },
    fallbacks=[MessageHandler(Filters.regex(r'.*'), return_to_main_menu)]
)
