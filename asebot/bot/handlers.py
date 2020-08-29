import logging
import random

import requests
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler)

import asebot.api
import asebot.config
from asebot.bot.rewards.points import Points
from asebot.constants import STATE, USER
from asebot.bot.alocate_points import alocate_points
from asebot.bot.leaderboard import leaderboard
from asebot.bot.english_lessons.english import English
from asebot.bot.english_lessons.lessons import Lessons
from asebot.bot.reading.reading import Reading
from asebot.bot.home.main_menu import MainMenu
from asebot.bot.english_lessons.lesson_quizz import LessonQuizz
from asebot.bot.english_lessons.end_of_unit import UnitQuizz


logger = logging.getLogger(__name__)
english_lessons = English()
inprogress_lesson = Lessons()
lessonQuizz = LessonQuizz()
mainmenu = MainMenu()
end_of_unit_test = UnitQuizz()
reading = Reading()
points = Points()


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def start(update, context):
    user = update.message.from_user
    if not context.user_data.get(USER.REPEAT_VISITOR):
        update.message.reply_text(
            f"👋 Hello, I'm Tsehai the Distance English Learning bot!"
        )
        # update.message.reply_text(
        #     f"Just read the stories and answer the questions as well as you can."
        # )
        # update.message.reply_text(
        #     f"I will show you new stories that match your own reading ability, helping you improve. "
        #     "Are you ready? Let's get started!"
        # )
        context.user_data[USER.REPEAT_VISITOR] = True
        context.user_data[USER.LESSON] = 1
    else:
        update.message.reply_text(f"Hello! 👋")
        update.message.reply_text(f"Nice to see you again, {user.first_name}.")
    return mainmenu.main_menu(update, context)


def view_book(update, context):
    books = context.user_data["books"]
    book_idx = context.user_data["book_idx"]
    update.message.reply_photo(
        photo=asebot.config.API_SERVER+books[book_idx]["cover"]["url"],
        caption=books[book_idx]["title"],
        parse_mode='Markdown',
        reply_markup=ReplyKeyboardMarkup([
            ['📖 Read this book'],
            ['➡️ Look for another book'],
            ['🏠 Return to Main Menu']
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

# lana
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
    points.validate_quizz_taken(context)
    
    num_questions = len(book["quizz"]["questions"])
    if num_questions > 0:
        context.user_data["quizz_idx"] = 0
        context.user_data["quizz_mistakes"] = 0
        update.message.reply_markdown(
            f"Now, answer {num_questions} questions as well as you can."
        )
        return view_quizz_question(update, context)
    else:
        return mainmenu.main_menu(update, context)

global quizCheck
quizCheck = True

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
    
    if len(qna["video"]) > 0:
            update.message.reply_video(
                video=asebot.config.API_SERVER+qna["video"][0]["url"],
                caption=text,
            )
            
    if qna["image"] and qna["audio"]:
                update.message.reply_photo(
                    photo=asebot.config.API_SERVER+qna["image"][0]["url"],
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                    )
                audio_href = asebot.config.API_SERVER+qna["audio"][0]["url"]
                update.message.reply_voice(
                    audio_href,
                    reply_markup=keyboard
                )
    elif qna["image"]:
        update.message.reply_photo(
                photo=asebot.config.API_SERVER+qna["image"][0]["url"],
                caption=text,
                parse_mode='Markdown',
                reply_markup=keyboard
                )
    elif qna["audio"]:
        audio_href = asebot.config.API_SERVER+qna["audio"][0]["url"]
        update.message.reply_voice(
            audio_href,
            caption=text,
            reply_markup=keyboard
            )
    if text:
        update.message.reply_markdown(text, reply_markup=keyboard)
    return STATE.QUIZZ


def check_quizz_answer(update, context):
    provided_answer = update.message.text.strip()
    quizz_idx = context.user_data["quizz_idx"]
    qna = context.user_data["book"]["quizz"]["questions"][quizz_idx]
    answer = qna["answer"]
    global quizCheck

    if provided_answer == answer:
        update.message.reply_text("✔️ That is correct.")
        return next_quizz_question(update, context)
    elif provided_answer != answer and quizCheck is True:
        quizCheck = False
        context.user_data["quizz_mistakes"] += 1
        update.message.reply_text(f"❌ Incorrect. Please try again.")
        return view_quizz_question(update, context)
    else:
        update.message.reply_text(f"❌ Incorrect. Please try again.")
        return view_quizz_question(update, context)


def next_quizz_question(update, context):
    next_idx = context.user_data["quizz_idx"] + 1
    if next_idx == len(context.user_data["book"]["quizz"]["questions"]):
        return quizz_finished(update, context)
    else:
        global quizCheck
        quizCheck = True
        context.user_data["quizz_idx"] = next_idx
        return view_quizz_question(update, context)


def quizz_finished(update, context):
    user = update.message.from_user

    quizz_mistakes = context.user_data["quizz_mistakes"]
    medal = points.points_medals_brain(context)
    medalattained = medal['medal']

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
    
    points.update_reading_level(update, context)

    update.message.reply_text(
            "Would you like to read another book?",
            reply_markup=ReplyKeyboardMarkup([
                [ "🟢 Yes", "🔴 No"],
            ], one_time_keyboard=False, resize_keyboard=True)
        )
    return STATE.BOOK_FINISHED

def next_book_after_quiz(update, context):
    books = len(context.user_data["books"])
    newbook = context.user_data["book_idx"] + 1 
    if newbook < books:
        context.user_data["book_idx"] += 1
    elif newbook == books:
        context.user_data["book_idx"] = 0
    return view_book(update,context)


def medals(update, context):
    context.user_data["levelSelectionPictures"] = asebot.api.load_level_Selection()
    if not context.user_data.get(USER.MEDALS_SEEN):
        update.message.reply_photo(
                photo=asebot.config.API_SERVER+context.user_data["levelSelectionPictures"][1]['Image'][0]['url'],
        )
        context.user_data[USER.MEDALS_SEEN] = True

    medals = context.user_data.setdefault(
        "medals", dict(gold=0, silver=0, bronze=0))
    update.message.reply_text(
        f"🏅 Your Medals\n"
        f"\n"
        f"🥇 Gold - {medals['gold']}\n"
        f"🥈 Silver - {medals['silver']}\n"
        f"🥉 Bronze - {medals['bronze']}",
        
        reply_markup=ReplyKeyboardMarkup([
            ["🏠 Return To Main Menu"],
            ["📋 See Leaderboard", "🎓 See My Quiz Marks"]
        ], one_time_keyboard=False, resize_keyboard=True)
    )
    return STATE.STARTED

def display_quiz_marks(update, context):
    numberOfquizz = 0
    
    update.message.reply_text(
        "Your Quiz Marks\n"
        "To go to a book click on its Book Id value"
    )
    if context.user_data.get(USER.QUIZZ_TAKEN) is not None:
        books = context.user_data[USER.QUIZZ_TAKEN]
        numberOfquizz = len(books)
        average = 0
        for book_elements in books:
            if books[book_elements]['level'] == context.user_data[USER.READING_LEVEL]:
                if books[book_elements]['percentage'] >= 80:
                    result = "Passed"
                else:
                    result = "Failure"
                average = average + books[book_elements]["percentage"]
                update.message.reply_text(
                    f"Book Id = /{books[book_elements]['book_idx']} Book Title = {books[book_elements]['title']}  results =  {result} percentage = {books[book_elements]['percentage']}"
                    )
        update.message.reply_text(
            f"Your average at the moment is {average/numberOfquizz}\n"
            )
    elif numberOfquizz == 0:
        update.message.reply_text(
            "You have not written any quizzes on this level Yet\n"
            "Good Luck with Your reading!!!\n"
            )
    
    if context.user_data.get(USER.UNIT_MARKS) is not None:
        print(context.user_data[USER.UNIT_MARKS])
        update.message.reply_text(
            "The averages you got for your english lessons grades Are:\n"
            )
        gradeMarks = context.user_data[USER.UNIT_MARKS]
        for grade_elements in gradeMarks:
            numberOfunitquizz = len(gradeMarks[grade_elements])
            averageGrades = 0
            for unit_quiz_marks in gradeMarks[grade_elements]:
                averageGrades = averageGrades + gradeMarks[grade_elements][unit_quiz_marks]
            update.message.reply_text(
                f"In grade {grade_elements} your average is {round(averageGrades/numberOfunitquizz)}"
                )
    
    update.message.reply_text(
        f"What would you like to do?",
        reply_markup=ReplyKeyboardMarkup([
            ['↩️ Return to main menu']
        ], one_time_keyboard=False, resize_keyboard=True)
    )
    return STATE.BOOK_REDIRECT

def book_redirect(update, context):
    book_redirect_id = int(update.message.text.replace('/',''))
    books = context.user_data[USER.QUIZZ_TAKEN]
    for book_elements in books:
        if books[book_elements]['book_idx'] == book_redirect_id and books[book_elements]['level'] == context.user_data[USER.READING_LEVEL]:
            context.user_data["book_idx"] = book_redirect_id
            return view_book(update, context)
    return mainmenu.return_to_main_menu(update, context)

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
    return mainmenu.main_menu(update, context)

# def return_to_main_menu(update, context):
#     update.message.reply_text("Sorry, I don't know how to help you with that.")
#     return main_menu(update, context)


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
            MessageHandler(Filters.regex(r'🏛️'), reading.reading_level),
            MessageHandler(Filters.regex(r'🏅'), medals),
            MessageHandler(Filters.regex(r'📔'), english_lessons.english_lessons),
            MessageHandler(Filters.regex(r'📋'), display_leaderboard),
            MessageHandler(Filters.regex(r'🎓'), display_quiz_marks),
            MessageHandler(Filters.regex("🏠"), mainmenu.main_menu),
            MessageHandler(Filters.regex(r'😜'), mainmenu.resetbutt)
        ],
        STATE.BROWSE_BOOKS: [
            MessageHandler(Filters.regex(r'📖'), read_book),
            MessageHandler(Filters.regex(r'➡️'), next_book),
            MessageHandler(Filters.regex("🏠"), mainmenu.main_menu)
        ],
        STATE.READING: [
            MessageHandler(Filters.regex(r'🏛️'), reading.reading_level),
            MessageHandler(Filters.regex(r'👂'), text_to_speech),
            MessageHandler(Filters.regex(r'➡️'), next_page)
        ],
        STATE.QUIZZ: [
            MessageHandler(Filters.all, check_quizz_answer),
        ],
        STATE.READINGLEVEL: [
            MessageHandler(Filters.all, reading.assign_reading_level),
        ],
        
        STATE.SECONDCONFIRMREADINGLEVEL: [
            MessageHandler(Filters.regex(r'🟢'), reading.yes_proceed), 
            MessageHandler(Filters.regex(r'🔴'), reading.no)  
        ],
        
        STATE.FIRSTCONFIRMREADINGLEVEL: [
            MessageHandler(Filters.all, reading.confirm),
        ],
        
        STATE.GRADE: [
            MessageHandler(Filters.all, english_lessons.assign_grade)
        ],
        
        STATE.BOOK_REDIRECT: [
            MessageHandler(Filters.regex(r'↩️'), mainmenu.main_menu),
            MessageHandler(Filters.regex(r'/'), book_redirect)
        ],

        STATE.UNIT: [
            MessageHandler(Filters.regex(r'↩️'), english_lessons.unit),
            MessageHandler(Filters.all, english_lessons.unit_decision)
        ],
        
        # STATE.UNIT_CHOICE: [
        #     MessageHandler(Filters.regex(r'🟢'), english_lessons.unit_response),
        #     MessageHandler(Filters.regex(r'🔴'), english_lessons.unit)
        # ],

        STATE.LESSON: [
           # MessageHandler(Filters.regex("🏠"), mainmenu.main_menu),
            MessageHandler(Filters.regex("🏠"), inprogress_lesson.skip_unit),
            MessageHandler(Filters.regex("➡️"), inprogress_lesson.next),
            MessageHandler(Filters.regex("▶"), english_lessons.proceed)
        ],
        
        STATE.RETRY_LESSON: [
            MessageHandler(Filters.regex("🏠"), mainmenu.main_menu),
            MessageHandler(Filters.regex("😃"), english_lessons.proceed)
        ],
        
        STATE.RETRY_UNIT: [
            MessageHandler(Filters.regex("🏠"), mainmenu.main_menu),
            MessageHandler(Filters.regex("😃"), inprogress_lesson.skip_unit)
        ],

        STATE.BOOK_FINISHED: [
            MessageHandler(Filters.regex("🔴"), mainmenu.main_menu),
            MessageHandler(Filters.regex("🟢"), next_book_after_quiz),
        ],

        STATE.UNIT_QUIZZ: [
            MessageHandler(Filters.all, end_of_unit_test.check_test_answer)
        ],

        STATE.LESSON_QUIZZ: [
            MessageHandler(Filters.all, lessonQuizz.check_quizz_answer),
        ],
        
        STATE.CHOOSE_LESSON: [
            MessageHandler(Filters.regex("🏠"), mainmenu.main_menu),
            MessageHandler(Filters.regex("▶"), english_lessons.proceed)
        ],
        
        STATE.AUDIO_LESSON: [
            MessageHandler(Filters.regex("🇫🇲"), inprogress_lesson.lesson_page)
        ],

        # STATE.COMFIRM_GRADE: [
        #     MessageHandler(Filters.regex("🟢"), english_lessons.reconfirm_grade),
        #     MessageHandler(Filters.regex("🔴"), english_lessons.english_lessons),
        # ],

        # STATE.RE_COMFIRM_GRADE: [
        #     MessageHandler(Filters.regex("🟢"), english_lessons.assign_grade),
        #     MessageHandler(Filters.regex("🔴"), english_lessons.english_lessons),
        # ]
    },
    fallbacks=[MessageHandler(Filters.all, mainmenu.return_to_main_menu)]


)
