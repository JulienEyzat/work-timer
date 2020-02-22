import tkinter as tk
from tkinter import ttk

class SummaryWindow:

    def __init__(self, parent_window, summary_table):
        self.create_summary_table_tree(parent_window, summary_table)

    def create_summary_table_tree(self, parent_window, summary_table):
        # Create a new window
        summary_window = tk.Toplevel(parent_window)
        summary_window.title("Summary")

        # Create the table
        treeview = ttk.Treeview(summary_window)
        treeview.grid()

        # Add the header to the table
        column_names = list(summary_table.columns.values)
        treeview["columns"] = column_names
        treeview["show"] = "headings"
        for column_name in column_names:
            treeview.heading(column_name, text=column_name)

        # Add the rows to the table
        for index, row in summary_table.iterrows():
            treeview.insert("", index, values=list(row))
