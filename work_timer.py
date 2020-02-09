from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar
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
        # Constants
        self.time_database_path = "time_database.csv"
        self.time_database_header = ["time", "project_name", "action_type"]
        self.project_list_database_pah = "project_list_database.csv"
        self.project_list_database_header = ["project_name"]
        self.database_path = "work_timer.db"
        self.end_action = "END"
        self.begin_action = "BEGIN"

        # Database connection
        self.conn = sqlite3.connect(self.database_path)

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
        self.week_day = datetime.today()

        # Tkinter
        self.root = tk.Tk()
        self.root.title("Work Timer")

        self.init_work_timer()

    ### Manage databases

    def create_time_database(self):
        with open(self.time_database_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(self.time_database_header)

    def create_project_list_database(self):
        with open(self.project_list_database_pah, "w") as file:
            writer = csv.writer(file)
            writer.writerow(self.project_list_database_header)

    def create_database_tables(self):
        c = self.conn.cursor()
        c.execute("CREATE TABLE project_names (project_name text)")
        c.execute("CREATE TABLE times (time text, project_name text, action_type text)")
        self.conn.commit()

    def add_project_name_in_database(self):
        # Get the project_name
        project_name = None
        # Add the project_name
        c = self.conn.cursor()
        c.execute("INSERT INTO project_names VALUES (?)", (project_name,))
        self.conn.commit()

    def remove_project_name_in_database(self):
        # Get the project_name
        project_name = None
        # Add the project_name
        c = self.conn.cursor()
        c.execute("DELETE FROM project_names WHERE project_name=?", (project_name,))
        self.conn.commit()

    def init_work_timer(self):
        if not os.path.isfile(self.time_database_path):
            self.create_time_database()
        if not os.path.isfile(self.project_list_database_pah):
            self.create_project_list_database()

    def get_project_names(self):
        project_names = []
        with open(self.project_list_database_pah, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                project_names.append(row[self.project_list_database_header[0]])
        return project_names

    def is_project_name_database_empty(self):
        project_names = self.get_project_names()
        if project_names:
            return False
        else:
            return True

    def get_last_action(self):
        with open(self.time_database_path, "r") as file:
            reader = csv.DictReader(file)
            reader_list = list(reader)
        if len(reader_list) == 0:
            return {"time": "N/A N/A", "project_name": "N/A", "action_type": "N/A"}
        else:
            return reader_list[-1]

    def get_active_project_name(self):
        active_project_name = self.project_names_combo_box.get()
        return active_project_name

    def write_work_time(self, active_project_name, action_type, last_action_time):
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        line = [now, active_project_name, action_type]
        with open(self.time_database_path, "a") as file:
            writer = csv.writer(file)
            writer.writerow(line)
        self.update_last_action_labels(now, active_project_name)

    def add_work_time(self):
        last_action = self.get_last_action()
        if last_action["action_type"] != self.end_action and last_action["action_type"] != "N/A":
            self.end_work_time()
        last_action = self.get_last_action()
        active_project_name = self.get_active_project_name()
        self.write_work_time(active_project_name, self.begin_action, last_action['time'])

    def end_work_time(self):
        last_action = self.get_last_action()
        if last_action["action_type"] != self.end_action and last_action["action_type"] != "N/A":
            self.write_work_time(last_action["project_name"], self.end_action, last_action['time'])

    ### Process data

    def create_summary_table(self):
        # Read the time database
        time_df = pd.read_csv(self.time_database_path)
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
        self.project_names_combo_box.current(0)

    def create_last_action_labels(self):
        last_action = self.get_last_action()
        self.last_action_label = tk.Label(self.root, text="Last update :")
        self.last_action_label.grid(row=3, column=1, columnspan=2)

        self.last_action_date_label = tk.Label(self.root, text="Date :")
        self.last_action_date_label.grid(row=4, column=1, columnspan=1, sticky="e")
        self.last_action_date_var = tk.StringVar()
        self.last_action_date_var.set(last_action["time"].split(" ")[0])
        self.last_action_date_value_label = tk.Label(self.root, textvariable=self.last_action_date_var)
        self.last_action_date_value_label.grid(row=4, column=2, columnspan=1, sticky="w")

        self.last_action_time_label = tk.Label(self.root, text="Time :")
        self.last_action_time_label.grid(row=5, column=1, columnspan=1, sticky="e")
        self.last_action_time_var = tk.StringVar()
        self.last_action_time_var.set(last_action["time"].split(" ")[1])
        self.last_action_time_value_label = tk.Label(self.root, textvariable=self.last_action_time_var)
        self.last_action_time_value_label.grid(row=5, column=2, columnspan=1, sticky="w")

        self.last_action_project_label = tk.Label(self.root, text="Project :")
        self.last_action_project_label.grid(row=6, column=1, columnspan=1, sticky="e")
        self.last_action_project_var = tk.StringVar()
        self.last_action_project_var.set(last_action["project_name"])
        self.last_action_project_value_label = tk.Label(self.root, textvariable=self.last_action_project_var)
        self.last_action_project_value_label.grid(row=6, column=2, columnspan=1, sticky="w")

    def create_summary_button(self):
        self.summary_button = tk.Button(self.root, text="Summary", command=self.create_summary_table_tree)
        self.summary_button.grid(row=7, column=1, columnspan=2)

    def create_calendar_button(self):
        self.summary_button = tk.Button(self.root, text="Calendar", command=self.create_calendar)
        self.summary_button.grid(row=8, column=1, columnspan=2)

    def update_last_action_labels(self, time, project_name):
        self.last_action_date_var.set(time.split(" ")[0])
        self.last_action_time_var.set(time.split(" ")[1])
        self.last_action_project_var.set(project_name)

    def create_summary_table_tree(self):
        time_df = self.create_summary_table()

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

    def create_coordinates_lines(self):
        self.w.create_line(0, self.up_heigth_offset, self.left_width_offset+self.grid_width, self.up_heigth_offset)
        self.w.create_line(self.left_width_offset, 0, self.left_width_offset, self.up_heigth_offset+self.grid_heigth)

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
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        index = 0
        for x in range(self.left_width_offset+self.between_days_range, self.canvas_width-self.right_width_offset, self.between_days_range):
            self.w.create_line(x, 0, x, self.canvas_height-self.down_heigth_offset)
            self.w.create_text(x-int(self.between_days_range/2), int(self.up_heigth_offset/2), text=weekdays[index])
            index+=1

    def create_legend(self):
        df = pd.read_csv(self.time_database_path)
        project_names = df["project_name"].unique()
        index = 0
        for project_name in project_names:
            self.project_color_dict[project_name] = self.project_colors[index]
            height_space = 20
            self.w.create_rectangle(self.canvas_width-self.right_width_offset+10, index*height_space+100, self.canvas_width-self.right_width_offset+30, 110+index*height_space, fill=self.project_color_dict[project_name])
            self.w.create_text(self.canvas_width-self.right_width_offset+35, 105+index*height_space, text=project_name, anchor="w")
            index+=1

    def add_working_time(self, first_project_date, last_project_date, first_day_date, last_day_date, day_int, color):
        begin_time_first = (((first_project_date-first_day_date)*(self.grid_heigth))/(last_day_date-first_day_date))+self.up_heigth_offset
        last_time_first = (((last_project_date-first_day_date)*(self.grid_heigth))/(last_day_date-first_day_date))+self.up_heigth_offset
        self.w.create_rectangle(self.left_width_offset+day_int*self.between_days_range+10, begin_time_first, self.left_width_offset+(day_int+1)*self.between_days_range-10, last_time_first, fill=color, tags="project_times")

    def add_all_working_time(self):
        df = pd.read_csv(self.time_database_path)
        df["time"] = pd.to_datetime(df["time"])

        # Only keep the current week
        start_of_week = self.week_day - timedelta(days=self.week_day.weekday())  # Monday
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=0)
        df = df[ (df["time"] >= start_of_week) & (df["time"] <= end_of_week) ]

        df["last_time"] = df["time"].shift()
        df = df[ df["action_type"] == "END" ]
        for row in df.itertuples(index=False):
            self.add_working_time(row.time, row.last_time, row.time.replace(hour=6, minute=0, second=0), row.last_time.replace(hour=20, minute=0, second=0), row.time.weekday(), self.project_color_dict[row.project_name])

    def set_prev_week(self):
        self.week_day = self.week_day - timedelta(days=7)
        self.w.delete("project_times")
        self.add_all_working_time()

    def set_next_week(self):
        self.week_day = self.week_day + timedelta(days=7)
        self.w.delete("project_times")
        self.add_all_working_time()

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

        self.create_coordinates_lines()
        self.create_hour_lines()
        self.create_day_lines()
        self.create_legend()

        self.add_all_working_time()

    ### Start

    def start(self):
        if self.is_project_name_database_empty():
            messagebox.showerror("Error", "The project database is empty")
            sys.exit(1)
        self.create_buttons()
        self.create_project_list()
        self.create_last_action_labels()
        self.create_summary_button()
        self.create_calendar_button()
        self.root.mainloop()

if __name__ == "__main__":
    my_work_timer = work_timer()
    my_work_timer.start()
