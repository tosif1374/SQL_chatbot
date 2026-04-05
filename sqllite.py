import sqlite3

connection = sqlite3.connect("student.db")
cursor = connection.cursor()

table_info = """
CREATE TABLE IF NOT EXISTS STUDENT(
NAME VARCHAR(25),
CLASS VARCHAR(25),
SECTION VARCHAR(25),
MARKS INT
)
"""

cursor.execute(table_info)

cursor.execute("INSERT INTO STUDENT VALUES ('Krish','Data Science','A',90)")
cursor.execute("INSERT INTO STUDENT VALUES ('John','Data Science','B',100)")
cursor.execute("INSERT INTO STUDENT VALUES ('Mukesh','Data Science','A',86)")
cursor.execute("INSERT INTO STUDENT VALUES ('Ravi','Maths','A',50)")
cursor.execute("INSERT INTO STUDENT VALUES ('Ankit','Physics','B',35)")

connection.commit()

data = cursor.execute("SELECT * FROM STUDENT")

for row in data:
    print(row)

connection.close()