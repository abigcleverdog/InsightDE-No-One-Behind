import mysql.connector as con
from mysql.connector import errorcode
import json, datetime


class DB_handler():
    """
    A class used to write message to MySQL database

    Attributes
    ----------
    table_name : str
        the table name to write the messages
    cnx : Connection
        the connection to database

    Methods
    -------
    close()
        close database connection
        
    create_table(message)
        initiate a table to wirte messages
    
    insert_entry(message)
        write message to database
    """

    def __init__(self):
        """
        Parameters
        ----------
        table_name : str
            the table name to write the messages
        cnx : Connection
            the connection to database
        """
        
        self.table_name = None
        self.cnx = con.connect(host = '<localhost or host address>', user='<user name>', password='<password>', database='<database name>')
        print("***---***"*3, "db connected!")
        
    def close(self):
        """ close database connection """
        self.cnx.close()
        print("mysql connection closed")

    def create_table(self, message):
        """ initiate a table to wirte messages """
        
        mycursor = self.cnx.cursor()
        self.table_name = datetime.datetime.now().strftime("%Y%m_%d%H%M%S")
        
        # create table
        exe = '''CREATE TABLE {} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            total INT,
            time_s VARCHAR(25),
            delay_s FLOAT,
            hasface JSON
            ) '''.format(self.table_name)
        
        mycursor.execute(exe)
        
        mycursor.close()
        
        return self.table_name
        
        
    def insert_entry(self, message):
        """ write message to database """
        mycursor = self.cnx.cursor()
        
        total = len(message[2])
        
        time_now = datetime.datetime.now().strftime("%d_%H_%M_%S")

        hasface = json.dumps(message[2])
        
        data_entry = {
            'total': total,
            'time_s': time_now, # message[0],
            'delay_s': message[1],
            'hasface': hasface,
        }
        
        add_entry = """INSERT INTO {} (total, time_s, delay_s, hasface) VALUES (%(total)s, %(time_s)s, %(delay_s)s, %(hasface)s)""".format(self.table_name)
        
        mycursor.execute(add_entry, data_entry)
        
        self.cnx.commit()
        
        mycursor.close()