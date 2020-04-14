import pandas as pd
import sqlite3
import sys
import os

class DatabaseInterface:

    def __init__(self):
        # Path to database
        database_name = "work_timer.db"
        home = os.path.expanduser("~")
        work_timer_directory = os.path.join(home, ".work_timer")
        if not os.path.isdir(work_timer_directory):
            os.mkdir(work_timer_directory)
        self.database_path = os.path.join(work_timer_directory, database_name)

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
        c.execute("CREATE TABLE IF NOT EXISTS project_names (project_name text, is_hidden integer)")
        c.execute("CREATE TABLE IF NOT EXISTS times (time text, project_name text, action_type text)")
        self.disconnect_from_database(conn)

    def add_project_name_in_database(self, project_name):
        conn, c = self.connect_to_database()
        c.execute("INSERT INTO project_names VALUES (?, ?)", (project_name, False))
        self.disconnect_from_database(conn)

    def delete_project_name_in_database(self, project_name):
        conn, c = self.connect_to_database()
        c.execute("DELETE FROM project_names WHERE project_name=?", (project_name,))
        self.disconnect_from_database(conn)

    def get_project_names(self):
        conn, c = self.connect_to_database()
        c.execute("SELECT project_name FROM project_names WHERE is_hidden IS FALSE")
        project_names = [ values[0] for values in c.fetchall() ]
        self.disconnect_from_database(conn)
        return project_names

    def get_all_project_names(self):
        conn, c = self.connect_to_database()
        c.execute("SELECT project_name FROM project_names")
        project_names = [ values[0] for values in c.fetchall() ]
        self.disconnect_from_database(conn)
        return project_names

    def hide_project_name(self, project_name):
        conn, c = self.connect_to_database()
        c.execute("UPDATE project_names SET is_hidden = ? WHERE project_name = ?;", (True, project_name))
        self.disconnect_from_database(conn)

    def show_project_name(self, project_name):
        conn, c = self.connect_to_database()
        c.execute("UPDATE project_names SET is_hidden = ? WHERE project_name = ?;", (False, project_name))
        self.disconnect_from_database(conn)

    def is_hidden_project_name(self, project_name):
        conn, c = self.connect_to_database()
        c.execute("SELECT is_hidden FROM project_names WHERE project_name = ?", (project_name,))
        result = c.fetchone()["is_hidden"]
        self.disconnect_from_database(conn)
        return result

    def get_last_action(self):
        conn, c = self.connect_to_database()
        c.execute("SELECT * FROM times WHERE Datetime(time) <= Datetime('now', 'localtime') ORDER BY Datetime(time) DESC, action_type ASC LIMIT 1")
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
        df = pd.read_sql_query("SELECT times.project_name, times.time, times.action_type FROM times INNER JOIN project_names ON times.project_name = project_names.project_name WHERE is_hidden IS FALSE ORDER BY Datetime(time) ASC, action_type DESC", conn)
        self.disconnect_from_database(conn)
        return df

    def get_dataframe_all_times(self):
        conn, c = self.connect_to_database()
        df = pd.read_sql_query("SELECT * FROM times ORDER BY Datetime(time) ASC, action_type DESC", conn)
        self.disconnect_from_database(conn)
        return df
