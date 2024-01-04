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
from kivy.config import Config
from kivy.graphics import Rectangle
from kivy.graphics import Color
import kivy_garden.contextmenu
from kivy.uix.codeinput import CodeInput
from kivy.extras.highlight import KivyLexer
from kivy.uix.scatter import Scatter
from kivy.graphics import Rectangle, Color
from kivy.uix.image import Image
import os
import sys
import shutil
import json




script_dir = os.path.dirname(os.path.realpath(__file__))
Builder.load_file("kivy/editor.kv")

prc_name = ""

if len(sys.argv) > 1:
    prc_name = sys.argv[1]
else: prc_name = "ExampleProject"


Config.set('input', 'mouse', 'mouse,disable_multitouch')

project_data_example = {
    "Scene1": {
        "player": {"position": [10,10]}
    }
}





project_data = {}

temp_scene_name = "Untitled"
temp_scene = {}

class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)

class DefaultButton(Button):
    selected = False
    root_link = None
    def __init__(self, **kwargs):
        super(DefaultButton, self).__init__(**kwargs)
    def visual_update(self):
        if self.selected:
            self.background_color = (178/255, 194/255, 214/255, 1)
        else:
            self.background_color = (125/255, 125/255, 125/255, 1)
        
    def select(self):
        self.selected = True
        self.visual_update()
        self.root_link.clear_select(self)
        
    def deselect(self): 
        self.selected = False
        self.visual_update()

class File(FloatLayout):
    file_menu = ObjectProperty()
    icon = ObjectProperty()

    root_link = None
    type = "script"
    selected = False

    def __init__(self, **kwargs):
        super(File, self).__init__(**kwargs)



    
    def select(self): 
        if self.selected: self.deselect()
        else:
            self.root_link.clear_file_select(exception=self)
            self.selected = True
            self.visual_update()
    def deselect(self): 
        self.selected = False
        self.visual_update()

    def visual_update(self):

            
        
        if self.type == "script":
            if self.selected:
                self.icon.background_normal = "kivy/icon/script_selected.png"
                self.icon.background_down = "kivy/icon/script_selected.png"
            else:
                self.icon.background_normal = "kivy/icon/script.png"
                self.icon.background_down = "kivy/icon/script.png"
        elif self.type == "image":
            if self.selected:
                self.icon.background_normal = "kivy/icon/image_selected.png"
                self.icon.background_down = "kivy/icon/image_selected.png"
            else:
                self.icon.background_normal = "kivy/icon/image.png"
                self.icon.background_down = "kivy/icon/image_selected.png"
                




class MyLayout(FloatLayout):
    scenetree_layout = ObjectProperty()
    viewport_layout = ObjectProperty()
    scenelist_layout = ObjectProperty()
    scene_name_label = ObjectProperty()
    file_manager = ObjectProperty()

    selected = None

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        with self.viewport_layout.canvas:
            Color(1,0,0,.5, mode="rgba")
            self.rect = Rectangle(pos=(0,0), size=(100,100))
            self.rect.pos = (1000,500)

    

    def load_project(self, name, path):
        self.scenetree_layout.clear_widgets()
        self.scenelist_layout.clear_widgets()
        #Checking for project existance and setting paths
        if os.path.exists(f"{path}\\project.json"):
            self.prc_path = path
            self.prc_name = name
        else:
            print(f"[ERROR] The Project {self.prc_name} doesn't exist at {self.prc_path}.")
            sys.exit()
        
        #Only continues if project exists
        scenes = {}
        objects = {}

        #Transforming all project files into 1 dictionary
        with open(f"{self.prc_path}\\Scenes\\scenes.json", "r") as file:
            data = json.load(file)
            for i in data:
                project_data[i] = {}
                for obj in data[i]:
                    project_data[i][obj] = {}
                    with open(f"{self.prc_path}\\Scenes\\{i}\\{obj}_config.json", "r") as obj_file:
                        obj_data = json.load(obj_file)
                        for key in obj_data:
                            project_data[i][obj][key] = obj_data[key]

            print("[READING PROJECT]")
            print(project_data)

            #Adding all loaded scenes to the scene list
            widgets = []
            for scene in project_data:
                instance = RoundedButton()
                instance.on_press = lambda x=scene: self.load_scene(x)  
                instance.text = scene
                widgets.append(instance)
                instance = None
            
            for widget in widgets:
                self.scenelist_layout.add_widget(widget)
            widgets.clear()


            if len(project_data) == 0:
                pass
            else:
                target = ""
                for scene in project_data:
                    target = scene
                    break

                self.load_scene(target)
        
        #loading files into file manager
        self.file_widgets = []
        for i in range(3):
            file = File()
            file.root_link = self
            file.type = "script"
            file.visual_update()
            self.file_widgets.append(file)

        for widget in self.file_widgets:
            self.file_manager.add_widget(widget)


    def save_project(self):
        #Converting data/scene/[objects] to list
        scenefile_structure = {}
        for scene in project_data:
            objlist = []
            for element in project_data[scene]:
                objlist.append(element)
            scenefile_structure[scene] = objlist

        print("[SAVING PROJECT]")
        print(scenefile_structure)

        #Writing list into scenes.json file
        with open(f"{self.prc_path}\\Scenes\\scenes.json", "w") as file:
            json.dump(scenefile_structure, file)

        #Writing objects data into their config files
        for scene in project_data:
            for obj in project_data[scene]:
                with open(f"{self.prc_path}\\Scenes\\{scene}\\{obj}_config.json", "w") as file:
                    json.dump(project_data[scene][obj], file)
    
    def load_scene(self, name):
        if name in project_data:
            self.scenetree_layout.clear_widgets()
            self.scene_name_label.text = name

            temp_scene = project_data[name]
            temp_scene_name = name
            
            #Adding objects of scene to scenetree
            widgets = []
            for obj in temp_scene:
                instance = DefaultButton()
                instance.text = obj
                instance.root_link = self
                widgets.append(instance)
                instance = None
            if len(widgets) >= 1:
                widgets[0].selected = True
                widgets[0].visual_update()
            for widget in widgets:
                self.scenetree_layout.add_widget(widget)
            self.scenetree_temp = widgets.copy()
            widgets.clear()
                

        else:
            print(f"[ERROR] Scene <{name}> doesnt exist")

    def clear_select(self, exception=None):
        for widget in self.scenetree_temp:
            if widget != exception: widget.deselect()

    def clear_file_select(self, exception=None):
        for widget in self.file_widgets:
            if widget != exception: widget.deselect()


class EditorApp(App):
    title = "Artix Editor> Untitled"
    def __init__(self, prc_name="", **kwargs):
        super(EditorApp, self).__init__(**kwargs)
        self.prc_name = prc_name
        self.title = f"Artix Editor > \"{prc_name}\"      | <v.1.0-beta>"

    def build(self):
        Window.clearcolor = (50/255, 50/255, 50/255, 1)
        #Window.fullscreen = 'auto'
        Window.maximize()
        self.layout = MyLayout()
        self.setup_layout()
        self.layout.load_project(self.prc_name, self.prc_path)
        return self.layout

    def setup_layout(self):
        self.getProjectPath()


    def getProjectPath(self):
        with open(script_dir+"\\projects.json") as projects_file:
            self.project_data = json.load(projects_file)
        self.prc_path = f"{self.project_data[self.prc_name][0]}\\{self.prc_name}"



EditorApp(prc_name=prc_name).run()
