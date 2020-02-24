import tkinter as tk
from tkinter import ttk

class ModifyProjectNamesWindow:

    def __init__(self, parent_window, window_type, project_names=None):
        self.window_type = window_type
        if window_type == "add":
            self.create_add_project_window(parent_window)
        elif window_type == "remove":
            self.create_remove_project_window(parent_window, project_names)

    # View

    def create_add_project_window(self, parent_window):
        # Create a new window
        self.modify_project_window = tk.Toplevel(parent_window)
        self.modify_project_window.title("Add project")

        self.modify_project_entry = tk.Entry(self.modify_project_window)
        self.modify_project_entry.grid()

        self.modify_button = tk.Button(self.modify_project_window, text="Add")
        self.modify_button.grid()

    def create_remove_project_window(self, parent_window, project_names):
        # Check if there is projects to remove
        if not project_names:
            messagebox.showerror("Error", "There is no project yet")
            return

        # Create a new window
        self.modify_project_window = tk.Toplevel(parent_window)
        self.modify_project_window.title("Remove project")

        # Combobox with the project names
        self.modify_project_combo_box = ttk.Combobox(self.modify_project_window, state='readonly', values=project_names)
        self.modify_project_combo_box.grid()
        if project_names:
            self.modify_project_combo_box.current(0)

        self.modify_button = tk.Button(self.modify_project_window, text="Remove")
        self.modify_button.grid()

    # Getters

    def get_selected_project_name(self):
        if self.window_type == "add":
            return self.modify_project_entry.get()
        elif self.window_type == "remove":
            return self.modify_project_combo_box.get()
