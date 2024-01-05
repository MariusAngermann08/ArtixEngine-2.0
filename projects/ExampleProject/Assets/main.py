import pygame
import sys
from random import randint
import subprocess

pygame.init()
pygame.font.init()

screen_res = [600,900]

screen = pygame.display.set_mode((screen_res[0],screen_res[1]))
pygame.display.set_caption("Snake Game")

clock = pygame.time.Clock()


#defining menus

def main_menu():
	headline_pos = [140,40]
	underline_pos = [170,130]
	textfont = pygame.font.SysFont("OCR-A Extended", 100)
	textfont_2 = pygame.font.SysFont("OCR-A Extended", 50)
	playbutton_render = pygame.transform.scale(pygame.image.load("src/play_button.png"), (300,100))
	play_button_collider = playbutton_render.get_rect()
	play_button_collider.x = 130
	play_button_collider.y = 400

	play_button_costumes = [
        pygame.image.load("src/play_button.png"),
        pygame.image.load("src/play_button_hover.png")
    ]

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
		
		

		if play_button_collider.collidepoint(pygame.mouse.get_pos()):
			playbutton_render = play_button_costumes[1]
		else:
			playbutton_render = play_button_costumes[0]

		if pygame.mouse.get_pressed()[0] and play_button_collider.collidepoint(pygame.mouse.get_pos()):
			break


		screen.fill((0,0,0))
		headline = textfont.render("Snake",1,(55, 255, 0))
		underline = textfont.render("Game",1,(55, 255, 0))
		nameline = textfont_2.render("by Marius Angermann",1,(255,255,255))
		screen.blit(headline, (headline_pos[0],headline_pos[1]))
		screen.blit(underline, (underline_pos[0],underline_pos[1]))
		screen.blit(pygame.transform.scale(playbutton_render, (300,100)), (140,400))
		screen.blit(nameline, (15,810))

		pygame.display.update()
		clock.tick(60)




#defining the game

snake_tiles = []
snake_tile_pos = {}

def create_snake_tile(position=[0,0]):
	square_obj = pygame.image.load("src/square.png")
	square_scaled = pygame.transform.scale(square_obj, (50,50))
	snake_tiles.append(square_scaled)
	snake_tile_pos[str(len(snake_tiles)-1)] = position
	
def render_snake():
	currentindex = 0
	for tiles in snake_tiles:
		screen.blit(tiles, (snake_tile_pos[str(currentindex)][0],snake_tile_pos[str(currentindex)][1]))
		currentindex += 1

def check_for_death():
	if snake_tile_pos[str(len(snake_tiles)-1)][0] < 0:
		return True
	elif snake_tile_pos[str(len(snake_tiles)-1)][0] > screen_res[0]:
		return True
	elif snake_tile_pos[str(len(snake_tiles)-1)][1] < 0:
		return True
	elif snake_tile_pos[str(len(snake_tiles)-1)][1] > screen_res[1]:
		return True
	else:
		return False


create_snake_tile(position=[0,0])
#create_snake_tile(position=[0,60])
#create_snake_tile(position=[0,120])
#create_snake_tile(position=[0,180])

#define variables for game
tile_count = 1
direction = "down"
game_speed = 0.2 #next move after ... sec
frame_counter = 0
frame_rate = 60
snake_speed = 60
positions = []
initital_count = 0

apple_grid = []
places_per_row = screen_res[0]/60
amount_of_rows = screen_res[1]/60
currentrow_used = 0
currentplace_used = 0

for currentrow in range(int(amount_of_rows)):
	for currentplace in range(int(places_per_row)):
		apple_grid.append([currentplace_used,currentrow_used])
		currentplace_used += 60
	currentplace_used = 0
	currentrow_used += 60

apples = []
apple_pos = []


			

def spawn_apple():
	apple_obj = pygame.image.load("src/apple.png")
	apple_scaled = pygame.transform.scale(apple_obj, (50,50))
	apples.append(apple_scaled)
	
	
	
	
		
new_apple = True
new_apple_pos = True


def render_apples():
	for apple_objects in apples:
		try:
			screen.blit(apple_objects, (apple_pos[0],apple_pos[1]))
			return "empty"
		except:
			return "new"




def apple_collect(apples,new_apple_pos,new_apple):
	if snake_tile_pos[str(len(snake_tiles)-1)] == apple_pos:
		apples.clear()
		return True

tiles_temp = []
pos_temp = {}
score = 0
textfont = pygame.font.SysFont("OCR-A Extended", 100)

mainmenu = True
answer = False

def game_over_menu(answer):
	headline_pos = [170,80]
	underline_pos = [170,170]
	textfont = pygame.font.SysFont("OCR-A Extended", 100)
	textfont_2 = pygame.font.SysFont("OCR-A Extended", 50)
	textfont_3 = pygame.font.SysFont("OCR-A Extended", 40)

	while True:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		keys_pressed = pygame.key.get_pressed()
		if keys_pressed[pygame.K_SPACE]:
			pygame.quit()
			sys.exit()
		screen.fill((0,0,0))

		

		headline = textfont.render("Game",1,(255, 255, 255))
		underline = textfont.render("Over",1,(255, 255, 255))
		scoreline = textfont_2.render("Your score is " + str(score),1,(255,255,255))
		continueline = textfont_3.render("Press space to continue",1,(255,255,255))
		screen.blit(headline, (headline_pos[0],headline_pos[1]))
		screen.blit(underline, (underline_pos[0],underline_pos[1]))
		screen.blit(continueline, (30,700))
		screen.blit(scoreline, (70,330))
	

		pygame.display.update()
		clock.tick(60)




while True:
	if mainmenu:
		mainmenu = False
		main_menu()
	
	if answer == "newgame":
		snake_tiles.clear()
		snake_tile_pos = {}
		score = 0
		apples.clear()
		tile_count = 0
		create_snake_tile(position=[60,60])
		spawn_apple()
		positions.clear()
		new_apple = True
		new_apple_pos = True
		tiles_temp.clear()
		pos_temp.clear()
		initital_count = 0
		frame_counter = 0



	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	keys_pressed = pygame.key.get_pressed()
	if keys_pressed[pygame.K_a]:
		direction = "left"
	elif keys_pressed[pygame.K_d]:
		direction = "right"
	elif keys_pressed[pygame.K_w]:
		direction = "up"
	elif keys_pressed[pygame.K_s]:
		direction = "down"

	if keys_pressed[pygame.K_LEFT]:
		direction = "left"
	elif keys_pressed[pygame.K_RIGHT]:
		direction = "right"
	elif keys_pressed[pygame.K_UP]:
		direction = "up"
	elif keys_pressed[pygame.K_DOWN]:
		direction = "down"
	
	
	if apple_collect(apples,new_apple_pos,new_apple) == True:
		new_apple = True
		new_apple_pos = True
		lastlength = len(snake_tiles)
		tiles_temp = snake_tiles.copy()
		new_pos = snake_tile_pos["0"]
		snake_tiles.clear()
		if direction == "down":
			pos_vector = [new_pos[0],new_pos[1]-60]
		elif direction == "up":
			pos_vector = [new_pos[0],new_pos[1]+60]
		elif direction == "left":
			pos_vector = [new_pos[0]+60,new_pos[1]]
		elif direction == "right":
			pos_vector = [new_pos[0]-60,new_pos[1]+60]
		create_snake_tile(position=pos_vector)
		for tiles_used in tiles_temp:
			snake_tiles.append(tiles_used)
		pos_temp = snake_tile_pos.copy()
		snake_tile_pos = {}
		snake_tile_pos["0"] = pos_vector
		currentindex = 1
		for left_tiles in pos_temp:
			snake_tile_pos[str(currentindex)] = pos_temp[str(currentindex-1)]
			currentindex += 1
		score += 1
		

	
	if new_apple == True:
		spawn_apple()
		new_apple = False
	if new_apple_pos == True:
		value = randint(0, len(apple_grid)-1)
		if apple_grid[value] in positions:
			new_apple_pos = True
		else:
			new_apple_pos = False
			apple_pos.clear()
			apple_pos = apple_grid[value]
				


	

	checked = []
	positions = []
	#game logic
	if frame_counter == game_speed*frame_rate:
		value = 0
		

		
		if check_for_death() == True:
			game_over_menu(answer)
		
		#update positions
		currentindex = 0
		for tiles in snake_tiles:
			positions.append(snake_tile_pos[str(currentindex)])
			currentindex += 1
				 
		

		frame_counter = 0
		if direction == "down":
			positions.append([snake_tile_pos[str(len(snake_tiles)-1)][0],snake_tile_pos[str(len(snake_tiles)-1)][1] + snake_speed])
		elif direction == "up":
			positions.append([snake_tile_pos[str(len(snake_tiles)-1)][0],snake_tile_pos[str(len(snake_tiles)-1)][1] - snake_speed])
		elif direction == "right":
			positions.append([snake_tile_pos[str(len(snake_tiles)-1)][0] + snake_speed,snake_tile_pos[str(len(snake_tiles)-1)][1]])
		elif direction == "left":
			positions.append([snake_tile_pos[str(len(snake_tiles)-1)][0] - snake_speed,snake_tile_pos[str(len(snake_tiles)-1)][1]])
		

		

		for i in range(len(positions)-1):
			snake_tile_pos[str(i)] = positions[i+1]


		checked = []
		currentindex = 0
		for single_obj in snake_tile_pos:
			if currentindex == 0:
				pass
				currentindex += 1
			else:
				if snake_tile_pos[str(currentindex)] in checked:
					game_over_menu(answer)
				else:
					checked.append(snake_tile_pos[str(currentindex)])
				currentindex += 1
	

		
		
			
	score_rendered = textfont.render(str(score),1,(255,255,255))	

	#rendering
	screen.fill((0,0,0))
	checker = render_apples()
	if checker == "new":
		apples.clear()
		apple_pos.clear()
		new_apple = True
		new_apple_pos = True
	render_snake()
	screen.blit(score_rendered, (260,0))

	
	pygame.display.update()
	
	frame_counter += 1
	clock.tick(frame_rate)

