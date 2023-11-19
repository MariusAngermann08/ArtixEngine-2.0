import pygame
import sys
import pymunk
from InputMap import input_map
import math
import pymunk.pygame_util
from Engine import Engine

engine = Engine("Engine Module Demo", [1000,800], 60)

class boxScript(engine.Method):
    def __init__(self, engine, scene, object):
        super().__init__(engine, scene, object)

    def update(self):
        if self.engine.key_hold("d"):
            self.object.move([5,0])
        elif self.engine.key_hold("a"):
            self.object.move([-5,0])

        if self.engine.key_pressed("space"):
            box = self.scene.getObjectByName("box")
            print(box)



level01 = engine.Scene("level01", (255,255,255))
engine.addScene(level01)

box1 = engine.GameObject("ball", ["img/ball.png"])
box1.addMethod(boxScript)

box2 = engine.GameObject("box", ["img/box.jpeg"])
box2.position.x = 400


level01.addObject(box2)
level01.addObject(box1)
engine.loadScene("level01")
engine.run()