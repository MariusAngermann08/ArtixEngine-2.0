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
Builder.load_file("kivy/editor.kv")


class MyLayout(GridLayout):
    def create(self):
        self.add_widget(Label(text="Hello Wolrd", font_size=35))


class EditorApp(App):
    title = "Artix Editor> Untitled"
    def __init__(self, prc_name="", **kwargs):
        super(EditorApp, self).__init__(**kwargs)
        self.title = f"Artix Editor > \"{prc_name}\"      | <v.1.0-beta>"

    def build(self):
        Window.clearcolor = (95/255, 118/255, 133/255, 1)
        Window.size = (800,600)
        layout = MyLayout()
        return layout



EditorApp(prc_name="Chill ma").run()
