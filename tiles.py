

import constants
import sys
sys.path.insert(0, '..')
import Game
import effects
import util
import spells
import libtcodpy as libtcod



class tile(object):

	block_path = False
	block_light = False
	explored = False
	sprite = "NONE"
	animation = None
	name = "tile"

	emit_light_radius = None
	light = 0

	hidden = False
	hidden_sprite = None
	hidden_animation = "HIDDEN"
	hidden_flicker_timer = 0
	hidden_flicker_speed = constants.HIDDEN_FLICKER_SPEED
	hidden_anim_index = libtcod.random_get_int(0, 0, 15)
	

	def __init__(self, x, y, z):
		
		self.x = x
		self.y = y
		self.z = z

		self.sub_layer = None
		self.super_layer = []

		if hasattr(self, "map_color") == False:

			if self.block_path:
				self.map_color = constants.COLOR_DARK_GREY

			else:
				self.map_color = constants.COLOR_LIGHT_GREY


		
	def step_onto(self, character, player):

		pass

	def interact(self, interactor):

		return "NONE"

	def step_off(self, character, player):

		pass

	def reveal(self):

		return "NONE"

	def stand_on_tick(self, character, delta_time):

		pass

	def get_critical_properties(self):

		return (self.name.replace(" ", "_")).lower()

	def set_critical_properties(self, properties):

		pass

	def get_tile_info(self):
		return "default method | tile name: " + self.name



class stone_floor(tile):

	sprite = "ROCK_FLOOR"
	name = "stone floor"

class stone_wall(tile):

	block_path = True
	block_light = True
	sprite = "WALL_1"
	name = "stone wall"

class wood_door(tile):

	block_path = True
	block_light = True
	sprite = "WOOD_DOOR"
	name = "wood door"

class fence(tile):

	block_path = True
	block_light = True
	sprite = "FENCE"
	name = "fence"

class fence_2(tile):

	block_path = True
	block_light = True
	sprite = "FENCE_2"
	name = "fence"

class fence_3(tile):

	block_path = True
	block_light = True
	sprite = "FENCE_3"
	name = "fence"

class fence_4(tile):

	block_path = True
	block_light = True
	sprite = "FENCE_4"
	name = "fence"

class grass(tile):
	animation = "GRASS_1"
	animation_loop_speed = 15
	flicker_timer = 0
	flicker_speed = .4
	current_anim_index = 0

	name = "grass"

class grass_2(tile):
	animation = "GRASS_2"
	animation_loop_speed = 15
	flicker_timer = 0
	flicker_speed = .4
	current_anim_index = 0

	name = "grass"

class dark_grass_1(tile):
	sprite = "DARK_GRASS_1"
	name = "grass"
class dark_grass_2(tile):
	sprite = "DARK_GRASS_2"
	name = "grass"
class dark_grass_3(tile):
	sprite = "DARK_GRASS_3"
	name = "grass"
class dark_grass_4(tile):
	sprite = "DARK_GRASS_4"
	name = "grass"
class dark_grass_5(tile):
	sprite = "DARK_GRASS_5"
	name = "grass"
class dark_grass_6(tile):
	sprite = "DARK_GRASS_6"
	name = "grass"
class dark_grass_7(tile):
	sprite = "DARK_GRASS_7"
	name = "grass"
class dark_grass_8(tile):
	sprite = "DARK_GRASS_8"
	name = "grass"
class dark_grass_9(tile):
	sprite = "DARK_GRASS_9"
	name = "grass"

class dark_path_1(tile):
	sprite = "DARK_PATH_1"
	name = "path"
class dark_path_2(tile):
	sprite = "DARK_PATH_2"
	name = "path"
class dark_path_3(tile):
	sprite = "DARK_PATH_3"
	name = "path"
		
class dirt_floor(tile):

	sprite = "DIRT_FLOOR"
	name = "dirt floor"

class dirt_wall(tile):

	block_path = True
	block_light = True
	sprite = "DIRT_WALL"
	name = "dirt wall"

class target(tile):

	sprite = "TARGET"
	name = "target"

	map_color = None

class wall_1(tile):

	block_path = True
	block_light = True

	sprite = "WALL_2"
	name = "stone wall"

	def get_critical_properties(self):

		return "wall_1"

class stair(tile):

	sprite = "STAIR_DOWN"
	name = "stair"

	map_color = constants.COLOR_RED

	leads_to = "NONE"

	def interact(self, interactor):

		interactor.level_transition(self.leads_to)

		return "LEVEL_CHANGE"

	def get_critical_properties(self):

		return ("stair", self.leads_to, self.super_layer)

	def set_critical_properties(self, properties):

		func, leads_to, super_layer = properties

		self.leads_to = leads_to
		self.super_layer = super_layer

	def get_tile_info(self):
		return ("name: " + self.name + " leads_to: " + str(self.leads_to))

class stair_down(tile):

	sprite = "STAIR_DOWN"
	name = "stair down"

	map_color = constants.COLOR_RED

	def interact(self, interactor):

		interactor.go_down()

		return "GO_DOWN"

class stair_up(tile):

	sprite = "STAIR_UP"
	name = "stair up"

	map_color = constants.COLOR_RED


	def interact(self, interactor):

		interactor.go_up()

		return "GO_UP"

class campfire(tile):

	animation = "CAMPFIRE"
	name = "campfire"

	map_color = constants.COLOR_ORANGE

	animation_loop_speed = 1.5
	flicker_timer = 0
	flicker_speed = 1.5 / 4 #animation_loop_speed / len(animation)
	current_anim_index = 0
	
	emit_light_radius = 4.5
	light = 4.5

	def __init__(self, x, y, z):

		super(campfire, self).__init__(x, y, z)

		self.sub_layer = "CAMP_FIRE_GLOW_2_2"

		self.printed_nearby_message = False

	def step_onto(self, character, player):

		if character == player:
			player.creature.take_damage(0, "Ouch, maybe I should just sit near the fire instead", fire_damage = 2, color = constants.COLOR_LIGHT_RED, ignore_armor = True)

class campfire_nearby(tile):

	name = ""

	map_color = None

	emit_light_radius = 4.5
	light = 4.5

	def __init__(self, x, y, z, tile_index = (0,0) ):#tile index = tuple ((-1->1), (-1->1))
	
		super(campfire_nearby, self).__init__(x, y, z)

		self.tile_index = tile_index
		x1, y1 = self.tile_index
		self.sprite = "CAMP_FIRE_GLOW_" + str(x1 + 2) + "_" + str(y1 + 2)

		self.fire = None


	def step_onto(self, character, player):

		if self.fire and self.fire.printed_nearby_message == False:
			character.creature.message("the fire looks comforting", constants.COLOR_PURPLE, only_when_player = True)
			self.fire.printed_nearby_message = True

	def interact(self, interactor):

		if interactor.player:
			Game.campfire_menu()

		return "NONE"

	def get_critical_properties(self):

		return ("campfire_nearby", self.tile_index)

	def set_critical_properties(self, properties):

		func, self.tile_index = properties

		x1, y1 = self.tile_index
		self.sprite = "CAMP_FIRE_GLOW_" + str(x1 + 2) + "_" + str(y1 + 2)

class p_confused(tile):

	animation = "CONFUSION"
	animation_loop_speed = 1.5
	flicker_timer = 0
	flicker_speed = 1.5 / 3 #animation loop speed / length of animation
	current_anim_index = 0

	map_color = None

	name = "p_confused"

class p_fire(tile):

	animation = "FIRE_1"
	animation_loop_speed = 1.5
	flicker_timer = 0
	flicker_speed = 1.5 / 8 #animation loop speed / length of animation
	current_anim_index = 0
	name = "p_fire"

	map_color = None

	def __init__(self, x, y, z):#tile index = tuple ((-1->1), (-1->1))
	
		super(p_fire, self).__init__(x, y, z)

		self.current_anim_index = libtcod.random_get_int(0, 0, len(constants.anim_dict[self.animation]) - 1)

class p_x(tile):

	sprite = "X"
	name = "x"

	map_color = None

class chest(tile):

	sprite = "CHEST_CLOSED"
	name = "Chest"

	map_color = None

	activated = False

	def interact(self, interactor):

		if interactor.player and self.activated == False:
			for i in range(3):
				interactor.player.spawn_random_item((self.x, self.y), 1.0)
				self.sprite = "CHEST_OPENED"
				self.activated = True

			interactor.player.network_tile_update((self.x, self.y, self.z))

		return "ITEM_ACTION"


	def get_critical_properties(self):

		return ("chest", self.sprite, self.activated)

	def set_critical_properties(self, properties):

		func, sprite, activated = properties

		self.sprite = sprite
		self.activated = activated

class trapped_chest(tile):

	sprite = "CHEST_CLOSED"
	name = "Trapped Chest"

	map_color = None

	activated = False

	def interact(self, interactor):

		if interactor.player and self.activated == False:
			for i in range(1):
				interactor.player.spawn_random_item((self.x, self.y), 1.0)
				interactor.creature.take_damage(2, "The chest was trapped!", color = constants.COLOR_RED)
				self.sprite = "CHEST_OPENED"
				self.activated = True

			interactor.player.network_tile_update((self.x, self.y, self.z))

		return "ITEM_ACTION"

	def get_critical_properties(self):

		return ("trapped_chest", self.sprite, self.activated)

	def set_critical_properties(self, properties):

		func, sprite, activated = properties

		self.sprite = sprite
		self.activated = activated

class hidden_door(tile):

	sprite = "WALL_1"
	name = "Unusual Wall"

	map_color = None

	hidden = True
	activated = False

	def __init__(self, x, y, z):#tile index = tuple ((-1->1), (-1->1))
	
		super(hidden_door, self).__init__(x, y, z)

		self.hidden_anim_index = libtcod.random_get_int(0, 0, 15)


	def get_critical_properties(self):

		return "hidden_door"

	def set_critical_properties(self, properties):

		pass


class message_tile(tile):

	sprite = "BOOK_PEDESTAL"

	name = "Pedestal"

	map_color = constants.COLOR_BROWN_2

	message = None
	activated = False

	def step_onto(self, character, player):

		if self.message and self.activated == False and character == player:
			Game.message_box(self.message)
			self.activated = True

	def interact(self, interactor):

		if self.message:
			Game.message_box(self.message)

	def get_critical_properties(self):

		return ("message_tile", self.message)

	def set_critical_properties(self, properties):

		func, self.message = properties


class strange_pool(tile):

	name = "Strange pool of liquid"

	activated = False

	map_color = constants.COLOR_GREEN

	def interact(self, interactor):

		if interactor.player:
			interactor.creature.message("You drink from the pool of liquid", constants.COLOR_PINK, only_when_player = True)
			interactor.player.random_potion_effect()
			self.sprite = "NONE"#change sprite to nothing

			interactor.player.network_tile_update((self.x, self.y, self.z))

	def get_critical_properties(self):

		return "strange_pool"

	def set_critical_properties(self, properties):

		pass

class trap_base(tile):

	name = "Trap Base"

	hidden = True
	activated = False

	color = None

	def __init__(self, x, y, z):
	
		super(trap_base, self).__init__(x, y, z)
		
		self.hidden_anim_index = libtcod.random_get_int(0, 0, 15)



class trap_instant_posion_cloud(trap_base):

	name = "Posion Cloud Trap"

	animation = "FIRE_1"
	animation_loop_speed = 1.5
	flicker_timer = 0
	flicker_speed = 1.5 / 8
	current_anim_index = 0
	


	def step_onto(self, character, player):

		if self.activated == False:
			
			self.activated = True
			self.hidden = False

			player.player.network_tile_update((self.x, self.y, self.z))

			self.animation = "GAS_CLOUD" #posion cloud

			if character and character.creature:
				character.creature.message("A cloud of posion rises from the ground", constants.COLOR_GREEN, only_when_player = True)

		if character and character.creature:
			character.creature.take_damage(0, "you choke on the gas", posion_damage = 22, color = constants.COLOR_GREEN)

	def get_critical_properties(self):

		return ("trap_instant_posion_cloud", self.sprite, self.activated, self.hidden)

	def set_critical_properties(self, properties):

		func, self.sprite, self.activated, self.hidden = properties

class trap_instant_posion_dart(trap_base):

	name = "Posion Dart Trap"

	def step_onto(self, character, player):

		if self.activated == False:
			
			self.activated = True

			if character and character.creature:
				character.creature.message("A dart hits the back of your neck", constants.COLOR_GREEN, only_when_player = True)
				character.creature.take_damage(10, "The dart was posioned", posion_damage = 15, color = constants.COLOR_GREEN)

			player.player.network_tile_update((self.x, self.y, self.z))

	def get_critical_properties(self):

		return ("trap_instant_posion_dart", self.activated)

	def set_critical_properties(self, properties):

		func, self.activated = properties

class trap_dart(trap_base):

	name = "Dart Trap"

	def step_onto(self, character, player):

		if self.activated == False:
			self.activated = True

			if character and character.creature:
				character.creature.message("A dart hits the back of your neck", constants.COLOR_GREEN, only_when_player = True)
				character.creature.take_damage(20, color = constants.COLOR_WHITE)

			player.player.network_tile_update((self.x, self.y, self.z))

	def get_critical_properties(self):

		return ("trap_dart", self.activated)

	def set_critical_properties(self, properties):

		func, self.activated = properties

class trap_floor_spikes(trap_base):

	name = "Spike Trap"

	def step_onto(self, character, player):

		if self.activated == True:
			if character and character.creature:
				character.creature.take_damage(10, "you implale your foot on the spikes", color = constants.COLOR_WHITE)


		elif self.activated == False:

			if character and character.creature:

				character.creature.message("Spikes shoot up from the floor", constants.COLOR_LIGHT_RED, only_when_player = True)
				character.creature.take_damage(40, color = constants.COLOR_WHITE)

			self.activated = True
			self.sprite = "SPIKES"#floor spikes
			self.hidden = False
			player.player.network_tile_update((self.x, self.y, self.z))

	def get_critical_properties(self):

		return ("trap_floor_spikes", self.activated, self.sprite, self.hidden)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite, self.hidden = properties

class trap_falling_boulder(trap_base):

	name = "Boulder Trap"

	def step_onto(self, character, player):

		if self.activated == False:
			self.activated = True

			if character and character.creature:


				character.creature.message("A Boulder falls from above", constants.COLOR_BROWN, only_when_player = True)
			
				if character.creature.dex_roll > 3 or character.creature.luck_roll > 3:
					message = ["You jump out of the way just in time", "The rock scrapes your shoulder"]
					character.creature.message(message[libtcod.random_get_int(0, 0, len(message) - 1)], constants.COLOR_BROWN, only_when_player = True)
				else:
					character.creature.take_damage(60, color = constants.COLOR_WHITE)

			player.player.network_tile_update((self.x, self.y, self.z))


	def get_critical_properties(self):

		return ("trap_falling_boulder", self.activated)

	def set_critical_properties(self, properties):

		func, self.activated = properties

class trap_sound(trap_base):

	name = "Sound Trap"

	def step_onto(self, character, player):

		if self.activated == False and (character == player or character == None):

			player.creature.message("You hear a loud, jarring sound", constants.COLOR_BROWN, only_when_player = True)
			self.activated = True
			player.player.network_tile_update((self.x, self.y, self.z))

	def get_critical_properties(self):

		return ("trap_sound", self.activated)

	def set_critical_properties(self, properties):

		func, self.activated = properties

class trap_monster(trap_base):

	name = "Monster Trap"

	def step_off(self, character, player):

		if self.activated == False and (character == player or character == None):

			player.creature.message("a monster appears behind you", constants.COLOR_RED, only_when_player = True)
			player.player.spawn_random_monster((self.x, self.y))
			self.activated = True
			player.player.network_tile_update((self.x, self.y, self.z))

	def get_critical_properties(self):

		return ("trap_monster", self.activated)

	def set_critical_properties(self, properties):

		func, self.activated = properties

class trap_block_path(trap_base):

	name = "Wall Trap"

	def step_onto(self, character, player):

			if self.activated == False and character == player:
				character.creature.message("you hear a clicking noise", constants.COLOR_WHITE, only_when_player = True)
				self.activated = True
				player.player.network_tile_update((self.x, self.y, self.z))


	def step_off(self, character, player):

		if self.activated == True and character == player:
			character.creature.message("the path closes behind you", constants.COLOR_RED, only_when_player = True)
			self.block_path = True
			self.sprite = "BARS" #bars sprite
			self.hidden = False
			player.player.network_tile_update((self.x, self.y, self.z))

	def get_critical_properties(self):

		return ("trap_block_path", self.activated, self.sprite, self.block_path, self.hidden)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite, self.block_path, self.hidden = properties

class trap_hole(trap_base):

	name = "Pit Trap"

	def step_onto(self, character, player):

			if self.activated == False and (character == player or character == None):
				if character and character.creature:
					character.creature.message("The floor collapses below you", constants.COLOR_WHITE, only_when_player = True)

				self.activated = True
				self.sprite = "PIT" #hole
				self.hidden = False
				player.player.network_tile_update((self.x, self.y, self.z))

			if character and character == player:
				player.player.fall_down()


	def get_critical_properties(self):

		return ("trap_hole", self.activated, self.sprite, self.hidden)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite, self.hidden = properties

class trap_collapsing_floor(trap_base):

	name = "Weak Floor"

	def step_onto(self, character, player):

			if self.activated == False and character == player:
				character.creature.message("you hear a worrying noise", constants.COLOR_WHITE, only_when_player = True)
				self.activated = True
				player.player.network_tile_update((self.x, self.y, self.z))
				
			if self.activated == False and character == None:
				self.sprite = "HOLE" #hole
				self.hidden = False
				player.player.network_tile_update((self.x, self.y, self.z))
			


	def interact(self, interactor):

		return "NONE"


	def step_off(self, character, player):

		if self.activated == True and character == player:
				character.creature.message("the floor falls appart as you set off", constants.COLOR_WHITE, only_when_player = True)
				self.sprite = "HOLE" #hole
				self.hidden = False
				player.player.network_tile_update((self.x, self.y, self.z))

	def reveal(self):

		pass

	def stand_on_tick(self, character, delta_time):

		pass

	def get_critical_properties(self):

		return ("trap_collapsing_floor", self.activated, self.sprite, self.hidden)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite, self.hidden = properties


class sacraficial_alter(tile): 

	sprite = "SACRAFICIAL_ALTER"
	name = "Alter"

	map_color = constants.COLOR_VERY_LIGHT_RED

	activated = False

	def step_off(self, character, player):


		if character == player and self.activated == False:

			items = Game.map_check_for_item(self.x, self.y)

			for item in items:
				if item.creature:
					Game.game_message("You sacrafice " + item.creature.name_instance, color = constants.COLOR_RED)
					Game.learn_spell(character, character, *constants.spell_dict["Desperate_Prayer"])
					Game.GAME.current_objects.remove(item)
					self.sprite = "BLOODY_ALTER"
					self.activated = True

					nearby_tiles = util.find_radius((self.x, self.y), 1)

					for index, coords in enumerate(nearby_tiles):
						mx, my = coords
						Game.GAME.current_map[mx][my][0].super_layer.append(constants.BLOOD[index])

	def interact(self, interactor):

		if interactor.player and self.activated == False:
			Game.yes_no_box("Cut your arm over the Alter?", self.sacrafice_func, None, "Cut arm", "Do Nothing", [interactor], None)
		
		elif self.activated == False:
			sacrafice_func(interactor)

	def sacrafice_func(self, interactor):

		interactor.creature.take_damage(20, "You feel weak", ignore_armor = True)
		effects.weakness(interactor, interactor, .2, 10)

		spells.learn_spell(interactor, interactor, *spells.dict["Desperate_Prayer"])


	def get_critical_properties(self):

		return ("sacraficial_alter", self.animation, self.activated)

	def set_critical_properties(self, properties):

		func, self.animation, self.activated = properties

class demon_alter(tile): 

	sprite = "SACRAFICIAL_ALTER"
	name = "Demon Alter"

	map_color = constants.COLOR_LIGHT_RED

	activated = False

	def interact(self, interactor):

		if interactor.player and self.activated == False:
			Game.yes_no_box("Cut your arm over the Demon Alter?", self.sacrafice_func, None, "Cut arm", "Do Nothing", [interactor], None)
		
		elif self.activated == False:
			sacrafice_func(interactor)

	def sacrafice_func(self, interactor):

		Game.gen_boss_hell_beast((self.x - 3,self.y - 3))
		Game.gen_boss_hell_beast((self.x + 2,self.y + 2))

		effects.weakness(interactor, interactor, .2, 10)
		interactor.creature.take_damage(20, "You feel weak", ignore_armor = True)

		self.sprite = "BLOODY_ALTER"

		nearby_tiles = util.find_radius((self.x, self.y), 1)

		for index, coords in enumerate(nearby_tiles):
			mx, my = coords
			Game.GAME.current_map[mx][my][0].super_layer.append(constants.BLOOD[index])

		for x in range(0, 11):
			Game.GAME.current_map[self.x - 5 + x][self.y + 5][1] = boss_wall(self.x - 5 + x, self.y + 5, 1)
			Game.GAME.current_map[self.x - 5 + x][self.y - 5][1] = boss_wall(self.x - 5 + x, self.y - 5, 1)

		for y in range(0, 11):
			Game.GAME.current_map[self.x - 5][self.y - 5  + y][1] = boss_wall(self.x - 5, self.y - 5  + y, 1)
			Game.GAME.current_map[self.x + 5][self.y - 5 + y][1] = boss_wall(self.x - 5, self.y - 5  + y, 1)

	def get_critical_properties(self):

		return ("demon_alter", self.sprite)

	def set_critical_properties(self, properties):

		func, self.sprite = properties


class shrine_base(tile):

	sprite = "SHRINE"
	name = "Shrine Base"

	map_color = constants.COLOR_WHITE

	activated = False

	def interact(self, interactor):

		if interactor.player and self.activated == False:
			Game.yes_no_box("Touch the " + self.name, self.shrine_effect, None, "Touch", "Do Nothing", [interactor], None)
		
		elif self.activated == False:
			sacrafice_func(interactor)

	def shrine_effect(self, interactor):

		print "using default shrine effect"

class shrine_health(shrine_base):

	name = "Shrine of Blood"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:
			interactor.creature.heal(interactor.creature.maxhp)
			self.activated = True
			self.sprite = "SHRINE_USED"

	def get_critical_properties(self):

		return ("shrine_health", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties

class shrine_strength(shrine_base):

	name = "Shrine of Might"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:
			interactor.creature.strength += 1
			self.activated = True
			self.sprite = "SHRINE_USED"

	def get_critical_properties(self):

		return ("shrine_strength", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties

class shrine_fireball(shrine_base):

	name = "Shaman Shrine"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:
			params = constants.spell_dict["Fireball"]
			params.append(True)
			Game.learn_spell(interactor, *params)
			self.activated = True
			self.sprite = "SHRINE_USED"

	def get_critical_properties(self):

		return ("shrine_fireball", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties

class shrine_random_stats(shrine_base):

	name = "Spider Shrine"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:

			rand = libtcod.random_get_int(0, 1, 3)
			for i in range(rand*2):
				stat = libtcod.random_get_int(0, 1, 4)

				if stat == 1:
					if i % 2 == 1:
						interactor.creature.strength += 1
					else:
						interactor.creature.strength -= 1

				if stat == 2:
					if i % 2 == 1:
						interactor.creature.dexterity += 1
					else:
						interactor.creature.dexterity -= 1

				if stat == 3:
					if i % 2 == 1:
						interactor.creature.intelligence += 1
					else:
						interactor.creature.intelligence -= 1

				if stat == 4:
					if i % 2 == 1:
						interactor.creature.vitality += 1
					else:
						interactor.creature.vitality -= 1


			self.activated = True
			self.sprite = "SHRINE_USED"

	def get_critical_properties(self):

		return ("shrine_random_stats", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties

class shrine_money(shrine_base):

	name = "Shrine of Greed"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:
			
			x = self.x + libtcod.random_get_int(0, -1, 1)
			y = self.y + libtcod.random_get_int(0, -1, 1)

			Game.gen_gold((x,y), libtcod.random_get_int(0, 1, 4), False)

			
			self.activated = True
			self.sprite = "SHRINE_USED"

	def get_critical_properties(self):

		return ("shrine_money", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties

class shrine_hurt(shrine_base):

	name = "Shrine of the Decrepit"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:
			
			interactor.creature.take_damage(int(interactor.creature.hp * .6), "you feel weak")
			interactor.creature.dexterity -= 1

			self.activated = True
			self.sprite = "SHRINE_USED"

	def get_critical_properties(self):

		return ("shrine_hurt", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties

class shrine_fire(shrine_base):

	name = "Brimstone Shrine"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:
			
			nearby = util.find_radius((self.x, self.y), 4, False)

			for coord in nearby:
				x, y = coord
				if Game.GAME.current_map[x][y][0].block_path == False:

					fire_tile = fire_tile(x, y, 2)
					fire_tile.caster = interactor
					fire_tile.tick_damage = 10
					fire_tile.damage_every_x_turns = 1
					fire_tile.source_id = "fire_blast_spell"

					Game.GAME.current_map[x][y][2] = fire_tile

					hit = Game.map_check_for_creatures(x,y)

					if hit:

						Game.GAME.current_map[x][y][2].step_onto(hit, PLAYER)

			
			self.activated = True
			self.sprite = "SHRINE_USED"


	def get_critical_properties(self):

		return ("shrine_fire", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties

class shrine_identify(shrine_base):

	name = "Shrine of Cain"

	def shrine_effect(self, interactor):

		if interactor.creature and self.activated == False:
			
			interactor.player.gold = 0

			for obj in interactor.container.inventory:
				obj.item.identify()

			self.activated = True
			self.sprite = "SHRINE_USED"

	def get_critical_properties(self):

		return ("shrine_identify", self.activated, self.sprite)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite = properties


class hidden_treasure(tile):

	name = "Hidden Treasure"
	hidden = True

	map_color = None

	activated = False

	def __init__(self, x, y, z):

		super(hidden_treasure, self).__init__(x, y, z)

		self.hidden_anim_index = libtcod.random_get_int(0, 0, 15)


	def interact(self, interactor):

		if interactor.player and self.sprite != "CHEST_OPENED":

			for i in range(2):
				interactor.player.spawn_random_item((self.x, self.y), 1.0)
				self.sprite = "CHEST_OPENED"
				self.hidden = False
				
			interactor.player.network_tile_update((self.x, self.y, self.z))

		return "ITEM_ACTION"

	def get_critical_properties(self):

		return ("hidden_treasure", self.activated, self.sprite, self.hidden)

	def set_critical_properties(self, properties):

		func, self.activated, self.sprite, self.hidden = properties


class burning_tile(tile):

	animation = "HOT_BARS"

	animation_loop_speed = 15
	flicker_timer = 0
	flicker_speed = 1.6
	current_anim_index = 0

	name = "Burning Tile"

	map_color = None

	activated = False

	def __init__(self, x, y, z):
	
		super(burning_tile, self).__init__(x, y, z)

		self.hit_spacer = .5
		self.next_hit = .01

	@property
	def calc_damage(self):

		damage = 0

		if 6 <= self.current_anim_index and self.current_anim_index <= 7:
			damage = 1

		elif 8 <= self.current_anim_index and self.current_anim_index <= 9:
			damage = 2

		elif 10 <= self.current_anim_index and self.current_anim_index <= 11:
			damage = 1

		return damage

	def step_off(self, character, player):

		self.next_hit = .01

	def stand_on_tick(self, character, delta_time):

		self.next_hit -= delta_time

		if self.next_hit <= 0:
			self.next_hit = self.hit_spacer
			character.creature.take_damage(0, fire_damage = self.calc_damage)

class fire_tile(tile): #temporary

	animation = "FIRE_1"
	animation_loop_speed = 1.5
	flicker_timer = 0
	flicker_speed = 1.5 / 8

	map_color = None
	

	name = "Fire"

	

	caster = None
	tick_damage = 5
	damage_every_x_turns = 1
	source_id = "fire_tile"

	activated = True

	def __init__(self, x, y, z):
	
		super(fire_tile, self).__init__(x, y, z)

		self.duration = libtcod.random_get_int(0, 2, 5)
		self.current_anim_index = libtcod.random_get_int(0, 0, len(constants.anim_dict[self.animation]) - 1)

		self.func = effects.on_fire
	

	def step_onto(self, character, player):

		effects.on_fire(character, self.caster, self.tick_damage, self.duration, self.damage_every_x_turns, source_id = self.source_id)

	def step_off(self, character, player):

		for effect in character.active_effects:
			if effect.id == "on_fire" and effect.source_id == self.source_id:
				character.active_effects.remove(effect)
				break

	def get_critical_properties(self):

		return ("fire_tile", self.caster, self.tick_damage, self.duration, self.damage_every_x_turns)

	def set_critical_properties(self, properties):

		func, self.caster, self.tick_damage, self.duration, self.damage_every_x_turns = properties

class posion_tile(tile): #temporary

	animation = "GAS_CLOUD"
	animation_loop_speed = 15
	flicker_timer = 0
	flicker_speed = .4
	current_anim_index = 0

	map_color = None

	name = "Posion Cloud"

	activated = True

	

	duration = 5

	caster = None
	tick_damage = 5
	damage_every_x_turns = 1
	source_id = None

	def __init__(self, x, y, z):
	
		super(posion_tile, self).__init__(x, y, z)

		self.posion_func = effects.dot_posion
	

	def step_onto(self, character, player):

		effects.dot_posion(character, self.caster, self.tick_damage, self.duration, self.damage_every_x_turns, source_id = self.source_id)

	def get_critical_properties(self):

		return ("posion_tile", self.caster, self.tick_damage, self.duration, self.damage_every_x_turns)

	def set_critical_properties(self, properties):

		func, self.caster, self.tick_damage, self.duration, self.damage_every_x_turns = properties


class boss_teleport_location(tile):

	sprite = "FLOOR_MARKER"
	sprite_scaled = "FLOOR_MARKER_scaled"

	map_color = None

	name = "Magic tile"

	def get_critical_properties(self):

		return "boss_teleport_location"

	def set_critical_properties(self, properties):

		pass

class boss_wall(tile):

	sprite = "BARS"
	name = "Gate"

	map_color = None

	def get_critical_properties(self):

		return "boss_wall"

	def set_critical_properties(self, properties):

		pass



print("tiles.py - Success")
