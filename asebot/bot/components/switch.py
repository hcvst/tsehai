class Switch:

    def grade(self, l):
        switcher={
            "1️⃣":1,
            "2️⃣":2,
            "3️⃣":3,
            "4️⃣":4,
            "5️⃣":5,
            "6️⃣":6,
            "7️⃣":7,
            "8️⃣":8
        }
        return switcher.get(l, 9)
    
    def unit(self, l):
        switcher={
            "1️⃣":1,
            "2️⃣":2,
            "3️⃣":3,
            "4️⃣":4,
            "5️⃣":5,
            "6️⃣":6,
            "7️⃣":7,
            "8️⃣":8,
            "9️⃣":9,
            "🔟":10
        }
        return switcher.get(l, 11)

    def level(self, l):
       switcher={
           "Level 1️⃣":1,
           "Level 2️⃣":2,
           "Level 3️⃣":3,
           "Level 4️⃣":4
       }
       return switcher.get(l, 5)
   
    def confirm(self, l):
       switcher={
           "🔴 No":0,
           "🟢 Yes":1
       }
       return switcher.get(l, 5)
    
    def num_to_words(self, l):
        switcher={
            1:"one",
            2:"two",
            3:"three",
            4:"four",
            5:"five",
            6:"six",
            7:"seven",
            8:"eight",
            9:"nine",
            10:"ten"
        }
        return switcher.get(l, 11)