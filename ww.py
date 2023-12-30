from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

class FileManagerApp(App):
    def build(self):
        # Number of columns in the grid layout
        num_cols = 3

        # Create a grid layout
        grid_layout = GridLayout(cols=num_cols, spacing=10)

        # Add buttons (representing files) to the grid layout
        for i in range(10):  # Replace this with the actual number of files
            # Use a Button as a placeholder for your file representation
            button = Button(text=f"File {i+1}", size_hint_x=None, width=150)
            
            # Add the button to the grid layout
            grid_layout.add_widget(button)

        return grid_layout

if __name__ == '__main__':
    FileManagerApp().run()
