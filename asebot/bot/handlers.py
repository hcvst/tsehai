import logging
import random

import requests
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler)

import asebot.api
import asebot.config
import asebot.pointsbrain
from asebot.pointsbrain import points_medals_brain
from asebot.constants import STATE, USER
from asebot.bot.alocate_points import alocate_points
from asebot.bot.leaderboard import leaderboard

logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    user = update.message.from_user
    if not context.user_data.get(USER.REPEAT_VISITOR):
        update.message.reply_text(
            f"👋 Hello, I'm Tsehai, the reading bot. I will help you to become a better reader."
        )
        update.message.reply_text(
            f"Just read the stories and answer the questions as well as you can."
        )
        update.message.reply_text(
            f"I will show you new stories that match your own reading ability, helping you improve. "
            "Are you ready? Let's get started!"
        )
        context.user_data[USER.REPEAT_VISITOR] = True
    else:
        update.message.reply_text(f"Hello! 👋")
        update.message.reply_text(f"Nice to see you again, {user.first_name}.")
    return main_menu(update, context)


def main_menu(update, context):
    # chatId = update.message.chat
    # testBoard = leaderboard(update)

    # for user in testBoard:
    #     if user['chatId'] == f"{chatId.id}":
    #         update.message.reply_text(
    #             f"You  --->  {user['totalPoints']}"
    #         )
    #     else:
    #         update.message.reply_text(
    #             f"{user['username']}  --->  {user['totalPoints']}"
    #         )

    update.message.reply_text(
        f"What would you like to do?",
        reply_markup=ReplyKeyboardMarkup([
            ["🏅 See my medals"],
            [ "🏛️ I want to read", "📔 I want English lessons"]
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

def reading_level(update, context):
    context.user_data["levelSelectionPictures"] = asebot.api.load_level_Selection()

    if not context.user_data.get(USER.READING_LEVEL):
        update.message.reply_text("Wow!")
        update.message.reply_text("I love reading too!")
        update.message.reply_text("Look at the pictures and choose your reading level")
        
        update.message.reply_photo(
            photo=asebot.config.API_SERVER+context.user_data["levelSelectionPictures"][0]['Image'][0]['url'],
            # caption=books[book_idx]["title"],
            parse_mode='Markdown',
            reply_markup=ReplyKeyboardMarkup([
                 ["Level 1️⃣","Level 2️⃣"],
                ["Level 3️⃣", "Level 4️⃣"]
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.READINGLEVEL  
    else:
        update.message.reply_text(f"🏛️ The Library")
        context.user_data["book_idx"] = 0
        # context.user_data[USER.READING_LEVEL] = false
    
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
        # return view_book(update, context)

# Level assignment is not dynamic ==>

def assign_reading_level_1(update, context):
    context.user_data[USER.READING_LEVEL] = 1
    context.user_data["books"] = asebot.api.load_books_on_level(context.user_data[USER.READING_LEVEL])
    update.message.reply_text(f"Level 1 assigned")
    return reading_level(update, context)


def assign_reading_level_2(update, context):
    context.user_data[USER.READING_LEVEL] = 2
    context.user_data["books"] = asebot.api.load_books_on_level(context.user_data[USER.READING_LEVEL])
    update.message.reply_text(f"Level 2 assigned")
    return reading_level(update, context)

def assign_reading_level_3(update, context):
    context.user_data[USER.READING_LEVEL] = 3
    context.user_data["books"] = asebot.api.load_books_on_level(context.user_data[USER.READING_LEVEL])
    update.message.reply_text(f"Level 3 assigned")
    return reading_level(update, context)

def assign_reading_level_4(update, context):
    context.user_data[USER.READING_LEVEL] = 4
    context.user_data["books"] = asebot.api.load_books_on_level(context.user_data[USER.READING_LEVEL])
    update.message.reply_text(f"Level 4 assigned")
    return reading_level(update, context)

# ============>


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
        [
            ['🏛️ Return to the library'],
            ['👂 Listen to this page'],
            ['➡️ Turn to the next page']
        ],
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


def text_to_speech(update, context):
    pages = context.user_data["book"]["pages"]
    page_idx = context.user_data["page_idx"]
    page = pages[page_idx]
    text = page["text"]

    resp = requests.post(
        url=asebot.config.TEXTTOSPEECH_ENDPOINT,
        json=dict(text=text),
        headers=dict(Authorization=asebot.config.TEXTTOSPEECH_AUTH_TOKEN)
    )

    audio_href = resp.json()["href"]
    update.message.reply_voice(audio_href)


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
        f"🎉 Well done, {user.first_name}."
    )
    return start_quizz(update, context)


def start_quizz(update, context):
    book = context.user_data["book"]
    asebot.pointsbrain.validate_quizz_taken(context)
    
    num_questions = len(book["quizz"]["questions"])
    if num_questions > 0:
        context.user_data["quizz_idx"] = 0
        context.user_data["quizz_mistakes"] = 0
        update.message.reply_markdown(
            f"Now, answer {num_questions} questions as well as you can."
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
    medal = points_medals_brain(context)
    medalattained = medal['medal']
    alocate_points(update, medal['percentage'])
    #test.createPoints(chatId.id , user.first_name, medal['percentage'])

    context.user_data.setdefault(
            "medals", dict(gold=0, silver=0, bronze=0,nomedal=0)
        )[f"{medalattained}"] += 1
    if quizz_mistakes == 0:
        update.message.reply_text(
            f"🎉 Very good, {user.first_name}. "
            "You answered all questions correctly.\n"
            "Check Your medal's 🏅 if you were writing the quiz for the first time."
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
        f"🥉 Bronze - {medals['bronze']}",
        
        reply_markup=ReplyKeyboardMarkup([
            ["📋 See Leaderboard"]
        ], one_time_keyboard=False, resize_keyboard=True)
    )
    return STATE.STARTED

def display_leaderboard(update, context):
    chatId = update.message.chat
    board = leaderboard(update)

    update.message.reply_text(
        "The Leaderboard\n"
    )
    for user in board:
        if user['chatId'] == f"{chatId.id}":
            update.message.reply_text(
                f"You  --->  {user['totalPoints']}"
            )
        else:
            update.message.reply_text(
                f"{user['username']}  --->  {user['totalPoints']}"
            )
    return main_menu(update, context)

def english_lessons(update,context):
    update.message.reply_text(
        f"Great!, What grade are you in?",
        reply_markup=ReplyKeyboardMarkup([
            ["1️⃣","2️⃣"],
            ["3️⃣", "4️⃣"],
            ["5️⃣","6️⃣"],
            [ "7️⃣", "8️⃣"]
        ], one_time_keyboard=False, resize_keyboard=True)
    )

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
            MessageHandler(Filters.regex(r'🏛️'), reading_level),
            MessageHandler(Filters.regex(r'🏅'), medals),
            MessageHandler(Filters.regex(r'📔'), english_lessons),
            MessageHandler(Filters.regex(r'📋'), display_leaderboard),
        ],
        STATE.BROWSE_BOOKS: [
            MessageHandler(Filters.regex(r'📖'), read_book),
            MessageHandler(Filters.regex(r'➡️'), next_book)
        ],
        STATE.READING: [
            MessageHandler(Filters.regex(r'🏛️'), reading_level),
            MessageHandler(Filters.regex(r'👂'), text_to_speech),
            MessageHandler(Filters.regex(r'➡️'), next_page)
        ],
        STATE.QUIZZ: [
            MessageHandler(Filters.all, check_quizz_answer)
        ],
        STATE.READINGLEVEL: [
            # MessageHandler(Filters.regex(r'1️⃣'), reading_level)
            MessageHandler(Filters.regex(r'1️⃣'), assign_reading_level_1),
            MessageHandler(Filters.regex(r'2️⃣'), assign_reading_level_2),
            MessageHandler(Filters.regex(r'3️⃣'), assign_reading_level_3),
            MessageHandler(Filters.regex(r'4️⃣'), assign_reading_level_4)
        ]
        # STATE.GRADE: [
        #     MessageHandler(Filters.all, check_quizz_answer)
        # ]
        
    },
    fallbacks=[MessageHandler(Filters.all, return_to_main_menu)]


)
