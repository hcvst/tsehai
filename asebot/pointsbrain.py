import math
from asebot.constants import USER

def validate_quizz_taken(context):
    booktitle = context.user_data["book"]["title"]
    userlevel = context.user_data.get(USER.READING_LEVEL)
    if context.user_data.get(USER.QUIZZ_TAKEN[int(context.user_data["books"][context.user_data["book_idx"]]["id"])]) is not None:
        if not context.user_data[USER.QUIZZ_TAKEN[int(context.user_data["books"][context.user_data["book_idx"]]["id"])]]:
            context.user_data[USER.QUIZZ_TAKEN[int(context.user_data["books"][context.user_data["book_idx"]]["id"])]] = {
                "taken": "true",
                "level": f"{userlevel}",
                "title": f"{booktitle}"
                }
        else:
            context.user_data[USER.QUIZZ_TAKEN[int(context.user_data["books"][context.user_data["book_idx"]]["id"])]] = {
                "taken": "false",
                "level": f"{userlevel}",
                "title": f"{booktitle}"
                }
    else:
        context.user_data[USER.QUIZZ_TAKEN[int(context.user_data["books"][context.user_data["book_idx"]]["id"])]] = {
            "taken": "true",
            "level": f"{userlevel}",
            "title": f"{booktitle}"
            }
        
    print(context.user_data)


def points_medals_brain(context):
    numberofquestions = len(context.user_data["book"]["quizz"]["questions"])
    incorrectanswers = context.user_data["quizz_mistakes"]
    correctanswers = numberofquestions - incorrectanswers
    percentage=round(correctanswers/numberofquestions * 100)
    validatemedal = context.user_data[USER.QUIZZ_TAKEN[int(context.user_data["books"][context.user_data["book_idx"]]["id"])]]
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
    