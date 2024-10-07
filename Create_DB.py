import mysql.connector
import re


# Thay đổi thông tin kết nối database cho phù hợp

def main():
    try:
        # Kết nối MySQL Server để thực hiện tạo cơ sở dữ liệu mới
        db_connection = mysql.connector.connect(
            host="localhost",
            user="tuan",
            password="123456tuan",
            auth_plugin='mysql_native_password'
        )
        db_cursor = db_connection.cursor()

        # Tạo cơ sở dữ liệu mới 'labsaledb3' nếu chưa tồn tại
        db_cursor.execute("CREATE DATABASE IF NOT EXISTS labsaledb2")

        # Đóng kết nối tạm thời với MySQL Server
        db_cursor.close()
        db_connection.close()

    except mysql.connector.Error as err:
        pass

    # finally:
    #     if db_cursor:
    #         db_cursor.close()
    #     if db_connection:
    #         db_connection.close()

    db = mysql.connector.connect(
        host="localhost",
        user="tuan",
        password="123456tuan",
        database="labsaledb2",
        auth_plugin='mysql_native_password'
    )

    try:
        with open('database.sql', 'r', encoding='utf-8') as f:
            sql_data = f.read()

            cursor = db.cursor()
            cursor.execute(sql_data)
            db.commit()

            print("Dữ liệu đã được import thành công!")
    except mysql.connector.Error as err:
        pass

    finally:
        db.close()


if __name__ == "__main__":
    main()
