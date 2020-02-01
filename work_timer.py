from datetime import datetime
import tkinter as tk
from tkinter import ttk
import time
import csv
import os

class work_timer:
    def __init__(self):
        self.time_database_path = "time_database.csv"
        self.time_database_header = ["time", "project_name", "action_type"]
        self.project_list_database_pah = "project_list_database.csv"
        self.project_list_database_header = ["project_name"]
        self.end_action = "END"
        self.begin_action = "BEGIN"
        self.root = tk.Tk()

        self.init_work_timer()

    def create_time_database(self):
        with open(self.time_database_path, "w") as file:
            writer = csv.writer(file)
            writer.writerow(self.time_database_header)

    def create_project_list_database(self):
        with open(self.project_list_database_pah, "w") as file:
            writer = csv.writer(file)
            writer.writerow(self.project_list_database_header)

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
        while now == last_action_time:
            time.sleep(1)
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

    def update_last_action_labels(self, time, project_name):
        self.last_action_date_var.set(time.split(" ")[0])
        self.last_action_time_var.set(time.split(" ")[1])
        self.last_action_project_var.set(project_name)

    def start(self):
        self.create_buttons()
        self.create_project_list()
        self.create_last_action_labels()
        self.root.mainloop()

if __name__ == "__main__":
    my_work_timer = work_timer()
    my_work_timer.start()
