import sqlite3

conn = sqlite3.connect('floodlens.db')
cursor = conn.cursor()

cursor.execute("UPDATE subscribers SET phone_number = '+91' || phone_number WHERE phone_number NOT LIKE '+%'")
print('Fixed numbers:', cursor.rowcount)

cursor.execute('DELETE FROM subscribers WHERE id = 2')
print('Removed duplicate:', cursor.rowcount)

conn.commit()
conn.close()