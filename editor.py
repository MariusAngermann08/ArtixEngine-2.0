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
import os
import sys
import shutil
import json

script_dir = os.path.dirname(os.path.realpath(__file__))
Builder.load_file("kivy/editor.kv")

Config.set('input', 'mouse', 'mouse,disable_multitouch')


class MyLayout(FloatLayout):
    file_manager_list = ObjectProperty()
    file_manager_icon = ObjectProperty()
    viewport_layout = ObjectProperty()

    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)
        with self.viewport_layout.canvas:
            Color(1,0,0,.5, mode="rgba")
            self.rect = Rectangle(pos=(0,0), size=(100,100))
            self.rect.pos = (1000,500)
    



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
        return self.layout

    def setup_layout(self):
        self.getProjectPath()
        self.layout.file_manager_list.path = self.prc_path
        self.layout.file_manager_icon.path = self.prc_path

    def getProjectPath(self):
        with open(script_dir+"\\projects.json") as projects_file:
            self.project_data = json.load(projects_file)
        self.prc_path = f"{self.project_data[self.prc_name][0]}/{self.prc_name}"



EditorApp(prc_name="ExampleProject").run()
