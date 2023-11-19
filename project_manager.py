from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.screenmanager import SlideTransition
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.progressbar import ProgressBar
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.core.window import Window
from kivy.clock import Clock
from plyer import filechooser
import os
import shutil
import json



script_dir = os.path.dirname(os.path.realpath(__file__))
Builder.load_file("kivy/projectmanager.kv")

default_project = {
    "name": None,
    "edit": "never",
}

default_build_settings = {
    
}

class DropDownMenu(Popup):
    option = None
    def select_option(self, option):
        self.option = option
        self.dismiss()

class LoadingDialog(Popup):
    loadinglabel = ObjectProperty(None)
    progressbar = ObjectProperty(None)
    def start_loading(self, *args):
        self.progressbar.value = 0
        self.load_event = Clock.schedule_interval(self.update_loading, 0.001)
    def update_loading(self, dt):
        if self.progressbar.value < 100:
            self.progressbar.value += 1
        else:
            self.load_event.cancel()
            self.dismiss()


class WarningDialog(Popup):
    warninglabel = ObjectProperty(None)

class YesNoDialog(Popup):
    warninglabel = ObjectProperty(None)
    answer = "no"
    def yes(self):
        self.answer = "yes"
        self.dismiss()

class ProjectDialog(Popup):
    dirpath = ObjectProperty(None)
    prcname = ObjectProperty(None)
    backup_switch = ObjectProperty(None)

    project_data = {}
    def choose_dir(self):
        try:
            directory = filechooser.choose_dir()
            if directory:
                self.dirpath.text = directory[0]
        except Exception as e:
            print(f"Process canceled! >\n\n{e}")

    def generate_project_files(self):
        #Generate Project Files
        project_dir = self.dirpath.text+f"\\{self.prcname.text}"
        if os.path.exists(project_dir):
            shutil.rmtree(project_dir)
        os.mkdir(project_dir)
        default_project["name"] = self.prcname.text
        with open(project_dir+"\\project.json", "w") as project_file:
            json.dump(default_project, project_file)
        os.mkdir(project_dir+"\\Assets")
        scenes_dir = project_dir+"\\Scenes"
        os.mkdir(scenes_dir)
        with open(scenes_dir+"\\scenes.json", "w") as scenes_file:
            json.dump({},scenes_file)
        build_dir = project_dir+"\\build"
        os.mkdir(build_dir)
        with open(build_dir+"\\build_settings.json", "w") as build_file:
            json.dump({}, build_file)
        os.mkdir(build_dir+"\\python-build")
        os.mkdir(build_dir+"\\standalone-build")
        
        #Generate Backup Archive
        if self.backup_switch.active:
            shutil.make_archive(self.prcname.text, 'zip', project_dir)
            shutil.move(f"{self.prcname.text}.zip", f"backup/{self.prcname.text}.zip")
        
        #Link Project in <projects.json>
        data = {}
        with open(script_dir+"\\projects.json", "r") as projects_file:
            data = json.load(projects_file)
        data[self.prcname.text] = [self.dirpath.text, self.backup_switch.active]
        with open(script_dir+"\\projects.json", "w") as projects_file:
            json.dump(data, projects_file)
        
        dialog = LoadingDialog()
        dialog.loadinglabel.text = "Generating Project Files:"
        dialog.bind(on_open=dialog.start_loading)
        dialog.open()
        self.dismiss()

    def create_project(self):
        #name check
        valid = True
        reason = ""
        if self.prcname.text == "":
            valid = False
            reason = "You need to specify a project name!"
        elif " " in self.prcname.text:
            valid = False
            reason = "Project name can't contain spaces!"

        elif os.path.isfile(self.dirpath.text+f"\\{self.prcname.text}\\project.json"):
            valid = False
            reason = "/yes-no:A project with this name\nalready exists in this directory\nDo you want to replace it?"

        characters = ["/","\\","\"","-","#","\'"]
        for char in characters:
            if char in self.prcname.text:
                valid = False
                reason = f"Project name can't contain special characters!\n{characters}"
                break
        if valid:
            self.generate_project_files()
        else:
            if reason.startswith("/yes-no:"):
                dialog = YesNoDialog()
                dialog.warninglabel.text = reason.replace("/yes-no:", "")

                def dialog_dismiss(instance):
                    if dialog.answer == "yes":
                        self.generate_project_files()

                dialog.bind(on_dismiss=dialog_dismiss)
                dialog.open()
            else:
                dialog = WarningDialog()
                dialog.warninglabel.text = reason
                dialog.open()
        
class ProjectLayout(FloatLayout):
    project_name = ObjectProperty(None)
    project_directory = ObjectProperty(None)
    open_button = ObjectProperty(None)
    option = None

    #links MyLayout for usage of functions
    panel_link = None

    def open_dropdown_menu(self):
        self.menu = DropDownMenu()
        self.menu.title = f"Options for:  {self.project_name.text}"
        self.menu.bind(on_dismiss=self.run_option)
        self.menu.open()
    
    def run_option(self, instance):
        if self.menu.option:
            if self.menu.option == "prc_settings":
                print("Project Settings aren't implemented yet")
            elif self.menu.option == "prc_remove":
                self.panel_link.RemoveProjectFromList(self.project_name.text)
            elif self.menu.option == "prc_delete":
                self.panel_link.DeleteProject(self.project_name.text)
        self.panel_link.UpdateProjectList()
        self.panel_link.UpdateProjectMenu()
    def run_editor_thread(self):
        thread = threading.Thread(target=self.open_project)
        thread.start()

    def open_project(self):
        import editor

        
    



class MyLayout(TabbedPanel):
    projects_grid = ObjectProperty(None)
    project_data = {}
    def OpenProjectDialog(self):
        self.UpdateProjectList()
        dialog = ProjectDialog()
        dialog.project_data = self.project_data
        dialog.dirpath.text = script_dir+"\\projects"
        dialog.bind(on_dismiss=self.update)
        dialog.open()
    def update(self, instance):
        self.UpdateProjectList()
        self.UpdateProjectMenu()
    def UpdateProjectList(self):
        with open(script_dir+"\\projects.json") as projects_file:
            self.project_data = json.load(projects_file)
    def UpdateProjectMenu(self):
        self.projects_grid.clear_widgets()
        for i in self.project_data:
            if os.path.exists(f"{self.project_data[i][0]}\\{i}\\project.json"):
                project = ProjectLayout()
                project.panel_link = self
                project.project_name.text = i
                project.project_directory.text = self.project_data[i][0]
                self.projects_grid.add_widget(project)
            else:
                project = ProjectLayout()
                project.panel_link = self
                project.project_name.text = i
                project.project_name.foreground_color = (1,0,0,1)
                project.project_directory.text = "Project has been removed"
                project.project_directory.foreground_color = (1,0,0,1)
                if self.project_data[i][1]:
                    project.open_button.text = "Restore"
                    project.open_button.on_press = lambda x=project.project_name.text: self.RestoreProject(x)
                else:
                    project.remove_widget(project.open_button)
                self.projects_grid.add_widget(project)
    def RestoreProject(self, name):
        self.UpdateProjectList()
        if name in self.project_data:
            backup_path = f"{script_dir}\\backup\\{name}.zip"
            extract_path = f"{self.project_data[name][0]}\\{name}"
            os.mkdir(extract_path)
            shutil.unpack_archive(backup_path, extract_path, "zip")
            dialog = LoadingDialog()
            dialog.loadinglabel.text = "Restoring Project"
            dialog.bind(on_open=dialog.start_loading)
            dialog.open()
        self.UpdateProjectMenu()
    def RemoveProjectFromList(self, name):
        self.UpdateProjectList()
        if name in self.project_data:
            del self.project_data[name]
            with open(script_dir+"\\projects.json", "w") as projects_file:
                json.dump(self.project_data, projects_file)
    def DeleteProject(self, name):
        self.UpdateProjectList()
        if name in self.project_data:
            shutil.rmtree(f"{self.project_data[name][0]}\\{name}")
            if self.project_data[name][1]:
                os.remove(f"{script_dir}\\backup\\{name}.zip")
            self.RemoveProjectFromList(name)
    def on_keyboard_down(self, window, key, *args):
        if key == 286:
            self.UpdateProjectList()
            self.UpdateProjectMenu()


    def TestProjectTemplate(self):
        self.projects_grid.add_widget(ProjectLayout())
        self.projects_grid.add_widget(ProjectLayout())


class ProjectManagerApp(App):
    def build(self):
        self.title = "Artix Project Manager"
        print(Window.size)
        Window.clearcolor = (95/255, 118/255, 133/255, 1)
        Window.size = (800,600)
        layout = MyLayout()
        Window.bind(on_key_down=layout.on_keyboard_down)
        layout.update(None)
        return layout


if __name__ == "__main__":
    ProjectManagerApp().run()