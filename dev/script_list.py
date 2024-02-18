from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.togglebutton import ToggleButton


class ObjectSelectorApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Create a list of object names
        objects = ['Object 1', 'Object 2', 'Object 3', 'Object 4']

        # Variable to hold the selected object
        self.selected_object = None

        # Function to update the selected_object variable
        def update_selected(instance, value):
            if value == 'down':
                self.selected_object = instance.text

        # Create ToggleButton for each object
        toggle_buttons = []
        group = ToggleButtonGroup()

        for obj_name in objects:
            button = ToggleButton(text=obj_name, group=group, size_hint_y=None, height=40)
            button.bind(state=update_selected)
            toggle_buttons.append(button)
            layout.add_widget(button)

        # Set the first button as the default selected
        toggle_buttons[0].state = 'down'
        self.selected_object = toggle_buttons[0].text

        return layout


class ToggleButtonGroup:
    def __init__(self):
        self.buttons = []

    def add_widget(self, button):
        self.buttons.append(button)


if __name__ == '__main__':
    ObjectSelectorApp().run()
