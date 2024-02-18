import pygame
import sys
import pymunk
from InputMap import input_map
import math
import pymunk.pygame_util

class Engine:
	remembered_keys = []
	def_physics_settings = {
		"mass":1,
		"inertia":100,
		"physics_type":"dynamic",
		"collider":"box"
	}
	def __init__(self, title="DefaultProject", res=[800,600], fps=60):
		self.title = title
		self.res = (res[0],res[1])
		self.fps = fps
		self.setup()
		self.prepare_defaults()
	def setup(self):
		self.screen = pygame.display.set_mode(self.res)
		pygame.display.set_caption(self.title)
		self.clock = pygame.time.Clock()
		self.methods = []
		self.events = []
	def prepare_defaults(self):
		self.scenes = []
		self.scene_map = {}
		self.current_scene = "None"
		self.next_scene_index = 0
	def handle_events(self):
		self.events = pygame.event.get()
		for event in self.events:
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
	def key_pressed(self, key):
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == input_map[key]: return True
	def key_hold(self, key):
		for event in self.events:
			if event.type == pygame.KEYDOWN and event.key == input_map[key]:
				if key not in self.remembered_keys:
					self.remembered_keys.append(key)
			if event.type == pygame.KEYUP and event.key == input_map[key]:
				if key in self.remembered_keys:
					self.remembered_keys.remove(key)

		return key in self.remembered_keys

	def run(self):
		if self.current_scene != "None":
			while True:
				self.handle_events()
				for func in self.methods:
					func(self)
				self.scenes[self.scene_map[self.current_scene]].render()

				pygame.display.update()
				self.clock.tick(self.fps)
	def addScene(self, scene_object):
		scene_object.engine_reference = self
		scene_object.set_draw_options()
		self.scenes.append(scene_object)
		self.scene_map[scene_object.name] = self.next_scene_index
		self.next_scene_index += 1
	def loadScene(self, scene_name):
		self.current_scene = scene_name
	def addMethod(self, method):
		self.methods.append(method)
	def key_pressed(self, key):
		check = False
		for event in self.events:
			if event.type == pygame.KEYDOWN:
				if event.key == input_map[key]:
					check = True
		return check
	def getMousePos(self):
		return [pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]]
	def getMouseX(self):
		return pygame.mouse.get_pos()[0]
	def getMouseY(self):
		return pygame.mouse.get_pos()[1]
	def getDefaultPhysicsSettings(self):
		return self.def_physics_settings
	def rectangular_collision(self, obj1, obj2):
		obj1.updateSurface()
		obj2.updateSurface()
		rect1 = obj1.surface.get_rect()
		rect2 = obj2.surface.get_rect()
		rect1.x, rect1.y = obj1.getRectPos()[0], obj1.getRectPos()[1]
		rect2.x, rect2.y = obj2.getRectPos()[0], obj2.getRectPos()[1]
		if rect1.colliderect(rect2):
			return True
		else:
			return False
	def point_collision(self, obj, point):
		pass

	class Scene:
		def __init__(self, name, bgcolor=(255,255,255)):
			self.name = name
			self.bgcolor = bgcolor
			self.setup()
		def setup(self):
			self.game_objects = []
			self.objects_map = {}
			self.next_object_index = 0
			self.engine_reference = None
			self.camera_pos = (0,0)
			self.space = pymunk.Space()
			self.space.gravity = (0, 981)
			self.dt = 1/60
		def set_draw_options(self):
			self.draw_options = pymunk.pygame_util.DrawOptions(self.engine_reference.screen)
		def render(self):
			self.dt = 1/self.engine_reference.fps
			self.engine_reference.screen.fill(self.bgcolor)
			for obj in self.game_objects:
				obj.run_methods()
				obj.draw(self.engine_reference.screen)
			self.space.step(self.dt)
		def addObject(self, object_source):
			object_source.engine_reference = self.engine_reference
			object_source.scene_reference = self
			self.game_objects.append(object_source)
			self.objects_map[object_source.name] = self.next_object_index
			self.next_object_index += 1
		def getObjectByName(self, object_name):
			return self.game_objects[self.objects_map[object_name]]
		def getObjectByTag(self, tag):
			for obj in self.game_objects:
				if tag in obj.tags:
					return obj
		def getObjectsByTag(self, tag):
			objects = []
			for obj in self.game_objects:
				if tag in obj.tags:
					objects.append(obj)
			return objects
	class GameObject:
		physics = False
		tags = []
		surface = None
		def __init__(self, name, textures=[]):
			self.setup()
			self.name = name
			self.image_textures = textures
			if len(self.image_textures) != 0: self.src = pygame.image.load(self.image_textures[0])
			self.updateSurface()
		def setup(self):
			self.engine_reference = None
			self.scene_reference = None
			self.image_textures = []
			self.position = self.Position(0,0)
			self.rotation = self.Rotation(0)
			self.scale = self.Scale(100,100)
			self.methods = []
		def updateSurface(self):
			self.surface = pygame.transform.scale(pygame.transform.rotate(self.src, self.rotation.angle), (self.scale.x,self.scale.y))
		def getRectPos(self):
			return (self.position.x-self.scene_reference.camera_pos[0],self.position.y-self.scene_reference.camera_pos[1])
		def run_methods(self):
			for method in self.methods:
				method.update()
		def draw(self, display_surface):
			if len(self.image_textures) != 0:
				if self.physics: self.updatePhyiscsView()
				self.updateSurface()
				display_surface.blit(self.surface, self.getRectPos())
		def move(self, vector=[0,0]):
			if self.physics:
				new_x = self.physics_body.body.position.x + vector[0]
				new_y = self.physics_body.body.position.y + vector[1]
				self.physics_body.body.position = pymunk.Vec2d(new_x, new_y)
				# Update the shape's position as well
				self.physics_body.position = pymunk.Vec2d(new_x, new_y)
			else:
				self.position.x += vector[0]
				self.position.y += vector[1]

		def set_position(self, vector=[0,0]):
			if self.physics:
				self.physics_body.body.position = pymunk.Vec2d(vector[0], vector[1])
				# Update the shape's position as well
				self.physics_body.position = pymunk.Vec2d(vector[0], vector[1])
			else:
				self.position.set(vector)

		def addAttribute(self, att_type, att_settings={"mass":1,"inertia":100,"physics_type":"dynamic","collider":"box"}):
			if att_type == "PhysicsObject":
				self.mass = att_settings["mass"]
				self.inertia = att_settings["inertia"]
				self.physics_type = att_settings["physics_type"]
				self.physics_collider = att_settings["collider"]
				self.createPhysicsObject()
				self.physics = True

		def addMethod(self, method):
			instance = method(self.engine_reference, self.scene_reference, self)
			self.methods.append(instance)
		def updatePhyiscsView(self):
			scale = self.scale.get()
			x = self.physics_body.body.position.x - scale[0] / 2
			y = self.physics_body.body.position.y - scale[1] / 2
			self.position.set([x,y])
		def createPhysicsObject(self):
			scale = (self.scale.get()[0],self.scale.get()[1])
			if self.physics_type == "dynamic": ptype = pymunk.Body.DYNAMIC
			elif self.physics_type == "static": ptype = pymunk.Body.STATIC
			body = pymunk.Body(self.mass,self.inertia,ptype)
			body.position = (self.position.get()[0]+scale[0]/2,self.position.get()[1]+scale[1]/2)
			damping_coefficient = 0.1
			body.angular_velocity *= (1.0 - damping_coefficient)
			if self.physics_collider == "circle":
				self.physics_body = pymunk.Circle(body,self.scale.x)
			elif self.physics_collider == "box":
				self.physics_body = pymunk.Poly.create_box(body,scale)
			self.scene_reference.space.add(body,self.physics_body)
		def apply_force(self, vector=[0,0]):
			if self.physics:
				x = self.physics_body.body.position.x
				y = self.physics_body.body.position.y
				self.physics_body.body.apply_impulse_at_world_point((vector[0]*100,vector[1]*100), (x,y))
			else:
				print("[Engine] Can't use apply_force() on GameObject without PhysicsObject Attribute")
		def add_tag(self, tag="default"):
			if tag not in self.tags:
				self.tags.append(tag)

		class Position:
			def __init__(self,x,y):
				self.x = x
				self.y = y
			def get(self):
				return [self.x,self.y]
			def set(self, pos=[0,0]):
				self.x, self.y = pos[0],pos[1]
		class Rotation:
			def __init__(self, angle):
				self.angle = angle
			def get(self):
				return self.angle
			def set(self, angle):
				self.angle = angle
		class Scale:
			def __init__(self,x,y):
				self.x = x
				self.y = y
			def get(self):
				return [self.x,self.y]
			def set(self, scale):
				self.x, self.y = scale[0],scale[1]
	class Method:
		def __init__(self, engine, scene, object):
			self.engine = engine
			self.scene = scene
			self.object = object
		def on_init(self): pass
		def update(self): pass
		def on_exit(self): pass