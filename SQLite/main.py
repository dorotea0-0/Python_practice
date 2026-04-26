import sqlite3
import csv
import os


#Подготовка данных
def prepare_external_files():
    # Создаем CSV файл с разделителем запятая
    with open('job_titles.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id_job_title', 'name'])
        writer.writerows([
            (1, 'Менеджер'), (2, 'Разработчик'), (3, 'Аналитик'),
            (4, 'Дизайнер'), (5, 'Тестировщик')
        ])

    # Создаем TXT файл с разделителем вертикальная черта |
    with open('employees.txt', 'w', encoding='utf-8') as f:
        f.write('id|surname|name|id_job_title\n')
        f.write('1|Иванов|Иван|1\n2|Петров|Пётр|2\n3|Сидорова|Мария|3\n4|Козлов|Алексей|4\n5|Васильева|Ольга|5\n6|Смирнов|Дмитрий|2\n7|Ильин|Сергей|3')


#Подключение к базе данных и создание её
def setup_database():
    # Удаляем старую БД, чтобы не было конфликтов при повторных запусках
    if os.path.exists('baza.db'):
        os.remove('baza.db')



    conn = sqlite3.connect('baza.db', timeout=10)
    cur = conn.cursor()
    # Включаем проверку внешних ключей
    cur.execute("PRAGMA foreign_keys = ON;")

    cur.execute('''CREATE TABLE IF NOT EXISTS job_titles (
        id_job_title INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        surname TEXT NOT NULL,
        name TEXT NOT NULL,
        id_job_title INTEGER NOT NULL,
        FOREIGN KEY(id_job_title) REFERENCES job_titles(id_job_title)
    )''')
    conn.commit()
    return conn, cur

#Импорт данных
def import_data(conn, cur):
    #Импорт из CSV
    with open('job_titles.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # пропускаем заголовок
        # Преобразуем ID в int, так как в БД он INTEGER
        data = [(int(row[0]), row[1]) for row in reader]
        cur.executemany("INSERT OR IGNORE INTO job_titles (id_job_title, name) VALUES (?, ?)", data)

    #Импорт из TXT
    with open('employees.txt', 'r', encoding='utf-8') as f:
        next(f)  # пропускаем заголовок
        data = []
        for line in f:
            parts = line.strip().split('|')
            if len(parts) == 4:
                # Преобразуем числовые поля в int
                data.append((int(parts[0]), parts[1], parts[2], int(parts[3])))
        cur.executemany("INSERT OR IGNORE INTO employees (id, surname, name, id_job_title) VALUES (?, ?, ?, ?)", data)

    conn.commit()
    print(" Данные успешно импортированы из CSV и TXT файлов.\n")

#Выполнение запросов
def run_queries(cur):
    print("5 ПРОСТЫХ ЗАПРОСОВ (COUNT, MAX, SUM, AVG, MIN)")

    simple_queries = [
        ("Количество сотрудников", "SELECT COUNT(*) FROM employees;"),
        ("Максимальный ID сотрудника", "SELECT MAX(id) FROM employees;"),
        ("Сумма всех ID сотрудников", "SELECT SUM(id) FROM employees;"),
        ("Среднее значение ID должности", "SELECT AVG(id_job_title) FROM employees;"),
        ("Минимальный ID сотрудника", "SELECT MIN(id) FROM employees;")
    ]

    for desc, sql in simple_queries:
        cur.execute(sql)
        res = cur.fetchone()[0]
        print(f" {desc}: {res}")

    print("3 ЗАПРОСА С АГРЕГАЦИЕЙ (GROUP BY / HAVING)")

    agg_queries = [
        ("Количество сотрудников по должностям", '''
            SELECT j.name, COUNT(e.id) as cnt
            FROM job_titles j
            LEFT JOIN employees e ON j.id_job_title = e.id_job_title
            GROUP BY j.id_job_title;
        '''),
        ("Должности, где средний ID сотрудника > 3", '''
            SELECT j.name, AVG(e.id) as avg_id
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id_job_title
            GROUP BY j.name
            HAVING AVG(e.id) > 3;
        '''),
        ("Максимальный ID в каждой должности", '''
            SELECT j.name, MAX(e.id) as max_id
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id_job_title
            GROUP BY j.id_job_title;
        ''')
    ]

    for desc, sql in agg_queries:
        print(f"\n {desc}:")
        cur.execute(sql)
        for row in cur.fetchall():
            print(f"   {row[0]}: {row[1]}")

    print("3 ЗАПРОСА С ОБЪЕДИНЕНИЕМ И УСЛОВИЯМИ (JOIN + WHERE/LIKE/IN)")

    join_queries = [
        ("Все Разработчики", '''
            SELECT e.surname, e.name, j.name
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id_job_title
            WHERE j.name = 'Разработчик';
        '''),
        ("Менеджеры и Аналитики", '''
            SELECT e.surname, e.name, j.name
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id_job_title
            WHERE j.name IN ('Менеджер', 'Аналитик');
        '''),
        ("Сотрудники с фамилией на 'И' и ID > 1", '''
            SELECT e.surname, e.name, j.name
            FROM employees e
            JOIN job_titles j ON e.id_job_title = j.id_job_title
            WHERE e.surname LIKE 'И%' AND e.id > 1;
        ''')
    ]

    for desc, sql in join_queries:
        print(f"\n {desc}:")
        cur.execute(sql)
        for row in cur.fetchall():
            print(f"   {row[0]} {row[1]} — {row[2]}")

if __name__ == "__main__":
    # 1. Генерируем внешние файлы
    prepare_external_files()

    # 2. Создаем БД и таблицы
    conn, cur = setup_database()

    # 3. Импортируем данные
    import_data(conn, cur)

    # 4. Выполняем запросы
    run_queries(cur)

    # 5. Закрываем соединение
    conn.close()
    print("Соединение с базой данных закрыто.")