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
        print(l)
        switcher={
            "1":1,
            "2":2,
            "3":3,
            "4":4,
            "5":5,
            "6":6,
            "7":7,
            "8":8,
            "9":9,
            "10":10,
            "11":11,
            "12":12,
            "13":13,
            "14":14,
            "15":15,
            "16":16,
            "17":17,
            "18":18,
            "19":19,
            "20":20,
            "21":21,
            "22":22,
            "23":23,
            "24":24,
            "25":25,
            "26":26,
            "27":27,
            "28":28,
            "29":29,
            "30":30
        }
        print(type(switcher.get(l)))
        return switcher.get(l, 31)

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