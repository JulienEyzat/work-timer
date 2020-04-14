from tkinter import messagebox
from datetime import timedelta
import pandas as pd

from DatabaseInterface import DatabaseInterface
from ModifyCalendarWindow import ModifyCalendarWindow

class ModifyCalendarController:

    def __init__(self, parent_window, caller_window, modify_type, clicked_time):
        self.database_interface = DatabaseInterface()

        # Get the window of the caller
        self.caller_window = caller_window

        # Initial values of times
        self.init_begin_time = self.database_interface.get_begin_row_from_time(clicked_time)
        self.init_end_time = self.database_interface.get_end_row_from_time(clicked_time)

        # Create the window
        begin_printed_time, end_printed_time = self.get_printed_times(clicked_time, modify_type)
        project_names = self.database_interface.get_project_names()
        current_project_name = self.init_begin_time["project_name"]
        self.modify_calendar_window = ModifyCalendarWindow(parent_window, modify_type, begin_printed_time, end_printed_time, project_names, current_project_name)

        # Modify buttons
        if modify_type == "update_or_delete":
            self.modify_calendar_window.set_update_button_command(self.update_time_row)
            self.modify_calendar_window.set_delete_button_command(self.delete_time_row)
        elif modify_type == "add":
            self.modify_calendar_window.set_add_button_command(self.add_time_row)

    # Get printed times

    def get_printed_times(self, clicked_time, modify_type):
        if modify_type == "update_or_delete":
            begin_printed_time = self.init_begin_time["time"]
            end_printed_time = self.init_end_time["time"]
        elif modify_type == "add":
            begin_printed_time = clicked_time.strftime(format="%Y-%m-%d %H:%M:%S")
            end_printed_time = (clicked_time + timedelta(hours=1)).strftime(format="%Y-%m-%d %H:%M:%S")

        return begin_printed_time, end_printed_time

    # Modify buttons

    def get_entry_time(self, entry_time, time_type):
        # Test if the time entered is ok
        if not entry_time.isdigit():
            return None
        entry_time = int(entry_time)
        if time_type == "hour" and (entry_time < 0 or entry_time > 23):
            return None
        if time_type in ["minute", "second"] and (entry_time < 0 or entry_time > 59):
            return None
        # Convert the time to a good string format
        entry_time = str(entry_time)
        if len(entry_time) == 1:
            entry_time = "0%s" %(entry_time)
        return entry_time

    def modify_time_row(self, modify_type):
        # Get the new values
        project_name = self.modify_calendar_window.get_project_name()
        row_date = self.modify_calendar_window.get_date()
        begin_hour = self.get_entry_time(self.modify_calendar_window.get_begin_hour(), "hour")
        begin_minute = self.get_entry_time(self.modify_calendar_window.get_begin_minute(), "minute")
        begin_second = self.get_entry_time(self.modify_calendar_window.get_begin_second(), "second")
        end_hour = self.get_entry_time(self.modify_calendar_window.get_end_hour(), "hour")
        end_minute = self.get_entry_time(self.modify_calendar_window.get_end_minute(), "minute")
        end_second = self.get_entry_time(self.modify_calendar_window.get_end_second(), "second")

        if None in [begin_hour, begin_minute, begin_second, end_hour, end_minute, end_second]:
            messagebox.showerror("Error", "A time is not well formated")
            return

        begin_time = "%s %s:%s:%s" %(row_date, begin_hour, begin_minute, begin_second)
        end_time = "%s %s:%s:%s" %(row_date, end_hour, end_minute, end_second)

        # Check if the new time does not overlap another one
        df = self.database_interface.get_dataframe_all_times()
        df["time"] = pd.to_datetime(df["time"])
        df["last_time"] = df["time"].shift()
        df = df[ df["action_type"] == "END" ]

        begin_datetime = pd.to_datetime(begin_time)
        end_datetime = pd.to_datetime(end_time)

        if not df[ ((df["last_time"] > begin_datetime) & (df["last_time"] < end_datetime)) | ((df["time"] > begin_datetime) & (df["time"] < end_datetime)) ].empty:
            messagebox.showerror("Error", "The new time overlap another block")
            return

        if not df[ ((begin_datetime > df["last_time"]) & (begin_datetime < df["time"])) | ((end_datetime > df["last_time"]) & (end_datetime < df["time"])) ].empty:
            messagebox.showerror("Error", "The new time overlap another block")
            return

        # Get all the project names
        project_names = self.database_interface.get_project_names()
        if not project_name in project_names:
            messagebox.showerror("Error", "%s is not in the database" %(project_name))
            return

        # Modify the database
        if modify_type == "update":
            self.database_interface.update_row(project_name, begin_time, self.init_begin_time["project_name"], self.init_begin_time["time"], self.database_interface.begin_action)
            self.database_interface.update_row(project_name, end_time, self.init_end_time["project_name"], self.init_end_time["time"], self.database_interface.end_action)
        elif modify_type == "delete":
            self.database_interface.delete_row(self.init_begin_time["project_name"], self.init_begin_time["time"], self.database_interface.begin_action)
            self.database_interface.delete_row(self.init_end_time["project_name"], self.init_end_time["time"], self.database_interface.end_action)
        elif modify_type == "add":
            self.database_interface.create_row(project_name, begin_time, self.database_interface.begin_action)
            self.database_interface.create_row(project_name, end_time, self.database_interface.end_action)

        # Update the canvas
        project_names = self.database_interface.get_project_names()
        times_df = self.database_interface.get_dataframe_times()
        self.caller_window.update_calendar_project_block(project_names, times_df)

        # Remove the window
        self.modify_calendar_window.destroy_window()

    def add_time_row(self):
        self.modify_time_row("add")

    def delete_time_row(self):
        self.modify_time_row("delete")

    def update_time_row(self):
        self.modify_time_row("update")
