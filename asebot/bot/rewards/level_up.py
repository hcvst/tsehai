
class LevelUp:
    def next_unit(self, update, context):
        print("level up")
        update.message.reply_text("Next unit")
    
    def next_lesson(self, update, context):
        print("Next lesson")