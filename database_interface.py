import sqlite3

class DatabaseInterface:

    def __init__(self):
        # Path to database
        self.self.database_path = "work_timer.db"

        # Database connection
        self.conn = sqlite3.connect(self.database_path)
        self.conn.row_factory = sqlite3.Row

        # Create the database if it not exists
        create_database_tables()

    def create_database_tables():
        c = self.conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS project_names (project_name text)")
        c.execute("CREATE TABLE IF NOT EXISTS times (time text, project_name text, action_type text)")
        self.conn.commit()

    def add_project_name_in_database(self, project_name):
        c = self.conn.cursor()
        c.execute("INSERT INTO project_names VALUES (?)", (project_name,))
        self.conn.commit()

    def remove_project_name_in_database(self, project_name):
        c = self.conn.cursor()
        c.execute("DELETE FROM project_names WHERE project_name=?", (project_name,))
        self.conn.commit()

    def get_project_names(self):
        c = self.conn.cursor()
        c.execute("SELECT project_name FROM project_names")
        project_names = [ values[0] for values in c.fetchall() ]
        return project_names

    def get_last_action(self):
        c = self.conn.cursor()
        c.execute("SELECT * FROM times ORDER BY time DESC LIMIT 1")
        result = c.fetchone()
        if result is None:
            return {"time": "N/A N/A", "project_name": "N/A", "action_type": "N/A"}
        else:
            return result

    def get_active_project_name(self):
        active_project_name = self.project_names_combo_box.get()
        return active_project_name

    def write_work_time(self, active_project_name, action_type, last_action_time):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = [now, active_project_name, action_type]
        c = self.conn.cursor()
        c.execute("INSERT INTO times (time, project_name, action_type) VALUES (?, ?, ?)", line)
        self.conn.commit()
        self.update_last_action_labels(now, active_project_name)

    def add_work_time(self):
        project_names = self.get_project_names()
        if not project_names:
            messagebox.error("Error", "The project list is empty")
            return
        last_action = self.get_last_action()
        if last_action["action_type"] != self.end_action and last_action["action_type"] != "N/A":
            self.end_work_time()
        last_action = self.get_last_action()
        active_project_name = self.get_active_project_name()
        self.write_work_time(active_project_name, self.begin_action, last_action['time'])

    def end_work_time(self):
        project_names = self.get_project_names()
        if not project_names:
            messagebox.error("Error", "The project list is empty")
            return
        last_action = self.get_last_action()
        if last_action["action_type"] != self.end_action and last_action["action_type"] != "N/A":
            self.write_work_time(last_action["project_name"], self.end_action, last_action['time'])

    def get_begin_row_from_time(self, clicked_time):
        c = self.conn.cursor()
        c.execute("SELECT * FROM times WHERE Datetime(time) <= Datetime(?) AND action_type = 'BEGIN' ORDER BY Datetime(time) DESC", (clicked_time,))
        return c.fetchone()

    def get_end_row_from_time(self, clicked_time):
        c = self.conn.cursor()
        c.execute("SELECT * FROM times WHERE Datetime(time) >= Datetime(?) AND action_type = 'END' ORDER BY Datetime(time) ASC", (clicked_time,))
        return c.fetchone()

    def update_row(self, new_project_name, new_time, old_project_name, old_time, action_type):
        c = self.conn.cursor()
        c.execute("UPDATE times SET project_name = ?, time = ? WHERE project_name = ? AND time = ? AND action_type = ?;", (new_project_name, new_time, old_project_name, old_time, action_type))
        self.conn.commit()

    def delete_row(self, project_name, time, action_type):
        c = self.conn.cursor()
        c.execute("DELETE FROM times WHERE project_name = ? AND time = ? AND action_type = ?;", (project_name, time, action_type))
        self.conn.commit()

    def create_row(self, project_name, time, action_type):
        c = self.conn.cursor()
        c.execute("INSERT INTO times (project_name, time, action_type) VALUES (?, ?, ?)", (project_name, time, action_type))
        self.conn.commit()
