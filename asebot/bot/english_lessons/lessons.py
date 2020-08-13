from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.english_lessons.end_of_unit import UnitQuizz
from asebot.bot.english_lessons.lesson_quizz import LessonQuizz
import asebot.config
from asebot.connect_api import ConnectAPI
#from asebot.bot.english_lessons.english import English

api = ConnectAPI()

end_of_unit_test = UnitQuizz()
lessonQuizz = LessonQuizz()
#english_lessons = English()


class Lessons:
    """ Open lessons for any specified grade
        read book equivalent
    """

    def open_lessons(self, update, context):
        context.user_data["lesson_page_idx"] = 0

        grade = context.user_data[USER.GRADE]
        unit = context.user_data[USER.UNIT]
        lesson = context.user_data[USER.LESSON]
        
        context.user_data["lesson"] = api.load_lesson(grade, unit, lesson)
        if len(context.user_data["lesson"]) == 0:
            update.message.reply_text(
                "There are no lessons available at the moment. "
                "Please try again later."
                )
            return self.skip_unit(update, context)
        return self.audio_introduction(update,context)

    """ equivalent to view page """
    def audio_introduction(self,update,context):
        if context.user_data["lesson"][0]["recordings"] is not None:
            audio_href = asebot.config.API_SERVER+context.user_data["lesson"][0]["recordings"]["url"]
            update.message.reply_voice(
                audio_href,
                reply_markup=ReplyKeyboardMarkup([
                    ["🇫🇲 NEXT"],
                    ], one_time_keyboard=False, resize_keyboard=True)
                )
            return STATE.AUDIO_LESSON
        else:
            return self.lesson_page(update,context)
    
    def lesson_page(self, update, context):
        pages = context.user_data["lesson"][0]["page"]
        page_idx = context.user_data["lesson_page_idx"]
        page = pages[page_idx]

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
            "Starting Lesson",
            reply_markup=keyboard
        )
        audio=page["audio"]
        if len(page["images"]) > 0:
            if not audio:
                update.message.reply_photo(
                    photo=asebot.config.API_SERVER+page["images"][0]["url"],
                    caption=page["text"],
                    parse_mode='Markdown',
                    reply_markup=keyboard
                )
            else:
                audio_href = asebot.config.API_SERVER+page["images"][0]["url"],
                update.message.reply_voice(
                    audio_href,
                    caption=page["text"],
                    reply_markup=keyboard
                )
        else:
            update.message.reply_markdown(
                page["text"],
                reply_markup=keyboard
            )
        return STATE.LESSON

    def next(self, update, context):
        next_idx = context.user_data["lesson_page_idx"] + 1
        if next_idx == len(context.user_data["lesson"][0]["page"]):
            return self.lesson_finished(update, context)
        else:
            context.user_data["lesson_page_idx"] = next_idx
            return self.lesson_page(update, context)

    def lesson_finished(self, update, context):
        user = update.message.from_user
        update.message.reply_text(
            f"🎉 Well done, {user.first_name}."
        )
        return lessonQuizz.start_quizz(update, context)

    def skip_unit(self, update, context):
        return end_of_unit_test.start_test(update, context)
