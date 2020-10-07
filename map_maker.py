import pygame
import libtcodpy as libtcod
import math
import pickle
import gzip
import datetime

#game files
import constants
import util

import tiles

class obj_camera:

	def __init__(self):

		self.width = constants.CAMERA_WIDTH
		self.height = constants.CAMERA_HEIGHT

		self.x, self.y = (0, 0)

		self.speed = .1

	def update(self):

		target_x = PLAYER.x * constants.GAME_TILE_SIZE + constants.GAME_TILE_SIZE/2
		target_y = PLAYER.y * constants.GAME_TILE_SIZE + constants.GAME_TILE_SIZE/2

		distance_x, distance_y = self.map_dist((target_x, target_y))

		self.x +=int(distance_x * self.speed)
		self.y += int(distance_y * self.speed)

	@property
	def rect(self):

		pos_rect = pygame.Rect((0, 0), (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT))

		pos_rect.center = (self.x, self.y)

		return pos_rect

	@property
	def map_address(self):

		map_x = self.x / constants.GAME_TILE_SIZE
		map_y = self.y / constants.GAME_TILE_SIZE

		return (map_x, map_y)

	def win_to_map(self, coords):
		tar_x, tar_y = coords

        #convert window coords to distace from camera
		cam_d_x, cam_d_y = self.cam_dist((tar_x, tar_y))

        #distance from cam -> map coord
		map_p_x = self.x + cam_d_x
		map_p_y = self.y + cam_d_y

		return((map_p_x, map_p_y))


	def map_dist(self, coords):


		new_x, new_y = coords 

		dist_x = new_x - self.x
		dist_y = new_y - self.y

		return (dist_x, dist_y)
	
	def cam_dist(self, coords):

		win_x, win_y = coords

		dist_x = win_x - (self.width / 2)
		dist_y = win_y - (self.height / 2)

		return (dist_x, dist_y)

class ui_button:

	def __init__(self, surface, coords, size, text, click_function = None, click_function_params = None,
	 text_color = constants.COLOR_RED, color_box = constants.COLOR_GREY,
	  color_mouseover = constants.COLOR_LIGHT_GREY, pos_from_center = False, font = "FONT_MENU", sprite = None, sprite_tag = None):

		self.surface = surface
		self.coords = coords
		self.size = size
		self.text = text
		self.font = font
		self.click_function = click_function
		self.text_color = text_color
		self.color_box = color_box
		self.color_mouseover = color_mouseover
		self.pos_from_center = pos_from_center
		self.click_function_params = click_function_params
		self.sprite = sprite
		self.bound_key_text = ""

		if sprite_tag:
			self.sprite = constants.anim_dict[sprite_tag]

		

		self.rect = pygame.Rect(coords, size)

		if self.pos_from_center == True:
			self.rect.center = self.center(coords)

			w, h = self.size
			x, y = self.rect.center
			x -= w/2
			y -= h/2

			self.coords = (x,y)


	@property
	def is_highlighted(self):

		x, y = self.coords
		w,h = self.size

		return (mouse_in_window(x, y, w, h) != None)

	def center(self, coords):

		x,y = coords

		x += constants.CAMERA_WIDTH/2
		y += constants.CAMERA_HEIGHT/2

		return (x,y)

	def draw(self):

		#print(self.bound_key_text)

		global MOUSE_CLICKED

		#print(self.coords)

		if self.is_highlighted:
			color = self.color_mouseover
		else:
			color = self.color_box

		if self.sprite:

			w,h = self.size
			x,y = self.coords 

			button_center = (w/2 + x, h/2 + y)

			d_x, d_y = button_center

			d_x -= constants.GAME_TILE_SIZE/2
			d_y -= constants.GAME_TILE_SIZE/2

			d_coords = (d_x, d_y)

			pygame.draw.rect(self.surface, color, self.rect)
			self.surface.blit(self.sprite, d_coords)
			util.draw_text(self.surface, self.bound_key_text, self.rect.topleft, self.text_color, center = False, font = self.font)
		else:

			pygame.draw.rect(self.surface, color, self.rect)
			util.draw_text(self.surface, self.text, self.rect.center, self.text_color, center = True, font = self.font)
			util.draw_text(self.surface, self.bound_key_text, self.rect.topleft, self.text_color, center = False, font = self.font)

		if self.is_highlighted == True:
			if MOUSE_CLICKED == True:

				MOUSE_CLICKED = False

				self.click()

				


				return "END"

			elif BIND_KEY:
				KEY_BINDINGS.append((BIND_KEY, self.click_function, self.click_function_params))
				self.bound_key_text = str(BIND_KEY.unicode)
				




		return None

	def click(self):

		if self.click_function:
			#print(str(self.click_function) + self.text)
			if self.click_function == "RETURN":

				return "END"

			elif self.click_function_params:
				self.click_function(self.click_function_params)


			else:
				self.click_function()

 
class ui_inputbox:

	def __init__(self, x, y, w, h, text='', pos_from_center = False):
		self.rect = pygame.Rect(x, y, w, h)
		self.color = constants.COLOR_LIGHT_GREY
		self.text = text

		self.txt_surface = pygame.Surface((w,h)) #constants.FONT_DEFAULT.render(text, True, self.color)
		self.active = False
		self.pos_from_center = pos_from_center

		if self.pos_from_center == True:


			x += constants.CAMERA_WIDTH/2
			y += constants.CAMERA_HEIGHT/2

			self.rect.center = (x,y)

			x -= w/2
			y -= h/2

			self.x = x
			self.y = y

		self.update()

	def handle_event(self, event):

		if event.type == pygame.MOUSEBUTTONDOWN:

			# If the user clicked on the input_box rect.
			if self.rect.collidepoint(event.pos):

				# Toggle the active variable.
				self.active = not self.active
			else:

				self.active = False
			# Change the current color of the input box.
			self.color = constants.COLOR_LIGHT_GREY if self.active else constants.COLOR_DARK_GREY
		if event.type == pygame.KEYDOWN:

			if self.active:

				if event.key == pygame.K_RETURN:
					#print(self.text)
					self.text = ''
				elif event.key == pygame.K_BACKSPACE:
					self.text = self.text[:-1]
				else:
					self.text += event.unicode
				# Re-render the text.
				self.update()

				#self.txt_surface = constants.FONT_DEFAULT.render(self.text, True, self.color)

	def update(self):
		# Resize the box if the text is too long.
		#width = max(200, self.txt_surface.get_width()+10)
		#self.rect.w = width

		self.txt_surface = pygame.Surface((self.rect.w,self.rect.h))
		self.txt_surface.fill(constants.COLOR_BLACK)

		self.msgs = util.wrapline(self.text, constants.FONT_MAIN_16, self.rect.w)
		i = 1
		for msg in self.msgs:
			util.draw_text(self.txt_surface, msg, (0, -20 + i * (util.helper_text_height("FONT_MAIN_12")+2) ), constants.COLOR_WHITE, font = "FONT_MAIN_12")
			i += 1	

	def draw(self, screen):

        # Blit the text.
		screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
		pygame.draw.rect(screen, self.color, self.rect, 2)

	







class player:

	def __init__(self):

		self.x = 5
		self.y = 5

		self.w = 3
		self.h = 3

def change_highlighted_blocks():

	if SUPER_LAYER == True:

		try:

			for a in range(constants.spritesheet_dict[str(VALUE_BOX.text)].width):
				for b in range(constants.spritesheet_dict[str(VALUE_BOX.text)].height):

					if MAP[PLAYER.x + a][PLAYER.y + b][DEPTH]:
						MAP[PLAYER.x + a][PLAYER.y + b][DEPTH].super_layer.append(str(VALUE_BOX.text) + "_" + str(a) + "_" + str(b))


		except:

			for i in range(PLAYER.w):
				for n in range(PLAYER.h):

					if MAP[PLAYER.x + i][PLAYER.y + n][DEPTH]:
						MAP[PLAYER.x + i][PLAYER.y + n][DEPTH].super_layer.append(str(VALUE_BOX.text))



	elif SUB_LAYER == True:
		for i in range(PLAYER.w):
			for n in range(PLAYER.h):

				if MAP[PLAYER.x + i][PLAYER.y + n]:
					MAP[PLAYER.x + i][PLAYER.y + n].sub_layer = str(VALUE_BOX.text) 

	elif SELECTION == "set_attr":
		for i in range(PLAYER.w):
			for n in range(PLAYER.h):
				try:
					val = float(ATTR_VAL_BOX.text)
				except ValueError:
					val = ATTR_VAL_BOX.text

				setattr(MAP[PLAYER.x + i][PLAYER.y + n][DEPTH], ATTR_BOX.text, val)

	elif SELECTION == "actor":
		for i in range(PLAYER.w):
			for n in range(PLAYER.h):

				OBJECTS[PLAYER.x + i][PLAYER.y + n] = ACTOR_BOX.text

	elif FORCE_DEPTH == 2:
		for i in range(PLAYER.w):
			for n in range(PLAYER.h):

				if SELECTION:
					OBJECTS[PLAYER.x + i][PLAYER.y + n] = SELECTION(PLAYER.x, PLAYER.y)

				else:
					OBJECTS[PLAYER.x + i][PLAYER.y + n] = None





	else:
		for i in range(PLAYER.w):
			for n in range(PLAYER.h):

				if SELECTION:
					MAP[PLAYER.x + i][PLAYER.y + n][DEPTH] = SELECTION(PLAYER.x, PLAYER.y, DEPTH)

				else:
					MAP[PLAYER.x + i][PLAYER.y + n][DEPTH] = None

def mouse_in_window(x, y, width, height):

	mouse_x, mouse_y = pygame.mouse.get_pos()

	mouse_x = int(mouse_x)
	mouse_y = int(mouse_y)

	rel_x = mouse_x - x
	rel_y = mouse_y - y
	if (rel_x > 0 and rel_y > 0) and (rel_x < width and rel_y < height):
		return (rel_x, rel_y)
	else:
		return None












def set_tile_by_name(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH, TILE_NAME_BOX
	try:
		SELECTION = getattr(tiles, TILE_NAME_BOX.text)
		FORCE_DEPTH = False
		if button:
			HIGHLIGHT = button.coords
			button.sprite_tag = SELECTION(0,0,0).sprite
	except:
		print "not a valid tile"


def set_stone_wall(stone_wall_button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.stone_wall
	FORCE_DEPTH = False
	if stone_wall_button:
		HIGHLIGHT = stone_wall_button.coords
def set_stone_floor(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.stone_floor
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_stair_up(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.stair_up
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_stair_down(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.stair_down
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_burning_tile(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.burning_tile
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_teleport_tile(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.boss_teleport_location
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_chest(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.chest
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_none(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = None
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_attr(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = "set_attr"
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords
def set_gate(button = None):
	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = tiles.boss_wall
	FORCE_DEPTH = False
	if button:
		HIGHLIGHT = button.coords

def set_actor(button = None):

	global SELECTION, HIGHLIGHT, FORCE_DEPTH
	SELECTION = "actor"
	FORCE_DEPTH = 2
	if button:
		HIGHLIGHT = button.coords		





def set_depth_0(button = None):
	global DEPTH, DEPTH_HIGHLIGHT
	DEPTH = 0
	if button:
		DEPTH_HIGHLIGHT = button.coords
def set_depth_1(button = None):
	global DEPTH, DEPTH_HIGHLIGHT
	DEPTH = 1
	if button:
		DEPTH_HIGHLIGHT = button.coords
def set_depth_2(button = None):

	print("PASS")

	# global DEPTH, DEPTH_HIGHLIGHT
	# DEPTH = 2
	# if button:
	# 	DEPTH_HIGHLIGHT = button.coords
def set_size_1(button = None):
	global PLAYER, SIZE_HIGHLIGHT
	PLAYER.w = 1
	PLAYER.h = 1
	SIZE_HIGHLIGHT = button.coords
def set_size_2(button = None):
	global PLAYER, SIZE_HIGHLIGHT
	PLAYER.w = 2
	PLAYER.h = 2
	SIZE_HIGHLIGHT = button.coords
def set_size_3(button = None):
	global PLAYER, SIZE_HIGHLIGHT
	PLAYER.w = 3
	PLAYER.h = 3
	SIZE_HIGHLIGHT = button.coords
def set_size_4(button = None):
	global PLAYER, SIZE_HIGHLIGHT
	PLAYER.w = 4
	PLAYER.h = 4
	SIZE_HIGHLIGHT = button.coords
def set_size_8(button = None):
	global PLAYER, SIZE_HIGHLIGHT
	PLAYER.w = 8
	PLAYER.h = 8
	SIZE_HIGHLIGHT = button.coords
def set_size_12(button = None):
	global PLAYER, SIZE_HIGHLIGHT
	PLAYER.w = 12
	PLAYER.h = 12
	SIZE_HIGHLIGHT = button.coords
def set_size_16(button = None):
	global PLAYER, SIZE_HIGHLIGHT
	PLAYER.w = 16
	PLAYER.h = 16
	SIZE_HIGHLIGHT = button.coords
def toggle_anims(button = None):
	global PAUSE_ANIMS

	if PAUSE_ANIMS == True:
		PAUSE_ANIMS = False
		print("anims resumed")

	else:
		PAUSE_ANIMS = True
		print("anims paused")
def toggle_super_layer(button = None):
	global SUPER_LAYER, LAYER_HIGHLIGHT

	if SUPER_LAYER == True:
		SUPER_LAYER = False
		button.color_box = constants.COLOR_GREY
		button.text_color = constants.COLOR_RED
		print("super layer off")

		LAYER_HIGHLIGHT = None
		

	else:
		SUPER_LAYER = True
		print("adding to super layer")
		button.text_color = constants.COLOR_BLACK
		button.color_box = constants.COLOR_RED

		if LAYER_HIGHLIGHT:
			LAYER_HIGHLIGHT.click()

		LAYER_HIGHLIGHT = button


def toggle_sub_layer(button = None):
	global SUB_LAYER, LAYER_HIGHLIGHT

	if SUB_LAYER == True:
		SUB_LAYER = False
		button.color_box = constants.COLOR_GREY
		button.text_color = constants.COLOR_RED
		print("sub layer off")

		LAYER_HIGHLIGHT = None

		

	else:
		SUB_LAYER = True
		print("adding to sub layer")
		button.text_color = constants.COLOR_BLACK
		button.color_box = constants.COLOR_RED

		if LAYER_HIGHLIGHT:
			LAYER_HIGHLIGHT.click()

		LAYER_HIGHLIGHT = button














def draw_map():

	camx , camy = CAMERA.map_address

	map_to_draw = MAP

	display_map_width = constants.CAMERA_WIDTH / constants.GAME_TILE_SIZE
	display_map_height = constants.CAMERA_HEIGHT / constants.GAME_TILE_SIZE

	render_min_w = camx - display_map_width/2 - 1
	render_min_h = camy - display_map_height/2 - 1

	render_max_w = camx + display_map_width/2 + 1
	render_max_h = camy + display_map_height/2 + 1

	render_min_w = util.clamp(render_min_w, 0, constants.GAME_TILES_X-1)
	render_min_h = util.clamp(render_min_h, 0, constants.GAME_TILES_Y-1)

	render_max_w = util.clamp(render_max_w, 0, constants.GAME_TILES_X-1)
	render_max_h = util.clamp(render_max_h, 0, constants.GAME_TILES_Y-1)

	for z in range(constants.GAME_TILES_Z):

		for x in range(render_min_w, render_max_w):
			for y in range(render_min_h, render_max_h):

				is_visable = True

				if is_visable:
					map_to_draw[x][y][0].explored = True

				if map_to_draw[x][y][0].explored == True:

				

					tile = map_to_draw[x][y][z]

					if tile != None:

						if tile.hidden == True and is_visable:

							if tile.hidden_animation and tile.activated == False:

								if CLOCK.get_fps() > 0.0:
									tile.hidden_flicker_timer += (1 / CLOCK.get_fps()) * (libtcod.random_get_int(0, 7, 13)/10)

								if tile.hidden_flicker_timer >= tile.hidden_flicker_speed:
									tile.hidden_flicker_timer = 0.0
									if tile.hidden_anim_index >= len((constants.anim_dict[tile.hidden_animation])) - 1:
										tile.hidden_anim_index = 0
									else:
									 tile.hidden_anim_index +=1

								SURFACE_MAP.blit(constants.anim_dict[tile.hidden_animation][tile.hidden_anim_index], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))
									


						elif tile.hidden == False:

							if tile.animation and len(tile.animation) > 1:
							

								if CLOCK.get_fps() > 0.0:
									tile.flicker_timer += 1 / CLOCK.get_fps()
								if tile.flicker_timer >= tile.flicker_speed:
									tile.flicker_timer = 0.0
									if tile.current_anim_index >= len((constants.anim_dict[tile.animation])) - 1:
										tile.current_anim_index = 0
									else:
									 tile.current_anim_index +=1

								if tile.sub_layer:
									SURFACE_MAP.blit(constants.anim_dict[tile.sub_layer], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

								SURFACE_MAP.blit(constants.anim_dict[tile.animation][tile.current_anim_index], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))
								
								for super_tile in tile.super_layer:
									SURFACE_MAP.blit(constants.anim_dict[super_tile], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

							else:

								if tile.sub_layer:
									SURFACE_MAP.blit(constants.anim_dict[tile.sub_layer], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

								SURFACE_MAP.blit(constants.anim_dict[tile.sprite], (x*constants.GAME_TILE_SIZE, y*constants.GAME_TILE_SIZE) )

								for super_tile in tile.super_layer:
									SURFACE_MAP.blit(constants.anim_dict[super_tile], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

							if not is_visable:
								SURFACE_MAP.blit(constants.S_TINT_DARK, (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))



				if OBJECTS[x][y]:
					util.draw_text(SURFACE_MAP, str(OBJECTS[x][y]), (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE), constants.COLOR_GREEN, back_color = None, font = "FONT_DEFAULT", center = False)

def draw_tile_at_coords(tile, x, y, require_visability = True):

	if tile.animation:


		if (require_visability == True and libtcod.map_is_in_fov(FOV_MAP, x, y) == True):

					if len(tile.animation) > 1:
						
						if CLOCK.get_fps() > 0.0:
							tile.flicker_timer += 1 / CLOCK.get_fps()

						if tile.flicker_timer >= tile.flicker_speed:
							tile.flicker_timer = 0.0

							if tile.current_anim_index >= len(tile.animation) - 1:
								tile.current_anim_index = 0
							else:
							 tile.current_anim_index +=1

						SURFACE_MAP.blit(constants.anim_dict[tile.animation][0], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

					
	elif not tile.animation:

		SURFACE_MAP.blit(constants.anim_dict[tile.sprite], (x*constants.GAME_TILE_SIZE, y*constants.GAME_TILE_SIZE) )

		#print((x,y))

def draw_attr_menu():

	menu_width = 300
	menu_height = 400
	menu_font = "FONT_DEFAULT"

	buff = constants.MENU_BUFFER

	coords_x = constants.CAMERA_WIDTH - menu_width
	coords_y = 0

	gui_surface = pygame.Surface((menu_width, menu_height))

	gui_surface.fill(constants.COLOR_BLACK)

	util.draw_text(gui_surface, "ATTR:", (10, 50), constants.COLOR_WHITE)
	util.draw_text(gui_surface, "ATTR Value:", (10, 150), constants.COLOR_WHITE)

	cur_val = ""
	if MAP[PLAYER.x][PLAYER.y][DEPTH]:
		if hasattr(MAP[PLAYER.x][PLAYER.y][DEPTH], ATTR_BOX.text):
			cur_val = getattr(MAP[PLAYER.x][PLAYER.y][DEPTH], ATTR_BOX.text)

	util.draw_text(gui_surface, "Current Val:" + str(cur_val), (10, 350), constants.COLOR_WHITE)

	SURFACE_MAIN.blit(gui_surface, (coords_x, coords_y))

	ATTR_BOX.update()
	ATTR_BOX.draw(SURFACE_MAIN)

	

	ATTR_VAL_BOX.update()
	ATTR_VAL_BOX.draw(SURFACE_MAIN)

def draw_actor_menu():

	menu_width = 300
	menu_height = 150
	menu_font = "FONT_DEFAULT"

	buff = constants.MENU_BUFFER

	coords_x = constants.CAMERA_WIDTH - menu_width
	coords_y = 0

	gui_surface = pygame.Surface((menu_width, menu_height))

	gui_surface.fill(constants.COLOR_BLACK)

	util.draw_text(gui_surface, "Actor:", (10, 50), constants.COLOR_WHITE)

	SURFACE_MAIN.blit(gui_surface, (coords_x, coords_y))

	ACTOR_BOX.update()
	ACTOR_BOX.draw(SURFACE_MAIN)

def draw_gui():

	global SELECTION, DEPTH, HIGHLIGHT, DEPTH_HIGHLIGHT, SIZE_HIGHLIGHT, BUTTONS

	menu_close = False
	menu_width = constants.MENU_WIDTH
	menu_height = constants.CAMERA_HEIGHT #constants.GAME_TILES_Y * constants.GAME_TILE_SIZE
	menu_font = "FONT_DEFAULT"

	buff = constants.MENU_BUFFER

	coords_x =  0
	coords_y = 0

	gui_surface = pygame.Surface((menu_width, menu_height))
	

	gui_surface.fill(constants.COLOR_BLACK)

	for box in TEXT_BOXES:
		box.update()
		box.draw(gui_surface)

	for button in BUTTONS:
		button.surface = gui_surface
		button.draw()

	


	gui_surface.blit(pygame.transform.scale(constants.S_TINT_RED, (50, 50) ), HIGHLIGHT)
	gui_surface.blit(pygame.transform.scale(constants.S_TINT_RED, (50, 50) ), DEPTH_HIGHLIGHT)
	gui_surface.blit(pygame.transform.scale(constants.S_TINT_RED, (50, 50) ), SIZE_HIGHLIGHT)

	if SELECTION == "set_attr":
		draw_attr_menu()

	if SELECTION == "actor":
		draw_actor_menu()



	SURFACE_MAIN.blit(gui_surface, (0,0))

def main_loop():
	global MOUSE_CLICKED

	exit = False

	while exit == False:

		MOUSE_CLICKED = False

		action = handle_input()
		if action == "QUIT":
			quit_game()



		draw()
		CLOCK.tick()

def draw():

	global SURFACE_MAIN

	#todo clear
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

	#draw_tile_at_coords(tiles.wall_1(0,0), 0, 0)

	CAMERA.update()

	display_rect = pygame.Rect( (0,0), (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT) )

	draw_map()
	for i in range(PLAYER.w):
		for n in range(PLAYER.h):
			draw_tile_at_coords(tiles.target(PLAYER.x + i, PLAYER.y + n, 1), PLAYER.x + i, PLAYER.y + n)


	SURFACE_MAIN.blit(SURFACE_MAP, (0,0), CAMERA.rect)
	draw_gui()

	#todo update display
	pygame.display.flip()

def Save_map(text_box):

	print("SAVE")

	name = text_box.text

	for z in range(0,constants.GAME_TILES_Z):
		for y in range(0, constants.GAME_TILES_Y):
			for x in range(0,constants.GAME_TILES_X):
				if MAP[x][y][z]:
					MAP[x][y][z].explored = False

	try:

		with gzip.open(name + ".mp", 'wb') as file:
			pickle.dump((MAP, OBJECTS), file)

			print("SAVE COMPLETE")

	except:
		print("SAVE FAILED")

def Load_map(text_box):
	global MAP, OBJECTS

	print("LOAD")

	name = text_box.text

	try:

		with gzip.open(name + ".mp", 'rb') as file:

			loaded_map, objects = pickle.load(file)

			MAP = loaded_map
			OBJECTS = objects

			print("LOAD COMPLETE")

	except:

		print("LOAD FAILED")

def quit_game():

	

	print("QUIT")

	pygame.quit()
	exit()

def init():

	global SURFACE_MAIN, MOUSE_CLICKED, SELECTION, MAP, CAMERA, SURFACE_MAP, PLAYER, DEPTH, DEPTH_HIGHLIGHT, HIGHLIGHT, SIZE_HIGHLIGHT, KEY_BINDINGS, BUTTONS, CLOCK
	global TEXT_BOXES, FORCE_DEPTH, OBJECTS, SUPER_LAYER, SUB_LAYER, LAYER_HIGHLIGHT, VALUE_BOX, TILE_NAME_BOX, ATTR_BOX, ATTR_VAL_BOX, ACTOR_BOX
	pygame.init()
	pygame.key.set_repeat(150, 40)

	SURFACE_MAIN = pygame.display.set_mode( (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT) )
	SURFACE_MAP = pygame.Surface((constants.GAME_TILES_X * constants.GAME_TILE_SIZE, constants.GAME_TILES_Y * constants.GAME_TILE_SIZE))

	CLOCK = pygame.time.Clock()	

	MOUSE_CLICKED = False

	FORCE_DEPTH = False

	SUPER_LAYER = False
	SUB_LAYER = False
	LAYER_HIGHLIGHT = None

	SELECTION = tiles.stone_wall

	DEPTH_HIGHLIGHT = (300,0)
	HIGHLIGHT = (-100,-100)
	SIZE_HIGHLIGHT = (-100,-100)


	MAP = [ [ [None  for z in range(0,constants.GAME_TILES_Z)  ] for y in range(0, constants.GAME_TILES_Y)  ] for x in range(0,constants.GAME_TILES_X) ]
	OBJECTS = [ [ None for y in range(0, constants.GAME_TILES_Y)  ] for x in range(0,constants.GAME_TILES_X) ]

	for x in range(constants.GAME_TILES_X):
		for y in range(constants.GAME_TILES_Y):
			MAP[x][y][0] = tiles.stone_wall(x,y,0)


	PLAYER = player()
	CAMERA = obj_camera()

	KEY_BINDINGS = []
	TEXT_BOXES = []

	DEPTH = 0


	BUTTONS = []

	stone_wall_button = ui_button("gui_surface", (0 *50,0 *50), (50,50), " ", click_function = set_stone_wall, sprite_tag = tiles.stone_wall(0,0, 0).sprite)
	stone_wall_button.click_function_params = stone_wall_button
	BUTTONS.append(stone_wall_button)

	stone_floor_button = ui_button("gui_surface", (1 *50,0 *50), (50,50), " ", click_function = set_stone_floor, sprite_tag = tiles.stone_floor(0,0,0).sprite)
	stone_floor_button.click_function_params = stone_floor_button	
	BUTTONS.append(stone_floor_button)

	stair_up_button = ui_button("gui_surface", (2 *50,0 *50), (50,50), "", click_function = set_stair_up, sprite_tag = tiles.stair_up(0,0,0).sprite)
	stair_up_button.click_function_params = stair_up_button
	BUTTONS.append(stair_up_button)

	stair_down_button = ui_button("gui_surface", (3 *50,0 *50), (50,50), "", click_function = set_stair_down, sprite_tag = tiles.stair_down(0,0,0).sprite)
	stair_down_button.click_function_params = stair_down_button
	BUTTONS.append(stair_down_button)

	burning_tile_button = ui_button("gui_surface", (0 *50,1 *50), (50,50), "", click_function = set_burning_tile, sprite = constants.anim_dict[tiles.burning_tile(0,0,0).animation][0])
	burning_tile_button.click_function_params = burning_tile_button
	BUTTONS.append(burning_tile_button)

	teleport_tile_button = ui_button("gui_surface", (1 *50,1 *50), (50,50), "", click_function = set_teleport_tile, sprite = constants.anim_dict[tiles.boss_teleport_location(0,0,0).sprite_scaled] )
	teleport_tile_button.click_function_params = teleport_tile_button
	BUTTONS.append(teleport_tile_button)

	chest_button = ui_button("gui_surface", (2 *50,1 *50), (50,50), "", click_function = set_chest, sprite = constants.anim_dict[tiles.chest(0,0,0).sprite] )
	chest_button.click_function_params = chest_button
	BUTTONS.append(chest_button)

	none_button = ui_button("gui_surface", (3 *50,1 *50), (50,50), "remove", click_function = set_none, font = "FONT_DEFAULT")
	none_button.click_function_params = none_button
	BUTTONS.append(none_button)

	attr_button = ui_button("gui_surface", (3 *50,2 *50), (50,50), "Attr", click_function = set_attr, font = "FONT_DEFAULT")
	attr_button.click_function_params = attr_button
	BUTTONS.append(attr_button)

	gate_button = ui_button("gui_surface", (0 *50,2 *50), (50,50), "", click_function = set_gate, sprite = constants.anim_dict[tiles.boss_wall(0,0,0).sprite] )
	gate_button.click_function_params = gate_button
	BUTTONS.append(gate_button)




	actor_button = ui_button("gui_surface", (0 *50,3 *50), (50,50), "actor", click_function = set_actor, font = "FONT_DEFAULT") 
	actor_button.click_function_params = actor_button
	BUTTONS.append(actor_button)






	save_box = ui_inputbox(1 *50, 10*50, 150, 25, text='test', pos_from_center = False)
	TEXT_BOXES.append(save_box)

	Save_button = ui_button("gui_surface", (0 *50,10 *50), (50,50), "Save", click_function = Save_map, font = "FONT_DEFAULT", click_function_params = save_box)
	BUTTONS.append(Save_button)

	load_button = ui_button("gui_surface", (3 *50,10 *50), (50,50), "Load", click_function = Load_map, font = "FONT_DEFAULT", click_function_params = save_box)
	BUTTONS.append(load_button)

	


	super_layer_button = ui_button("gui_surface", (0 *50, 9 *50), (50,50), "Super", click_function = toggle_super_layer, font = "FONT_DEFAULT")
	super_layer_button.click_function_params = super_layer_button
	BUTTONS.append(super_layer_button)

	sub_layer_button = ui_button("gui_surface", (3 *50, 9 *50), (50,50), "Sub", click_function = toggle_sub_layer, font = "FONT_DEFAULT")
	sub_layer_button.click_function_params = sub_layer_button
	BUTTONS.append(sub_layer_button)

	value_box = ui_inputbox(1 *50, 9*50, 150, 25, text='NONE', pos_from_center = False)
	TEXT_BOXES.append(value_box)
	VALUE_BOX = value_box



	tile_name_button = ui_button("gui_surface", (0 *50, 5 *50), (50,50), "Tile", click_function = set_tile_by_name, font = "FONT_DEFAULT")
	tile_name_button.click_function_params = tile_name_button
	BUTTONS.append(tile_name_button)

	tile_name_box = ui_inputbox(1 *50, 5*50, 150, 25, text='stone_wall', pos_from_center = False)
	TEXT_BOXES.append(tile_name_box)
	TILE_NAME_BOX = tile_name_box


	depth_0_button = ui_button("gui_surface", (0 *50, 6 *50), (50,50), "0", click_function = set_depth_0)
	depth_0_button.click_function_params = depth_0_button
	BUTTONS.append(depth_0_button)

	depth_1_button = ui_button("gui_surface", (1 *50, 6 *50), (50,50), "1", click_function = set_depth_1)
	depth_1_button.click_function_params = depth_1_button
	BUTTONS.append(depth_1_button)

	depth_2_button = ui_button("gui_surface", (2 *50, 6 *50), (50,50), "objects", click_function = set_depth_2, font = "FONT_DEFAULT")
	depth_2_button.click_function_params = depth_2_button
	BUTTONS.append(depth_2_button)

	size_1_button = ui_button("gui_surface", (0 *50, 7 *50), (50,50), "1", click_function = set_size_1)
	size_1_button.click_function_params = size_1_button
	BUTTONS.append(size_1_button)

	size_2_button = ui_button("gui_surface", (1 *50, 7 *50), (50,50), "2", click_function = set_size_2)
	size_2_button.click_function_params = size_2_button
	BUTTONS.append(size_2_button)

	size_3_button = ui_button("gui_surface", (2 *50, 7 *50), (50,50), "3", click_function = set_size_3)
	size_3_button.click_function_params = size_3_button
	BUTTONS.append(size_3_button)

	size_4_button = ui_button("gui_surface", (3 *50, 7 *50), (50,50), "4", click_function = set_size_4)
	size_4_button.click_function_params = size_4_button
	BUTTONS.append(size_4_button)

	size_8_button = ui_button("gui_surface", (0 *50, 8 *50), (50,50), "8", click_function = set_size_8)
	size_8_button.click_function_params = size_8_button
	BUTTONS.append(size_8_button)

	size_12_button = ui_button("gui_surface", (1 *50, 8 *50), (50,50), "12", click_function = set_size_12)
	size_12_button.click_function_params = size_12_button
	BUTTONS.append(size_12_button)

	size_16_button = ui_button("gui_surface", (2 *50, 8 *50), (50,50), "16", click_function = set_size_16)
	size_16_button.click_function_params = size_16_button
	BUTTONS.append(size_16_button)

	toggle_anims_button = ui_button("gui_surface", (3 *50, 8 *50), (50,50), "anims", click_function = toggle_anims, font = "FONT_DEFAULT")
	toggle_anims_button.click_function_params = toggle_anims_button
	BUTTONS.append(toggle_anims_button)
	global PAUSE_ANIMS
	PAUSE_ANIMS = False

	ATTR_BOX = ui_inputbox(constants.CAMERA_WIDTH - 275, 75, 175, 25, "attr")
	ATTR_VAL_BOX = ui_inputbox(constants.CAMERA_WIDTH - 275, 175, 225, 150, "attrVal")
	ACTOR_BOX = ui_inputbox(constants.CAMERA_WIDTH - 275, 75, 175, 25, "actor")



	


def handle_input():
	global BIND_KEY, MOUSE_CLICKED
	BIND_KEY = None
	events_list = pygame.event.get()


	#todo process input
	for event in events_list:
		if event.type == pygame.QUIT:
			return "QUIT"

		found_key = False

		for box in TEXT_BOXES:
			box.handle_event(event)
			if box.active == True:
				found_key = True

		ATTR_BOX.handle_event(event)
		if ATTR_BOX.active == True:
				found_key = True
		ATTR_VAL_BOX.handle_event(event)
		if ATTR_VAL_BOX.active == True:
				found_key = True

		ACTOR_BOX.handle_event(event)
		if ACTOR_BOX.active == True:
				found_key = True

		
		if event.type == pygame.MOUSEBUTTONDOWN and found_key == False:
			if event.button == 1:
				MOUSE_CLICKED = True
				return ("CLICK")


		
		

						

		



		if event.type == pygame.KEYDOWN and found_key == False:

			if event.key == pygame.K_d and found_key == False:
				PLAYER.x += 1
				found_key = True

			elif event.key == pygame.K_a and found_key == False:
				PLAYER.x -= 1
				found_key = True

			elif event.key == pygame.K_w and found_key == False:
				PLAYER.y -= 1
				found_key = True

			elif event.key == pygame.K_s and found_key == False:
				PLAYER.y += 1
				found_key = True

			elif event.key == pygame.K_e and found_key == False:
				change_highlighted_blocks()
				found_key = True

			elif found_key == False:
				for keybind in KEY_BINDINGS:
					key, func, param = keybind
					key = key.key
					if event.key == key:
						func(param)
						found_key = True

			


			if found_key == False:
				BIND_KEY = event
				#print(event.unicode)

def Run():
	init()
	main_loop()


if __name__ == '__main__':
	Run()
	
	




