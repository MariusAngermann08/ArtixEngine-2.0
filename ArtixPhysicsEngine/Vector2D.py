class Vector2D:
	def __init__(self, x, y):
		self.X = x
		self.Y = y
def addVector(a, b):
	return Vector2D(a.X+b.X,a.Y+b.Y)