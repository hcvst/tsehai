class Switch:

    def grade(self, value):
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
        
        return switcher.get(value, 9)
    
    def unit(self, value):
        out_of_range = 31
        try:
            return int(value)
        except:
            return out_of_range
        
    def level(self, value):
       switcher={
           "Level 1️⃣":1,
           "Level 2️⃣":2,
           "Level 3️⃣":3,
           "Level 4️⃣":4
       }
       return switcher.get(value, 5)
       
   
    def confirm(self, value):
       switcher={
           "🔴 No":0,
           "🟢 Yes":1
       }
       return switcher.get(value, 0)