import sqlite3
from database import init_db, get_db_connection

def seed_data():
    init_db()
    conn = get_db_connection()
    c = conn.cursor()
    
    # Check if words exist
    count = c.execute('SELECT count(*) FROM words').fetchone()[0]
    if count > 0:
        print("Database already populated.")
        conn.close()
        return

    # Sample data: 10 words per level for demonstration
    # In a real scenario, this would load from a massive JSON/CSV
    
    # Level 1: Basic
    level_1 = [
        ("time", "وقت"), ("year", "سنة"), ("people", "ناس"), ("way", "طريق"), ("day", "يوم"),
        ("man", "رجل"), ("thing", "شيء"), ("woman", "امرأة"), ("life", "حياة"), ("child", "طفل")
    ]
    
    # Level 2: Elementary
    level_2 = [
        ("ask", "يسأل"), ("work", "عمل"), ("seem", "يبدو"), ("feel", "يشعر"), ("try", "يحاول"),
        ("leave", "يغادر"), ("call", "ينادي"), ("family", "عائلة"), ("school", "مدرسة"), ("plant", "نبات")
    ]

    # Level 3: Intermediate
    level_3 = [
        ("begin", "يبدأ"), ("help", "يساعد"), ("talk", "يتحدث"), ("turn", "يدور"), ("start", "يبدأ"),
        ("might", "قد"), ("show", "يعرض"), ("hear", "يسمع"), ("play", "يلعب"), ("run", "يجري")
    ]

    # Level 4: Upper Intermediate
    level_4 = [
        ("move", "يتحرك"), ("like", "يحب"), ("live", "يعيش"), ("believe", "يصدق"), ("hold", "يمسك"),
        ("bring", "يحضر"), ("happen", "يحدث"), ("write", "يكتب"), ("provide", "يزود"), ("sit", "يجلس")
    ]
    
    # Level 5: Advanced
    level_5 = [
        ("stand", "يقف"), ("lose", "يخسر"), ("pay", "يدفع"), ("meet", "يقابل"), ("include", "يشمل"),
        ("continue", "يستمر"), ("set", "يضع"), ("learn", "يتعلم"), ("change", "يغير"), ("leader", "قائد")
    ]
    
    # Level 6: Proficiency
    level_6 = [
        ("watch", "يشاهد"), ("follow", "يتبع"), ("stop", "يتوقف"), ("create", "ينشئ"), ("speak", "يتحدث"),
        ("read", "يقرأ"), ("allow", "يسمح"), ("add", "يضيف"), ("spend", "ينفق"), ("grow", "ينمو")
    ]

    all_levels = [level_1, level_2, level_3, level_4, level_5, level_6]

    print("Seeding data...")
    for idx, words in enumerate(all_levels):
        level_num = idx + 1
        for en, ar in words:
            c.execute('INSERT INTO words (level, english_word, arabic_word) VALUES (?, ?, ?)', (level_num, en, ar))
    
    conn.commit()
    print(f"Inserted {60} words across 6 levels.")
    conn.close()

if __name__ == "__main__":
    seed_data()
