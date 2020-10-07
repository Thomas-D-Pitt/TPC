

import Game
import constants
import pygame
import util

Mod_id = 666 #a mod_id and version must be declared in order for the mod to load
Mod_version = 0.1 #the variables are case sensative and must be spelled exactly as they are here

def credit_card_transfer(amount = 0.0):

	message = "spend $" + str(amount)
	yes = "Yes"
	no = "No"
	yes_function = None
	no_function = None

	button_size_x = 70
	button_size_y = 30
	text_height = 0

	spacer = 3

	menu_width = 200 
	menu_height = button_size_y + util.helper_text_height("FONT_DIABLO_18") + spacer + text_height
	#buff = constants.MENU_BUFFER

	coords_x =  constants.CAMERA_WIDTH/2 - menu_width/2 
	coords_y = constants.CAMERA_HEIGHT/2 - menu_height/2 

	text_surface = pygame.Surface((menu_width, menu_height))
	text_surface.fill(constants.COLOR_DARK_GREY)



	pos = (coords_x, coords_y + menu_height - button_size_y)
	pos4 = (coords_x + menu_width - button_size_x, coords_y + menu_height - button_size_y)
	pos2 = (coords_x + menu_width - button_size_x, coords_y)
	x3 = coords_x
	y3 = coords_y
	pos5 = (coords_x + menu_width/2 - button_size_x/2, coords_y + menu_height - button_size_y)

	size = (button_size_x, button_size_y)


	response = False
	drop_item = False


	yes_button = Game.ui_button(Game.SURFACE_MAIN, pos4, size, yes, click_function = yes_function, click_function_params = None,
	 font = "FONT_DEFAULT")

	no_button = Game.ui_button(Game.SURFACE_MAIN, pos, size, no, click_function = no_function, click_function_params = None,
	 font = "FONT_DEFAULT")


	while True:
					
		Game.SURFACE_MAIN.blit(text_surface, (coords_x, coords_y))

		events_list = pygame.event.get()

		util.draw_text(Game.SURFACE_MAIN, message, (constants.CAMERA_WIDTH/2, coords_y + spacer*2), constants.COLOR_WHITE, font = "FONT_DIABLO_18", center = True)

		for event in events_list:
			if event.type == pygame.QUIT:
				Game.quit_game()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					Game.MOUSE_CLICKED = True
		

		if yes_button.draw() == "END" :
			val = True
			break

		elif no_button.draw() == "END" :
			val = False
			break



		Game.MOUSE_CLICKED = False
		Game.CLOCK.tick()
		pygame.display.flip()

	return val

def spell_credit_card(caster = None, value = 10, origin = None, Shoot = False, target = None, radius = 0, m_range = 50):

	start_pos = origin
	max_range = m_range
	penetrate_walls = False
	penetrate_characters = False#ignore characters along path = false
	name = spell_credit_card
	hit_along_path = False#can hit multiple characters
	can_cast_on_self = True
	caster = caster

	if origin == None:
		origin = (caster.x, caster.y)
		start_pos = origin
	
	if Shoot == False:	
		Game.ONGOING_FUNCTIONS.append((Game.select, [start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name, [caster, value, start_pos, True, "SELECT_RESULT", radius]))


	else:

		list_of_tiles = target





		for x,y in list_of_tiles:

			hit = Game.map_check_for_creatures(x,y)

			if hit and ((x,y) != origin or can_cast_on_self == True):
				####ACUTAL AFFECT####
				####ACUTAL AFFECT####
				####ACUTAL AFFECT####

				if hit.creature and not hit.player:

					result = credit_card_transfer(round(float(hit.creature.hp)/300, 2))

					if result == True:
						hit.creature.death_function(hit)

		if caster == Game.PLAYER:
			Game.PLAYER_TOOK_ACTION = "SPELL"

def init():
	pass
	
def menu_start():
	Game.message_box_while_loop("Enter~Credit~Card~information: disabled for testing")

def game_start():

	Game.learn_spell(Game.PLAYER, "Credit Card", spell_credit_card, ["10 * *LEVEL*", None, False, None, "*LEVEL* / 3 + 1"], 0, 0 )
	#Game.ONGOING_FUNCTIONS_GUI.append((Game.yes_no_box, ("test message", None, None, "yes", "no"), None, None))

