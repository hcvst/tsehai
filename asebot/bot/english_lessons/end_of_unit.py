import random
import asebot.config
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.home.main_menu import MainMenu
from asebot.bot.rewards.level_up import LevelUp
from asebot.connect_api import ConnectAPI

mainmenu = MainMenu()
level_up = LevelUp()
api = ConnectAPI()

class UnitTest:
    def start_test(self, update, context):
        update.message.reply_text("start test")
        grade = context.user_data[USER.GRADE]
        unit = context.user_data[USER.UNIT]
        context.user_data["unit_quiz"] = api.load_unit_quiz(grade, unit)
        if len(context.user_data["unit_quiz"]) > 0:
            level_up.validate_unit_quizz_taken(context)
            context.user_data["unit_quizz_idx"] = 0
            context.user_data["unit_quizz_mistakes"] = 0
            num_questions = len(context.user_data["unit_quiz"][0]["Questions"])
            update.message.reply_markdown(
                f"Now, answer {num_questions} questions as well as you can.\n"
                f"{context.user_data['unit_quiz'][0]['Instructions']}"
                )
            return self.view_test_question(update, context)
        else:
            update.message.reply_markdown(
                "Siyaxolisa awakabikhona ama unit quiz 🤣"
                )
            return mainmenu.main_menu(update, context)

    def view_test_question(self, update, context):
        unit_quizz_idx = context.user_data["unit_quizz_idx"]
        qna = context.user_data["unit_quiz"][0]["Questions"][unit_quizz_idx]
        question = qna["question"]
        answers = [qna["answer"]] + [d["wrong_answer"] for d in qna["distractors"]]
        random.shuffle(answers)
        text = f"**Question {unit_quizz_idx +1}**: {question}"
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
        return STATE.UNIT_TEST

    def check_test_answer(self, update, context):
        provided_answer = update.message.text.strip()
        unit_quizz_idx = context.user_data["unit_quizz_idx"]
        qna = context.user_data["unit_quiz"][0]["Questions"][unit_quizz_idx]
        answer = qna["answer"]
        if provided_answer == answer:
            update.message.reply_text("✔️ That is correct.")
        else:
            context.user_data["unit_quizz_mistakes"] += 1
            update.message.reply_text(f"❌ The correct answer is '{answer}'.")
        return self.next_test_question(update, context)

    def next_test_question(self, update, context):
        next_idx = context.user_data["unit_quizz_idx"] + 1
        if next_idx == len(context.user_data["unit_quiz"][0]["Questions"]):
            return self.test_finished(update, context)
        else:
            context.user_data["unit_quizz_idx"] = next_idx
            return self.view_test_question(update, context)

    def test_finished(self, update, context):
        update.message.reply_text("finished")
        medal = level_up.points_medals_unit_quiz(context)
        medalattained = medal['medal']
        
        context.user_data.setdefault(
            "medals", dict(gold=0, silver=0, bronze=0,nomedal=0)
            )[f"{medalattained}"] += 1
        update.message.reply_text(
            f"Congratulations, you got {str(medalattained)} a medal 🎉."
            )
        return level_up.next_unit(update, context)

    def view_test_results(self, update, context):
        update.message.reply_text("results")
        return mainmenu.main_menu(update, context)