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
from kivy.uix.stencilview import StencilView
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
from kivy.uix.relativelayout import RelativeLayout
import keyboard
from pynput.mouse import Controller#, Button
from distutils.dir_util import copy_tree
import builder
import subprocess
from kivy.uix.dropdown import DropDown
from kivy.uix.togglebutton import ToggleButton

script_dir = os.path.dirname(os.path.realpath(__file__))
print(script_dir)
Builder.load_file("kivy/editor.kv")

#Load Properties
Builder.load_file("kivy/properties/property.kv")
Builder.load_file("kivy/properties/transform.kv")
Builder.load_file("kivy/properties/image_texture.kv")
Builder.load_file("kivy/properties/physics.kv")
Builder.load_file("kivy/properties/scripts.kv")

#Load Tabs
Builder.load_file("kivy/tabs/scripting.kv")

#Load Special Widgets
Builder.load_file("kivy/special_widgets/visual_script_editor.kv")

prc_name = ""




Config.set('input', 'mouse', 'mouse,disable_multitouch')

project_data_example = {
    "Scene1": {
        "player": {"position": [10,10]}
    }
}

pre_method_code = [
    "\tdef __init__(self, engine, scene, object):\n",
    "\t\tsuper().__init__(engine, scene, object)\n\n",
    "\tdef on_init(self):\n",
    "\t\tpass\n\n",
    "\tdef update(self):\n",
    "\t\tpass\n\n",
    "\tdef on_exit(self):\n",
    "\t\tpass\n\n"
]

pre_xml_code = [
    "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n",
    "<eventsystem>\n",
    "</eventsystem>\n"
]

event_list = ["engine.key_pressed","engine.key_hold"]


project_data = {}
build_settings = {}
deleted_objects = {}
deleted_scenes = []

mouse = Controller()

temp_scene_name = "Untitled"
temp_scene = {}

def is_numeric(string):
    try:
        float_value = float(string)
        return True
    except ValueError:
        return False

class WarningDialog(Popup):
    warninglabel = ObjectProperty(None)

class PropertyLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(PropertyLayout, self).__init__(**kwargs)

class TransformLayout(FloatLayout):
    pos_x = ObjectProperty()
    pos_y = ObjectProperty()
    scale_x = ObjectProperty()
    scale_y = ObjectProperty()
    def __init__(self, **kwargs):
        super(TransformLayout, self).__init__(**kwargs)
    
class ImageTextureLayout(FloatLayout):
    texture_preview = ObjectProperty()
    texture_name = ObjectProperty()
    layout = None
    def __init__(self, **kwargs):
        super(ImageTextureLayout,self).__init__(**kwargs)

class PhysicsLayout(FloatLayout):
    mass_input = ObjectProperty()
    physics_main_switch = ObjectProperty()
    static_state_switch = ObjectProperty()

    layout = None
    def __init__(self, **kwargs):
        super(PhysicsLayout, self).__init__(**kwargs)

class ScriptsLayout(FloatLayout):
    scripts_grid = ObjectProperty()
    layout = None
    selected_script = None
    def __init__(self, **kwargs):
        super(ScriptsLayout, self).__init__(**kwargs)
    def stop_deselection(self, instance, **kwargs):
        for widget in self.scripts_grid.children:
            if widget.text == instance.text:
                widget.state = "down"
                break
    def update_selected(self, instance, value):
        if instance.state == "down":
            self.selected_script = instance.text
    def add_script(self):
        global project_data
        scriptdict = project_data[self.layout.currentscene][self.layout.selected_object]["scripts"].copy()
        selected = self.layout.get_selected_file()
        if not selected in scriptdict:
            if selected.endswith(".py") or selected.endswith(".xml"):
                project_data[self.layout.currentscene][self.layout.selected_object]["scripts"].append(selected)
                self.layout.load_properties(self.layout.selected_object)
    def remove_script(self):
        global project_data
        if self.selected_script:
            project_data[self.layout.currentscene][self.layout.selected_object]["scripts"].remove(self.selected_script)
            self.layout.load_properties(self.layout.selected_object)

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

class ImageScatter(Scatter):
    viewport = None
    name = None
    def __init__(self, source, **kwargs):
        super(ImageScatter, self).__init__(**kwargs)
        self.image = Image(source=source)
        self.image.allow_stretch = True
        self.image.keep_ratio = False
        self.add_widget(self.image)
        self.bind(size=self.update_image)
    def update_image(self, instance, value):
        self.image.width = self.width
        self.image.height = self.height
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            self.viewport.update_object_position(self.name)
        return super().on_touch_up(touch)


class Viewport(RelativeLayout):
    layout = None
    bg_color = (255,255,255)
    display_offset = (0,0)

    object_widgets = []
    mouse_wheel_pressed = False

    last_mouse_pos = None
    current_mouse_pos = None

    corner_markers = []


    def __init__(self, **kwargs):
        super(Viewport, self).__init__(**kwargs)

        with self.canvas.before:
            # Set the background color (in this case, it's set to red)
            Color(self.bg_color[0]/255,self.bg_color[1]/255,self.bg_color[2]/255,1)  # RGBA values (red, green, blue, alpha)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        
        

        self.stencil_view = StencilView(size_hint=(1,1))
        self.add_widget(self.stencil_view)
        print("Viewport init")

        Clock.schedule_interval(self.on_update, 1 / 60)
        self.bind(size=self.update_rect)
        Window.bind(on_touch_down=self.mouse_down)
        Window.bind(on_touch_up=self.mouse_up)

    def add_offset_label(self):
        #self.offset_label = Label(text="No Offset")
        #self.offset_label.color = (0,0,0,1)
        #self.layout.add_widget(self.offset_label)
        pass

    def update_rect(self, instance, value):
        # Update the background color when the size changes
        self.rect.pos = self.pos
        self.rect.size = self.size
        self.layout.load_viewport()

    def add_object(self,name):
        global project_data
        global build_settings


        #getting values from project data
        path = self.layout.convert_image_name_to_path(project_data[self.layout.currentscene][name]["img_texture"])
        posx = project_data[self.layout.currentscene][name]["position"][0]
        posy = project_data[self.layout.currentscene][name]["position"][1]
        scalex = project_data[self.layout.currentscene][name]["scale"][0]
        scaley = project_data[self.layout.currentscene][name]["scale"][1]

        scatter = ImageScatter(path)
        scatter.viewport = self
        scatter.name = name

        #Converting values
        posy = build_settings["resolution"][1] - posy

        #Calculate offsets
        posx += self.display_offset[0]
        posy += self.display_offset[1]

        #Setting values
        scatter.pos = (posx,posy)
        scatter.width = scalex
        scatter.height = scaley
        scatter.image.width = scalex
        scatter.image.height = scaley

        self.object_widgets.append(scatter)
        self.stencil_view.add_widget(scatter)

    def add_corner_markers(self):
        global build_settings
        global script_dir

        self.corner_markers.clear()

        scatter1 = Scatter()
        img1 = Image(source=f"{script_dir}\\kivy\\corner_markers\\left_top.png")
        img1.width = 35
        img1.height = 35
        scatter1.width = 35
        scatter1.height = 35
        scatter1.add_widget(img1)
        scatter1.pos = (0+self.display_offset[0],build_settings["resolution"][1]-35+self.display_offset[1])
        #self.stencil_view.add_widget(scatter1)

        scatter2 = Scatter()
        img2 = Image(source=f"{script_dir}\\kivy\\corner_markers\\left_bottom.png")
        img2.width = 35
        img2.height = 35
        scatter2.width = 35
        scatter2.height = 35
        scatter2.add_widget(img2)
        scatter2.pos = (0+self.display_offset[0],0+self.display_offset[1])
        #self.stencil_view.add_widget(scatter2)

        scatter3 = Scatter()
        img3 = Image(source=f"{script_dir}\\kivy\\corner_markers\\right_top.png")
        img3.width = 35
        img3.height = 35
        scatter3.width = 35
        scatter3.height = 35
        scatter3.add_widget(img3)
        scatter3.pos = (build_settings["resolution"][0]-35+self.display_offset[0],build_settings["resolution"][1]-35+self.display_offset[1])
        #self.stencil_view.add_widget(scatter3)

        scatter4 = Scatter()
        img4 = Image(source=f"{script_dir}\\kivy\\corner_markers\\right_bottom.png")
        img4.width = 35
        img4.height = 35
        scatter4.width = 35
        scatter4.height = 35
        scatter4.add_widget(img4)
        scatter4.pos = (build_settings["resolution"][0]+self.display_offset[0],0+self.display_offset[1])
        #self.stencil_view.add_widget(scatter4)

        #self.corner_markers.append(scatter1)
        #self.corner_markers.append(scatter2)
        #self.corner_markers.append(scatter3)
        #self.corner_markers.append(scatter4)

    def clear_all(self):
        self.stencil_view.clear_widgets()
        self.object_widgets.clear()


    def mouse_down(self, instance, touch):
        if touch.button == "middle":
            self.mouse_wheel_pressed = True

    def mouse_up(self, instance, touch):
        if touch.button == "middle":
            self.mouse_wheel_pressed = False
    
    def on_update(self, dt):
        #self.offset_label.text = f"Offset> X:{str(self.display_offset[0])}  Y:{str(self.display_offset[1])}"
        if self.mouse_wheel_pressed:
            if self.last_mouse_pos != self.layout.mouse_pos:
                deltax = self.last_mouse_pos[0]-self.layout.mouse_pos[0]
                deltay = self.last_mouse_pos[1]-self.layout.mouse_pos[1]
                self.display_offset = (self.display_offset[0]-deltax,self.display_offset[1]-deltay)
                self.layout.load_viewport()
        self.last_mouse_pos = self.layout.mouse_pos
    
    def update_object_position(self, name):
        global build_settings
        global project_data

        target = None
        for item in self.object_widgets:
            if item.name == name: target=item
        if target:
            #Getting values
            posx = target.pos[0]
            posy = target.pos[1]
            #Reverting Offsets
            posx -= self.display_offset[0]
            posy -= self.display_offset[1]
            
            #posy -= target.height/2
            #Converting values
            posy = build_settings["resolution"][1] - posy
            fixed_x = str(posx).split(".")[0]
            fixed_y = str(posy).split(".")[0]
            project_data[self.layout.currentscene][name]["position"] = [int(fixed_x),int(fixed_y)]

            self.layout.load_viewport()
            self.layout.load_properties(self.layout.selected_object)
        


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
                self.icon.background_normal = f"{script_dir}\\kivy\\icon\\script_selected.png"
                self.icon.background_down = f"{script_dir}\\kivy\\icon\\script_selected.png"
            else:
                self.icon.background_normal = f"{script_dir}\\kivy\\icon\\script.png"
                self.icon.background_down = f"{script_dir}\\kivy\\icon\\script.png"
        elif self.type == "image":
            if self.selected:
                self.icon.background_normal = f"{script_dir}\\kivy\\icon\\image_selected.png"
                self.icon.background_down = f"{script_dir}\\kivy\\icon\\image_selected.png"
            else:
                self.icon.background_normal = f"{script_dir}\\kivy\\icon\\image.png"
                self.icon.background_down = f"{script_dir}\\kivy\\icon\\image_selected.png"

class ToggleButtonGroup:
    def __init__(self):
        self.buttons = []

    def add_widget(self, button):
        self.buttons.append(button)

class EventSelector(Popup):
    layout = None
    event_widgets = []
    def __init__(self, **kwargs):
        super(EventSelector, self).__init__(**kwargs)
        self.size_hint = (0.2,0.5)
        self.auto_dismiss = True
        self.title = "Selector"
        
        self.floatlayout = FloatLayout()
        self.add_widget(self.floatlayout)

        self.scrollview = ScrollView()
        self.scrollview.size_hint = (0.8,0.875)
        self.scrollview.pos_hint = {"x":0.1,"top":1}
        with self.scrollview.canvas.before:
            Color(35/255,35/255,35/255,1)
            self.bg_rect = Rectangle(pos=self.pos,size=self.size)
        self.scrollview.bind(pos=self.update_bg_rect,size=self.update_bg_rect)
        self.floatlayout.add_widget(self.scrollview)

        self.gridlayout = GridLayout()
        self.gridlayout.size_hint_y = None
        self.gridlayout.spacing = 0
        self.gridlayout.height = self.gridlayout.minimum_height
        self.gridlayout.cols = 1
        self.scrollview.add_widget(self.gridlayout)

        self.button = Button(text="Add")
        self.button.font_size = 20
        self.button.size_hint = (0.4,0.1)
        self.button.pos_hint = {"x":0.3,"y":0}
        self.floatlayout.add_widget(self.button)

        self.group = ToggleButtonGroup()
        self.load_event_list()

    def load_event_list(self):
        global event_list
        self.event_widgets.clear()
        for item in event_list:
            togglebutton = ToggleButton(group=self.group)
            togglebutton.size_hint_y = None
            togglebutton.height = 40
            togglebutton.text = item
            self.gridlayout.add_widget(togglebutton)
            self.event_widgets.append(togglebutton)



    def update_bg_rect(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

class VisualScriptEditor(FloatLayout):
    def __init__(self, **kwargs):
        super(VisualScriptEditor, self).__init__(**kwargs)
        self.size_hint = (0.75,0.875)
        with self.canvas.before:
            Color(69/255, 69/255, 71/255,1)
            self.rect = Rectangle(pos=self.pos,size=self.size)
        self.bind(pos=self.update_rect,size=self.update_rect)
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
    def open_event_select(self):
        self.selector = EventSelector()
        self.selector.layout = self
        self.selector.bind(on_dismiss=self.check_event_select)
        self.selector.open()
    def check_event_select(self, instance):
        pass

    


class ScriptingTab(FloatLayout):
    scrollview = ObjectProperty()
    selected_file = None
    layout = None
    script_list_widgets = []
    def __init__(self, **kwargs):
        super(ScriptingTab, self).__init__(**kwargs)
        self.file_grid = GridLayout()
        self.file_grid.size_hint_y = None
        self.file_grid.cols = 1
        self.file_grid.spacing = 0
        with self.scrollview.canvas.before:
            Color(54/255,54/255,54/255,1)
            self.rect = Rectangle(size=self.size, pos=self.pos)
        self.scrollview.bind(pos=self.update_background_rect,size=self.update_background_rect)
        self.scrollview.add_widget(self.file_grid)

        self.codeinput = CodeInput()
        self.codeinput.tab_width = 4
        self.codeinput.size_hint = (0.75,0.88)
        self.codeinput.pos_hint = {"x":0.25,"y":0.05}
        self.codeinput.font_size = 20
        #self.add_widget(self.codeinput)

        self.vscriptedit = VisualScriptEditor()
        self.vscriptedit.pos_hint = {"x":0.25,"y":0.05}
    
    def load_python_script(self, name):
        if self.vscriptedit in self.children:
            self.remove_widget(self.vscriptedit)
        if not self.codeinput in self.children:
            self.add_widget(self.codeinput)
        path = f"{self.layout.prc_path}\\Assets\\{name}"
        content = ""
        with open(path, "r") as file:
            content = file.read()
        self.codeinput.text = content
    
    def load_visual_script(self, name):
        if self.codeinput in self.children:
            self.remove_widget(self.codeinput)
        if not self.vscriptedit in self.children:
            self.add_widget(self.vscriptedit)
        path = f"{self.layout.prc_path}\\Assets\\{name}"
        content = ""
        with open(path, "r") as file:
            content = file.read()

    def save_python_script(self):
        path = f"{self.layout.prc_path}\\Assets\\{self.selected_file}"
        with open(path, "w") as file:
            file.write(self.codeinput.text)

    def update_background_rect(self, instance, value):
        self.rect.size = instance.size
        self.rect.pos = instance.pos

    def update_file_list(self):
        self.file_grid.clear_widgets()
        self.selected_file = None
        self.script_list_widgets.clear()
        script_list = []
        for item in self.layout.files: 
            if item.endswith(".py") or item.endswith(".xml"):
                script_list.append(item)

        group = ToggleButtonGroup()

        for script in script_list:
            togglebutton = ToggleButton(text=script,group=group)
            togglebutton.text = script
            togglebutton.size_hint_y = None
            togglebutton.height = 40
            togglebutton.bind(state=self.update_selected)
            togglebutton.bind(on_press=self.stop_deselection)
            self.file_grid.add_widget(togglebutton)
            self.script_list_widgets.append(togglebutton)
        
        if len(self.script_list_widgets) > 0:
            self.script_list_widgets[0].state = "down"
            self.selected_file = self.script_list_widgets[0].text

    def stop_deselection(self, instance, **kwargs):
        for widget in self.script_list_widgets:
            if widget.text == instance.text:
                widget.state = "down"
                self.selected_file = widget.text
                break

    def update_selected(self, instance, value):
        if value == "down":
            self.selected_file = instance.text
            if self.selected_file.endswith(".py"):
                self.load_python_script(self.selected_file)
            elif self.selected_file.endswith(".xml"):
                self.load_visual_script(self.selected_file)





class AppLayout(FloatLayout):
    scenetree_layout = ObjectProperty()
    scenelist_layout = ObjectProperty()
    scene_name_label = ObjectProperty()
    file_manager = ObjectProperty()
    properties_layout = ObjectProperty()
    scene_context_menu = ObjectProperty()
    viewport_panel_item = ObjectProperty()
    scripting_panel_item = ObjectProperty()

    selected = None
    currentscene = ""
    selected_object = None
    property_widgets = []
    file_widgets = []

    app_link = None
    scene_focus = ""

    mouse_pos = None

    #project dir at self.prc_path

    def __init__(self, **kwargs):
        super(AppLayout, self).__init__(**kwargs)
        Window.bind(mouse_pos=self.update_mouse_pos)
        self.viewport = Viewport()
        self.viewport.layout = self
        self.viewport.add_offset_label()
        self.viewport_panel_item.add_widget(self.viewport)

        self.scripting = ScriptingTab()
        self.scripting.layout = self
        self.scripting_panel_item.add_widget(self.scripting)

    def load_viewport(self):
        global project_data
        self.viewport.clear_all()
        self.viewport.add_corner_markers()
        for obj in project_data[self.currentscene]:
            self.viewport.add_object(obj)

    def load_build_settings(self):
        global build_settings
        with open(f"{self.prc_path}\\build\\build_settings.json", "r") as file:
            build_settings = json.load(file)

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


    def after_load(self, dt):
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
        self.load_viewport()
        self.scripting.update_file_list()

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

    def convert_image_name_to_path(self, name):
        return f"{self.prc_path}\\Assets\\{name}"

    def convert_absolute_to_relative_path(self,absolute_path):
        global script_dir
        script_path = os.path.abspath(script_dir)
        relative_path = os.path.relpath(absolute_path, script_path)
        return relative_path

    def load_properties(self, object_name):
        global project_data
        global script_dir

        self.properties_layout.clear_widgets()
        self.property_widgets.clear()

        transform = TransformLayout()
        posx = project_data[self.currentscene][object_name]["position"][0]
        posy = project_data[self.currentscene][object_name]["position"][1]
        scalex = project_data[self.currentscene][object_name]["scale"][0]
        scaley = project_data[self.currentscene][object_name]["scale"][1]
        transform.pos_x.text = str(posx)
        transform.pos_y.text = str(posy)
        transform.scale_x.text = str(scalex)
        transform.scale_y.text = str(scaley)

        image_texture = ImageTextureLayout()
        image_texture.layout = self
        src = project_data[self.currentscene][object_name]["img_texture"]
        if src:
            path = self.convert_image_name_to_path(src)
            print(path)
            image_texture.texture_preview.source = src
            image_texture.texture_name.text = os.path.basename(path)

        physics = PhysicsLayout()
        physics.layout = self
        physics.physics_main_switch.active = project_data[self.currentscene][object_name]["PhysicsObject"][0]
        physics.mass_input.text = str(project_data[self.currentscene][object_name]["PhysicsObject"][1])
        physics_type = project_data[self.currentscene][object_name]["PhysicsObject"][3]
        if physics_type == "static": physics.static_state_switch.active = True
        
        scripts = ScriptsLayout()
        scripts.layout = self
        btnlist = []
        group = ToggleButtonGroup()
        for script in project_data[self.currentscene][object_name]["scripts"]:
            togglebutton = ToggleButton(text=script,group=group)
            togglebutton.size_hint_y = None
            togglebutton.height = 40
            togglebutton.bind(state=scripts.update_selected)
            togglebutton.bind(on_press=scripts.stop_deselection)
            scripts.scripts_grid.add_widget(togglebutton)
            btnlist.append(togglebutton)

        if len(btnlist) > 0:
            btnlist[0].state = "down"
            scripts.selected_script = btnlist[0].text


        self.property_widgets.append(transform)
        self.property_widgets.append(image_texture)
        self.property_widgets.append(physics)
        self.property_widgets.append(scripts)
        for widget in self.property_widgets:
            self.properties_layout.add_widget(widget)
    
    def apply_properties(self):
        global project_data
        global is_numeric

        values = []
        values.append(self.property_widgets[0].pos_x.text)
        values.append(self.property_widgets[0].pos_y.text)
        values.append(self.property_widgets[0].scale_x.text)
        values.append(self.property_widgets[0].scale_y.text)
        
        for value in values:
            if not is_numeric(value):
                print("[ERROR] Transform values must be numbers only")
                dialog = WarningDialog()
                dialog.title = "Value Error"
                dialog.warninglabel.text = "Transform values must be numbers only!"
                dialog.open()
                return None

        project_data[self.currentscene][self.selected_object]["position"][0] = int(values[0])
        project_data[self.currentscene][self.selected_object]["position"][1] = int(values[1])
        project_data[self.currentscene][self.selected_object]["scale"][0] = int(values[2])
        project_data[self.currentscene][self.selected_object]["scale"][1] = int(values[3])

        img = self.property_widgets[1].texture_name.text
        if img != "No Texture Assigned":
            project_data[self.currentscene][self.selected_object]["img_texture"] = img

        physics_switch_value = self.property_widgets[2].physics_main_switch.active
        project_data[self.currentscene][self.selected_object]["PhysicsObject"][0] = physics_switch_value
        mass_value = self.property_widgets[2].mass_input.text
        project_data[self.currentscene][self.selected_object]["PhysicsObject"][1] = mass_value
        static_switch_value = self.property_widgets[2].static_state_switch.active
        if static_switch_value: project_data[self.currentscene][self.selected_object]["PhysicsObject"][3] = "static"
        else: project_data[self.currentscene][self.selected_object]["PhysicsObject"][3] = "dynamic"





        self.load_properties(self.selected_object)
        self.load_viewport()
                
    def assign_image_texture(self):
        name = self.get_selected_file()
        if name:
            image_path = self.convert_image_name_to_path(name)
            self.property_widgets[1].texture_preview.source = image_path
            self.property_widgets[1].texture_name.text = name
            print(image_path)

    def load_files(self):
        self.file_manager.clear_widgets()
        self.file_widgets.clear()

        project_dict = {}
        with open(f"{self.prc_path}\\project.json", "r") as file:
            project_dict = json.load(file)
        
        self.files = project_dict["registered_files"]
        self.project_dict = project_dict

        #loading files into file manager
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
    
    def create_python_file(self):
        self.pfile_dialog = InputDialog()
        self.pfile_dialog.title = "Create Python Script"
        self.pfile_dialog.label.text = "Script Name:"
        self.pfile_dialog.submit_button.text = "Create"
        self.pfile_dialog.bind(on_dismiss=self.check_pfile_dialog)
        self.pfile_dialog.open()

    def check_pfile_dialog(self, instance):
        global pre_method_code
        name = self.pfile_dialog.get_input()
        if name != "" and not name in self.files:
            with open(f"{self.prc_path}\\Assets\\{name}.py", "w") as file:
                file.write(f"class {name}(engine.Method):\n")
                for line in pre_method_code:
                    file.write(line)
            self.files.append(name+".py")
            self.update_project_file()
            self.scripting.update_file_list()

    def create_visual_script(self):
        self.vfile_dialog = InputDialog()
        self.vfile_dialog.title = "Create Visual Script"
        self.vfile_dialog.label.text = "Script Name:"
        self.vfile_dialog.submit_button.text = "Create"
        self.vfile_dialog.bind(on_dismiss=self.check_vfile_dialog)
        self.vfile_dialog.open()

    def check_vfile_dialog(self, instance):
        global pre_xml_code
        name = self.vfile_dialog.get_input()
        if name != "" and not name in self.files:
            with open(f"{self.prc_path}\\Assets\\{name}.xml", "w") as file:
                for line in pre_xml_code:
                    file.write(line)
            self.files.append(name+".xml")
            self.update_project_file()
            self.scripting.update_file_list()

    def update_project_file(self):
        self.project_dict["registered_files"] = self.files
        with open(f"{self.prc_path}\\project.json", "w") as file:
            json.dump(self.project_dict, file)
        self.load_files()
    
    def get_selected_file(self):
        for widget in self.file_widgets:
            if widget.selected:
                return widget.text
        return None

    def delete_file(self):
        name = self.get_selected_file()
        if name in self.files:
            self.files.remove(name)
        path = f"{self.prc_path}\\Assets\\{name}"
        if os.path.exists(path):
            os.remove(path)
        self.update_project_file()
        self.scripting.update_file_list()

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
                self.selected_object = widgets[0].text
            for widget in widgets:
                self.scenetree_layout.add_widget(widget)
            self.scenetree_temp = widgets.copy()
            widgets.clear()
            if len(self.scenetree_temp) > 0:
                self.load_properties(self.scenetree_temp[0].text)
            self.load_viewport()

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
            project_data[self.currentscene][name] = {"position":[0,0],"scale":[100,100],"PhysicsObject": [False,1,100,"dynamic","box"],"img_texture":None,"scripts":[]}
            self.app_link.title = f"Artix Editor > \"{prc_name}\"      | <v.1.0-beta>*"
            self.load_scene(self.currentscene)
        elif name != "" and name in project_data[self.currentscene]:
            project_data[self.currentscene][name+"1"] = {"position":[0,0],"scale":[100,100],"PhysicsObject": [False,1,100,"dynamic","box"],"img_texture":None,"scripts":[]}
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

    def build_project(self):
        project_path = self.prc_path
        output_path = f"{project_path}\\build\\python-build" 
        BuilderInstance = builder.Builder(project_path, output_path)
        BuilderInstance.mode = "launch"
        BuilderInstance.build()
        os.chdir(f"{self.prc_path}\\Assets\\")
    
    def launch_project(self):
        global script_dir
        self.apply_properties()
        self.save_project()
        self.build_project()
        source_dir = f"{self.prc_path}\\build\\python-build"
        final_dir = f"{script_dir}\\launch"
        copy_tree(source_dir, final_dir)
        try:
            python_executable = sys.executable
            subprocess.Popen([python_executable, f"{script_dir}\\launch\\main.py"])
        except:
            dialog = WarningDialog()
            dialog.title = "Build Error"
            dialog.warninglabel.text = "Cant build with python because its not installed. Change build settings to use Executable-Build."
            dialog.open()

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
        self.setup_layout()
        os.chdir(f"{self.prc_path}\\Assets\\")
        Window.clearcolor = (50/255, 50/255, 50/255, 1)
        #Window.set_system_cursor('hand')
        #Window.fullscreen = 'auto'
        Window.maximize()
        self.layout = AppLayout()
        self.layout.app_link = self
        self.layout.load_project(self.prc_name, self.prc_path)
        self.layout.load_build_settings()
        Clock.schedule_once(self.layout.after_load, 0)
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

