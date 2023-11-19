from Vector2D import Vector2D

class PhysicsObject:
    position = Vector2D(0,0)
    scale = Vector2D(0,0)
    rotation = 0
    velocity = Vector2D(0,0)
    angular_velocity = 0
    acceleration = Vector2D(0,0)
    force = Vector2D(0,0)
    mass = 1
    inertia = 0