import sqlite3
import os


def setup_database():
    if os.path.exists('students_db.sqlite'):
        os.remove('students_db.sqlite')

    conn = sqlite3.connect('students_db.sqlite')
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # Создание таблиц
    cur.execute('''CREATE TABLE уровень_обучения (
        id_уровня INTEGER PRIMARY KEY,
        название TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE направления (
        id_направления INTEGER PRIMARY KEY,
        название TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE типы_обучения (
        id_типа INTEGER PRIMARY KEY,
        название TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE студенты (
        id_студента INTEGER PRIMARY KEY,
        id_уровня INTEGER,
        id_направления INTEGER,
        id_типа_обучения INTEGER,
        фамилия TEXT,
        имя TEXT,
        отчество TEXT,
        средний_балл INTEGER,
        FOREIGN KEY(id_уровня) REFERENCES уровень_обучения(id_уровня),
        FOREIGN KEY(id_направления) REFERENCES направления(id_направления),
        FOREIGN KEY(id_типа_обучения) REFERENCES типы_обучения(id_типа)
    )''')

    # Заполнение справочников
    levels_data = [
        (1, 'Бакалавр'),
        (2, 'Магистр'),
        (3, 'Специалист')
    ]
    cur.executemany("INSERT INTO уровень_обучения VALUES (?, ?)", levels_data)

    majors_data = [
        (1, 'Прикладная информатика'),
        (2, 'Экономика'),
        (3, 'Менеджмент'),
        (4, 'Дизайн')
    ]
    cur.executemany("INSERT INTO направления VALUES (?, ?)", majors_data)

    types_data = [
        (1, 'Очная'),
        (2, 'Заочная'),
        (3, 'Вечерняя')
    ]
    cur.executemany("INSERT INTO типы_обучения VALUES (?, ?)", types_data)

    # Заполнение студентов
    students_data = [
        # Прикладная информатика
        (1, 1, 1, 1, 'Иванов', 'Алексей', 'Игоревич', 5),
        (2, 1, 1, 1, 'Иванов', 'Дмитрий', 'Сергеевич', 5),
        (3, 1, 1, 1, 'Сидоров', 'Анна', 'Петровна', 5),
        (4, 1, 1, 1, 'Кузнецов', 'Олег', 'Викторович', 4),
        (5, 1, 1, 1, 'Морозов', 'Илья', 'Александрович', 5),
        (6, 1, 1, 1, 'Волков', 'Сергей', 'Дмитриевич', 5),

        # Другие направления или формы
        (7, 2, 1, 2, 'Петров', 'Иван', 'Иванович', 3),
        (8, 1, 2, 1, 'Смирнова', 'Елена', 'Олеговна', 4),
        (9, 1, 3, 3, 'Орлов', 'Максим', 'Андреевич', 3),

        # Однофамильцы (Ивановы)
        (10, 1, 2, 1, 'Иванов', 'Мария', 'Алексеевна', 4),

        # Полные тезки
        (11, 1, 4, 1, 'Тестов', 'Тест', 'Тестович', 4),
        (12, 1, 4, 1, 'Тестов', 'Тест', 'Тестович', 3)
    ]
    cur.executemany("INSERT INTO студенты VALUES (?, ?, ?, ?, ?, ?, ?, ?)", students_data)

    conn.commit()
    return conn, cur


def run_queries(cur):

    print(f"\nЗАПРОС 1: Количество всех студентов")
    cur.execute("SELECT COUNT(*) FROM студенты")
    print(f"Всего студентов: {cur.fetchone()[0]}\n")

    print(f"\nЗАПРОС 2: Количество студентов по направлениям")
    cur.execute('''
        SELECT n.название, COUNT(s.id_студента) 
        FROM студенты s 
        JOIN направления n ON s.id_направления = n.id_направления 
        GROUP BY n.id_направления
    ''')
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} чел.")

    print(f"\nЗАПРОС 3: Количество студентов по формам обучения")
    cur.execute('''
        SELECT t.название, COUNT(s.id_студента) 
        FROM студенты s 
        JOIN типы_обучения t ON s.id_типа_обучения = t.id_типа 
        GROUP BY t.id_типа
    ''')
    for row in cur.fetchall():
        print(f"{row[0]}: {row[1]} чел.")
    print(f"\nЗАПРОС 4: Макс, Мин, Средний баллы по направлениям")
    cur.execute('''
        SELECT n.название, MAX(s.средний_балл), MIN(s.средний_балл), AVG(s.средний_балл)
        FROM студенты s
        JOIN направления n ON s.id_направления = n.id_направления
        GROUP BY n.id_направления
    ''')
    for row in cur.fetchall():
        print(f"{row[0]}: Max={row[1]}, Min={row[2]}, Avg={row[3]:.2f}")
    print(f"\nЗАПРОС 5: Средний балл по направлениям, уровням и формам")
    cur.execute('''
        SELECT n.название, u.название, t.название, AVG(s.средний_балл)
        FROM студенты s
        JOIN направления n ON s.id_направления = n.id_направления
        JOIN уровень_обучения u ON s.id_уровня = u.id_уровня
        JOIN типы_обучения t ON s.id_типа_обучения = t.id_типа
        GROUP BY n.id_направления, u.id_уровня, t.id_типа
    ''')
    for row in cur.fetchall():
        print(f"{row[0]} ({row[1]}, {row[2]}): Средний балл = {row[3]:.2f}")

    print(f"\nЗАПРОС 6: Стипендия (5 студентов, Прикладная информатика, Очная)")
    cur.execute('''
        SELECT s.фамилия, s.имя, s.средний_балл
        FROM студенты s
        JOIN направления n ON s.id_направления = n.id_направления
        JOIN типы_обучения t ON s.id_типа_обучения = t.id_типа
        WHERE n.название = 'Прикладная информатика' AND t.название = 'Очная'
        ORDER BY s.средний_балл DESC
        LIMIT 5
    ''')
    for i, row in enumerate(cur.fetchall(), 1):
        print(f"{i}. {row[0]} {row[1]} - {row[2]} баллов")

    print(f"\nЗАПРОС 7: Сколько однофамильцев в базе?")
    cur.execute('''
        SELECT фамилия, COUNT(*) 
        FROM студенты 
        GROUP BY фамилия 
        HAVING COUNT(*) > 1
    ''')
    res = cur.fetchall()
    if res:
        for row in res:
            print(f"Фамилия '{row[0]}' встречается {row[1]} раз(а)")
    else:
        print("Однофамильцев нет")

    print(f"\nЗАПРОС 8: Есть ли полные тезки?")
    cur.execute('''
        SELECT фамилия, имя, отчество, COUNT(*) 
        FROM студенты 
        GROUP BY фамилия, имя, отчество 
        HAVING COUNT(*) > 1
    ''')
    res = cur.fetchall()
    if res:
        for row in res:
            print(f"Найдены тезки: {row[0]} {row[1]} {row[2]} (совпадений: {row[3]})")
    else:
        print("Полных тезок нет")


if __name__ == "__main__":
    print("Создание базы данных и заполнение данными...\n")
    conn, cur = setup_database()
    print("База данных создана успешно!\n")
    run_queries(cur)
    conn.close()
    print("Работа завершена. База данных 'students_db.sqlite' создана.")