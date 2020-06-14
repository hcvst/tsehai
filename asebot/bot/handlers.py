import logging
import random

from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler)

import asebot.api
import asebot.bot.keyboards as keyboards
import asebot.config
from asebot.constants import STATE, USER

logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    user = update.message.from_user
    if not context.user_data.get(USER.REPEAT_VISITOR):
        update.message.reply_text(f"Hi {user.first_name}. I am Tsehai! 👋")
        update.message.reply_photo(
            photo=asebot.config.TSEHAI_IMAGE_URL, caption="Here is a photo of me. 📷")
        update.message.reply_text(f"It is very nice to meet you.")
        context.user_data[USER.REPEAT_VISITOR] = True
    else:
        update.message.reply_text(f"Hello! 👋")
        update.message.reply_text(f"Nice to see you again, {user.first_name}.")
    return main_menu(update, context)


def main_menu(update, context):
    update.message.reply_text(
        f"What would you like to do?",
        reply_markup=ReplyKeyboardMarkup([
            ["🏛️ Go to the library", "🏅 See my medals"]
        ], one_time_keyboard=False, resize_keyboard=True)
    )
    return STATE.STARTED


def library(update, context):
    update.message.reply_text(f"🏛️ The Library")

    context.user_data["books"] = asebot.api.load_books()
    context.user_data["book_idx"] = 0

    if len(context.user_data["books"]) == 0:
        update.message.reply_text(
            "There are no books available at the moment. "
            "Please try again later."
        )
        return STATE.END
    else:
        update.message.reply_text(
            "Let's find a book for you."
        )
        return view_book(update, context)


def view_book(update, context):
    books = context.user_data["books"]
    book_idx = context.user_data["book_idx"]
    update.message.reply_photo(
        photo=asebot.config.API_SERVER+books[book_idx]["cover"]["url"],
        caption=books[book_idx]["title"],
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([
            ['📖 Read this book'], 
            ['➡️ Look for another book']
        ], one_time_keyboard=False, resize_keyboard=True)
    )
    return STATE.BROWSE_BOOKS


def next_book(update, context):
    next_idx = context.user_data["book_idx"] + 1
    if next_idx == len(context.user_data["books"]):
        next_idx = 0
    context.user_data["book_idx"] = next_idx
    return view_book(update, context)


def read_book(update, context):
    books = context.user_data["books"]
    book_idx = context.user_data["book_idx"]
    context.user_data["book"] = asebot.api.load_book(books[book_idx]["id"])
    context.user_data["page_idx"] = 0
    return view_page(update, context)


def view_page(update, context):
    pages = context.user_data["book"]["pages"]
    page_idx = context.user_data["page_idx"]
    page = pages[page_idx]

    keyboard = ReplyKeyboardMarkup(
        [['🏛️ Return to the library'], ['➡️ Turn to the next page']],
        one_time_keyboard=False,
        resize_keyboard=True
    )

    if len(page["images"]) > 0:
        update.message.reply_photo(
            photo=asebot.config.API_SERVER+page["images"][0]["url"],
            caption=page["text"],
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    else:
        update.message.reply_markdown(
            page["text"],
            reply_markup=keyboard
        )
    return STATE.READING


def next_page(update, context):
    next_idx = context.user_data["page_idx"] + 1
    if next_idx == len(context.user_data["book"]["pages"]):
        return book_finished(update, context)
    else:
        context.user_data["page_idx"] = next_idx
        return view_page(update, context)


def book_finished(update, context):
    user = update.message.from_user
    update.message.reply_text(
        f"🎉 Well done, {user.first_name}. You've finished the book."
    )
    return start_quizz(update, context)


def start_quizz(update, context):
    num_questions = len(context.user_data["book"]["quizz"]["questions"])
    if num_questions > 0:
        context.user_data["quizz_idx"] = 0
        context.user_data["quizz_mistakes"] = 0
        update.message.reply_text(
            f"Let's have fun with a quizz. "
            f"Answer {num_questions} questions to test your understanding. 🤔"
        )
        return view_quizz_question(update, context)
    else:
        return main_menu(update, context)


def view_quizz_question(update, context):
    quizz_idx = context.user_data["quizz_idx"]
    qna = context.user_data["book"]["quizz"]["questions"][quizz_idx]
    question = qna["question"]
    answers = [qna["answer"]] + [d["wrong_answer"] for d in qna["distractors"]]
    random.shuffle(answers)
    text = f"**Question {quizz_idx+1}**: {question}"
    keyboard = ReplyKeyboardMarkup(
        [[a] for a in answers],
        one_time_keyboard=False,
        resize_keyboard=True)
    if qna["image"]:
        update.message.reply_photo(
            photo=asebot.config.API_SERVER+qna["image"]["url"],
            caption=text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    else:
        update.message.reply_markdown(text, reply_markup=keyboard)
    return STATE.QUIZZ


def check_quizz_answer(update, context):
    provided_answer = update.message.text
    quizz_idx = context.user_data["quizz_idx"]
    qna = context.user_data["book"]["quizz"]["questions"][quizz_idx]
    answer = qna["answer"]
    if provided_answer == answer:
        update.message.reply_text("✔️ That is correct.")
    else:
        context.user_data["quizz_mistakes"] += 1
        update.message.reply_text(f"❌ The correct answer is '{answer}'.")
    return next_quizz_question(update, context)


def next_quizz_question(update, context):
    next_idx = context.user_data["quizz_idx"] + 1
    if next_idx == len(context.user_data["book"]["quizz"]["questions"]):
        return quizz_finished(update, context)
    else:
        context.user_data["quizz_idx"] = next_idx
        return view_quizz_question(update, context)


def quizz_finished(update, context):
    user = update.message.from_user
    quizz_mistakes = context.user_data["quizz_mistakes"]
    if quizz_mistakes == 0:
        context.user_data.setdefault(
            "medals", dict(gold=0, silver=0, bronze=0)
        )["gold"] += 1
        update.message.reply_text(
            f"🎉 Very good, {user.first_name}. "
            "You answered all questions correctly.\n"
            "You've won a medal 🏅. "
            "Congratulations 🎉.")
    elif quizz_mistakes == 1:
        update.message.reply_text(
            f"🎉 Well done, {user.first_name}. "
            "You made only one mistake.")
    else:
        update.message.reply_text(
            f"You made a few mistakes, {user.first_name}. "
            "That's ok. You are still learning.")
    return main_menu(update, context)


def medals(update, context):
    medals = context.user_data.setdefault(
        "medals", dict(gold=0, silver=0, bronze=0))
    update.message.reply_text(
        f"🏅 Your Medals\n"
        f"\n"
        f"🥇 Gold - {medals['gold']}\n"
        f"🥈 Silver - {medals['silver']}\n"
        f"🥉 Bronze - {medals['bronze']}")
    return main_menu(update, context)


def return_to_main_menu(update, context):
    update.message.reply_text("Sorry, I don't know how to help you with that.")
    return main_menu(update, context)


def prompt_to_start_over(update, context):
    update.message.reply_text(
        "Sorry, I cannot help you with that just now.\n"
        "You can start over by pressing /start.",
        reply_markup=ReplyKeyboardMarkup([
            ["/start ↩️"]
        ], one_time_keyboard=False, resize_keyboard=True))


fallback = MessageHandler(Filters.all, prompt_to_start_over)

root_conversation = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        STATE.STARTED: [
            MessageHandler(Filters.regex(r'🏛️'), library),
            MessageHandler(Filters.regex(r'🏅'), medals),
        ],
        STATE.BROWSE_BOOKS: [
            MessageHandler(Filters.regex(r'📖'), read_book),
            MessageHandler(Filters.regex(r'➡️'), next_book)
        ],
        STATE.READING: [
            MessageHandler(Filters.regex(r'🏛️'), library),
            MessageHandler(Filters.regex(r'➡️'), next_page)
        ],
        STATE.QUIZZ: [
            MessageHandler(Filters.all, check_quizz_answer)
        ]

    },
    fallbacks=[MessageHandler(Filters.all, return_to_main_menu)]


)
