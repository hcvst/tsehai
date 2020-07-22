from asebot.connect_api import ConnectAPI

api = ConnectAPI()

def alocate_points(update, points):
    chatId = update.message.chat
    user = update.message.from_user
    data = user_found(chatId.id)
    
    if not data:
        api.createPoints(chatId.id , user.first_name, points)
    else:
        points += data['totalPoints']
        id = data['id']
        api.updatePoints(id, points)

def user_found(chatId):
    userPoints = api.getPoints(chatId)
    
    if len(userPoints['points']) == 0:
        return None
    else:
        return userPoints['points'][0]