# O módulo sqlite3 do Python fornece uma interface para bancos de dados SQLite. O SQLite é uma biblioteca leve e
# autônoma de banco de dados baseada em disco que não requer um processo de servidor separado. Ele permite que você
# acesse o banco de dados usando uma variante não padrão da linguagem de consulta SQL.
import sqlite3

connection = sqlite3.connect('tutorial.db')
cursor = connection.cursor()

cursor.execute('SELECT * FROM events')
print(cursor.fetchall())
# [('Lions', 'Lion', '2024.06.12'), ('Tiger', 'Tiger City', '2021.12.21'), ('Vizela', 'Vizela City', '2021.12.21')]
cursor.execute('SELECT * FROM events WHERE band="Vizela"')
print(cursor.fetchall())  # [('Vizela', 'Vizela City', '2021.12.21')]

cursor.execute('SELECT band, city FROM events WHERE date="2021.12.21"')
print(cursor.fetchall())  # [('Vizela', 'Vizela City'), ('Vizela', 'Vizela City')]

# Como adicionar rows numa tabela de database:
new_rows = [('Trofa', 'Trofa city', '2024.12.21'), ('Chaves', 'Chaves city', '2024.12.21')]
cursor.executemany('INSERT INTO events VALUES(?, ?, ?)', new_rows)
connection.commit()
