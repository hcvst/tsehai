import math

def points_medals_brain(context):
    numberofquestions = len(context.user_data["book"]["quizz"]["questions"])
    incorrectanswers = context.user_data["quizz_mistakes"]
    correctanswers = numberofquestions - incorrectanswers
    percentage=round(correctanswers/numberofquestions * 100)
    print(percentage)
    if percentage == 100:
        medalcalculation = {
            "medal": "gold",
            "percentage": percentage
            }
    elif percentage >= 90 or percentage <= 80:
        medalcalculation = {
            "medal": "silver",
            "percentage": percentage
            }
    elif percentage >= 79 or percentage <= 70:
        medalcalculation = {
            "medal": "bronze",
            "percentage": percentage
            }
    else:
        medalcalculation = {
            "percentage": percentage
            }
    return medalcalculation