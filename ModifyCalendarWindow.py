import tkinter as tk
from tkinter import ttk

class ModifyCalendarWindow:

    def __init__(self, parent_window, modify_type, begin_printed_time, end_printed_time, project_names, current_project_name):
        self.create_window(parent_window, modify_type)
        self.create_date_label(begin_printed_time)
        self.create_project_name_combo_box(project_names, modify_type, current_project_name)
        self.create_modify_begin_hour(begin_printed_time)
        self.create_modify_end_hour(end_printed_time)
        self.create_modify_buttons(modify_type)

    def create_window(self, parent_window, modify_type):
        if modify_type == "update_or_delete":
            window_title = "Update or delete project block"
        elif modify_type == "add":
            window_title = "Add project block"
        self.modify_times_window = tk.Toplevel(parent_window)
        self.modify_times_window.title(window_title)

    def create_date_label(self, begin_printed_time):
        # Project date
        self.modify_times_date_label = tk.Label(self.modify_times_window, text=begin_printed_time.split(" ")[0])
        self.modify_times_date_label.grid(row=1, column=1, columnspan=6)

    def create_project_name_combo_box(self, project_names, modify_type, current_project_name):
        # Project name
        self.modify_times_project_name_combobox = ttk.Combobox(self.modify_times_window, state='readonly', values=project_names)
        if project_names:
            if modify_type == "update_or_delete":
                project_name_index = project_names.index(current_project_name)
            elif modify_type == "add":
                project_name_index = 0
            self.modify_times_project_name_combobox.current(project_name_index)
        self.modify_times_project_name_combobox.grid(row=2, column=1, columnspan=6)

    def create_modify_begin_hour(self, begin_printed_time):
        # Begin hour
        index_row = 3

        # Time label
        self.begin_time_label = tk.Label(self.modify_times_window, text="Begin :")
        self.begin_time_label.grid(row=index_row, column=1, sticky="e")

        # Time
        begin_hour_strvar = tk.StringVar()
        begin_hour_strvar.set(begin_printed_time.split(" ")[1].split(":")[0])
        self.begin_hour_entry = tk.Entry(self.modify_times_window, width=2, textvariable=begin_hour_strvar)
        self.begin_hour_entry.grid(row=index_row, column=2, sticky="w")
        self.begin_hour_label = tk.Label(self.modify_times_window, width=1, text=":")
        self.begin_hour_label.grid(row=index_row, column=3, sticky="w")
        begin_minute_strvar = tk.StringVar()
        begin_minute_strvar.set(begin_printed_time.split(" ")[1].split(":")[1])
        self.begin_minute_entry = tk.Entry(self.modify_times_window, width=2, textvariable=begin_minute_strvar)
        self.begin_minute_entry.grid(row=index_row, column=4, sticky="w")
        self.begin_minute_label = tk.Label(self.modify_times_window, width=1, text=":")
        self.begin_minute_label.grid(row=index_row, column=5, sticky="w")
        begin_second_strvar = tk.StringVar()
        begin_second_strvar.set(begin_printed_time.split(" ")[1].split(":")[2])
        self.begin_second_entry = tk.Entry(self.modify_times_window, width=2, textvariable=begin_second_strvar)
        self.begin_second_entry.grid(row=index_row, column=6, sticky="w")

    def create_modify_end_hour(self, end_printed_time):
        # end hour
        index_row = 4

        # Time label
        self.end_time_label = tk.Label(self.modify_times_window, text="End :")
        self.end_time_label.grid(row=index_row, column=1, sticky="e")

        # Time
        end_hour_strvar = tk.StringVar()
        end_hour_strvar.set(end_printed_time.split(" ")[1].split(":")[0])
        self.end_hour_entry = tk.Entry(self.modify_times_window, width=2, textvariable=end_hour_strvar)
        self.end_hour_entry.grid(row=index_row, column=2, sticky="w")
        self.end_hour_label = tk.Label(self.modify_times_window, text=":")
        self.end_hour_label.grid(row=index_row, column=3, sticky="w")
        end_minute_strvar = tk.StringVar()
        end_minute_strvar.set(end_printed_time.split(" ")[1].split(":")[1])
        self.end_minute_entry = tk.Entry(self.modify_times_window, width=2, textvariable=end_minute_strvar)
        self.end_minute_entry.grid(row=index_row, column=4, sticky="w")
        self.end_minute_label = tk.Label(self.modify_times_window, text=":")
        self.end_minute_label.grid(row=index_row, column=5, sticky="w")
        end_second_strvar = tk.StringVar()
        end_second_strvar.set(end_printed_time.split(" ")[1].split(":")[2])
        self.end_second_entry = tk.Entry(self.modify_times_window, width=2, textvariable=end_second_strvar)
        self.end_second_entry.grid(row=index_row, column=6, sticky="w")

    def create_modify_buttons(self, modify_type):
        if modify_type == "update_or_delete":
            # Change button
            self.update_button = tk.Button(self.modify_times_window, text="Update")
            self.update_button.grid(row=5, column=1, columnspan=6)
            # Delete button
            self.delete_button = tk.Button(self.modify_times_window, text="Delete")
            self.delete_button.grid(row=6, column=1, columnspan=6)
        elif modify_type == "add":
            # Add button
            self.add_button = tk.Button(self.modify_times_window, text="Add")
            self.add_button.grid(row=5, column=1, columnspan=6)

    # Getters

    def get_project_name(self):
        return self.modify_times_project_name_combobox.get()

    def get_date(self):
        return self.modify_times_date_label.cget("text")

    def get_begin_hour(self):
        return self.begin_hour_entry.get()
    def get_begin_minute(self):
        return self.begin_minute_entry.get()
    def get_begin_second(self):
        return self.begin_second_entry.get()
    def get_end_hour(self):
        return self.end_hour_entry.get()
    def get_end_minute(self):
        return self.end_minute_entry.get()
    def get_end_second(self):
        return self.end_second_entry.get()

    # Destroy

    def destroy_window(self):
        self.modify_times_window.destroy()

    # Set commands

    def set_update_button_command(self, function):
        self.update_button.config(command=function)

    def set_add_button_command(self, function):
        self.add_button.config(command=function)

    def set_delete_button_command(self, function):
        self.delete_button.config(command=function)
