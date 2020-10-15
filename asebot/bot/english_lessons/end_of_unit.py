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
    global quizCheck
    quizCheck = True
    
    def start_test(self, update, context):
        grade = context.user_data[USER.GRADE]
        unit = context.user_data[USER.UNIT]
        context.user_data["unit_quiz"] = api.load_unit_quiz(grade, unit)
        print(grade)
        print(unit)
        if len(context.user_data["unit_quiz"]) > 0:
            print(context.user_data["unit_quiz"])
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
        qna = None
        qna = context.user_data["unit_quiz"][0]["Questions"][unit_quizz_idx]
        question = qna["question"]
        answers = [qna["answer"]] + [d["wrong_answer"] for d in qna["distractors"]]
        random.shuffle(answers)
        text = f"**Question {unit_quizz_idx +1}**: {question}"
        keyboard = ReplyKeyboardMarkup(
            [[a] for a in answers],
            one_time_keyboard=False,
            resize_keyboard=True)
        
        if qna["video"]:
            audio_href = qna["video"]
            update.message.reply_voice(
                audio_href,
                #caption=text,
                 reply_markup=keyboard
            )
        
        if qna["image"] and qna["audio"]:
                update.message.reply_photo(
                    photo=asebot.config.API_SERVER+qna["image"]["url"],
                    #caption=text,
                    parse_mode='Markdown',
                    reply_markup=keyboard
                    )
                audio_href = asebot.config.API_SERVER+qna["audio"][0]["url"]
                update.message.reply_voice(
                    audio_href,
                    #caption=text,
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
            audio_href = asebot.config.API_SERVER+qna["audio"][0]["url"]
            update.message.reply_voice(
                audio_href,
                #caption=text,
                reply_markup=keyboard
            )
        if text:
            update.message.reply_markdown(text, reply_markup=keyboard)
        return STATE.UNIT_QUIZZ

    def check_test_answer(self, update, context):
        provided_answer = update.message.text.strip()
        unit_quizz_idx = context.user_data["unit_quizz_idx"]
        qna = context.user_data["unit_quiz"][0]["Questions"][unit_quizz_idx]
        answer = qna["answer"]
        global quizCheck
        
        if provided_answer == answer:
            update.message.reply_text("✔️ That is correct.")
            return self.next_test_question(update, context)
        elif provided_answer != answer and quizCheck is True:
            quizCheck = False
            context.user_data["unit_quizz_mistakes"] += 1
            update.message.reply_text(f"❌ Incorrect. Please try again.")
            return self.view_test_question(update, context)
        else:
            update.message.reply_text(f"❌ Incorrect. Please try again.")
            return self.view_test_question(update, context)

    def next_test_question(self, update, context):
        next_idx = context.user_data["unit_quizz_idx"] + 1
        if next_idx == len(context.user_data["unit_quiz"][0]["Questions"]):
            return self.test_finished(update, context)
        else:
            global quizCheck
            quizCheck = True
            context.user_data["unit_quizz_idx"] = next_idx
            return self.view_test_question(update, context)

    def test_finished(self, update, context):
        medal = level_up.points_medals_unit_quiz(context)
        medalattained = medal['medal']
        percentageattained = medal['percentage']
        context.user_data.setdefault(
            "medals", dict(gold=0, silver=0, bronze=0,nomedal=0)
            )[f"{medalattained}"] += 1
        userGrade = context.user_data[USER.GRADE]
        self.check_percentage(context, percentageattained)
        numberofquizzes = len(api.load_unit_quiz_length(userGrade)["unitQuizs"])
        quizlength = 0
        
        print(context.user_data[USER.UNIT_MARKS])
        if context.user_data.get(USER.UNIT_MARKS) is not None:
            quizlength = len(context.user_data[USER.UNIT_MARKS][userGrade])
        
        if quizlength == numberofquizzes and percentageattained >= 70:
            update.message.reply_text(f"You have unlocked a new grade {context.user_data[USER.GRADE] + 1}, Congratulations 🎉.")
            if  context.user_data[USER.GRADE] + 1 == 9:
                update.message.reply_text(f"You are Done with english lessons, but you can still access any grade and the library😜😜😜")
            else:
                context.user_data[USER.GRADE] += 1
            return mainmenu.main_menu(update, context)
        elif percentageattained >= 70 :
            update.message.reply_text(
                f"Congratulations, you got a {str(medalattained)} medal 🎉."
                )
            update.message.reply_text(f"You can now access a new unit {context.user_data[USER.UNIT] + 1}")
            return level_up.next_unit(update, context)
        return self.view_test_results(update, context)

    def check_percentage(self,context, percentage):
        userGrade = context.user_data[USER.GRADE]
        if context.user_data.get(USER.UNIT_MARKS) is not None:
            if userGrade in context.user_data[USER.UNIT_MARKS].keys():
                if context.user_data[USER.UNIT] in context.user_data[USER.UNIT_MARKS].keys():
                    if percentage > context.user_data[USER.UNIT_MARKS][userGrade][context.user_data[USER.UNIT]]:
                        context.user_data[USER.UNIT_MARKS][userGrade][context.user_data[USER.UNIT]] = percentage
                else:
                    context.user_data[USER.UNIT_MARKS][userGrade][context.user_data[USER.UNIT]] = percentage
            else:
                context.user_data[USER.UNIT_MARKS][userGrade] = {
                context.user_data[USER.UNIT] : percentage
                }
        else:
            context.user_data[USER.UNIT_MARKS] = {
                userGrade : {
                    context.user_data[USER.UNIT] : percentage
                    }
                }

    def view_test_results(self, update, context):
        userGrade = context.user_data[USER.GRADE]
        if context.user_data[USER.UNIT_MARKS] is not None:
            update.message.reply_text("These are your unit quiz Results")
            results = context.user_data[USER.UNIT_MARKS][userGrade]
            for elements in results:
                update.message.reply_text(f"For unit:{elements} your results are: {results[elements]}")
            
            update.message.reply_text("Good Luck on the next one.😃")
            update.message.reply_text(
                "Select [Main Menu] to go to Main Menu, or [Try again] to return to the unit",
                reply_markup=ReplyKeyboardMarkup([
                    [ "🏠 Main Menu", "😃 Try Again"],
                    ], one_time_keyboard=False, resize_keyboard=True)
                )
        else:
            update.message.reply_text("Sorry you haven't passed any quizzes at the moment\n")
            update.message.reply_text("Good Luck on the next one.😃")
            update.message.reply_text(
                "Select [Main Menu] to go to Main Menu, or [Try again] to return to the unit",
                reply_markup=ReplyKeyboardMarkup([
                    [ "🏠 Main Menu", "😃 Try Again"],
                    ], one_time_keyboard=False, resize_keyboard=True)
                )
        return STATE.RETRY_UNIT