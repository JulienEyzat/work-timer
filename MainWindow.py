import tkinter as tk
from tkinter import ttk

class MainWindow:

    def __init__(self, root, project_names, last_action):
        root.title("Work Timer")
        self.create_start_stop_buttons(root)
        self.create_project_list(root, project_names)
        self.create_project_list_buttons(root)
        self.create_last_action_labels(root, last_action)
        self.create_summary_button(root)
        self.create_calendar_button(root)

    # Create the view

    def create_start_stop_buttons(self, root):
        self.start_button = tk.Button(root, text="Start")
        self.start_button.grid(row=1,column=1)
        self.stop_button = tk.Button(root, text="End")
        self.stop_button.grid(row=1,column=2)

    def create_project_list(self, root, project_names):
        self.project_names_combo_box = ttk.Combobox(root, state='readonly', values=project_names)
        self.project_names_combo_box.grid(row=2, column=1, columnspan=2)
        if project_names:
            self.project_names_combo_box.current(0)

    def create_project_list_buttons(self, root):
        self.add_project_button = tk.Button(root, text="Add")
        self.add_project_button.grid(row=3,column=1)
        self.remove_project_button = tk.Button(root, text="Remove")
        self.remove_project_button.grid(row=3,column=2)

    def create_last_action_labels(self, root, last_action):
        self.last_action_label = tk.Label(root, text="Last update :")
        self.last_action_label.grid(row=4, column=1, columnspan=2)

        self.last_action_date_label = tk.Label(root, text="Date :")
        self.last_action_date_label.grid(row=5, column=1, columnspan=1, sticky="e")
        self.last_action_date_var = tk.StringVar()
        self.last_action_date_var.set(last_action["time"].split(" ")[0])
        self.last_action_date_value_label = tk.Label(root, textvariable=self.last_action_date_var)
        self.last_action_date_value_label.grid(row=5, column=2, columnspan=1, sticky="w")

        self.last_action_time_label = tk.Label(root, text="Time :")
        self.last_action_time_label.grid(row=6, column=1, columnspan=1, sticky="e")
        self.last_action_time_var = tk.StringVar()
        self.last_action_time_var.set(last_action["time"].split(" ")[1])
        self.last_action_time_value_label = tk.Label(root, textvariable=self.last_action_time_var)
        self.last_action_time_value_label.grid(row=6, column=2, columnspan=1, sticky="w")

        self.last_action_project_label = tk.Label(root, text="Project :")
        self.last_action_project_label.grid(row=7, column=1, columnspan=1, sticky="e")
        self.last_action_project_var = tk.StringVar()
        self.last_action_project_var.set(last_action["project_name"])
        self.last_action_project_value_label = tk.Label(root, textvariable=self.last_action_project_var)
        self.last_action_project_value_label.grid(row=7, column=2, columnspan=1, sticky="w")

    def create_summary_button(self, root):
        self.summary_button = tk.Button(root, text="Summary")
        self.summary_button.grid(row=8, column=1, columnspan=2)

    def create_calendar_button(self, root):
        self.calendar_button = tk.Button(root, text="Calendar")
        self.calendar_button.grid(row=9, column=1, columnspan=2)

    # Get informations on the view

    def get_active_project_name(self):
        active_project_name = self.project_names_combo_box.get()
        return active_project_name

    # Update

    def update_project_names_combo_box(self, project_names):
        self.project_names_combo_box.config(values=project_names)
        if project_names:
            self.project_names_combo_box.current(len(project_names)-1)
        else:
            self.project_names_combo_box.set("")

    def update_last_action_labels(self, new_time, new_project_name):
        self.last_action_date_var.set(new_time.split(" ")[0])
        self.last_action_time_var.set(new_time.split(" ")[1])
        self.last_action_project_var.set(new_project_name)
