import sqlite3


def main():
    connection = sqlite3.connect("player.db")

    cursor = connection.cursor()

    sql_file = open("create_tables.sql")

    sql_as_string = sql_file.read()

    cursor.executescript(sql_as_string)


if __name__ == "__main__":
    main()
