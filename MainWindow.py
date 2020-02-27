import tkinter as tk
from tkinter import ttk

class MainWindow:

    def __init__(self, root, project_names, last_action):
        root.title("Work Timer")
        self.create_timer_frame(root, project_names)
        self.create_project_list_buttons(root)
        self.create_last_action_labels(root, last_action)
        self.create_visualizations(root)

    # Create the view

    def create_timer_frame(self, root, project_names):
        timer_separator = ttk.Separator(root,orient=tk.HORIZONTAL)
        timer_separator.grid(row=1, column=1, sticky="ew")
        timer_label = tk.Label(root, text="Timer")
        timer_label.grid(row=1, column=1)
        timer_frame = tk.Frame(root)
        timer_frame.grid(row=2, column=1)

        # Project list
        project_label = tk.Label(timer_frame, text="Project name :")
        project_label.grid(row=1, column=1, columnspan=2)
        self.project_names_combo_box = ttk.Combobox(timer_frame, state='readonly', values=project_names)
        self.project_names_combo_box.grid(row=2, column=1, columnspan=2)
        if project_names:
            self.project_names_combo_box.current(0)

        # Start and stop buttons
        self.start_button = tk.Button(timer_frame, text="Start")
        self.start_button.grid(row=3,column=1)
        self.stop_button = tk.Button(timer_frame, text="Stop")
        self.stop_button.grid(row=3,column=2)

    def create_project_list_buttons(self, root):
        project_list_buttons_separator = ttk.Separator(root,orient=tk.HORIZONTAL)
        project_list_buttons_separator.grid(row=3, column=1, sticky="ew")
        project_list_buttons_label = tk.Label(root, text="Projects list")
        project_list_buttons_label.grid(row=3, column=1)
        project_list_buttons_frame = tk.Frame(root)
        project_list_buttons_frame.grid(row=4, column=1)

        self.add_project_button = tk.Button(project_list_buttons_frame, text="Add")
        self.add_project_button.grid(row=1,column=1)
        self.delete_project_button = tk.Button(project_list_buttons_frame, text="Delete")
        self.delete_project_button.grid(row=1,column=2)

    def create_last_action_labels(self, root, last_action):
        # Frame of the last action
        last_action_separator = ttk.Separator(root,orient=tk.HORIZONTAL)
        last_action_separator.grid(row=5, column=1, sticky="ew")
        last_action_label = tk.Label(root, text="Last action")
        last_action_label.grid(row=5, column=1)
        last_action_frame = tk.Frame(root)
        last_action_frame.grid(row=6, column=1)

        self.last_action_date_label = tk.Label(last_action_frame, text="Date :")
        self.last_action_date_label.grid(row=1, column=1, columnspan=1, sticky="e")
        self.last_action_date_var = tk.StringVar()
        self.last_action_date_var.set(last_action["time"].split(" ")[0])
        self.last_action_date_value_label = tk.Label(last_action_frame, textvariable=self.last_action_date_var)
        self.last_action_date_value_label.grid(row=1, column=2, columnspan=1, sticky="w")

        self.last_action_time_label = tk.Label(last_action_frame, text="Time :")
        self.last_action_time_label.grid(row=2, column=1, columnspan=1, sticky="e")
        self.last_action_time_var = tk.StringVar()
        self.last_action_time_var.set(last_action["time"].split(" ")[1])
        self.last_action_time_value_label = tk.Label(last_action_frame, textvariable=self.last_action_time_var)
        self.last_action_time_value_label.grid(row=2, column=2, columnspan=1, sticky="w")

        self.last_action_project_label = tk.Label(last_action_frame, text="Project :")
        self.last_action_project_label.grid(row=3, column=1, columnspan=1, sticky="e")
        self.last_action_project_var = tk.StringVar()
        self.last_action_project_var.set(last_action["project_name"])
        self.last_action_project_value_label = tk.Label(last_action_frame, textvariable=self.last_action_project_var)
        self.last_action_project_value_label.grid(row=3, column=2, columnspan=1, sticky="w")

        self.last_action_type_label = tk.Label(last_action_frame, text="Action :")
        self.last_action_type_label.grid(row=4, column=1, columnspan=1, sticky="e")
        self.last_action_type_var = tk.StringVar()
        if last_action["action_type"] == "BEGIN":
            last_action_type = "Start"
        else:
            last_action_type = "Stop"
        self.last_action_type_var.set(last_action_type)
        self.last_action_type_value_label = tk.Label(last_action_frame, textvariable=self.last_action_type_var)
        self.last_action_type_value_label.grid(row=4, column=2, columnspan=1, sticky="w")

    def create_summary_button(self, visualizations_frame):
        self.summary_button = tk.Button(visualizations_frame, text="Summary")
        self.summary_button.grid(row=1, column=1)

    def create_calendar_button(self, visualizations_frame):
        self.calendar_button = tk.Button(visualizations_frame, text="Calendar")
        self.calendar_button.grid(row=1, column=2)

    def create_visualizations(self, root):
        visualizations_separator = ttk.Separator(root,orient=tk.HORIZONTAL)
        visualizations_separator.grid(row=7, column=1, sticky="ew")
        visualizations_label = tk.Label(root, text="Visualization")
        visualizations_label.grid(row=7, column=1)
        visualizations_frame = tk.Frame(root)
        visualizations_frame.grid(row=8, column=1)

        self.create_summary_button(visualizations_frame)
        self.create_calendar_button(visualizations_frame)

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

    def update_last_action_labels(self, new_time, new_project_name, new_action_type):
        self.last_action_date_var.set(new_time.split(" ")[0])
        self.last_action_time_var.set(new_time.split(" ")[1])
        self.last_action_project_var.set(new_project_name)
        self.last_action_type_var.set(new_action_type)

    # Set commands

    def set_start_button_command(self, function):
        self.start_button.config(command=function)

    def set_stop_button_command(self, function):
        self.stop_button.config(command=function)

    def set_add_project_button_command(self, function):
        self.add_project_button.config(command=function)

    def set_delete_project_button_command(self, function):
        self.delete_project_button.config(command=function)

    def set_summary_button_command(self, function):
        self.summary_button.config(command=function)

    def set_calendar_button_command(self, function):
        self.calendar_button.config(command=function)
