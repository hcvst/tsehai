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