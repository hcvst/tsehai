from asebot.bot.english_lessons.english import English
from asebot.constants import USER
from asebot.bot.home.main_menu import MainMenu
from asebot.bot.components.switch import Switch

english_lessons = English()
mainmenu = MainMenu()
switcher = Switch()
english_lessons = English()

class LevelUp:
    def next_unit(self, update, context):
        print("level up")
        update.message.reply_text("Next unit")
        print("I am here")
        #points allocation and moving on
        return mainmenu.main_menu(update, context)
    
    def next_lesson(self, update, context):
        print("Next lesson")
        context.user_data[USER.LESSON] += 1
        print(context.user_data[USER.LESSON])
        #add markup to choose main menu or go to the lesson
        return mainmenu.main_menu(update, context)
        #return english_lessons.proceed(self, update, context)
    
    def validate_lesson_quizz_taken(self, context):
        grade = switcher.num_to_words(context.user_data[USER.GRADE])
        unit = switcher.num_to_words(context.user_data[USER.UNIT])
        lesson = switcher.num_to_words(context.user_data[USER.LESSON])
        element_id = int(context.user_data["lesson"][0]["id"])
        
        if context.user_data[USER.LESSON_QUIZ] is not None:
            if element_id in context.user_data[USER.LESSON_QUIZ].keys():
                context.user_data[USER.LESSON_QUIZ][element_id]["taken"] = "false"
            else:
                context.user_data[USER.LESSON_QUIZ][element_id] = {
                    "taken": "true",
                    "grade": grade,
                    "unit": unit,
                    "lessson": lesson,
                    "percentage": None
                    }
        else:
            context.user_data[USER.LESSON_QUIZ] = {
                element_id: {
                    "taken": "true",
                    "grade": grade,
                    "unit": unit,
                    "lessson": lesson,
                    "percentage": None
                    }
                }
        print(context.user_data[USER.LESSON_QUIZ])
    
    def validate_unit_quizz_taken(self, context):
        grade = switcher.num_to_words(context.user_data[USER.GRADE])
        unit = switcher.num_to_words(context.user_data[USER.UNIT])
        element_id = int(context.user_data["unit_quiz"][0]["id"])
        
        if context.user_data[USER.UNIT_QUIZ] is not None:
            if element_id in context.user_data[USER.UNIT_QUIZ].keys():
                context.user_data[USER.UNIT_QUIZ][element_id]["taken"] = "false"
            else:
                context.user_data[USER.UNIT_QUIZ][element_id] = {
                    "taken": "true",
                    "grade": grade,
                    "unit": unit,
                    "percentage": None
                    }
        else:
            context.user_data[USER.UNIT_QUIZ] = {
                element_id: {
                    "taken": "true",
                    "grade": grade,
                    "unit": unit,
                    "percentage": None
                    }
                }
        print(context.user_data[USER.UNIT_QUIZ])
    
    def points_medals_unit_quiz(self, context):
        numberofquestions = len(context.user_data["unit_quiz"][0]["Questions"])
        incorrectanswers = context.user_data["unit_quizz_mistakes"]
        correctanswers = numberofquestions - incorrectanswers
        percentage= round(correctanswers/numberofquestions * 100)
        if percentage == 100:
            medalcalculation = {
                "medal": "gold",
                "percentage": percentage
                }
        elif percentage <= 90 and percentage >= 80:
            medalcalculation = {
                "medal": "silver",
                "percentage": percentage
                }
        elif percentage <= 79 and percentage >= 70:
            medalcalculation = {
                "medal": "bronze",
                "percentage": percentage
                }
        else:
            medalcalculation = {
                "medal": "nomedal",
                "percentage": percentage
                }
        return medalcalculation
    
    def points_medals_lesson_quiz(self, context):
        numberofquestions = len(context.user_data["lesson"][0]["lesson_quizz"]["questions"])
        incorrectanswers = context.user_data["lesson_quizz_mistakes"]
        correctanswers = numberofquestions - incorrectanswers
        percentage= round(correctanswers/numberofquestions * 100)
        if percentage == 100:
            medalcalculation = {
                "points": 3,
                "percentage": percentage
                }
        elif percentage <= 90 and percentage >= 80:
            medalcalculation = {
                "points": 2,
                "percentage": percentage
                }
        elif percentage <= 79 and percentage >= 70:
            medalcalculation = {
                "points": 1,
                "percentage": percentage
                }
        else:
            medalcalculation = {
                "points": "nomedal",
                "percentage": percentage
                }
        return medalcalculation