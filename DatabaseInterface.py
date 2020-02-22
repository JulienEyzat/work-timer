import pandas as pd
import sqlite3
import sys
import os

class DatabaseInterface:

    def __init__(self):
        # Path to database
        database_name = "work_timer.db"
        execution_directory = os.path.split(os.path.abspath(sys.argv[0]))[0]
        self.database_path = os.path.join(execution_directory, database_name)

        # Action names in database
        self.end_action = "END"
        self.begin_action = "BEGIN"

        # Create the database if it not exists
        self.create_database_tables()

    def connect_to_database(self):
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        return conn, cursor

    def disconnect_from_database(self, conn):
        conn.commit()
        conn.close()

    def create_database_tables(self):
        conn, c = self.connect_to_database()
        c.execute("CREATE TABLE IF NOT EXISTS project_names (project_name text)")
        c.execute("CREATE TABLE IF NOT EXISTS times (time text, project_name text, action_type text)")
        self.disconnect_from_database(conn)

    def add_project_name_in_database(self, project_name):
        conn, c = self.connect_to_database()
        c.execute("INSERT INTO project_names VALUES (?)", (project_name,))
        self.disconnect_from_database(conn)

    def remove_project_name_in_database(self, project_name):
        conn, c = self.connect_to_database()
        c.execute("DELETE FROM project_names WHERE project_name=?", (project_name,))
        self.disconnect_from_database(conn)

    def get_project_names(self):
        conn, c = self.connect_to_database()
        c.execute("SELECT project_name FROM project_names")
        project_names = [ values[0] for values in c.fetchall() ]
        self.disconnect_from_database(conn)
        return project_names

    def get_times_project_names(self):
        conn, c = self.connect_to_database()
        c.execute("SELECT DISTINCT project_name FROM times")
        project_names = [ values[0] for values in c.fetchall() ]
        self.disconnect_from_database(conn)
        return project_names

    def get_last_action(self):
        conn, c = self.connect_to_database()
        c.execute("SELECT * FROM times ORDER BY Datetime(time) DESC LIMIT 1")
        result = c.fetchone()
        self.disconnect_from_database(conn)
        return result

    def get_begin_row_from_time(self, time):
        conn, c = self.connect_to_database()
        c.execute("SELECT * FROM times WHERE Datetime(time) <= Datetime(?) AND action_type = ? ORDER BY Datetime(time) DESC", (time, self.begin_action))
        result = c.fetchone()
        self.disconnect_from_database(conn)
        return result

    def get_end_row_from_time(self, time):
        conn, c = self.connect_to_database()
        c.execute("SELECT * FROM times WHERE Datetime(time) >= Datetime(?) AND action_type = ? ORDER BY Datetime(time) ASC", (time, self.end_action))
        result = c.fetchone()
        self.disconnect_from_database(conn)
        return result

    def update_row(self, new_project_name, new_time, old_project_name, old_time, action_type):
        conn, c = self.connect_to_database()
        c.execute("UPDATE times SET project_name = ?, time = ? WHERE project_name = ? AND time = ? AND action_type = ?;", (new_project_name, new_time, old_project_name, old_time, action_type))
        self.disconnect_from_database(conn)

    def delete_row(self, project_name, time, action_type):
        conn, c = self.connect_to_database()
        c.execute("DELETE FROM times WHERE project_name = ? AND time = ? AND action_type = ?;", (project_name, time, action_type))
        self.disconnect_from_database(conn)

    def create_row(self, project_name, time, action_type):
        conn, c = self.connect_to_database()
        c.execute("INSERT INTO times (project_name, time, action_type) VALUES (?, ?, ?)", (project_name, time, action_type))
        self.disconnect_from_database(conn)

    def get_dataframe_times(self):
        conn, c = self.connect_to_database()
        df = pd.read_sql_query("SELECT * FROM times", conn)
        self.disconnect_from_database(conn)
        return df