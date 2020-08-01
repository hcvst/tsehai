import math
from asebot.constants import USER
import asebot.bot.handlers

def validate_quizz_taken(context):
    booktitle = context.user_data["book"]["title"]
    userlevel = context.user_data.get(USER.READING_LEVEL)
    book_idx = context.user_data["book_idx"]
    element_id = int(context.user_data["books"][book_idx]["id"])
    
    if context.user_data[USER.QUIZZ_TAKEN] is not None:
        if element_id in context.user_data[USER.QUIZZ_TAKEN].keys():
            context.user_data[USER.QUIZZ_TAKEN][element_id]["taken"] = "false"
        else:
            context.user_data[USER.QUIZZ_TAKEN][element_id] = {
                "taken": "true",
                "level": userlevel,
                "title": f"{booktitle}",
                "book_idx": book_idx,
                "percentage": None
                }
    else:
        context.user_data[USER.QUIZZ_TAKEN] = {
            element_id: {
                "taken": "true",
                "level": userlevel,
                "title": f"{booktitle}",
                "book_idx": book_idx,
                "percentage": None
                }
            }
    print(context.user_data)

    

def points_medals_brain(context):
    numberofquestions = len(context.user_data["book"]["quizz"]["questions"])
    incorrectanswers = context.user_data["quizz_mistakes"]
    correctanswers = numberofquestions - incorrectanswers
    percentage= round(correctanswers/numberofquestions * 100)
    book_idx = context.user_data["book_idx"]
    element_id = int(context.user_data["books"][book_idx]["id"]) 
    validatemedal = context.user_data[USER.QUIZZ_TAKEN][element_id]
    update_percentage(validatemedal,percentage)
    print(validatemedal)
    if validatemedal["taken"] == "true":
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
    else:
        medalcalculation = {
            "medal": "nomedal",
            "percentage": percentage
            }
        return medalcalculation
    
def update_percentage(validate_percentage_element,percentage):
    if validate_percentage_element["percentage"] is not None:
        if validate_percentage_element["percentage"] < percentage:
            validate_percentage_element["percentage"] = percentage
    else:
       validate_percentage_element["percentage"] = percentage

def update_reading_level(update, context):
    numberofbooks = len(context.user_data["books"])
    numberOfquizz = len(context.user_data[USER.QUIZZ_TAKEN])
    books = context.user_data[USER.QUIZZ_TAKEN]
    average = 0
    if numberofbooks == numberOfquizz:
        for book_elements in books:
            if books[book_elements]["level"] == context.user_data[USER.READING_LEVEL]:
                average = average + books[book_elements]["percentage"]
        level_mark = average/numberOfquizz
        if level_mark >= 80 and context.user_data[USER.READING_LEVEL] < 4:
            context.user_data[USER.READING_LEVEL] += 1
            return level_up(update, context)
        

def level_up(update, context):
    newlevel = context.user_data[USER.READING_LEVEL]
    if newlevel == 2:
        asebot.bot.handlers.assign_reading_level_2(update, context)
    elif newlevel == 3:
        asebot.bot.handlers.assign_reading_level_3(update, context)
    else:
        asebot.bot.handlers.assign_reading_level_4(update, context)

    