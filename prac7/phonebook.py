import csv
import psycopg2
from connect import create_connection, create_table

# 1. Добавить из CSV
def insert_from_csv(filename):
    conn = create_connection()
    cur = conn.cursor()
    with open(filename, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute("""
                INSERT INTO phonebook (first_name, last_name, phone)
                VALUES (%s, %s, %s)
                ON CONFLICT (phone) DO NOTHING
            """, (row['first_name'], row['last_name'], row['phone']))
    conn.commit()
    cur.close()
    conn.close()
    print("CSV загружен!")

# 2. Добавить вручную
def insert_from_console():
    first = input("Имя: ")
    last = input("Фамилия: ")
    phone = input("Телефон: ")
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO phonebook (first_name, last_name, phone)
        VALUES (%s, %s, %s)
    """, (first, last, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("Контакт добавлен!")

# 3. Показать все
def show_all():
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook ORDER BY id")
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

# 4. Поиск по имени
def search_by_name(name):
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM phonebook WHERE first_name ILIKE %s", (f"%{name}%",))
    rows = cur.fetchall()
    for row in rows:
        print(row)
    cur.close()
    conn.close()

# 5. Обновить телефон
def update_phone():
    name = input("Имя контакта: ")
    new_phone = input("Новый телефон: ")
    conn = create_connection()
    cur = conn.cursor()
    cur.execute("UPDATE phonebook SET phone=%s WHERE first_name=%s", (new_phone, name))
    conn.commit()
    cur.close()
    conn.close()
    print("Обновлено!")

# 6. Удалить
def delete_contact():
    choice = input("Удалить по (1) имени или (2) телефону? ")
    conn = create_connection()
    cur = conn.cursor()
    if choice == "1":
        name = input("Имя: ")
        cur.execute("DELETE FROM phonebook WHERE first_name=%s", (name,))
    else:
        phone = input("Телефон: ")
        cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
    conn.commit()
    cur.close()
    conn.close()
    print("Удалено!")

# Меню
def menu():
    create_table()
    while True:
        print("\n--- PhoneBook ---")
        print("1. Загрузить из CSV")
        print("2. Добавить вручную")
        print("3. Показать все")
        print("4. Поиск по имени")
        print("5. Обновить телефон")
        print("6. Удалить контакт")
        print("0. Выход")
        choice = input("Выбор: ")
        if choice == "1":
            insert_from_csv("contacts.csv")
        elif choice == "2":
            insert_from_console()
        elif choice == "3":
            show_all()
        elif choice == "4":
            name = input("Введи имя: ")
            search_by_name(name)
        elif choice == "5":
            update_phone()
        elif choice == "6":
            delete_contact()
        elif choice == "0":
            break

menu()