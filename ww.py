from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Rectangle, Color

class TwoFloatLayoutsApp(App):
    def build(self):
        # Create the first float layout
        layout1 = FloatLayout(size=(300, 300), pos=(0, 0))
        with layout1.canvas.before:
            self.color1 = Color(0.5, 0.5, 1, 1)  # Selected color
            self.rect1 = Rectangle(pos=layout1.pos, size=layout1.size)

        # Create the second float layout
        layout2 = FloatLayout(size=(300, 300), pos=(300, 0))
        with layout2.canvas.before:
            self.color2 = Color(1, 0.5, 0.5, 1)  # Unselected color
            self.rect2 = Rectangle(pos=layout2.pos, size=layout2.size)

        # Add the float layouts to the root layout
        root_layout = FloatLayout()
        root_layout.add_widget(layout1)
        root_layout.add_widget(layout2)

        # Bind the on_touch_down event to handle selection
        root_layout.bind(on_touch_down=self.on_touch_down)

        return root_layout

    def on_touch_down(self, instance, touch):
        if instance.collide_point(*touch.pos):
            # Determine which layout is selected based on touch position
            layout1 = instance.children[0]
            layout2 = instance.children[1]

            if layout1.collide_point(*touch.pos):
                # Select layout 1
                self.color1.rgba = (0.5, 0.5, 1, 1)
                self.color2.rgba = (1, 0.5, 0.5, 1)
            elif layout2.collide_point(*touch.pos):
                # Select layout 2
                self.color1.rgba = (1, 0.5, 0.5, 1)
                self.color2.rgba = (0.5, 0.5, 1, 1)

if __name__ == '__main__':
    TwoFloatLayoutsApp().run()
