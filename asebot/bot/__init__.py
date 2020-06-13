from telegram.ext import PicklePersistence, Updater

import asebot.bot.handlers
import asebot.config


def run():
    updater = Updater(
        asebot.config.TELEGRAM_TOKEN,
        persistence=PicklePersistence(asebot.config.PERSISTANCE_FILE), use_context=True)

    updater.dispatcher.add_handler(asebot.bot.handlers.root_conversation)
    updater.dispatcher.add_handler(asebot.bot.handlers.fallback)
    updater.dispatcher.add_error_handler(asebot.bot.handlers.error)
    updater.start_polling()
    updater.idle()
