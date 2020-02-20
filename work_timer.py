from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from matplotlib import cm
from matplotlib import colors
import calendar
import pandas as pd
import sqlite3
import time
import sys
import csv
import os

class work_timer:
    def __init__(self):
        # Constants$
        execution_directory = os.path.split(os.path.abspath(sys.argv[0]))[0]
        self.database_path = os.path.join(execution_directory, "work_timer.db")
        self.end_action = "END"
        self.begin_action = "BEGIN"

        # Database connection
        self.conn = sqlite3.connect(self.database_path)
        self.conn.row_factory = sqlite3.Row

        ### Tkinter canvas constants
        self.canvas_width = 1280
        self.canvas_height = 720

        # Variables that defined the offset for the coordinate axis
        self.left_width_offset = 50
        self.right_width_offset = 200
        self.up_heigth_offset = 50
        self.down_heigth_offset = 0

        # The size of the grid which contains the project times
        self.grid_width = self.canvas_width - self.left_width_offset - self.right_width_offset
        self.grid_heigth = self.canvas_height - self.up_heigth_offset - self.down_heigth_offset

        # List of colors for projects
        pc = cm.get_cmap("tab10")
        self.project_colors = [ colors.rgb2hex(pc(i)[:3]) for i in range(pc.N) ]
        self.project_color_dict = {}

        # Variables to create day lines
        total_days = 7
        self.between_days_range = int(self.grid_width/total_days)

        # Today (for calendar)
        self.reference_day = datetime.today()

        # Tkinter
        self.root = tk.Tk()
        self.root.title("Work Timer")

        self.create_database_tables()

    ### Manage databases

    def create_database_tables(self):
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

    ### Process data

    def create_summary_table(self):
        # Read the time database
        time_df = pd.read_sql_query("SELECT * FROM times", self.conn)
        if time_df.empty:
            return None
        time_df["time"] = pd.to_datetime(time_df["time"])
        # Get the begining time and ending time on the same line to get the time range
        time_df["last_time"] = time_df["time"].shift()
        time_df["time_range"] = time_df["time"] - time_df["last_time"]
        # Keep the interesting lines and columns
        time_df = time_df[ time_df["action_type"] == "END" ]
        time_df = time_df[ ["project_name", "time", "time_range"] ]
        # Group by month and project name
        time_df.set_index("time", inplace=True)
        time_df = time_df.groupby([pd.Grouper(freq='M'), "project_name"]).sum()
        # Get the time range in hours
        time_df["time_range"] = time_df["time_range"] / pd.Timedelta(hours=1)
        time_df = time_df.round(2)
        time_df.reset_index(inplace=True)
        time_df["time"] = time_df['time'].dt.month.apply(lambda x: "%s (h)" %(calendar.month_abbr[x]))
        time_df.rename(columns={"time": "month", "project_name": "Project Name"}, inplace=True)
        # Place the months as columns
        time_df = time_df.pivot(index='Project Name', columns='month', values='time_range')
        time_df.reset_index(inplace=True)
        time_df.fillna(0, inplace=True)

        return time_df

    ### Create GUI

    # Buttons to add times in the database
    def create_buttons(self):
        self.start_button = tk.Button(self.root, text="Start", command=self.add_work_time)
        self.start_button.grid(row=1,column=1)
        self.stop_button = tk.Button(self.root, text="End", command=self.end_work_time)
        self.stop_button.grid(row=1,column=2)

    def create_project_list(self):
        project_names = self.get_project_names()
        self.project_names_combo_box = ttk.Combobox(self.root, state='readonly', values=project_names)
        self.project_names_combo_box.grid(row=2, column=1, columnspan=2)
        if project_names:
            self.project_names_combo_box.current(0)

    def add_project(self):
        # Get the new project_name
        project_name = self.add_project_entry.get().strip()
        # Get the previous project names
        current_project_names = self.get_project_names()
        if project_name in current_project_names:
            messagebox.showerror("Error", "%s is already in the database" %(project_name))
            return
        elif not project_name:
            messagebox.showerror("Error", "The project name is empty")
            return

        # Add the project name in the database
        self.add_project_name_in_database(project_name)
        # Update the list of project names
        project_names = self.get_project_names()
        self.project_names_combo_box.config(values=project_names)
        self.project_names_combo_box.current(len(project_names)-1)
        # Destroy the window
        self.add_project_window.destroy()

    def create_add_project_window(self):
        # Create a new window
        self.add_project_window = tk.Toplevel(self.root)
        self.add_project_window.title("Add project")

        self.add_project_entry = tk.Entry(self.add_project_window)
        self.add_project_entry.grid()

        add_button = tk.Button(self.add_project_window, text="Add", command=self.add_project)
        add_button.grid()

    def remove_project(self):
        # Get the project_name
        project_name = self.remove_project_combo_box.get()
        # Get the previous project names
        current_project_names = self.get_project_names()
        if not project_name in current_project_names:
            messagebox.showerror("Error", "%s is not in the database" %(project_name))
            return

        # Remove the project name in the database
        self.remove_project_name_in_database(project_name)
        # Update the list of project names
        project_names = self.get_project_names()
        self.project_names_combo_box.config(values=project_names)
        if project_names:
            self.project_names_combo_box.current(0)
        else:
            self.project_names_combo_box.set("")
        # Destroy the window
        self.remove_project_window.destroy()

    def create_remove_project_window(self):

        # Check if there is projects to remove
        project_names = self.get_project_names()
        if not project_names:
            messagebox.showerror("Error", "There is no project yet")
            return

        # Create a new window
        self.remove_project_window = tk.Toplevel(self.root)
        self.remove_project_window.title("Remove project")

        project_names = self.get_project_names()
        self.remove_project_combo_box = ttk.Combobox(self.remove_project_window, state='readonly', values=project_names)
        self.remove_project_combo_box.grid()
        if project_names:
            self.remove_project_combo_box.current(0)

        remove_button = tk.Button(self.remove_project_window, text="Remove", command=self.remove_project)
        remove_button.grid()

    def create_project_list_buttons(self):
        self.add_project_button = tk.Button(self.root, text="Add", command=self.create_add_project_window)
        self.add_project_button.grid(row=3,column=1)
        self.remove_project_button = tk.Button(self.root, text="Remove", command=self.create_remove_project_window)
        self.remove_project_button.grid(row=3,column=2)

    def create_last_action_labels(self):
        last_action = self.get_last_action()
        self.last_action_label = tk.Label(self.root, text="Last update :")
        self.last_action_label.grid(row=4, column=1, columnspan=2)

        self.last_action_date_label = tk.Label(self.root, text="Date :")
        self.last_action_date_label.grid(row=5, column=1, columnspan=1, sticky="e")
        self.last_action_date_var = tk.StringVar()
        self.last_action_date_var.set(last_action["time"].split(" ")[0])
        self.last_action_date_value_label = tk.Label(self.root, textvariable=self.last_action_date_var)
        self.last_action_date_value_label.grid(row=5, column=2, columnspan=1, sticky="w")

        self.last_action_time_label = tk.Label(self.root, text="Time :")
        self.last_action_time_label.grid(row=6, column=1, columnspan=1, sticky="e")
        self.last_action_time_var = tk.StringVar()
        self.last_action_time_var.set(last_action["time"].split(" ")[1])
        self.last_action_time_value_label = tk.Label(self.root, textvariable=self.last_action_time_var)
        self.last_action_time_value_label.grid(row=6, column=2, columnspan=1, sticky="w")

        self.last_action_project_label = tk.Label(self.root, text="Project :")
        self.last_action_project_label.grid(row=7, column=1, columnspan=1, sticky="e")
        self.last_action_project_var = tk.StringVar()
        self.last_action_project_var.set(last_action["project_name"])
        self.last_action_project_value_label = tk.Label(self.root, textvariable=self.last_action_project_var)
        self.last_action_project_value_label.grid(row=7, column=2, columnspan=1, sticky="w")

    def create_summary_button(self):
        self.summary_button = tk.Button(self.root, text="Summary", command=self.create_summary_table_tree)
        self.summary_button.grid(row=8, column=1, columnspan=2)

    def create_calendar_button(self):
        self.summary_button = tk.Button(self.root, text="Calendar", command=self.create_calendar)
        self.summary_button.grid(row=9, column=1, columnspan=2)

    def update_last_action_labels(self, time, project_name):
        self.last_action_date_var.set(time.split(" ")[0])
        self.last_action_time_var.set(time.split(" ")[1])
        self.last_action_project_var.set(project_name)

    def create_summary_table_tree(self):
        time_df = self.create_summary_table()
        if time_df is None:
            messagebox.showerror("Error", "The time database is empty")
            return

        # Create a new window
        summary_window = tk.Toplevel(self.root)
        summary_window.title("Summary")

        # Create the table
        treeview = ttk.Treeview(summary_window)
        treeview.grid()

        # Add the header to the table
        column_names = list(time_df.columns.values)
        treeview["columns"] = column_names
        treeview["show"] = "headings"
        for column_name in column_names:
            treeview.heading(column_name, text=column_name)

        # Add the rows to the table
        for index, row in time_df.iterrows():
            treeview.insert("", index, values=list(row))

    ### Create the agenda of project times

    # This rectangle is used to add new project blocks
    def create_invisible_rectangle(self):
        self.w.create_rectangle(self.left_width_offset, self.up_heigth_offset, self.grid_width+self.left_width_offset, self.grid_heigth+self.up_heigth_offset, fill="", outline="", tags="add_times")


    def create_coordinates_lines(self):
        self.w.create_line(0, self.up_heigth_offset, self.left_width_offset+self.grid_width, self.up_heigth_offset, width=2)
        self.w.create_line(self.left_width_offset, 0, self.left_width_offset, self.up_heigth_offset+self.grid_heigth, width=2)

    def create_hour_lines(self):
        # Variables to create hour lines
        total_hours = 14
        nb_hours_between_line = 2
        between_lines_range = int(self.grid_heigth/(total_hours/nb_hours_between_line))
        base = 8
        hours_shown = ["%s:00" %(base+nb_hours_between_line*x) for x in range(total_hours)]
        index = 0
        for y in range(self.up_heigth_offset+between_lines_range, self.canvas_height-self.down_heigth_offset, between_lines_range):
            self.w.create_text(self.left_width_offset-5, y, text=hours_shown[index], anchor="e")
            index+=1
            self.w.create_line(self.left_width_offset, y, self.left_width_offset+self.grid_width, y, dash=(10,10))

    def create_day_lines(self):
        start_of_week = self.reference_day - timedelta(days=self.reference_day.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        weekdays = [ "%s %s/%s" %(calendar.day_name[my_date.weekday()], my_date.day, my_date.month) for my_date in pd.date_range(start_of_week, end_of_week) ]
        index = 0
        for x in range(self.left_width_offset+self.between_days_range, self.canvas_width-self.right_width_offset, self.between_days_range):
            self.w.create_line(x, 0, x, self.canvas_height-self.down_heigth_offset, tags="day_line")
            self.w.create_text(x-int(self.between_days_range/2), int(self.up_heigth_offset/2), text=weekdays[index], tags="day_line")
            index+=1

    def create_legend(self):
        df = pd.read_sql_query("SELECT * FROM times", self.conn)
        project_names = df["project_name"].unique()
        index = 0
        for project_name in project_names:
            self.project_color_dict[project_name] = self.project_colors[index]
            height_space = 20
            self.w.create_rectangle(self.canvas_width-self.right_width_offset+10, index*height_space+100, self.canvas_width-self.right_width_offset+30, 110+index*height_space, fill=self.project_color_dict[project_name], tags="legend")
            self.w.create_text(self.canvas_width-self.right_width_offset+35, 105+index*height_space, text=project_name, anchor="w", tags="legend")
            index+=1

    def add_working_time(self, first_project_date, last_project_date, first_day_date, last_day_date, day_int, color):
        begin_time_first = (((first_project_date-first_day_date)*(self.grid_heigth))/(last_day_date-first_day_date))+self.up_heigth_offset
        last_time_first = (((last_project_date-first_day_date)*(self.grid_heigth))/(last_day_date-first_day_date))+self.up_heigth_offset
        self.w.create_rectangle(self.left_width_offset+day_int*self.between_days_range+10, begin_time_first, self.left_width_offset+(day_int+1)*self.between_days_range-10, last_time_first, fill=color, tags="project_times")

    def add_all_working_time(self):
        df = pd.read_sql_query("SELECT * FROM times", self.conn)
        df["time"] = pd.to_datetime(df["time"])

        # Only keep the current week
        start_of_week = self.reference_day - timedelta(days=self.reference_day.weekday())  # Monday
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=0)
        df = df[ (df["time"] >= start_of_week) & (df["time"] <= end_of_week) ]

        df["last_time"] = df["time"].shift()
        df = df[ df["action_type"] == "END" ]
        for row in df.itertuples(index=False):
            self.add_working_time(row.last_time, row.time, row.time.replace(hour=6, minute=0, second=0), row.last_time.replace(hour=20, minute=0, second=0), row.time.weekday(), self.project_color_dict[row.project_name])

    def set_prev_week(self):
        self.reference_day = self.reference_day - timedelta(days=7)
        self.w.delete("day_line")
        self.create_day_lines()
        self.w.delete("project_times")
        self.add_all_working_time()

    def set_next_week(self):
        self.reference_day = self.reference_day + timedelta(days=7)
        self.w.delete("day_line")
        self.create_day_lines()
        self.w.delete("project_times")
        self.add_all_working_time()

    def modify_time_row(self, modify_type):
        # Get the new values
        project_name = self.modify_times_project_name_combobox.get()
        row_date = self.modify_times_date_label.cget("text")
        begin_hour = self.begin_hour_entry.get()
        if len(begin_hour) == 1:
            begin_hour = "0%s" %(begin_hour)
        begin_minute = self.begin_minute_entry.get()
        if len(begin_minute) == 1:
            begin_minute = "0%s" %(begin_minute)
        begin_second = self.begin_second_entry.get()
        if len(begin_second) == 1:
            begin_second = "0%s" %(begin_second)
        begin_time = "%s %s:%s:%s" %(row_date, begin_hour, begin_minute, begin_second)
        end_hour = self.end_hour_entry.get()
        if len(end_hour) == 1:
            end_hour = "0%s" %(end_hour)
        end_minute = self.end_minute_entry.get()
        if len(end_minute) == 1:
            end_minute = "0%s" %(end_minute)
        end_second = self.end_second_entry.get()
        if len(end_second) == 1:
            end_second = "0%s" %(end_second)
        end_time = "%s %s:%s:%s" %(row_date, end_hour, end_minute, end_second)

        # Get all the project names
        project_names = self.get_project_names()
        if not project_name in project_names:
            messagebox.showerror("Error", "%s is not in the database" %(project_name))
            return

        # Modify the database
        if modify_type == "update":
            self.update_row(project_name, begin_time, self.begin_row["project_name"], self.begin_row["time"], "BEGIN")
            self.update_row(project_name, end_time, self.end_row["project_name"], self.end_row["time"], "END")
        elif modify_type == "delete":
            self.delete_row(self.begin_row["project_name"], self.begin_row["time"], "BEGIN")
            self.delete_row(self.end_row["project_name"], self.end_row["time"], "END")
        elif modify_type == "add":
            self.create_row(project_name, begin_time, "BEGIN")
            self.create_row(project_name, end_time, "END")

        # Update the canvas
        self.w.delete("legend")
        self.create_legend()
        self.w.delete("project_times")
        self.add_all_working_time()

        # Remove the window
        self.modify_times_window.destroy()

    def add_time_row(self):
        self.modify_time_row("add")

    def delete_time_row(self):
        self.modify_time_row("delete")

    def update_time_row(self):
        self.modify_time_row("update")

    def get_clicked_time(self, event):
        # Get clicked time
        x, y = event.x, event.y
        # Get the current day
        start_of_week = self.reference_day.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=self.reference_day.weekday())
        number_of_day_in_week = int((x-self.left_width_offset)/self.between_days_range)
        clicked_day = start_of_week + timedelta(days=number_of_day_in_week)
        # Get the current hour
        first_hour = timedelta(hours=6)
        last_hour = timedelta(hours=20)
        clicked_hour = first_hour + ((last_hour-first_hour)*(y-self.up_heigth_offset))/(self.grid_heigth)
        # Merge in the current time
        clicked_time = clicked_day + clicked_hour

        return clicked_time

    def modify_times(self, event, modify_type):
        clicked_time = self.get_clicked_time(event)

        # Get associated rows
        if modify_type == "update_or_delete":
            self.begin_row = self.get_begin_row_from_time(clicked_time)
            self.end_row = self.get_end_row_from_time(clicked_time)
            begin_printed_time = self.begin_row["time"]
            end_printed_time = self.end_row["time"]
        elif modify_type == "add":
            begin_printed_time = clicked_time.strftime(format="%Y-%m-%d %H:%M:%S")
            end_printed_time = (clicked_time + timedelta(hours=1)).strftime(format="%Y-%m-%d %H:%M:%S")

        # Create window with these infos
        index_row = 1
        if modify_type == "update_or_delete":
            window_title = "Update or delete project block"
        elif modify_type == "add":
            window_title = "Add project block"
        self.modify_times_window = tk.Toplevel(self.w)
        self.modify_times_window.title(window_title)

        # Project date
        index_row+=1
        self.modify_times_date_label = tk.Label(self.modify_times_window, text=begin_printed_time.split(" ")[0])
        self.modify_times_date_label.grid(row=index_row, column=1, columnspan=5)

        # Project name
        index_row+=1
        project_names = self.get_project_names()
        self.modify_times_project_name_combobox = ttk.Combobox(self.modify_times_window, state='readonly', values=project_names)
        if project_names:
            if modify_type == "update_or_delete":
                project_name_index = project_names.index(self.begin_row["project_name"])
            elif modify_type == "add":
                project_name_index = 0
            self.modify_times_project_name_combobox.current(project_name_index)
        self.modify_times_project_name_combobox.grid(row=index_row, column=1, columnspan=5)

        # Begin hour
        index_row+=1
        begin_hour_strvar = tk.StringVar()
        begin_hour_strvar.set(begin_printed_time.split(" ")[1].split(":")[0])
        self.begin_hour_entry = tk.Entry(self.modify_times_window, width=2, textvariable=begin_hour_strvar)
        self.begin_hour_entry.grid(row=index_row, column=1)
        self.begin_hour_label = tk.Label(self.modify_times_window, text=":")
        self.begin_hour_label.grid(row=index_row, column=2)
        begin_minute_strvar = tk.StringVar()
        begin_minute_strvar.set(begin_printed_time.split(" ")[1].split(":")[1])
        self.begin_minute_entry = tk.Entry(self.modify_times_window, width=2, textvariable=begin_minute_strvar)
        self.begin_minute_entry.grid(row=index_row, column=3)
        self.begin_minute_label = tk.Label(self.modify_times_window, text=":")
        self.begin_minute_label.grid(row=index_row, column=4)
        begin_second_strvar = tk.StringVar()
        begin_second_strvar.set(begin_printed_time.split(" ")[1].split(":")[2])
        self.begin_second_entry = tk.Entry(self.modify_times_window, width=2, textvariable=begin_second_strvar)
        self.begin_second_entry.grid(row=index_row, column=5)

        # end hour
        index_row+=1
        end_hour_strvar = tk.StringVar()
        end_hour_strvar.set(end_printed_time.split(" ")[1].split(":")[0])
        self.end_hour_entry = tk.Entry(self.modify_times_window, width=2, textvariable=end_hour_strvar)
        self.end_hour_entry.grid(row=index_row, column=1)
        self.end_hour_label = tk.Label(self.modify_times_window, text=":")
        self.end_hour_label.grid(row=index_row, column=2)
        end_minute_strvar = tk.StringVar()
        end_minute_strvar.set(end_printed_time.split(" ")[1].split(":")[1])
        self.end_minute_entry = tk.Entry(self.modify_times_window, width=2, textvariable=end_minute_strvar)
        self.end_minute_entry.grid(row=index_row, column=3)
        self.end_minute_label = tk.Label(self.modify_times_window, text=":")
        self.end_minute_label.grid(row=index_row, column=4)
        end_second_strvar = tk.StringVar()
        end_second_strvar.set(end_printed_time.split(" ")[1].split(":")[2])
        self.end_second_entry = tk.Entry(self.modify_times_window, width=2, textvariable=end_second_strvar)
        self.end_second_entry.grid(row=index_row, column=5)

        if modify_type == "update_or_delete":
            # Change button
            index_row+=1
            modify_button = tk.Button(self.modify_times_window, text="Update", command=self.update_time_row)
            modify_button.grid(row=index_row, column=1, columnspan=5)
            # Delete button
            index_row+=1
            modify_button = tk.Button(self.modify_times_window, text="Delete", command=self.delete_time_row)
            modify_button.grid(row=index_row, column=1, columnspan=5)
        elif modify_type == "add":
            # Add button
            index_row+=1
            add_button = tk.Button(self.modify_times_window, text="Add", command=self.add_time_row)
            add_button.grid(row=index_row, column=1, columnspan=5)

    def add_times(self, event):
        self.modify_times(event, "add")

    def update_or_delete_times(self, event):
        self.modify_times(event, "update_or_delete")

    def create_calendar(self):
        top = tk.Toplevel(self.root)

        prev_week_button = tk.Button(top, text="Prev week", command=self.set_prev_week)
        prev_week_button.grid(row=1, column=1)
        next_week_button = tk.Button(top, text="Next week", command=self.set_next_week)
        next_week_button.grid(row=1, column=2)

        self.w = tk.Canvas(top,
                   width=self.canvas_width,
                   height=self.canvas_height)
        self.w.grid(row=2, column=1, columnspan=2)

        self.create_invisible_rectangle()
        self.create_coordinates_lines()
        self.create_hour_lines()
        self.create_day_lines()
        self.create_legend()

        self.add_all_working_time()

        self.w.tag_bind("project_times", '<ButtonPress-1>', self.update_or_delete_times)
        self.w.tag_bind("add_times", "<ButtonPress-1>", self.add_times)

    ### Start

    def start(self):
        self.create_buttons()
        self.create_project_list()
        self.create_project_list_buttons()
        self.create_last_action_labels()
        self.create_summary_button()
        self.create_calendar_button()
        self.root.mainloop()

if __name__ == "__main__":
    my_work_timer = work_timer()
    my_work_timer.start()
