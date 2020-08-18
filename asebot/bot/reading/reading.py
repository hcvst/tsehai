from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from asebot.constants import STATE, USER
from asebot.bot.components.switch import Switch
import asebot.bot.handlers
import asebot.api


class Reading:
    def reading_level(self, update, context):
        context.user_data["levelSelectionPictures"] = asebot.api.load_level_Selection()

        if not context.user_data.get(USER.READING_LEVEL):
            # update.message.reply_text("Choose your reading level💃")
            # update.message.reply_text("Wow!")
            # update.message.reply_text("I love reading too!")
            update.message.reply_text("Look at the pictures and choose your reading level💃")

            update.message.reply_photo(
                photo=asebot.config.API_SERVER+context.user_data["levelSelectionPictures"][0]['Image'][0]['url'],
                # caption=books[book_idx]["title"],
                parse_mode='Markdown',
                reply_markup=ReplyKeyboardMarkup([
                     ["Level 1️⃣","Level 2️⃣"],
                    ["Level 3️⃣", "Level 4️⃣"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.READINGLEVEL  
        else:
            update.message.reply_text(f"🏛️ The Library")
            context.user_data["book_idx"] = 0

            if len(context.user_data["books"]) == 0:
                update.message.reply_text(
                    "There are no books available at the moment. "
                    "Please try again later.",
                    reply_markup=ReplyKeyboardMarkup([
                        ["🏅 See my medals"],
                        [ "🏛️ I want to read", "📔 I want English lessons"]
                        ], one_time_keyboard=False, resize_keyboard=True)
                    )
                return STATE.STARTED
            else:
                update.message.reply_text(
                    "Let's find a book for you."
                )
                return asebot.bot.handlers.view_book(update, context)
            # return view_book(update, context)
            
    def invalid_selection(self, update, context, *args):
        selection = args[0]
        
        if selection == "level":
            update.message.reply_text(
                "You entered an invalid level"
            )
            update.message.reply_text(
                "Please select a valid level",
                eply_markup=ReplyKeyboardMarkup([
                     ["Level 1️⃣","Level 2️⃣"],
                    ["Level 3️⃣", "Level 4️⃣"]
                ], one_time_keyboard=False, resize_keyboard=True)
            )
            return STATE.READINGLEVEL
        return STATE.READINGLEVEL

    def assign_reading_level(self, update, context):

        switcher = Switch()
        level = switcher.level(update.message.text)
        
        if level >= 1 and level <= 4 and not None:
            context.user_data[USER.READING_LEVEL] = level
            return self.first_confirm_level(update, context)
        else:
            return self.invalid_selection(update, context, "level")
        # return self.reading_level(update, context)
    
    def first_confirm_level(self, update, context):
        update.message.reply_text(
            f"Are you sure you want to select Reading Level {context.user_data[USER.READING_LEVEL]}",
            
                reply_markup=ReplyKeyboardMarkup([
                    ["🟢 Yes","🔴 No"]
                ], one_time_keyboard=False, resize_keyboard=True)             
            )
        return STATE.FIRSTCONFIRMREADINGLEVEL
        
    def second_confirm_level(self, update, context):
        update.message.reply_text(
            f"You have selected Reading Level {context.user_data[USER.READING_LEVEL]} \n Select [yes] to confirm or [no] to go back",
            
                reply_markup=ReplyKeyboardMarkup([
                    ["🟢 Yes","🔴 No"]
                ], one_time_keyboard=False, resize_keyboard=True)     
            )
        return STATE.SECONDCONFIRMREADINGLEVEL
        
    def confirm(self, update, context):
        switcher = Switch()
        response = switcher.confirm(update.message.text)
        
        if response == 1:
            return self.second_confirm_level(update, context)
        else:
            return self.no(update, context)
            
        
    
    def yes_proceed(self, update, context):
        context.user_data[USER.QUIZZ_TAKEN] = None
        context.user_data["books"] = asebot.api.load_books_on_level(context.user_data[USER.READING_LEVEL])
        update.message.reply_text(f"Level {context.user_data[USER.READING_LEVEL]} assigned")
        return self.reading_level(update, context)
    
    def no(self, update, context):
        context.user_data[USER.READING_LEVEL] = None
        return self.reading_level(update, context)