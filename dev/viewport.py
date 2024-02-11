from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.properties import BooleanProperty
from kivy.uix.scatter import Scatter

class MovableViewport(Widget):
    def __init__(self, **kwargs):
        super(MovableViewport, self).__init__(**kwargs)
        self.scatter_layout = ScatterLayout()
        self.add_widget(self.scatter_layout)

        for i in range(10):
            label = Label(text=f'Object {i+1}')
            scatter = Scatter()
            scatter.add_widget(label)
            self.scatter_layout.add_widget(scatter)

        self.is_ctrl_pressed = BooleanProperty(False)
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)
        Window.bind(on_mouse_move=self.on_mouse_move)

    def on_key_down(self, keyboard, keycode, text, modifiers, **kwargs):
        if 'ctrl' in modifiers:
            self.is_ctrl_pressed = True

    def on_key_up(self, keyboard, keycode, text, modifiers, **kwargs):
        if 'ctrl' in modifiers:
            self.is_ctrl_pressed = False

    def on_mouse_move(self, window, pos):
        if self.is_ctrl_pressed:
            dx, dy = Window.mouse_pos
            self.scatter_layout.x += dx
            self.scatter_layout.y += dy

class MovableViewportApp(App):
    def build(self):
        return MovableViewport()

if __name__ == '__main__':
    MovableViewportApp().run()
