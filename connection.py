import pymysql

def db_connection():
    try:
        connection = pymysql.connect(
            host='localhost', 
            user='root', 
            password='root',  
            database='Resume',
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Error connecting to the database: {e}")
        return None
