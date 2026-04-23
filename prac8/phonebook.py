import psycopg2
from config import DB_CONFIG

def get_conn():
    return psycopg2.connect(**DB_CONFIG)
[]
def load_sql(filename):
    conn = get_conn()
    cur = conn.cursor()
    with open(filename, 'r') as f:
        cur.execute(f.read())
    conn.commit()
    cur.close()
    conn.close()
    print(f"{filename} загружен!")

def search_pattern(pattern):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_by_pattern(%s)", (pattern,))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

def upsert(first, last, phone):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s, %s)", (first, last, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Upsert выполнен!")

def paginated(limit, offset):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

def delete(value, by_type):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("CALL delete_contact(%s, %s)", (value, by_type))
    conn.commit()
    cur.close()
    conn.close()
    print("Удалено!")

def menu():
    load_sql("functions.sql")
    load_sql("procedures.sql")

    while True:
        print("\n--- PhoneBook 8 ---")
        print("1. Поиск по паттерну")
        print("2. Добавить/обновить контакт")
        print("3. Показать с пагинацией")
        print("4. Удалить контакт")
        print("0. Выход")

        choice = input("Выбор: ")
        if choice == "1":
            p = input("Паттерн: ")
            search_pattern(p)
        elif choice == "2":
            f = input("Имя: ")
            l = input("Фамилия: ")
            ph = input("Телефон: ")
            upsert(f, l, ph)
        elif choice == "3":
            lim = int(input("Сколько записей: "))
            off = int(input("Пропустить сколько: "))
            paginated(lim, off)
        elif choice == "4":
            t = input("По (name) или (phone)? ")
            v = input("Значение: ")
            delete(v, t)
        elif choice == "0":
            break

menu()