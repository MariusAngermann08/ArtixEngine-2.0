from distutils.dir_util import copy_tree
import shutil
import sys
import os
import json


class Builder:
    mode = "export"
    def __init__(self, project_path, output_path) -> None:
        self.prc_path = project_path
        self.output_path = output_path
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.name = os.path.basename(os.path.normpath(self.prc_path))
    def prepare_build(self):
        self.file = []
        self.build_settings = {}
        self.scenes = {}
        self.scenelist = []
        self.object_map = {}
        self.libraries = ["pygame","pymunk","sys","math","pymunk.pygame_util"]
        print(self.prc_path)
        print(self.output_path)
        os.chdir(self.prc_path)
    def load_build_settings(self):
        with open(f"{self.prc_path}\\build\\build_settings.json", "r") as temp_file:
            self.build_settings = json.load(temp_file)
    def set_object_methods(self):
        project_file = None
        with open(f"{self.prc_path}\\project.json", "r") as file:
            project_file = json.load(file)
        if not project_file: return 0
        registered_files = project_file["registered_files"].copy()
        scripts = []
        for file in registered_files:
            if file.endswith(".py"):
                scripts.append(file)
        for script in scripts:
            content = ""
            with open(f"{self.prc_path}\\Assets\\{script}", "r") as file:
                content = file.read()
            self.file.append(content+"\n\n")
    def load_scenes(self):
        with open(f"{self.prc_path}\\Scenes\\scenes.json", "r") as temp_file:
            self.scenes = json.load(temp_file)
    def set_imports(self):
        for lib in self.libraries:
            self.file.append(f"import {lib}\n")
        self.file.append("from InputMap import input_map\n")
        self.file.append("from Engine import Engine\n")
    def set_scenes(self):
        for scene in self.scenes:
            self.scenelist.append(scene)
            self.file.append(f"{scene} = engine.Scene(\"{scene}\", (255,255,255))\n")
            self.file.append(f"engine.addScene({scene})\n\n")
    def set_objects(self):
        for scene in self.scenes:
            for obj in self.scenes[scene]:
                obj_temp = {}
                with open(f"{self.prc_path}\\Scenes\\{scene}\\{obj}_config.json") as temp_file:
                    obj_temp = json.load(temp_file)
                if self.mode == "launch":
                    fixed_path = self.output_path.replace("\\","\\\\")
                    texture_path = f"{fixed_path}\\\\Assets\\\\{obj_temp['img_texture']}"
                else:
                    texture_path = f"Assets/{obj_temp['img_texture']}"
                self.file.append(f"{obj} = engine.GameObject(\"{obj}\", [\"{texture_path}\"])\n")
                self.file.append(f"{obj}.position.x = {str(obj_temp['position'][0])}\n")
                self.file.append(f"{obj}.position.y = {str(obj_temp['position'][1])}\n")
                self.file.append(f"{obj}.scale.x = {str(obj_temp['scale'][0])}\n")
                self.file.append(f"{obj}.scale.y = {str(obj_temp['scale'][1])}\n")
                #Add Object To Scene
                self.file.append(f"{scene}.addObject({obj})\n")
                #Add Attributes
                if obj_temp["PhysicsObject"][0]:
                    mass = str(obj_temp["PhysicsObject"][1])
                    inertia = str(obj_temp["PhysicsObject"][2])
                    physics_type = obj_temp["PhysicsObject"][3]
                    collider = obj_temp["PhysicsObject"][4]
                    dict_parse = "{"+f"\"mass\":{mass},\"inertia\":{inertia},\"physics_type\":\"{physics_type}\",\"collider\":\"{collider}\""+"}"
                    self.file.append(f"{obj}.addAttribute(\"PhysicsObject\", {dict_parse})\n")
                #Put Methods Here
                for script in obj_temp["scripts"]:
                    self.file.append(f"{obj}.addMethod({script.rstrip('.py')})\n")            


                #[false, 1, 100, "dynamic", "box"]

                #def_physics_settings = {
                #    "mass":1,
                #    "inertia":100,
                #    "physics_type":"dynamic",
                #    "collider":"box"
                #}


    def add_engine_commands(self):
        self.file.append(f"\nengine.loadScene(\"{self.scenelist[0]}\")\n")
        self.file.append("engine.run()")
    def finalize_build(self):
        asset_path = f"{self.output_path}\\Assets"
        if not os.path.exists(asset_path): os.mkdir(asset_path)
        copy_tree(f"{self.prc_path}\\Assets",f"{self.output_path}\\Assets")
        shutil.copy2(f"{self.script_dir}\\Engine.py",f"{self.output_path}\\Engine.py")
        shutil.copy2(f"{self.script_dir}\\InputMap.py",f"{self.output_path}\\InputMap.py")
    def build(self, type="python"):
        self.prepare_build()
        self.load_build_settings()
        self.set_imports()
        #Setup Engine
        self.file.append(f"\nengine = Engine(\"{self.name}\", [{str(self.build_settings['resolution'][0])},{str(self.build_settings['resolution'][1])}], 60)\n\n")
        self.set_object_methods()
        self.load_scenes()
        self.set_scenes()
        self.set_objects()
        self.add_engine_commands()
        self.write()
        self.finalize_build()
    def write(self):
        with open(f"{self.output_path}\\main.py", "w") as output_file:
            for line in self.file:
                output_file.write(line)


if __name__ == "__main__":
    project_path = 'C:\\Users\\xdgam\\Documents\\ArtixEngine-main\\projects\\example_project'
    output_path = 'C:\\Users\\xdgam\\Downloads\\build'
    builder = Builder(project_path, output_path)
    builder.build()