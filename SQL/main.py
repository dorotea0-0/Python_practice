import sqlite3
import os

DB_FILE = "students.db"


def pretty_print(cursor):
    #Выводит результат запроса в виде выровненной таблицы.
    rows = cursor.fetchall()
    if not rows:
        print("  (Нет данных)")
        return

    headers = [desc[0] for desc in cursor.description]
    # Вычисляем ширину каждого столбца
    col_widths = [
        max(len(str(h)), max((len(str(row[i])) for row in rows), default=0))
        for i, h in enumerate(headers)
    ]

    # Форматируем заголовок и разделитель
    header_line = " | ".join(str(h).ljust(w) for h, w in zip(headers, col_widths))
    sep_line = "-+-".join("-" * w for w in col_widths)

    print(header_line)
    print(sep_line)
    for row in rows:
        print(" ".join(str(val).ljust(w) for val, w in zip(row, col_widths)))


def run_demo():
    # Удаляем старую БД для чистого запуска
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)

    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA journal_mode=WAL;")
    cur = conn.cursor()

    #Создание таблиц
    print("🗃  Создание таблиц...")
    cur.executescript("""
    CREATE TABLE IF NOT EXISTS `уровни` (`id_ровня` INTEGER PRIMARY KEY NOT NULL UNIQUE, `название` TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS `направления` (`id_направления` INTEGER PRIMARY KEY NOT NULL UNIQUE, `название` TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS `типы` (`id_типа` INTEGER PRIMARY KEY NOT NULL UNIQUE, `название` TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS `студенты` (`id_студента` INTEGER PRIMARY KEY NOT NULL UNIQUE, `id_уровня` INTEGER NOT NULL, `id_направления` INTEGER NOT NULL, `id_типа` INTEGER NOT NULL, `фамилия` TEXT NOT NULL, `имя` TEXT NOT NULL, `средний_балл` REAL NOT NULL, FOREIGN KEY(`id_уровня`) REFERENCES `уровни`(`id_ровня`), FOREIGN KEY(`id_направления`) REFERENCES `направления`(`id_направления`), FOREIGN KEY(`id_типа`) REFERENCES `типы`(`id_типа`));
    """)

    #Заполнение демо-данными
    print("Вставка тестовых данных...")
    levels = [(1, 'Бакалавриат'), (2, 'Магистратура'), (3, 'Аспирантура')]
    directions = [(1, 'Информатика'), (2, 'Математика'), (3, 'Физика')]
    types = [(1, 'Бюджет'), (2, 'Контракт'), (3, 'Платное обучение')]
    students = [
        (1, 1, 1, 1, 'Иванов', 'Алексей', 4.8),
        (2, 1, 1, 2, 'Петрова', 'Мария', 4.2),
        (3, 2, 1, 1, 'Сидоров', 'Дмитрий', 3.5),
        (4, 1, 2, 3, 'Кузнецова', 'Анна', 4.6),
        (5, 2, 2, 1, 'Смирнов', 'Игорь', 3.2),
        (6, 3, 3, 2, 'Попов', 'Сергей', 4.9),
        (7, 1, 3, 1, 'Васильева', 'Елена', 3.8),
        (8, 2, 1, 2, 'Новиков', 'Павел', 4.5),
        (9, 1, 2, 3, 'Морозова', 'Ольга', 4.1),
        (10, 3, 3, 1, 'Лебедев', 'Артем', 3.0),
        (11, 1, 1, 1, 'Козлов', 'Никита', 4.7),
        (12, 2, 3, 2, 'Соколова', 'Татьяна', 3.9)
    ]

    cur.executemany("INSERT OR IGNORE INTO уровни VALUES (?, ?)", levels)
    cur.executemany("INSERT OR IGNORE INTO направления VALUES (?, ?)", directions)
    cur.executemany("INSERT OR IGNORE INTO типы VALUES (?, ?)", types)
    cur.executemany("INSERT OR IGNORE INTO студенты VALUES (?, ?, ?, ?, ?, ?, ?)", students)
    conn.commit()

    #Выполнение заданий
    queries = {
        "ЗАДАНИЕ 1: CASE (Категоризация по успеваемости)": """
            SELECT фамилия, имя, средний_балл,
            CASE WHEN средний_балл >= 4.5 THEN 'Отличник'
                 WHEN средний_балл >= 4.0 THEN 'Хорошист'
                 WHEN средний_балл >= 3.0 THEN 'Троечник'
                 ELSE 'Неудовлетворительно' END AS категория
            FROM студенты ORDER BY средний_балл DESC;""",

        "ЗАДАНИЕ 1: CASE (Статус финансирования)": """
            SELECT s.фамилия, s.имя, t.название AS тип_обучения,
            CASE WHEN LOWER(t.название) LIKE '%бюджет%' THEN 'Гос. финансирование'
                 WHEN LOWER(t.название) LIKE '%контракт%' OR LOWER(t.название) LIKE '%платн%' THEN 'Самофинансирование'
                 ELSE 'Не определено' END AS статус
            FROM студенты s JOIN типы t ON s.id_типа = t.id_типа;""",

        "ЗАДАНИЕ 2: Подзапрос (Студенты выше общего среднего)": """
            SELECT фамилия, имя, средний_балл FROM студенты
            WHERE средний_балл > (SELECT AVG(средний_балл) FROM студенты);""",

        "ЗАДАНИЕ 2: Подзапрос (Самое популярное направление)": """
            SELECT фамилия, имя, id_направления FROM студенты
            WHERE id_направления = (
                SELECT id_направления FROM студенты GROUP BY id_направления ORDER BY COUNT(*) DESC LIMIT 1
            );""",

        "ЗАДАНИЕ 3: CTE (Направления со средним баллом > 4.0)": """
            WITH dir_stats AS (
                SELECT id_направления, AVG(средний_балл) AS avg_gpa FROM студенты GROUP BY id_направления
            )
            SELECT n.название AS направление, ROUND(d.avg_gpa, 2) AS средний_балл
            FROM dir_stats d JOIN направления n ON d.id_направления = n.id_направления
            WHERE d.avg_gpa > 4.0 ORDER BY d.avg_gpa DESC;""",

        "ЗАДАНИЕ 3: CTE (Отличники с полной информацией)": """
            WITH top_students AS (
                SELECT id_студента, фамилия, имя, средний_балл, id_уровня, id_направления 
                FROM студенты WHERE средний_балл >= 4.5
            ),
            full_info AS (
                SELECT ts.фамилия, ts.имя, ts.средний_балл, u.название AS уровень, nd.название AS направление
                FROM top_students ts
                JOIN уровни u ON ts.id_уровня = u.id_ровня
                JOIN направления nd ON ts.id_направления = nd.id_направления
            )
            SELECT * FROM full_info ORDER BY средний_балл DESC, фамилия;"""
    }

    for title, sql in queries.items():
        print(f"\n{'=' * 70}")
        print(f" {title}")
        print("=" * 70)
        cur.execute(sql)
        pretty_print(cur)

    conn.close()
    print(f"\n Скрипт выполнен успешно. БД сохранена в: {DB_FILE}")


if __name__ == "__main__":
    run_demo()