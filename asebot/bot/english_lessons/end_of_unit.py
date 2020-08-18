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

class UnitQuizz:
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
                "There are no unit quizzes available at the moment. "
                "Please try again later."
                )
            return mainmenu.main_menu(update, context)

    def view_test_question(self, update, context):
        unit_quizz_idx = context.user_data["unit_quizz_idx"]
        qna = context.user_data["unit_quiz"][0]["Questions"][unit_quizz_idx]
        audio = qna["audio"]
        question = qna["question"]
        answers = [qna["answer"]] + [d["wrong_answer"] for d in qna["distractors"]]
        random.shuffle(answers)
        text = f"**Question {unit_quizz_idx +1}**: {question}"
        keyboard = ReplyKeyboardMarkup(
            [[a] for a in answers],
            one_time_keyboard=False,
            resize_keyboard=True)
        if qna["image"]:
            if not audio:
                update.message.reply_photo(
                    photo=asebot.config.API_SERVER+qna["image"]["url"],
                    caption=text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                    )
            else:
                audio_href = asebot.config.API_SERVER+qna["image"]["url"]
                update.message.reply_voice(
                    audio_href,
                    reply_markup=keyboard
                )
        else:
            update.message.reply_markdown(text, reply_markup=keyboard)
        return STATE.UNIT_QUIZZ

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
        percentageattained = medal['percentage']
        context.user_data.setdefault(
            "medals", dict(gold=0, silver=0, bronze=0,nomedal=0)
            )[f"{medalattained}"] += 1
        if percentageattained >= 70:
            update.message.reply_text(
            f"Congratulations, you got a {str(medalattained)} medal 🎉."
            )
            self.check_percentage(context, percentageattained)
            numberofquizzes = len(api.load_unit_quiz_length(context.user_data[USER.GRADE]))
            quizlength = len(context.user_data[USER.UNIT_MARKS])
            if  quizlength != numberofquizzes :
                context.user_data[USER.UNIT_CHOSEN].append(context.user_data[USER.UNIT] + 1)
                update.message.reply_text(f"You can now access a new unit {context.user_data[USER.UNIT] + 1}")
                return level_up.next_unit(update, context)
            elif quizlength == numberofquizzes:
                update.message.reply_text(f"You have unlocked a new grade {context.user_data[USER.GRADE] + 1}")
                if  context.user_data[USER.GRADE] + 1 == 9:
                    update.message.reply_text(f"You are Done with english lessons, but you can still access grade 8nand the library😜😜😜")
                else:
                    context.user_data[USER.GRADE] += 1 
                return mainmenu.main_menu(update, context)
        
        return self.view_test_results(update, context)

    def check_percentage(self,context, percentage):
        if context.user_data[USER.UNIT_MARKS] is not None:
            if context.user_data[USER.UNIT] in context.user_data[USER.UNIT_MARKS].keys():
                if percentage > context.user_data[USER.UNIT_MARKS][context.user_data[USER.UNIT]]:
                    context.user_data[USER.UNIT_MARKS][context.user_data[USER.UNIT]] = percentage
            else:
                context.user_data[USER.UNIT_MARKS] = {
                context.user_data[USER.UNIT] : percentage
                }
        else:
            context.user_data[USER.UNIT_MARKS] = {
                context.user_data[USER.UNIT] : percentage
                }

    def view_test_results(self, update, context):
        update.message.reply_text("results")
        if context.user_data[USER.UNIT_MARKS] is not None:
            update.message.reply_text("These are the quizzes you have written and passed.\n")
            update.message.reply_text("Good Luck on the next one's 😃")
            results = context.user_data[USER.UNIT_MARKS].sort()
            for elements in results:
                update.message.reply_text("These are you unit quiz Results")
                update.message.reply_text(f"units:{elements} results:{results[elements]}")
            
            update.message.reply_text(
                "Select [Main Menu] to go to Main Menu, or [try again] to return to the unit",
                reply_markup=ReplyKeyboardMarkup([
                    [ "🏠 Main Menu", "😃 try Again"],
                    ], one_time_keyboard=False, resize_keyboard=True)
                )
        else:
            update.message.reply_text("Sorry you haven't passed any quizzes at the moment\n")
            update.message.reply_text("Good Luck on the next one's 😃")
            update.message.reply_text(
                "Select [Main Menu] to go to Main Menu, or [try again] to return to the unit",
                reply_markup=ReplyKeyboardMarkup([
                    [ "🏠 Main Menu", "😃 try Again"],
                    ], one_time_keyboard=False, resize_keyboard=True)
                )
        return STATE.RETRY_UNIT