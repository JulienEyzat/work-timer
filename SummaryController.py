import pandas as pd
import calendar

from DatabaseInterface import DatabaseInterface
from SummaryWindow import SummaryWindow

class SummaryController:

    def __init__(self, parent_window):
        # Database interface
        self.database_interface = DatabaseInterface()

        summary_table = self.create_summary_table()
        self.summary_window = SummaryWindow(parent_window, summary_table)

    def create_summary_table(self):
        # Read the time database
        time_df = self.database_interface.get_dataframe_times()
        if time_df.empty:
            return time_df
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
