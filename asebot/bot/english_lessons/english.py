from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.components.switch import Switch
from asebot.bot.english_lessons.lessons import Lessons
from asebot.bot.home.main_menu import MainMenu

mainmenu = MainMenu()
lessons = Lessons()

class English:
    grade = None
    unit_chosen = 1

    def english_lessons(self, update,context):
        
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

    # def confirm_grade(self, update, context):
    #     global grade
    #     grade = update.message.text
    #     switcher = Switch()
    #     selected_grade = switcher.grade(grade)
    #     grade = selected_grade
        
    #     if selected_grade >= 1 and selected_grade <= 8 and not None:
    #         update.message.reply_text(
    #             "Are you sure you want to select this grade?",
    #             reply_markup=ReplyKeyboardMarkup([
    #                 ["🟢 Yes", "🔴 No"]
    #             ], one_time_keyboard=False, resize_keyboard=True)
    #         )
    #         return STATE.COMFIRM_GRADE
    #     else:
    #         return self.invalid_selection(update, context, "grade")

    # def reconfirm_grade(self, update, context):
    #     global grade
    #     update.message.reply_text(f"You have selected grade {grade}")
    #     update.message.reply_text("Select [Yes] to confirm or [No] to go back")
    #     update.message.reply_text(
    #         "Are you sure you want to select this grade?",
    #         reply_markup=ReplyKeyboardMarkup([
    #             ["🟢 Yes", "🔴 No"]
    #         ], one_time_keyboard=False, resize_keyboard=True)
    #     )
    #     return STATE.RE_COMFIRM_GRADE

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
            context.user_data[USER.TEMP_UNIT] = None
            update.message.reply_text(
                "You entered an invalid unit"
            )
            update.message.reply_text(
                "Select the unit you are doing at school",
                reply_markup=ReplyKeyboardMarkup([
                    ["1","2"],
                    ["3", "4"],
                    ["5","6"],
                    [ "7", "8"],
                    ["9", "10"],
                    ["⏭ More Units"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.UNIT

    def unit(self, update, context):
        global unit_chosen 
        unit_chosen = 1
        context.user_data[USER.FINAL_UNIT] = None
        context.user_data[USER.TEMP_UNIT] = None

        update.message.reply_text(
            "Select the unit you are doing at school",
            reply_markup=ReplyKeyboardMarkup([
                ["1","2"],
                ["3", "4"],
                ["5","6"],
                [ "7", "8"],
                ["9", "10"],
                ["⏭ More Units"]
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.UNIT

    def unit_decision(self, update, context):
        global unit_chosen
        if update.message.text == "⏭ More Units":
            if unit_chosen == 1:
                return self.first_10_units(update, context)
            elif unit_chosen == 2:
                return self.second_10_units(update, context)
        else:
            return self.assign_unit(update, context)

    def first_10_units(self, update, context):
        global unit_chosen
        unit_chosen += 1

        context.user_data[USER.TEMP_UNIT] = None
        update.message.reply_text(
            "Select the unit you are doing at school",
            reply_markup=ReplyKeyboardMarkup([
                ["11","12"],
                ["13", "14"],
                ["15","16"],
                ["17", "18"],
                ["19", "20"],
                ["⏭ More Units"]
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.UNIT

    def second_10_units(self, update, context):
        global unit_chosen
        unit_chosen += 1

        update.message.reply_text(
            "Select the unit you are doing at school",
            reply_markup=ReplyKeyboardMarkup([
                ["21","22"],
                ["23", "24"],
                ["25","26"],
                [ "27", "28"],
                ["29", "30"],
                ["↩️ Back (1-10)"]
            ], one_time_keyboard=False, resize_keyboard=True)
        )
        return STATE.UNIT

    def more_units(self, update, context):
        pass

    def unit_response(self, update, context):
        
        # if context.user_data[USER.FINAL_UNIT] is None:
        #     return self.unit_choice(update, context)
        # else:
            # context.user_data[USER.UNIT] = context.user_data[USER.FINAL_UNIT]
            # context.user_data[USER.FINAL_UNIT] = None
            # context.user_data[USER.TEMP_UNIT] = None
            update.message.reply_text(f"You have selected unit {context.user_data[USER.UNIT]}")
            update.message.reply_text("You can choose to skip this unit by taking a unit test")
            update.message.reply_text(
                "Select [Skip] to write the test, or [Next] to begin your lessons",
                reply_markup=ReplyKeyboardMarkup([
                    ["🏠 Return To Main Menu"],
                    ["⏭ Skip","▶ Next"]
                    ], one_time_keyboard=False, resize_keyboard=True)
                )
            # if context.user_data[USER.UNIT] not in context.user_data[USER.UNIT_CHOSEN]:
            #     context.user_data[USER.UNIT_CHOSEN].append(context.user_data[USER.UNIT])
            
            return STATE.LESSON
        

    def proceed(self, update, context):
        return lessons.open_lessons(update, context)

    def assign_unit(self, update, context):
        switcher = Switch()
        unit = switcher.unit(update.message.text)
        if unit >= 1 and unit <= 30 and not None:
            """ The grade and unit filters for getting the correct lessons to be done here """
            context.user_data[USER.UNIT] = unit
            return self.unit_response(update,context)
        else:
            return self.invalid_selection(update, context, "unit")
        
    
    # def unit_choice(self, update, context):
    #     switcher = Switch()
        #run_time_unit = switcher.unit(update.message.text)
        # if run_time_unit in context.user_data[USER.UNIT_CHOSEN]:
        #     context.user_data[USER.FINAL_UNIT] = run_time_unit
        #     return self.unit_response(update, context)
        
        # update.message.reply_text(
        #     "Select [Yes] to confirm or [No] to go back",
        #     reply_markup=ReplyKeyboardMarkup([
        #         ["🟢 Yes","🔴 No"],
        #     ], one_time_keyboard=False, resize_keyboard=True)
        # )
        
        #if context.user_data[USER.TEMP_UNIT] is None:
        #unit = switcher.unit(update.message.text)
        # update.message.reply_text(f"Are you sure you want to select unit {unit}?")
        #context.user_data[USER.TEMP_UNIT] = self.assign_unit(update,context,unit)
        # else:
        #     unit = context.user_data[USER.TEMP_UNIT]
        #     update.message.reply_text(f"Are you sure you want to select unit {unit}?")
        #     context.user_data[USER.FINAL_UNIT] = self.assign_unit(update,context,unit)
        
        #return STATE.UNIT_CHOICE
        
    def assign_grade(self, update, context):
        global grade
        grade = update.message.text
        switcher = Switch()
        selected_grade = switcher.grade(grade)
        grade = selected_grade

        if grade >= 1 and grade <= 8 and not None:
            # context.user_data[USER.FINAL_UNIT] = None
            # context.user_data[USER.TEMP_UNIT] = None
            # context.user_data[USER.UNIT_MARKS] = None
            # context.user_data[USER.UNIT_CHOSEN] = []
            context.user_data[USER.GRADE] = grade
            context.user_data[USER.LESSON] = 1
            return self.unit(update, context)
        else:
            return self.invalid_selection(update, context, "grade")