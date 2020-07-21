from asebot.connect_api import ConnectAPI

api = ConnectAPI()

def leaderboard(update):
    user_in_top10 = False

    chatId = update.message.chat
    
    top10 = api.get_top10()
    top10_List = top10['points']

    for users in top10_List:
        if users['chatId'] == f"{chatId.id}":
            user_in_top10 = True
    
    if not user_in_top10:
        userPoints = api.getPoints(chatId.id)['points']
        top10_List += userPoints
    
    return top10_List