from os import lseek
import pygame
import sys

pygame.init()

class Button:
    def __init__(self,width,height,text,action):
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.setup()
        self.create()
    def setup(self):
        self.font_scale = 36
        self.x = 0
        self.y = 0
        self.bgcolor = (0,0,0)
        self.border = 300
    def create(self):
        self.font = pygame.font.Font(None, self.font_scale)
        self.rect = pygame.Rect(self.x,self.y,self.width,self.height)
        self.border_rect = self.rect.inflate(self.border*2,self.border*2)
        self.button_text = self.font.render(self.text, True, (255,255,255))
    def draw(self, display_surface):
        pygame.draw.rect(display_surface, (255,255,255), self.border_rect, self.border)
        pygame.draw.rect(display_surface, self.bgcolor, self.rect)
        txt_width, txt_height = self.button_text.get_size()
        txt_x = self.rect.x+self.width/2-txt_width/2
        txt_y = self.rect.y+self.height/2-txt_height/2
        display_surface.blit(self.button_text, (txt_x,txt_y))
    def configure(self, width=None,height=None,bgcolor=None,font_scale=None):
        if width: self.width = width
        if height: self.height = height
        if bgcolor: self.bgcolor = bgcolor
        if font_scale: self.font_scale = font_scale
        self.create()

screen = pygame.display.set_mode((1000,800))
clock = pygame.time.Clock()
pygame.display.set_caption("ArtixUI Showcase")


button1 = Button(200,50,"Click Me",)
button1.configure(bgcolor=(0, 61, 102))













while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.fill((255,255,255))

    button1.draw(screen)


    pygame.display.update()
    clock.tick(60)