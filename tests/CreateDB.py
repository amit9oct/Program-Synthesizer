import sqlite3

# code to create table(s) and some entries in DB
conn = sqlite3.connect('testing.db')
cursor = conn.cursor()

# cursor.execute("CREATE TABLE Employees("
#                "id INTEGER PRIMARY KEY,"
#                "name TEXT,"
#                "age INTEGER,"
#                "sex TEXT,"
#                "salary INTEGER,"
#                "city TEXT,"
#                "manager TEXT)")
#
# cursor.execute("INSERT INTO Employees (name, age, sex, salary, city, manager) VALUES ('Tom Cruise', 55, 'Male', 150000, 'Paris', NULL)")
# cursor.execute("INSERT INTO Employees (name, age, sex, salary, city, manager) VALUES ('Tom Hanks', 53, 'Male', 125000, 'California', 'Tom Cruise')")
# cursor.execute("INSERT INTO Employees (name, age, sex, salary, city, manager) VALUES ('Daniel Radcliffe', 26, 'Male', 75000, 'London', 'Tom Cruise')")
# cursor.execute("INSERT INTO Employees (name, age, sex, salary, city, manager) VALUES ('Emma Watson', 25, 'Female', 75000, 'London', 'Tom Cruise')")
# cursor.execute("INSERT INTO Employees (name, age, sex, salary, city, manager) VALUES ('Anne Hathaway', 40, 'Female', 100000, 'California', 'Tom Cruise')")
# cursor.execute("INSERT INTO Employees (name, age, sex, salary, city, manager) VALUES ('Rebecca', 45, 'Female', 120000, 'Paris', 'Tom Cruise')")
# cursor.execute("INSERT INTO Employees (name, age, sex, salary, city, manager) VALUES ('Natalie Portman', 35, 'Female', 130000, 'LA', 'Tom Cruise')")

cursor.execute("CREATE TABLE Test("
               "id INTEGER PRIMARY KEY,"
               " name TEXT, maker TEXT,"
               " type TEXT,"
               " ram INTEGER,"
               " harddisk REAL,"
               " screensize REAL,"
               " price REAL,"
               " processor TEXT,"
               " graphics TEXT,"
               " resolution TEXT)")
cursor.execute("INSERT INTO Test (name, maker, type, ram, harddisk, screensize, price, processor, graphics, resolution) VALUES "
               "('Dell Inspiron 2', 'Dell', 'Laptop', 4, 512, 14, 42000, 'i5', 'Nvidia-420', '1366x768')")
cursor.execute("INSERT INTO Test (name, maker, type, ram, harddisk, screensize, price, processor, graphics, resolution) VALUES "
               "('Lenovo Z50-70', 'Lenovo', 'Laptop', 16, 1024, 13, 82000, 'i7', 'Nvidia-840', '1920x1080')")
cursor.execute("INSERT INTO Test (name, maker, type, ram, harddisk, screensize, price, processor, graphics, resolution) VALUES "
               "('Dell Alienware', 'Dell', 'Laptop', 32, 2048, 15, 150000, 'i7', 'Nvidia-1080X', '3840x2160')")
cursor.execute("INSERT INTO Test (name, maker, type, ram, harddisk, screensize, price, processor, graphics, resolution) VALUES "
               "('HP Yoga', 'HP', 'Laptop', 16, 256, 13, 75000, 'i7', 'Nvidia-420', '1920x1080')")
cursor.execute("INSERT INTO Test (name, maker, type, ram, harddisk, screensize, price, processor, graphics, resolution) VALUES "
               "('Dell Inspiron 1', 'Dell', 'Laptop', 3, 320, 14, 33000, 'i3', NULL, '1366x768')")
cursor.execute("INSERT INTO Test (name, maker, type, ram, harddisk, screensize, price, processor, graphics, resolution) VALUES "
               "('Dell Inspiron 3', 'Dell', 'Laptop', 3, 320, 15, 36000, 'i3', 'Integrated Intel Graphics', '1366x768')")