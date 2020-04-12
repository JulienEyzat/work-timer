from DatabaseInterface import DatabaseInterface
from ModifyProjectNamesWindow import ModifyProjectNamesWindow

from tkinter import messagebox

class ModifyProjectNamesController:

    def __init__(self, parent_window, caller_window, window_type):
        self.database_interface = DatabaseInterface()

        # Get the window of the caller
        self.caller_window = caller_window

        # Create the window
        project_names = self.database_interface.get_all_project_names()
        self.modify_project_names_window = ModifyProjectNamesWindow(parent_window, window_type, project_names)
        if window_type == "modify":
            self.update_is_hidden()

        # Add and delete buttons
        if window_type == "add":
            self.modify_project_names_window.set_modify_button_command(self.add_project)
        elif window_type == "modify":
            self.modify_project_names_window.set_update_is_hidden_command(self.update_is_hidden)
            self.modify_project_names_window.set_show_hide_button_command(self.show_hide_project)
            self.modify_project_names_window.set_modify_button_command(self.delete_project)

        # Click enter in the entry field
        if window_type == "add":
            self.modify_project_names_window.set_modify_project_entry_command(self.add_project)
        # elif window_type == "modify":
        #     self.modify_project_names_window.set_modify_project_combo_box_command(self.delete_project)


    def modify_project_list(self, modify_type):
        # Get the selected project_name
        project_name = self.modify_project_names_window.get_selected_project_name().strip()
        # Get the previous project names
        current_project_names = self.database_interface.get_all_project_names()
        if modify_type == "add" and project_name in current_project_names:
            messagebox.showerror("Error", "%s is already in the database" %(project_name))
            return
        if modify_type == "delete" and not project_name in current_project_names:
            messagebox.showerror("Error", "%s is not in the database" %(project_name))
            return
        elif modify_type == "delete" and not project_name:
            messagebox.showerror("Error", "The project name is empty")
            return

        # Add the project name in the database or delete it
        if modify_type == "add":
            self.database_interface.add_project_name_in_database(project_name)
        elif modify_type == "show_hide":
            is_hidden = self.database_interface.is_hidden_project_name(project_name)
            if is_hidden:
                self.database_interface.show_project_name(project_name)
            else:
                self.database_interface.hide_project_name(project_name)
        elif modify_type == "delete":
            self.database_interface.delete_project_name_in_database(project_name)

        # Update the list of project names
        project_names = self.database_interface.get_project_names()
        self.caller_window.update_project_names_combo_box(project_names)
        # Destroy the window
        if modify_type == "show_hide":
            self.update_is_hidden()
        else:
            self.modify_project_names_window.destroy_window()

    def update_is_hidden(self, event=None):
        selected_project_name = self.modify_project_names_window.get_selected_project_name()
        is_hidden_project_name = self.database_interface.is_hidden_project_name(selected_project_name)
        self.modify_project_names_window.update_is_hidden_label(is_hidden_project_name)

    def add_project(self, event=None):
        self.modify_project_list("add")

    def show_hide_project(self, event=None):
        self.modify_project_list("show_hide")

    def delete_project(self, event=None):
        self.modify_project_list("delete")
