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
from plyer import filechooser



script_dir = os.path.dirname(os.path.realpath(__file__))
Builder.load_file("kivy/editor.kv")
Builder.load_file("kivy/properties/property.kv")
Builder.load_file("kivy/properties/transform.kv")

prc_name = ""




Config.set('input', 'mouse', 'mouse,disable_multitouch')

project_data_example = {
    "Scene1": {
        "player": {"position": [10,10]}
    }
}




project_data = {}
deleted_objects = {}
deleted_scenes = []


temp_scene_name = "Untitled"
temp_scene = {}


class PropertyLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(PropertyLayout, self).__init__(**kwargs)

class TransformLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(TransformLayout, self).__init__(**kwargs)
    



class RoundedButton(Button):
    scene_mode = False
    layout = None
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.bind(on_touch_down=self.right_click)
    def right_click(self, instance, touch):
        if touch.button == 'right' and instance.collide_point(*touch.pos) and self.scene_mode:
            if self.layout:
                self.layout.show_scene_menu(self.text)

class InputDialog(Popup):
    label = ObjectProperty()
    cancel_button = ObjectProperty()
    submit_button = ObjectProperty()
    text_input = ObjectProperty()

    input = ""
    def __init__(self, **kwargs):
        super(InputDialog, self).__init__(**kwargs)
    def submit(self):
        self.input = self.text_input.text
        self.dismiss()
    def get_input(self): return self.input


class GameObject(Button):
    selected = False
    root_link = None
    def __init__(self, **kwargs):
        super(GameObject, self).__init__(**kwargs)
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
    file_name = ObjectProperty()

    root_link = None
    type = "script"
    selected = False
    text = "script.py"

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

        self.file_name.text = self.text
        
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
                




class AppLayout(FloatLayout):
    scenetree_layout = ObjectProperty()
    viewport_layout = ObjectProperty()
    scenelist_layout = ObjectProperty()
    scene_name_label = ObjectProperty()
    file_manager = ObjectProperty()
    properties_layout = ObjectProperty()
    scene_context_menu = ObjectProperty()


    selected = None
    currentscene = ""
    selected_object = None
    property_widgets = []

    app_link = None
    scene_focus = ""

    mouse_pos = None

    #project dir at self.prc_path

    def __init__(self, **kwargs):
        super(AppLayout, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.update_mouse_pos)
        with self.viewport_layout.canvas:
            Color(1,0,0,.5, mode="rgba")
            self.rect = Rectangle(pos=(0,0), size=(100,100))
            self.rect.pos = (1000,500)

    def update_mouse_pos(self, window, pos): self.mouse_pos = pos
    
    def create_untitled_scene(self):
        global project_data
        project_data["Untitled"] = {}

    def load_project(self, name, path):
        global deleted_objects
        global project_data

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

            self.update_scenelist()


            if len(project_data) == 0:
                self.create_untitled_scene()
            
            target = ""
            for scene in project_data:
                target = scene
                break
            self.load_scene(target)
        
        deleted_objects.clear()
        for scene in project_data:
            deleted_objects[scene] = []

        self.load_files()

    def update_scenelist(self):
        self.scenelist_layout.clear_widgets()

        #Adding all loaded scenes to the scene list
        widgets = []
        for scene in project_data:
            instance = RoundedButton()
            instance.scene_mode = True
            instance.layout = self
            instance.on_press = lambda x=scene: self.load_scene(x)  
            instance.text = scene
            widgets.append(instance)
            instance = None
        
        for widget in widgets:
            self.scenelist_layout.add_widget(widget)
        widgets.clear()

    def show_scene_menu(self, scene=None):
        self.scene_context_menu.x = self.mouse_pos[0]
        self.scene_context_menu.y = self.mouse_pos[1] - self.scene_context_menu.height #+ 20
        self.scene_context_menu.show()
        self.scene_focus = scene



    def load_properties(self, object_name):
        self.properties_layout.clear_widgets()
        self.property_widgets.clear()


        transform = TransformLayout()
        


        default = PropertyLayout()



        self.property_widgets.append(transform)
        self.property_widgets.append(default)
        for widget in self.property_widgets:
            self.properties_layout.add_widget(widget)
        
        

    def load_files(self):
        self.file_manager.clear_widgets()

        project_dict = {}
        with open(f"{self.prc_path}\\project.json", "r") as file:
            project_dict = json.load(file)
        
        self.files = project_dict["registered_files"]
        self.project_dict = project_dict

        #loading files into file manager
        self.file_widgets = []
        for i in self.files:
            file = File()
            file.root_link = self
            if i.endswith(".py"):
                file.type = "script"
            elif i.endswith(".png") or i.endswith(".jpg") or i.endswith(".jpeg"):
                file.type = "image"
            file.text = i
            file.visual_update()
            self.file_widgets.append(file)

        for widget in self.file_widgets:
            self.file_manager.add_widget(widget)

    def import_file(self):
        try:
            selected_file = filechooser.open_file(multiple=True, filters = ["*.jpeg","*.jpg","*.png","*.py"])
            if selected_file:
                print(selected_file)
        except Exception as e:
            print(f"Process canceled! >\n\n{e}")
            return 1
        if len(selected_file) >= 1:
            file_name = os.path.basename(selected_file[0])
            if file_name in self.files:
                return 1
            shutil.copy(selected_file[0],self.prc_path+f"\\Assets\\{file_name}")
            self.files.append(file_name)
            self.update_project_file()

    def update_project_file(self):
        self.project_dict["registered_files"] = self.files
        with open(f"{self.prc_path}\\project.json", "w") as file:
            json.dump(self.project_dict, file)
        self.load_files()
    
    def get_selected_file(self):
        for widget in self.file_widgets:
            if widget.selected:
                return widget.text

    def delete_file(self):
        name = self.get_selected_file()
        if name in self.files:
            self.files.remove(name)
        path = f"{self.prc_path}\\Assets\\{name}"
        if os.path.exists(path):
            os.remove(path)
        self.update_project_file()

    def delete_object(self):
        global project_data
        global deleted_objects
        name = None
        if name in project_data[self.currentscene]:
            del project_data[self.currentscene][name]
            deleted_objects[self.currentscene].append(name)
        else:
            print(f"[ERROR] Object <{name}> cant be deleted because it doesnt exist in scene <{self.currentscene}>")
        self.load_scene(self.currentscene)

    def delete_scene(self):
        global project_data
        global deleted_scenes
        name = self.scene_focus
        print(name)
        if name in project_data:
            del project_data[name]
            deleted_scenes.append(name)
        else:
            print(f"[ERROR] Scene <{name}> cant be deleted because it doesnt exist")
        if len(project_data) > 0:
            target = ""
            for item in project_data:
                target = item
                break
            self.load_scene(target)
        else:
            self.create_untitled_scene()
            self.load_scene("Untitled")
        self.update_scenelist()


    def save_project(self):
        global project_data
        global deleted_objects
        global deleted_scenes

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
            if not os.path.exists(f"{self.prc_path}\\Scenes\\{scene}\\"):
                os.mkdir(f"{self.prc_path}\\Scenes\\{scene}\\")
            for obj in project_data[scene]:
                with open(f"{self.prc_path}\\Scenes\\{scene}\\{obj}_config.json", "w") as file:
                    json.dump(project_data[scene][obj], file)
    
        #Removing files of deleted game objects
        for scene in deleted_objects:
            for item in scene:
                try:
                    os.remove(f"{self.prc_path}\\Scenes\\{scene}\\{item}_config.json")
                except:
                    print(f"[Error] Cant remove files of object: {item}")

        #Removing directorys of deleted scenes
        for scene in deleted_scenes:
            try:
                shutil.rmtree(f"{self.prc_path}\\Scenes\\{scene}\\")
            except:
                print(f"[Error] Canceled directory removal of scene {scene}")


        self.app_link.title = f"Artix Editor > \"{prc_name}\"      | <v.1.0-beta>"

    def load_scene(self, name):
        if name in project_data:
            self.currentscene = name
            self.scenetree_layout.clear_widgets()
            self.scene_name_label.text = name

            temp_scene = project_data[name]
            temp_scene_name = name
            
            #Adding objects of scene to scenetree
            widgets = []
            for obj in temp_scene:
                instance = GameObject()
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
            if len(self.scenetree_temp) > 0:
                self.load_properties(self.scenetree_temp[0].text)
                

        else:
            print(f"[ERROR] Scene <{name}> doesnt exist")

    def create_object(self, type=None):
        if type == "sprite":
            self.dialog = InputDialog()
            self.dialog.title = "Create Object"
            self.dialog.label.text = "Object Name"
            self.dialog.submit_button.text = "Create"
            self.dialog.open()
            self.dialog.bind(on_dismiss=self.check_object_dialog)
            

    def check_object_dialog(self, instance):
        name = self.dialog.get_input()
        if name != "" and name not in project_data[self.currentscene]:
            project_data[self.currentscene][name] = {"position":[0,0],"scale":[100,100]}
            self.app_link.title = f"Artix Editor > \"{prc_name}\"      | <v.1.0-beta>*"
            self.load_scene(self.currentscene)
        elif name != "" and name in project_data[self.currentscene]:
            project_data[self.currentscene][name+"1"] = {"position":[0,0],"scale":[100,100]}
            self.app_link.title = f"Artix Editor > \"{prc_name}\"      | <v.1.0-beta>*"
            self.load_scene(self.currentscene)

    def create_scene(self):
        self.scene_dialog = InputDialog()
        self.scene_dialog.title = "New Scene"
        self.scene_dialog.label.text = "Scene Name"
        self.scene_dialog.submit_button.text = "Create"
        self.scene_dialog.open()
        self.scene_dialog.bind(on_dismiss=self.check_scene_dialog)

    def check_scene_dialog(self, instance):
        name = self.scene_dialog.get_input()
        if name != "" and name not in project_data:
            project_data[name] = {}
            self.load_scene(name)
        elif name != "" and name in project_data:
            project_data[name+"1"] = {}
            self.load_scene[name+1]
        self.update_scenelist()

        


    def clear_select(self, exception=None):
        for widget in self.scenetree_temp:
            if widget != exception: widget.deselect()
        if exception: 
            self.selected_object = exception.text
            self.load_properties(self.selected_object)

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
        self.layout = AppLayout()
        self.layout.app_link = self
        self.setup_layout()
        self.layout.load_project(self.prc_name, self.prc_path)
        return self.layout

    def setup_layout(self):
        self.getProjectPath()


    def getProjectPath(self):
        with open(script_dir+"\\projects.json") as projects_file:
            self.project_data = json.load(projects_file)
        self.prc_path = f"{self.project_data[self.prc_name][0]}\\{self.prc_name}"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        prc_name = sys.argv[1]
    else: 
        #print(print("[ERROR] Please specify project name --> ArtixEngine \"<project_name>\""))
        #sys.exit()
        prc_name = "example_project"
    EditorApp(prc_name=prc_name).run()

