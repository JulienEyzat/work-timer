from datetime import datetime, timedelta
from matplotlib import cm
from matplotlib import colors
import tkinter as tk
import pandas as pd
import calendar

class CalendarWindow:

    def __init__(self, parent_window, project_names, times_df):

        # Canvas constants
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
        self.nb_days_in_week = 7
        self.between_days_range = int(self.grid_width/self.nb_days_in_week)

        # Limit hours
        self.first_hour = 6
        self.last_hour = 20

        # Reference day for the week to plot
        self.reference_day = datetime.today()

        # Create the window
        self.create_calendar(parent_window, project_names, times_df)

    def create_prev_next_week_buttons(self, calendar_window):
        self.prev_week_button = tk.Button(calendar_window, text="Prev week")
        self.prev_week_button.grid(row=1, column=1)
        self.next_week_button = tk.Button(calendar_window, text="Next week")
        self.next_week_button.grid(row=1, column=2)

    def create_canvas(self, calendar_window):
        self.w = tk.Canvas(calendar_window, width=self.canvas_width, height=self.canvas_height)
        self.w.grid(row=2, column=1, columnspan=2)

    # This rectangle is used to add new project blocks
    def create_invisible_rectangle(self):
        self.w.create_rectangle(self.left_width_offset, self.up_heigth_offset, self.grid_width+self.left_width_offset, self.grid_heigth+self.up_heigth_offset, fill="", outline="", tags="add_broject_block")

    def create_coordinates_lines(self):
        self.w.create_line(0, self.up_heigth_offset, self.left_width_offset+self.grid_width, self.up_heigth_offset, width=2)
        self.w.create_line(self.left_width_offset, 0, self.left_width_offset, self.up_heigth_offset+self.grid_heigth, width=2)

    def create_hour_lines(self):
        # Variables to create hour lines
        total_hours = self.last_hour - self.first_hour
        nb_hours_between_line = 2
        between_lines_range = int(self.grid_heigth/(total_hours/nb_hours_between_line))
        base = self.first_hour + nb_hours_between_line
        hours_shown = ["%s:00" %(base+nb_hours_between_line*x) for x in range(total_hours)]

        # Create the hour lines
        index = 0
        for y in range(self.up_heigth_offset+between_lines_range, self.canvas_height-self.down_heigth_offset, between_lines_range):
            self.w.create_text(self.left_width_offset-5, y, text=hours_shown[index], anchor="e")
            index+=1
            self.w.create_line(self.left_width_offset, y, self.left_width_offset+self.grid_width, y, dash=(10,10))

    def create_day_lines(self):
        # Variables
        start_of_week = self.reference_day - timedelta(days=self.reference_day.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        weekdays = [ "%s %s/%s" %(calendar.day_name[my_date.weekday()], my_date.day, my_date.month) for my_date in pd.date_range(start_of_week, end_of_week) ]

        # Create the lines
        index = 0
        for x in range(self.left_width_offset+self.between_days_range, self.canvas_width-self.right_width_offset, self.between_days_range):
            self.w.create_line(x, 0, x, self.canvas_height-self.down_heigth_offset, tags="day_line")
            self.w.create_text(x-int(self.between_days_range/2), int(self.up_heigth_offset/2), text=weekdays[index], tags="day_line")
            index+=1

    def create_legend(self, project_names):
        index = 0
        for project_name in project_names:
            self.project_color_dict[project_name] = self.project_colors[index]
            height_space = 20
            self.w.create_rectangle(self.canvas_width-self.right_width_offset+10, index*height_space+100, self.canvas_width-self.right_width_offset+30, 110+index*height_space, fill=self.project_color_dict[project_name], tags="legend")
            self.w.create_text(self.canvas_width-self.right_width_offset+35, 105+index*height_space, text=project_name, anchor="w", tags="legend")
            index+=1

    def get_project_blocks_df(self, df):
        df["time"] = pd.to_datetime(df["time"])

        # Only keep the current week
        start_of_week = self.reference_day - timedelta(days=self.reference_day.weekday())  # Monday
        start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_week = start_of_week + timedelta(days=6)  # Sunday
        end_of_week = end_of_week.replace(hour=23, minute=59, second=59, microsecond=0)
        df = df[ (df["time"] >= start_of_week) & (df["time"] <= end_of_week) ].copy()

        df["last_time"] = df["time"].shift()
        df = df[ df["action_type"] == "END" ]
        return df

    def add_working_time(self, first_project_date, last_project_date, first_day_date, last_day_date, day_int, color):
        begin_time_first = (((first_project_date-first_day_date)*(self.grid_heigth))/(last_day_date-first_day_date))+self.up_heigth_offset
        if begin_time_first < self.up_heigth_offset:
            begin_time_first = self.up_heigth_offset
        last_time_first = (((last_project_date-first_day_date)*(self.grid_heigth))/(last_day_date-first_day_date))+self.up_heigth_offset
        self.w.create_rectangle(self.left_width_offset+day_int*self.between_days_range+10, begin_time_first, self.left_width_offset+(day_int+1)*self.between_days_range-10, last_time_first, fill=color, tags="project_block")

    def add_all_working_time(self, times_df):
        project_blocks_df = self.get_project_blocks_df(times_df)
        for row in project_blocks_df.itertuples(index=False):
            self.add_working_time(row.last_time, row.time, row.time.replace(hour=self.first_hour, minute=0, second=0), row.last_time.replace(hour=self.last_hour, minute=0, second=0), row.time.weekday(), self.project_color_dict[row.project_name])

    def create_calendar(self, parent_window, project_names, times_df):
        calendar_window = tk.Toplevel(parent_window)

        # Create the prev and next week buttons
        self.create_prev_next_week_buttons(calendar_window)

        # Create the canvas
        self.create_canvas(calendar_window)

        # Create the inside of the canvas
        self.create_invisible_rectangle()
        self.create_coordinates_lines()
        self.create_hour_lines()
        self.create_day_lines()
        self.create_legend(project_names)
        self.add_all_working_time(times_df)

    # Update

    def update_calendar_week(self, reference_day, times_df):
        self.reference_day = reference_day
        self.w.delete("day_line")
        self.create_day_lines()
        self.w.delete("project_block")
        self.add_all_working_time(times_df)

    def update_calendar_project_block(self, project_names, times_df):
        self.w.delete("legend")
        self.create_legend(project_names)
        self.w.delete("project_block")
        self.add_all_working_time(times_df)
