from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.scatter import Scatter
from kivy.uix.image import Image
from kivy.graphics import Rectangle, Color

class DraggableImage(Scatter):
    pass

class MyLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(MyLayout, self).__init__(**kwargs)

        # Add a rectangle with an image to the canvas
        with self.canvas:
            Color(1, 1, 1, 1)  # White color (adjust as needed)
            self.rect = Rectangle(pos=self.pos, size=(100, 100))  # Adjust size as needed

        # Create a draggable image
        image = Image(source='path_to_your_image.jpg')  # Replace with the actual path to your image
        draggable_image = DraggableImage()
        draggable_image.add_widget(image)
        self.add_widget(draggable_image)

        # Bind the rectangle's position to the layout's position
        self.bind(pos=self.update_rect_pos)

    def update_rect_pos(self, instance, value):
        self.rect.pos = self.pos

class MyApp(App):
    def build(self):
        return MyLayout()

if __name__ == '__main__':
    MyApp().run()
