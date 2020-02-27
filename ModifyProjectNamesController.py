from DatabaseInterface import DatabaseInterface
from ModifyProjectNamesWindow import ModifyProjectNamesWindow

from tkinter import messagebox

class ModifyProjectNamesController:

    def __init__(self, parent_window, caller_window, window_type):
        self.database_interface = DatabaseInterface()

        # Get the window of the caller
        self.caller_window = caller_window

        # Create the window
        project_names = self.database_interface.get_project_names()
        self.modify_project_names_window = ModifyProjectNamesWindow(parent_window, window_type, project_names)

        # Add and delete buttons
        if window_type == "add":
            self.modify_project_names_window.set_modify_button_command(self.add_project)
        elif window_type == "delete":
            self.modify_project_names_window.set_modify_button_command(self.delete_project)

        # Click enter in the entry field
        if window_type == "add":
            self.modify_project_names_window.set_modify_project_entry_command(self.add_project)
        elif window_type == "delete":
            self.modify_project_names_window.set_modify_project_combo_box_command(self.delete_project)


    def modify_project_list(self, modify_type):
        # Get the new project_name
        project_name = self.modify_project_names_window.get_selected_project_name().strip()
        # Get the previous project names
        current_project_names = self.database_interface.get_project_names()
        if modify_type == "add" and project_name in current_project_names:
            messagebox.showerror("Error", "%s is already in the database" %(project_name))
            return
        if modify_type == "delete" and not project_name in current_project_names:
            messagebox.showerror("Error", "%s is not in the database" %(project_name))
            return
        elif modify_type == "delete" and not project_name:
            messagebox.showerror("Error", "The project name is empty")
            return

        # Add the project name in the database
        if modify_type == "add":
            self.database_interface.add_project_name_in_database(project_name)
        elif modify_type == "delete":
            self.database_interface.delete_project_name_in_database(project_name)

        # Update the list of project names
        project_names = self.database_interface.get_project_names()
        self.caller_window.update_project_names_combo_box(project_names)
        # Destroy the window
        self.modify_project_names_window.destroy_window()

    def add_project(self, event=None):
        self.modify_project_list("add")

    def delete_project(self, event=None):
        self.modify_project_list("delete")
