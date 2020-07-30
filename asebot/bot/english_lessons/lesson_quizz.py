from asebot.constants import STATE, USER
from asebot.bot.home.main_menu import MainMenu
from asebot.bot.rewards.level_up import LevelUp

mainmenu = MainMenu()
level_up = LevelUp()

class LessonQuizz:
    def start_quizz(self, update, context):
        update.message.reply_text("start quizz")
        return self.view_quizz_question(update, context)

    def view_quizz_question(self, update, context):
        update.message.reply_text("question")
        return STATE.LESSON_QUIZZ

    def check_quizz_answer(self, update, context):
        update.message.reply_text("answer")
        return self.next_quizz_question(update, context)

    def next_quizz_question(self, update, context):
        update.message.reply_text("next")
        return self.view_quizz_question(update, context)

    def quizz_finished(self, update, context):
        update.message.reply_text("finished")
        level_up.next_lesson(update, context)
        return mainmenu.main_menu