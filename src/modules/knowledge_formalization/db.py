import psycopg2


class Database:
    """
    Class used for communication with postgreSQL database.
    """
    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = self.connect(db_name)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    @staticmethod
    def connect(db_name):
        username = "postgres"
        password = "testtest"
        hostname = "localhost"
        port = "5432"

        # create connection
        connection = psycopg2.connect(user=username,
                                      password=password,
                                      host=hostname,
                                      port=port,
                                      database=db_name)
        return connection

    def create_database(self, db_name):
        # get cursor, check if database exists and if it doesn't, create new one
        self.get_cursor().execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname = '" + db_name + "';")
        exists = self.cursor.fetchone()
        if not exists:
            print("Database " + db_name + " doesn't exist. Creating new database in progress.")
            self.cursor.execute("CREATE DATABASE " + db_name)
        else:
            print("Database " + db_name + " exists.")

    def get_connection(self):
        # get postgres connection
        if self.connection is not None:
            return self.connection
        else:
            return self.connect(self.db_name)

    def get_cursor(self):
        # get cursor for database manipulation
        if self.cursor is not None:
            return self.cursor
        else:
            if self.connection is not None:
                return self.connection.cursor()
            else:
                return self.get_connection().cursor()

    def close(self):
        # close connection and set cursor to none
        if self.cursor is not None:
            self.cursor.close()
            self.cursor = None
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    def create_table(self, line):
        print("Creating table with line", line)
        try:
            self.connection = self.get_connection()
            self.cursor = self.get_cursor()
            self.cursor.execute(line)
            # commit the changes
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error creating table with line " + line, "Error:", error)
        finally:
            if self.connection is not None:
                self.close()

    def drop_table(self, table):
        print("Dropping table", table)
        try:
            self.connection = self.get_connection()
            self.cursor = self.get_cursor()
            self.cursor.execute("DROP TABLE " + table)
            # commit the changes
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error dropping table " + table, "Error:", error)
        finally:
            if self.connection is not None:
                self.close()

    def query(self, line, parameters=None):
        """
        Query the table with parameters or without. Examples:
        1) "SELECT * FROM concepts"
        2) "SELECT * FROM concepts WHERE id = %s", (9,)
        :param line:
        :param parameters:
        :return:
        """
        result = None
        try:
            self.connection = self.get_connection()
            self.cursor = self.get_cursor()

            # execute query
            if parameters is not None:
                self.cursor.execute(line, parameters)
            else:
                self.cursor.execute(line)
            result = self.cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error executing line " + line, "Error:", error)
        finally:
            if self.connection is not None:
                self.close()
            return result

    def execute(self, content, parameters=None, fetch=False):
        """
        Execute insert or update with parameters or without. Examples:
        1) "INSERT INTO concepts(id, timestamp, alpha, concepts) VALUES(DEFAULT, 431234124, 0.2, 10)"
        2) "UPDATE concepts set result = %s where id = %s", ("testtest", 6)
        :param fetch:
        :param content:
        :param parameters:
        :return:
        """
        row_id = None
        try:
            self.connection = self.get_connection()
            self.cursor = self.get_cursor()
            if parameters is not None:
                self.cursor.execute(content, parameters)
            else:
                self.cursor.execute(content)
            # fetch row_id
            if fetch:
                row_id = self.cursor.fetchone()[0]
            self.connection.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print("Error executing line " + content, "Error:", error)
        finally:
            if self.connection is not None:
                self.close()
            return row_id
