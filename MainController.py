from datetime import datetime, timedelta

from tkinter import messagebox

from DatabaseInterface import DatabaseInterface

from MainWindow import MainWindow

from ModifyProjectNamesController import ModifyProjectNamesController
from SummaryController import SummaryController
from CalendarController import CalendarController

class MainController:

    def __init__(self, root):
        # Variables
        self.database_interface = DatabaseInterface()
        self.root = root

        # Time format
        self.time_format = '%Y-%m-%d %H:%M:%S'

        # Get variables to create the main window
        last_action = self.database_interface.get_last_action()
        if last_action is None:
            last_action = {"time": "N/A N/A", "project_name": "N/A", "action_type": "N/A"}
        project_names = self.database_interface.get_project_names()

        # Create the main window
        self.main_window = MainWindow(self.root, project_names, last_action)

        # Start and stop buttons
        self.main_window.set_start_button_command(self.add_work_time)
        self.main_window.set_stop_button_command(self.end_work_time)

        # Add and delete project buttons
        self.main_window.set_add_project_button_command(self.create_add_project_window)
        self.main_window.set_modify_project_button_command(self.create_modify_project_window)
        # self.main_window.set_delete_project_button_command(self.create_delete_project_window)

        # Summary button
        self.main_window.set_summary_button_command(self.create_summary_window)

        # Calendar button
        self.main_window.set_calendar_button_command(self.create_calendar_window)

    # Start and stop buttons

    def write_work_time(self, project_name, now, action_type):
        self.database_interface.create_row(project_name, now, action_type)
        if action_type == self.database_interface.begin_action:
            action_type = "Start"
        else:
            action_type = "Stop"
        self.main_window.update_last_action_labels(now, project_name, action_type)

    def is_project_names(self):
        project_names = self.database_interface.get_project_names()
        if not project_names:
            messagebox.error("Error", "The project list is empty")
            return False
        return True

    def add_work_time(self):
        if self.is_project_names():
            self.end_work_time()
            active_project_name = self.main_window.get_active_project_name()
            now = datetime.now().strftime(self.time_format)
            self.write_work_time(active_project_name, now, self.database_interface.begin_action)

    def fill_missing_days(self, now, last_action):
        last_date = datetime.strptime(last_action["time"], self.time_format)
        while (last_date.day < now.day):
            # Write the time to the end of the day
            last_date_end_day = last_date.replace(hour=23, minute=59, second=59, microsecond=0).strftime(self.time_format)
            self.write_work_time(last_action["project_name"], last_date_end_day, self.database_interface.end_action)
            # Write the time begining the next day
            last_date = last_date + timedelta(days=1)
            last_date_begin_day = last_date.replace(hour=0, minute=0, second=0, microsecond=0).strftime(self.time_format)
            self.write_work_time(last_action["project_name"], last_date_begin_day, self.database_interface.begin_action)

    def end_work_time(self):
        if self.is_project_names():
            last_action = self.database_interface.get_last_action()
            if last_action and last_action["action_type"] == self.database_interface.begin_action:
                    now = datetime.now()
                    self.fill_missing_days(now, last_action)
                    now_str = now.strftime(self.time_format)
                    self.write_work_time(last_action["project_name"], now_str, self.database_interface.end_action)

    # Add and delete project buttons

    def create_add_project_window(self):
        modify_project_names_controller = ModifyProjectNamesController(self.root, self.main_window, "add")

    def create_modify_project_window(self):
        modify_project_names_controller = ModifyProjectNamesController(self.root, self.main_window, "modify")

    # def create_delete_project_window(self):
    #     modify_project_names_controller = ModifyProjectNamesController(self.root, self.main_window, "delete")

    # Summary button

    def create_summary_window(self):
        summary_controller = SummaryController(self.root)

    # Calendar button

    def create_calendar_window(self):
        calendar_controller = CalendarController(self.root)
