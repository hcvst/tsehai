import random
import asebot.config
import re 
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.home.main_menu import MainMenu
from asebot.bot.rewards.level_up import LevelUp
from asebot.bot.alocate_points import alocate_points
from asebot.bot.components.special_characters import SpecialCharacters


mainmenu = MainMenu()
level_up = LevelUp()

class LessonQuizz:
    global quizCheck
    quizCheck = True

    global regex
    regex = re.compile('[@_!#$%^&()<>/\|}{~]')
    
    def start_quizz(self, update, context):
        lesson = context.user_data["lesson"]
        if lesson:
            level_up.validate_lesson_quizz_taken(context)
            context.user_data["lesson_quizz_idx"] = 0
            context.user_data["lesson_quizz_mistakes"] = 0
            num_questions = len(lesson[0]["lesson_quizz"]["questions"])
            update.message.reply_markdown(
                f"Now, answer {num_questions} questions as well as you can.\n"
                f"{context.user_data['lesson'][0]['lesson_quizz']['instructions']}"
                )
            return self.view_quizz_question(update, context)
        else:
            update.message.reply_markdown(
                "There are no lesson quizzes available at the moment. "
                "Please try again later."
                )
            return mainmenu.main_menu(update, context)

    def view_quizz_question(self, update, context):
        global regex
        lesson_quizz_idx = context.user_data["lesson_quizz_idx"]
        qna = context.user_data["lesson"][0]["lesson_quizz"]["questions"][lesson_quizz_idx]
        question = qna["question"]
        answers = [qna["answer"]] + [d["wrong_answer"] for d in qna["distractors"]]
        random.shuffle(answers)
        text = f"**Question {lesson_quizz_idx +1}**: {question}"
        keyboard = ReplyKeyboardMarkup(
            [[a] for a in answers],
            one_time_keyboard=False,
            resize_keyboard=True)
        
        if qna["video"]:
            update.message.reply_video(
                video=qna["video"],
                #caption=text,
            )
        
        if qna["image"] and qna["audio"]:
                update.message.reply_photo(
                    photo=asebot.config.API_SERVER+qna["image"]["url"],
                    #caption=text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                    )
                audio_href = asebot.config.API_SERVER+qna["audio"]["url"]
                update.message.reply_voice(
                    audio_href,
                    reply_markup=keyboard
                )
        elif qna["image"]:
            update.message.reply_photo(
                    photo=asebot.config.API_SERVER+qna["image"]["url"],
                    #caption=text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                    )
        elif qna["audio"]:
            audio_href = asebot.config.API_SERVER+qna["audio"]["url"]
            update.message.reply_voice(
                audio_href,
                #caption=text,
                reply_markup=keyboard
                )
        if text:
            text = SpecialCharacters.checkSpecialCharacter(SpecialCharacters, text)
            update.message.reply_markdown(
                text,
                reply_markup=keyboard
            )
        return STATE.LESSON_QUIZZ

    def check_quizz_answer(self, update, context):
        provided_answer = update.message.text.strip()
        lesson_quizz_idx = context.user_data["lesson_quizz_idx"]
        qna = context.user_data["lesson"][0]["lesson_quizz"]["questions"][lesson_quizz_idx]
        answer = qna["answer"]
        global quizCheck
        
        if provided_answer == answer:
            update.message.reply_text("✔️ That is correct.")
            return self.next_quizz_question(update, context)
        elif provided_answer != answer and quizCheck is True:
            quizCheck = False
            context.user_data["lesson_quizz_mistakes"] += 1
            update.message.reply_text(f"❌ Incorrect. Please try again.")
            return self.view_quizz_question(update, context)
        else:
            update.message.reply_text(f"❌ Incorrect. Please try again.")
            return self.view_quizz_question(update, context)

    def next_quizz_question(self, update, context):
        next_idx = context.user_data["lesson_quizz_idx"] + 1
        if next_idx == len(context.user_data["lesson"][0]["lesson_quizz"]["questions"]):
            return self.quizz_finished(update, context)
        else:
            global quizCheck
            quizCheck = True
            context.user_data["lesson_quizz_idx"] = next_idx
            return self.view_quizz_question(update, context)

    def quizz_finished(self, update, context):
        points = level_up.points_medals_lesson_quiz(context)
        pointsattained = points["points"]
        percentattained = points["percentage"]
        alocate_points(update, pointsattained)
        pointsChoice = "points"
        
        if pointsattained == 1:
            pointsChoice = "point"
        
        if percentattained >= 70:
            update.message.reply_text(
                f"Congratulations, you got {pointsattained} {pointsChoice}🎉."
                )
            return level_up.next_lesson(update, context)
        elif percentattained <= 69:
            update.message.reply_text(
                f"Sorry 😔, you got {pointsattained} {pointsChoice} for this quiz. Don't worry, you can try again.😃"
                )
            return level_up.retry_lesson(update, context)
        