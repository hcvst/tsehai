from asebot.constants import STATE, USER
from asebot.bot.home.main_menu import MainMenu
from asebot.bot.rewards.level_up import LevelUp

mainmenu = MainMenu()
level_up = LevelUp()

class UnitTest:
    def start_test(self, update, context):
        update.message.reply_text("start test")
        return self.view_test_question(update, context)

    def view_test_question(self, update, context):
        update.message.reply_text("question")
        return STATE.UNIT_TEST

    def check_test_answer(self, update, context):
        update.message.reply_text("answer")
        return self.next_test_question(update, context)

    def next_test_question(self, update, context):
        update.message.reply_text("next")
        return self.view_test_question(update, context)

    def test_finished(self, update, context):
        update.message.reply_text("finished")
        level_up.next_unit(update, context)
        return mainmenu.main_menu

    def view_test_results(self, update, context):
        update.message.reply_text("results")
        return mainmenu.main_menu