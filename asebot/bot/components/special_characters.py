import re

class SpecialCharacters :
    global regex
    regex = re.compile('[@_!#$%^&()<>/\|}{~]')

    def checkSpecialCharacter(self, text):
        global regex
        if regex.search(text) != None:
            specialChar = regex.search(text).group(0)
            text = text.replace(specialChar, f'\{specialChar}')
        return text
