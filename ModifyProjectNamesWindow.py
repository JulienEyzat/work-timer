import tkinter as tk
from tkinter import ttk

class ModifyProjectNamesWindow:

    def __init__(self, parent_window, window_type, project_names=None):
        self.window_type = window_type
        if window_type == "add":
            self.create_add_project_window(parent_window)
        elif window_type == "modify":
            self.create_modify_project_window(parent_window, project_names)

    # View

    def create_add_project_window(self, parent_window):
        # Create a new window
        self.modify_project_window = tk.Toplevel(parent_window)
        self.modify_project_window.title("Add project")

        self.modify_project_entry = tk.Entry(self.modify_project_window)
        self.modify_project_entry.grid()

        self.modify_button = tk.Button(self.modify_project_window, text="Add")
        self.modify_button.grid()

    def create_modify_project_window(self, parent_window, project_names):
        # Check if there is projects to delete
        if not project_names:
            messagebox.showerror("Error", "There is no project yet")
            return

        # Create a new window
        self.modify_project_window = tk.Toplevel(parent_window)
        self.modify_project_window.title("Modify project")

        # Combobox with the project names
        self.modify_project_combo_box = ttk.Combobox(self.modify_project_window, state='readonly', values=project_names)
        self.modify_project_combo_box.grid(row=1, column=1, columnspan=2)
        if project_names:
            self.modify_project_combo_box.current(0)

        # Label with information about shown/hidden project
        self.is_hidden_label = tk.Label(self.modify_project_window, text="Hidden :")
        self.is_hidden_label.grid(row=2, column=1, columnspan=1, sticky="e")
        self.is_hidden_var = tk.StringVar()
        self.is_hidden_var.set("")
        self.is_hidden_value_label = tk.Label(self.modify_project_window, textvariable=self.is_hidden_var)
        self.is_hidden_value_label.grid(row=2, column=2, columnspan=1, sticky="w")

        self.show_hide_button = tk.Button(self.modify_project_window, text="Show/Hide")
        self.show_hide_button.grid(row=3, column=1)

        self.modify_button = tk.Button(self.modify_project_window, text="Delete")
        self.modify_button.grid(row=3, column=2)

    # Update

    def update_is_hidden_label(self, is_current_project_hidden):
        if is_current_project_hidden:
            self.is_hidden_var.set("True")
        else:
            self.is_hidden_var.set("False")

    # Getters

    def get_selected_project_name(self):
        if self.window_type == "add":
            return self.modify_project_entry.get()
        elif self.window_type == "modify":
            return self.modify_project_combo_box.get()

    # Set commands

    def set_modify_button_command(self, function):
        self.modify_button.config(command=function)

    def set_show_hide_button_command(self, function):
        self.show_hide_button.config(command=function)

    def set_update_is_hidden_command(self, function):
        self.modify_project_combo_box.bind("<<ComboboxSelected>>", function)

    def set_modify_project_entry_command(self, function):
        self.modify_project_entry.bind('<Return>', function)

    def set_modify_project_combo_box_command(self, function):
        self.modify_project_combo_box.bind('<Return>', function)

    # Destroy window

    def destroy_window(self):
        self.modify_project_window.destroy()
