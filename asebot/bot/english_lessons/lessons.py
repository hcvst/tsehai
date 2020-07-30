from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.english_lessons.end_of_unit import UnitTest
from asebot.bot.english_lessons.lesson_quizz import LessonQuizz


end_of_unit_test = UnitTest()
lessonQuizz = LessonQuizz()

class Lessons:
    """ Open lessons for any specified grade
        read book equivalent
    """
    def open_lessons(self, update, context):
        print("open lessons")
        return self.lesson_page(update, context)

    """ equivalent to view page """
    def lesson_page(self, update, context):
        print("Got here")
        keyboard = ReplyKeyboardMarkup(
            [
                ['🏠 Return to main menu'],
                ['⏭ Skip Unit'],
                ['➡️ Turn to the next page']
            ],
            one_time_keyboard=False,
            resize_keyboard=True
        )
        update.message.reply_markdown(
            'testing',
            reply_markup=keyboard
        )
        return STATE.LESSON

    def next(self, update, context):
        return self.lesson_finished(update, context)

    def lesson_finished(self, update, context):
         return lessonQuizz.start_quizz(update, context)

    def skip_unit(self, update, context):
        return end_of_unit_test.start_test(update, context)