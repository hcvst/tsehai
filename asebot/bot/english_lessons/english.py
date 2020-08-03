from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.components.switch import Switch
from asebot.bot.english_lessons.lessons import Lessons

lessons = Lessons()

class English:
    grade = None
    def english_lessons(self, update,context):
        if not context.user_data.get(USER.GRADE):
            update.message.reply_text(
                f"Great!, What grade are you in?",
                reply_markup=ReplyKeyboardMarkup([
                    ["1️⃣","2️⃣"],
                    ["3️⃣", "4️⃣"],
                    ["5️⃣","6️⃣"],
                    [ "7️⃣", "8️⃣"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.GRADE
        # elif not context.user_data.get(USER.GRADE) and not context.user_data.get(USER.UNIT):
        #     pass
        else:
            return self.unit(update, context)

    def confirm_grade(self, update, context):
        global grade
        grade = update.message.text
        switcher = Switch()
        selected_grade = switcher.grade(grade)
        grade = selected_grade
        
        if selected_grade >= 1 and selected_grade <= 8 and not None:
            update.message.reply_text(
                "Are you sure you want to select this grade?",
                reply_markup=ReplyKeyboardMarkup([
                    ["🟢 Yes", "🔴 No"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.COMFIRM_GRADE
        else:
            return self.invalid_selection(update, context, "grade")

    def reconfirm_grade(self, update, context):
        global grade
        update.message.reply_text(f"You have selected grade {grade}")
        update.message.reply_text("Select [Yes] to confirm or [No] to go back")
        update.message.reply_text(
            "Are you sure you want to select this grade?",
            reply_markup=ReplyKeyboardMarkup([
                ["🟢 Yes", "🔴 No"]
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.RE_COMFIRM_GRADE

    def invalid_selection(self, update, context, *args):
        selection = args[0]
        
        if selection == "grade":
            update.message.reply_text(
                "You entered an invalid grade"
            )
            update.message.reply_text(
                "Please select a valid grade",
                reply_markup=ReplyKeyboardMarkup([
                    ["1️⃣","2️⃣"],
                    ["3️⃣", "4️⃣"],
                    ["5️⃣","6️⃣"],
                    [ "7️⃣", "8️⃣"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.GRADE
        elif selection == "unit":
            update.message.reply_text(
                "You entered an invalid unit"
            )
            update.message.reply_text(
                "Select the unit you are doing at school",
                reply_markup=ReplyKeyboardMarkup([
                    ["1️⃣","2️⃣"],
                    ["3️⃣", "4️⃣"],
                    ["5️⃣","6️⃣"],
                    [ "7️⃣", "8️⃣"],
                    ["9️⃣", "🔟"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.UNIT

    def unit(self, update, context):
        update.message.reply_text(
            "Select the unit you are doing at school",
            reply_markup=ReplyKeyboardMarkup([
                ["1️⃣","2️⃣"],
                ["3️⃣", "4️⃣"],
                ["5️⃣","6️⃣"],
                [ "7️⃣", "8️⃣"],
                ["9️⃣", "🔟"]
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.UNIT

    def unit_response(self, update, context, *args):
        unit = args[0]

        update.message.reply_text(f"You have selected unit {unit}")
        update.message.reply_text("You can choose to skip this unit by taking a unit test")
        update.message.reply_text(
            "Select [Skip] to write the test, or [Proceed] to begin your lessons",
            reply_markup=ReplyKeyboardMarkup([
                ["⏭ Skip","▶ Proceed"],
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.LESSON

    def proceed(self, update, context):
        return lessons.open_lessons(update, context)

    def assign_unit(self, update, context):
        print("Assign unit")
        switcher = Switch()
        unit = switcher.unit(update.message.text)

        if unit >= 1 and unit <= 10 and not None:
            """ The grade and unit filters for getting the correct lessons to be done here """
            context.user_data[USER.UNIT] = unit
            return self.unit_response(update, context, unit)
        else:
            return self.invalid_selection(update, context, "unit")
    
    def assign_grade(self, update, context):
        global grade
        
        if grade >= 1 and grade <= 8 and not None:
            context.user_data[USER.GRADE] = grade
            context.user_data[USER.LESSON] = 1
            return self.unit(update, context)
        else:
            return self.invalid_selection(update, context, "grade")