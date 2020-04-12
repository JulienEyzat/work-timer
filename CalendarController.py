from datetime import datetime, timedelta

from DatabaseInterface import DatabaseInterface
from CalendarWindow import CalendarWindow
from ModifyCalendarController import ModifyCalendarController

class CalendarController:

    def __init__(self, parent_window):
        # Database interface
        self.database_interface = DatabaseInterface()

        # Create the window
        project_names = self.database_interface.get_project_names()
        times_df = self.database_interface.get_dataframe_times()
        self.calendar_window = CalendarWindow(parent_window, project_names, times_df)

        # Prev and next week buttons
        self.calendar_window.set_prev_week_button_command(self.set_prev_week)
        self.calendar_window.set_next_week_button_command(self.set_next_week)

        # Click inside the canvas
        self.calendar_window.set_project_blocks_command(self.update_or_delete_project_block)
        self.calendar_window.set_add_project_blocks_command(self.add_project_block)

    # Prev and next week buttons

    def set_prev_week(self):
        reference_day = self.calendar_window.reference_day - timedelta(days=7)
        times_df = self.database_interface.get_dataframe_times()
        self.calendar_window.update_calendar_week(reference_day, times_df)

    def set_next_week(self):
        reference_day = self.calendar_window.reference_day + timedelta(days=7)
        times_df = self.database_interface.get_dataframe_times()
        self.calendar_window.update_calendar_week(reference_day, times_df)

    # Add, update and remove project blocks

    def get_clicked_time(self, event):
        # Get clicked time
        x, y = event.x, event.y
        # Get the current day
        start_of_week = self.calendar_window.reference_day.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=self.calendar_window.reference_day.weekday())
        current_day_in_week = int((x-self.calendar_window.left_width_offset)/self.calendar_window.between_days_range)
        clicked_day = start_of_week + timedelta(days=current_day_in_week)
        # Get the current hour
        first_hour = timedelta(hours=self.calendar_window.first_hour)
        last_hour = timedelta(hours=self.calendar_window.last_hour)
        clicked_hour = first_hour + ((last_hour-first_hour)*(y-self.calendar_window.up_heigth_offset))/(self.calendar_window.grid_heigth)
        # Merge in the current time
        clicked_time = clicked_day + clicked_hour

        return clicked_time

    def add_project_block(self, event):
        clicked_time = self.get_clicked_time(event)
        modify_calendar_controller = ModifyCalendarController(self.calendar_window.w, self.calendar_window, "add", clicked_time)

    def update_or_delete_project_block(self, event):
        clicked_time = self.get_clicked_time(event)
        modify_calendar_controller = ModifyCalendarController(self.calendar_window.w, self.calendar_window, "update_or_delete", clicked_time)
