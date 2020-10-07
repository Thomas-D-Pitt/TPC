""" 

When I started this project I had never programmed in python, nor had I ever used graphics outide of a game engine (I've used Unity and Unreal engine).
The quality of the code varies alot, as I learned more about python I found better ways to do things and have fixed some of the code to reflect thing
however I am sure there are still many places where I've done things inconsistently or in an absurd way

"""

if __name__ == '__main__':

	print "Warning: Game must be started using Game_Start"
	
	raw_input()
	import sys
	sys.exit(0)

else:
	import pygame
	import pygame.mixer
	import libtcodpy as libtcod
	import math
	from math import sqrt
	import pickle
	import gzip
	import zlib
	import datetime
	import random
	import sys
	import json

	import PodSixNet, time
	from PodSixNet.Connection import connection, ConnectionListener

	from time import sleep

	#game files
	import constants
	import util
	import effects
	import tiles
	import spells



#multiplayer bugs:
#shopkeeper Broken
#item affixes

#   _____ _                _____ _____ ______  _____ 
#  / ____| |        /\    / ____/ ____|  ____|/ ____|
# | |    | |       /  \  | (___| (___ | |__  | (___  
# | |    | |      / /\ \  \___ \\___ \|  __|  \___ \ 
# | |____| |____ / ____ \ ____) |___) | |____ ____) |
#  \_____|______/_/    \_\_____/_____/|______|_____/ 








class obj_Game():
	"""stores core game information and handles map transitioning
		this is saved when the game is closed"""
	def __init__(self):

		self.message_log = []

		self.current_objects = []
		self.current_map = None
		self.user_map = None
		self.current_map_id = "NONE"

		self.maps_previous = []
		self.maps_next = []
		self.current_rooms = []

		#array of (current_map, current_rooms, current_objects, current_map_id)
		self.all_maps = []

		self.area_level = -1

		self.tile_wall = tiles.stone_wall
		self.tile_floor = tiles.stone_floor

		
		self.dungeon_generator = gen_map_tunneling

		self.id_counter = 0
		self.map_counter = 0

		self.map_gen_dict = { # map_id substring -> (map_gen_function, wall_tile, floor_tile)
			#keywords to specify the generation method and tiles used for a specific level

			"dungeon" : (gen_map_tunneling, tiles.stone_wall, tiles.stone_floor),
			"cave" : (gen_map_cellular_automata, tiles.dirt_wall, tiles.dirt_floor),

		}

		self.level_list = ["dungeon_01", "dungeon_02", "dungeon_03", "Boss_1", "cave_01", "cave_02", "cave_03"]

		self.previous_level = "NONE"
	

	@property
	def next_id(self):
		#used for referencing specific objects in a multiplayer setting
		self.id_counter+= -1
		return self.id_counter

	@property
	def next_map_id(self):
		#used for referencing specific maps in a multiplayer setting
		self.map_counter -=1
		return self.map_counter

	def map_transition_by_id(self, map_id):
		"""transitions to a specific given its id, if the map exists then it loads it,
			if not then the map is created using a keyword in its id that relates to an element in the map_gen_dict"""

		global FOV_CALCULATE, PARTICLES

		PARTICLES = []

		

		if map_id and map_id != "NONE":

			loading_screen(map_id, "FONT_MAIN_18")

		 # Save Current Map
			if self.current_map:
				for obj in self.current_objects:
					obj.animation_destroy()

				if PLAYER and NETWORK_LISTENER:
					NETWORK_LISTENER.object_update(PLAYER, remove = True)

				self.all_maps.append((self.current_map, self.current_rooms, self.current_objects, self.current_map_id, self.area_level, self.user_map))

		 # Look For Map To load
			found_map = False
			print "looking for saved maps"
			for saved_map_obj in self.all_maps:

				saved_map, saved_rooms, saved_objects, saved_map_id, area_level, user_map = saved_map_obj
				print "found map", saved_map_id

				# Load Map if one is found
				if saved_map_id == map_id:

					found_map = True
					self.current_map = saved_map
					self.user_map = user_map
					self.current_rooms = saved_rooms
					self.current_objects = saved_objects
					self.previous_level = self.current_map_id
					self.current_map_id = saved_map_id
					self.area_level = area_level
					

					GUIDE_MAP.fill(constants.COLOR_BLACK)

					for x in range(constants.GAME_TILES_X):
						for y in range(constants.GAME_TILES_Y):
							new_surface = pygame.Surface((constants.MAP_TILE_SIZE, constants.MAP_TILE_SIZE))

							new_surface.fill(GAME.user_map[x][y])

							GUIDE_MAP.blit(new_surface, (x * constants.MAP_TILE_SIZE, y * constants.MAP_TILE_SIZE))
				

					if PLAYER:

					# Add Player To Current Objects And Init Animation
						player_in_list = False
						for obj in self.current_objects:
							if obj == PLAYER:
								player_in_list = True
								break

						if player_in_list == False:
							self.current_objects.append(PLAYER)

						for obj in self.current_objects:
							obj.anim_init()


					# Move Player To Stairs
						stair_search = True
						for x in range(constants.GAME_TILES_X):
							for y in range(constants.GAME_TILES_Y):
								if self.current_map[x][y][1] and self.current_map[x][y][1].name == "stair":
									if self.current_map[x][y][1].leads_to == self.previous_level:
										PLAYER.x = x
										PLAYER.y = y
										stair_search = False
										break

									else:
										error_message("no stair found func: map_transition_by_id")

							if stair_search == False:
								break


						if NETWORK_LISTENER: #if multiplayer; add player to their game
							NETWORK_LISTENER.new_obj(PLAYER)

						
					else: #if no player:
						gen_player()


						if NETWORK_LISTENER: #if multiplayer; add player to their game
							NETWORK_LISTENER.new_obj(PLAYER)

					

						for obj in self.current_objects:
						 	obj.anim_init()

					if NETWORK_LISTENER: #if an object has changed due to another player, apply that change
						NETWORK_LISTENER.get_retro_updates()

					map_make_fov(self.current_map)
					create_map_lighting(self.current_map)
					map_create_pathfinding()
					FOV_CALCULATE = True

					if USER_OPTIONS.play_music == True: #play song for this level
						print "aL", area_level
						index = (self.area_level % len(constants.MUSIC)) + 1
						pygame.mixer.music.stop()
						pygame.mixer.music.load(constants.MUSIC[index])
						pygame.mixer.music.play(-1)


					break # stop looking through saved maps
				
		 # If No Map To Load, Make One	
			if found_map == False:

				try:
					#check if map has already been created with the map maker (usually because its a boss level)
					load_map(map_id)
					self.area_level += 1

					self.current_map_id = map_id

					GUIDE_MAP.fill(constants.COLOR_BLACK)

				except: #create the map using a map generation function
					GUIDE_MAP.fill(constants.COLOR_BLACK)
					success = False
					for map_type in self.map_gen_dict:

						if map_id.find(map_type) != -1: #finds the dictionary element that should be used for making this level

							gen_func, wall, floor = self.map_gen_dict[map_type]

							self.dungeon_generator = gen_func
							self.tile_wall = wall
							self.tile_floor = floor

							if PLAYER:
								self.current_objects = [PLAYER]
								PLAYER.anim_init()

							

							i = 0
							next_map = "error"
							for m_id in self.level_list: #figures out where in the level list we are
								i+=1

								if m_id == map_id: #then gets the next level

									next_map = self.level_list[i]#next in list

							if not self.current_map_id:
								self.current_map_id = "NONE"



							self.current_map, self.current_rooms = map_create(self.current_map_id, next_map)

							self.user_map = [[constants.COLOR_BLACK for y in range(constants.GAME_TILES_Y)] for x in range(constants.GAME_TILES_X)]

							self.previous_level = self.current_map_id
							self.current_map_id = map_id
							self.area_level += 1

							if PLAYER:

								stair_search = True
								for x in range(constants.GAME_TILES_X): #move player to stairs
									for y in range(constants.GAME_TILES_Y):
										if self.current_map[x][y][1] and self.current_map[x][y][1].name == "stair":
											if self.current_map[x][y][1].leads_to == self.previous_level:
												PLAYER.x = x
												PLAYER.y = y
												stair_search = False
												break

									if stair_search == False:
										break

							else:
								gen_player()

								if NETWORK_LISTENER: #if there is no player and was previously no map, the game just started, 
								# therefore tell other players you made the first map and entered game
									NETWORK_LISTENER.game_start()


							if NETWORK_LISTENER: #send map to other players

								NETWORK_LISTENER.send_map()

							if USER_OPTIONS.play_music == True: #play song for this level
								index = (self.area_level % (len(constants.MUSIC) - 1)) + 1 #index from second element(1) to last element
								pygame.mixer.music.stop()
								pygame.mixer.music.load(constants.MUSIC[index])
								pygame.mixer.music.play(-1)


							FOV_CALCULATE = True

							success = True

					if success == False:
						error_message("Unable to find map keyword: " + str(map_id))



	def transition_next(self):
		"""loads the next map in level list"""
		for i in range(len(self.level_list)):

			if self.level_list[i] == self.current_map_id:
				self.map_transition_by_id(self.level_list[i+1])
				break

	def transition_previous(self):
		"""loads the previous map in level list"""
		for i in range(len(self.level_list)):

			if self.level_list[i] == self.current_map_id:
				self.map_transition_by_id(self.level_list[i-1])
				break

	def transition_to(self, new_map):

			"""moves player to new_map (param), used by load_map function"""

			global FOV_CALCULATE, PARTICLES

			PARTICLES = []

		#save current map

			for obj in self.current_objects:

				obj.animation_destroy()

			if NETWORK_LISTENER:
				NETWORK_LISTENER.obj_update(PLAYER, remove = True)

			self.maps_previous.append((self.current_map, self.current_rooms, self.current_objects, self.current_map_id))

		#change current map to new_map

			self.current_objects = [PLAYER]

			PLAYER.anim_init()

			self.current_map = new_map

			self.current_map = create_map_lighting(self.current_map)

			map_make_fov(self.current_map)
			create_map_lighting(self.current_map)

			map_create_pathfinding()

			for x in range(constants.GAME_TILES_X): #move player to stairs
				for y in range(constants.GAME_TILES_Y):
					if self.current_map[x][y][1] and self.current_map[x][y][1].name == "stair up":
						PLAYER.x = x
						PLAYER.y = y
						break

			FOV_CALCULATE = True


			map_create_pathfinding()

			if NETWORK_LISTENER: #add player character to other player's maps if game is multiplayer
				NETWORK_LISTENER.new_obj(PLAYER)




	"""old level transitioning for my reference,
		I switched to the current map transitioning method to allow for non-linear map progression"""
				
		# def transition_next(self):

		# 	global FOV_CALCULATE, PARTICLES

		# 	PARTICLES = []

		# 	for obj in self.current_objects:

		# 		obj.animation_destroy()

		# 	if PLAYER and NETWORK_LISTENER:
		# 		NETWORK_LISTENER.object_update(PLAYER, remove = True)
				

		# 	if self.current_map:
		# 		self.maps_previous.append((self.current_map, self.current_rooms, self.current_objects, self.current_map_id))

		# 	if len(self.maps_previous) > 3:
		# 		self.tile_wall = tiles.dirt_wall
		# 		self.tile_floor = tiles.dirt_floor
		# 		self.dungeon_generator = gen_map_cellular_automata

		# 	# Load Saved Map
		# 	if len(self.maps_next) >= 1:

		# 		(self.current_map, self.current_rooms, self.current_objects, self.current_map_id) = self.maps_next[-1]

				
				
		# 		if PLAYER:
					


		# 			player_in_list = False
		# 			for obj in self.current_objects:
		# 				if obj == PLAYER:
		# 					player_in_list = True
		# 					break

		# 			if player_in_list == False:
		# 				self.current_objects.append(PLAYER)

		# 			for obj in self.current_objects:
		# 				obj.anim_init()

					


		# 			for x in range(constants.GAME_TILES_X):
		# 				for y in range(constants.GAME_TILES_Y):
		# 					if self.current_map[x][y][1] and self.current_map[x][y][1].name == "stair up":
		# 						PLAYER.x = x
		# 						PLAYER.y = y
		# 						break

		# 			if NETWORK_LISTENER:
		# 				NETWORK_LISTENER.new_obj(PLAYER)

					
					

		# 		else:
		# 			gen_player()

		# 			if NETWORK_LISTENER:
		# 				NETWORK_LISTENER.new_obj(PLAYER)

				

		# 			for obj in self.current_objects:
		# 			 	obj.anim_init()

		# 		if NETWORK_LISTENER:
		# 			#print "map id", self.current_map_id
		# 			NETWORK_LISTENER.get_retro_updates()


		# 		map_make_fov(self.current_map)
		# 		create_map_lighting(self.current_map)

		# 		FOV_CALCULATE = True

		# 		del self.maps_next[-1]

		# 	# Load Manually Created Maps
		# 	elif len(self.maps_next) == 0 and len(self.maps_previous) == 3:

		# 		load_map("Boss_1")

		# 		if NETWORK_LISTENER:
		# 			NETWORK_LISTENER.send_map()

		# 		else:
		# 			self.current_map_id = "Boss_1"

		# 	# Generate Next Map
		# 	elif len(self.maps_next) == 0:


		# 		if PLAYER:
		# 			self.current_objects = [PLAYER]
		# 			PLAYER.anim_init()

		# 		self.current_map, self.current_rooms = map_create()

		# 		if PLAYER:

		# 			for x in range(constants.GAME_TILES_X):
		# 				for y in range(constants.GAME_TILES_Y):
		# 					if self.current_map[x][y][1] and self.current_map[x][y][1].name == "stair":
		# 						#if stair has the id of the previous map
		# 						PLAYER.x = x
		# 						PLAYER.y = y
		# 						break

		# 		else:
		# 			gen_player()

		# 			if NETWORK_LISTENER:
		# 				NETWORK_LISTENER.game_start()


		# 		if NETWORK_LISTENER:

		# 			NETWORK_LISTENER.send_map()


		# 		else:
		# 			print "NO NETWORK_LISTENER"

		# 		FOV_CALCULATE = True

			
			
		# 	index = (len(self.maps_previous) % 4) + 3 
		# 	#pygame.mixer.music.stop()
		# 	#pygame.mixer.music.load(constants.MUSIC[index])
		# 	#pygame.mixer.music.play(-1)

		# 	map_create_pathfinding()

		# def transition_to(self, new_map):

		# 	global FOV_CALCULATE, PARTICLES

		# 	PARTICLES = []

		# 	for obj in self.current_objects:

		# 		obj.animation_destroy()

		# 	if NETWORK_LISTENER:
		# 		NETWORK_LISTENER.obj_update(PLAYER, remove = True)

		# 	self.maps_previous.append((self.current_map, self.current_rooms, self.current_objects, self.current_map_id))


		# 	self.current_objects = [PLAYER]

		# 	PLAYER.anim_init()

		# 	self.current_map = new_map

		# 	self.current_map = create_map_lighting(self.current_map)

		# 	map_make_fov(self.current_map)
		# 	create_map_lighting(self.current_map)

		# 	map_create_pathfinding()

		# 	for x in range(constants.GAME_TILES_X):
		# 		for y in range(constants.GAME_TILES_Y):
		# 			if self.current_map[x][y][1] and self.current_map[x][y][1].name == "stair up":
		# 				PLAYER.x = x
		# 				PLAYER.y = y
		# 				break

		# 	FOV_CALCULATE = True


		# 	map_create_pathfinding()

		# 	if NETWORK_LISTENER:
		# 		NETWORK_LISTENER.new_obj(PLAYER)

		# def transition_previous(self):

		# 	global FOV_CALCULATE, PARTICLES

		# 	PARTICLES = []

		# 	if len(self.maps_previous) < 4:
		# 		self.tile_wall = tiles.stone_wall
		# 		self.tile_floor = tiles.stone_floor
		# 		self.dungeon_generator = gen_map_tunneling

		# 	if len(self.maps_previous) != 0:

		# 		for obj in self.current_objects:

		# 			obj.animation_destroy()

		# 		self.maps_next.append((self.current_map, self.current_rooms, self.current_objects, self.current_map_id))

		# 		(self.current_map, self.current_rooms, self.current_objects, self.current_map_id) = self.maps_previous[-1]

		# 		for obj in self.current_objects:

		# 			obj.anim_init()

		# 		for x in range(constants.GAME_TILES_X):
		# 			for y in range(constants.GAME_TILES_Y):
		# 				if self.current_map[x][y][1] and self.current_map[x][y][1].name == "stair up":
		# 					PLAYER.x = x
		# 					PLAYER.y = y
		# 					break

		# 		map_make_fov(self.current_map)
		# 		create_map_lighting(self.current_map)

		# 		FOV_CALCULATE = True

		# 		del self.maps_previous[-1]
		# 	map_create_pathfinding()

	def game_start(self):

		self.map_transition_by_id("dungeon_01")

		if USER_OPTIONS.play_music == True: #play song for this level
			index = (self.area_level % len(constants.MUSIC)) + 1 #index from second element(1) to last element
			pygame.mixer.music.stop()
			pygame.mixer.music.load(constants.MUSIC[index])
			pygame.mixer.music.play(-1)

class obj_options():
	"""all character settings are saved here
		this is saved when options_save() is called"""
	def __init__(self):
		self.music_volume = .5
		
		self.music_enabled = True

		self.player_class = "CHAR_KNIGHT"
		self.player_name = "Thomas"

		self.write_legacy = False

		#cheat/debugging settings
		self.DISPLAY_ALL_TILES_IN_PATH = False #when targeting a spell this will show the tiles that will be affected by it
		self.AUTO_IDENTIFY = False

		# Key Binds
		self.spell_key_binds = [None for x in range(9)]

		self.key_w = 'w'
		self.key_a = 'a'
		self.key_s = 's'
		self.key_d = 'd'
		self.key_rest = 'x'

		self.key_interact = 'g'
		self.key_map = 'm'
		self.key_drop = 'f'
		self.key_game_info = 'r'
		self.key_look = 'l'
		self.key_console = '='

	@property
	def play_music(self):
		#sometimes I dont upload sound files due to having very slow internet and sound takes up most of the game size
		#therfore this ensures that audio files are present and should be used
		return self.music_enabled and constants.MUSIC_FOUND
	

	def sound_adjust(self):
		pygame.mixer.music.set_volume(float(self.music_volume)/8)

	def get_anim_key(self):
		return constants.char_dict[self.player_class][0]

	def toggle_easy(self, player): #toggle cheat/debugging settings
		if self.DISPLAY_ALL_TILES_IN_PATH == True:
			self.DISPLAY_ALL_TILES_IN_PATH = False
			self.AUTO_IDENTIFY = False
			player.player.god_mode()
			print "EASY: OFF"

		else:
			self.DISPLAY_ALL_TILES_IN_PATH = True
			self.AUTO_IDENTIFY = True
			player.player.god_mode()
			print "EASY: ON"

	def toggle_target_help(self, player): #toggle cheat/debugging settings
		if self.DISPLAY_ALL_TILES_IN_PATH == True:
			self.DISPLAY_ALL_TILES_IN_PATH = False
			print "TARGET HELP: OFF"

		else:
			self.DISPLAY_ALL_TILES_IN_PATH = True
			print "TARGET HELP: ON"

	def key_is_bound(self, key):#key must be in unicode

	#go through all the keybinds and check if it is equal to key
		bound = False

		if key == self.key_w:
			bound = True

		if key == self.key_a:
			bound = True

		if key == self.key_s:
			bound = True

		if key == self.key_d:
			bound = True

		if key == self.key_rest:
			bound = True
		
		if key == self.key_interact:
			bound = True

		if key == self.key_map:
			bound = True

		if key == self.key_drop:
			bound = True

		if key == self.key_game_info:
			bound = True

		if key == self.key_look:
			bound = True

		if key == self.key_console:
			bound = True

		for bound_key in self.spell_key_binds:
			if key == bound_key:
				bound = True

		return bound



class obj_network_listener(ConnectionListener):
	"""handles multiplayer connections """
	def __init__(self, host, port):
		self.Connect((host, port))

		self.other_players = []
		self.used_map_ids = []
		self.used_obj_command_ids = []

		self.players_in_game = 0


		self.id = None

	def Network_connected(self, data):
		print "connected to the server"
	
	def Network_error(self, data):
		print "error:", data['error'][1]
	
	def Network_disconnected(self, data):
		print "disconnected from the server"

	def Network_joinedserver(self, data):
		self.id = data["id"]

		print "my id:", self.id
		#print "other players:", self.other_players

	def Network_player_count(self, data):

		self.players_in_game = data["player_count"]
		print "players_in_game:", self.players_in_game	

	def Network(self, data):#called on all network activity
		#print 'network data:', data
		pass

	def close(self):
		connection.Send({"action": "close"})

	def game_start(self):
		connection.Send({"action": "game_start"})

	def send_map(self):
		"""simplifys map information to include only necessary information, then compresses it and sends it to server """
		map_depth = GAME.area_level + 1
		map_simplified = [ [ [None for z in range(0,constants.GAME_TILES_Z)  ] for y in range(0, constants.GAME_TILES_Y)  ] for x in range(0,constants.GAME_TILES_X) ]

		for x in range(constants.GAME_TILES_X):
			for y in range(constants.GAME_TILES_Y):
				for z in range(constants.GAME_TILES_Z):
					if GAME.current_map[x][y][z]:
						map_simplified[x][y][z] = GAME.current_map[x][y][z].get_critical_properties()
						#critical properties are the properties of a tile class that change, such as a chest being open or closed



		compressed_map = zlib.compress(json.dumps(map_simplified))


		objects_simplified = []
		for obj in GAME.current_objects:
			if type(obj) != list:
				hp = True
				if obj.creature:
					hp = obj.creature.hp
				objects_simplified.append((obj.create_function, obj.create_function_params, obj.x, obj.y, hp, obj.id))


		compressed_objs = zlib.compress(json.dumps(objects_simplified))
		
		connection.Send({"action": "new_map", "depth" : map_depth, "compressed_map" : compressed_map, "id" : self.id, "objects" : compressed_objs, "map_id" : GAME.current_map_id, "area_level" : GAME.area_level})
		

	def object_update(self, obj, remove = False, new_effect = None):

		"""when an object moves or loses health this sends that information to other players on the server """

		obj_id = obj.id
		x = obj.x
		y = obj.y

		delete = False

		if obj.creature:

			if remove == False:
				hp = obj.creature.hp
				

			else:
				hp = obj.creature.hp
				delete = True

		else:
			if remove == True:
				hp = False
			else:
				hp = True

		obj_target = None
		if obj.ai:

			if obj.ai.target:

				obj_target = obj.ai.target.id


		obj_effect = None
		if new_effect:
			obj_effect = (new_effect.id, new_effect.get_critical_properties())
			#critical properties are the properties of a class that change, such as a chest being open or closed
		


		connection.Send({"action": "obj_update", "obj": (obj_id, x, y, hp), "map_id": GAME.current_map_id, "delete": delete, "id": self.id, "retro": False, "new_effect": obj_effect, "target": obj_target})

	def player_ate(self, amount):
		connection.Send({"action": "ate", "amount": amount})

	def player_died(self):
		connection.Send({"action": "death"})

	def tile_update(self, coords):

		"""when a tile changes, this sends that information to other players on the server """

		x, y, z = coords

		props = GAME.current_map[x][y][z].get_critical_properties()
		#critical properties are the properties of a tile class that change, such as a chest being open or closed

		connection.Send({"action": "tile_update", "props": props, "coords": (x,y,z), "map_id": GAME.current_map_id, "id": self.id, "retro": False})

	def new_obj(self, obj, force_id = False):
		#when a new object is created, such as a monster dropping loot, this informs other players on the server of this event
		obj_type = "unknown"
		if obj.player:
			obj_type = "player"

		elif obj.creature:
			obj_type = "creature"

		elif obj.item:
			obj_type = "item"


		hp = True
		if obj.creature:
			hp = obj.creature.hp

		object_simplified = ((obj.create_function, obj.create_function_params, obj.x, obj.y, hp, obj.id))

		compressed_obj = zlib.compress(json.dumps(object_simplified))
 
		cmd_id = libtcod.random_get_int(0, 100000, 9999999) #a temporary id used until the server can assign a unique one
		connection.Send({"action": "new_object", "object" : compressed_obj, "cmd_id" : cmd_id, "id" : self.id, "map_id": GAME.current_map_id, "type": obj_type, "force_id": force_id})
		
	def server_clear_cache(self):
		connection.Send({"action": "clear_cache", "id" : self.id})
		
	def Network_setmap(self, data):
		"""when a map is recived from another player on the server it converted from its simplified from to a complete level """
		global GAME

		used_map = False #ensures that the map_id is unique
		for mid in self.used_map_ids:
			if mid == data["map_id"]:
				used_map = True



		if data["id"] != self.id and used_map == False: #if the map was recived from another player

			self.used_map_ids.append(data["map_id"])
			depth = data["depth"]
			compressed_map = data["compressed_map"]

			map_simplified = json.loads(zlib.decompress(compressed_map))
			if map_simplified:
				new_map = [ [ [None  for z in range(0,constants.GAME_TILES_Z)  ] for y in range(0, constants.GAME_TILES_Y)  ] for x in range(0,constants.GAME_TILES_X) ]

				#convert simplified map into usable map
				for x in range(constants.GAME_TILES_X): 
					for y in range(constants.GAME_TILES_Y):
						for z in range(constants.GAME_TILES_Z):
							if map_simplified[x][y][z]:


								if type(map_simplified[x][y][z]) == unicode:
									tile = tiles.tile_dict[map_simplified[x][y][z]]
									new_map[x][y][z] = tile(x, y, z)

								elif type(map_simplified[x][y][z]) == list:
									tile = tiles.tile_dict[map_simplified[x][y][z][0]]
									new_map[x][y][z] = tile(x, y, z)
									new_map[x][y][z].set_critical_properties(map_simplified[x][y][z])
									#critical properties are object properties that change, such as a chest being open or closed
				

				#add map objects to game
				compressed_objs = data["objects"]

				objects_simplified = json.loads(zlib.decompress(compressed_objs))


				objs = []
				for obj in objects_simplified:

					func, params, obj_x, obj_y, obj_hp, obj_id_old, obj_id_new = obj
					if func:
						func = GEN_DICT.gen_dict[func]
						obj_actor = func(*params)
						obj_actor.id = obj_id_new

						if obj_hp == True:
							#object is item and is still in game
							pass

						else:
							obj_actor.creature.hp = obj_hp

						objs.append(obj_actor)

				
				user_map = [[constants.COLOR_BLACK for y in range(constants.GAME_TILES_Y)] for x in range(constants.GAME_TILES_X)]
				GAME.all_maps.append((new_map, [], objs, data["map_id"], data["area_level"], user_map))

		elif used_map == False: #if the map was sent by this client
			compressed_objs = data["objects"]
			objects_simplified = json.loads(zlib.decompress(compressed_objs))

			for obj in objects_simplified: #changes object ids to match the ids used by the server
					func, params, obj_x, obj_y, obj_hp, obj_id_old, obj_id_new = obj

					for obj in GAME.current_objects:

						if obj.id == obj_id_old:
							obj.id = obj_id_new

	def Network_update_object(self, data):

		#data = action : obj_update, obj : obj.id, obj.x, obj.y, hp

		if data["map_id"] == GAME.current_map_id and data["id"] != self.id: #if the object is on the same map as the player
			#...then change object based on information recived
			obj_id, new_x, new_y, new_hp = data["obj"]



			for obj in GAME.current_objects:

				if obj.id == obj_id:



					obj.x = new_x
					obj.y = new_y


					if obj.creature:

						if data["delete"] == False:
							obj.creature.hp = new_hp
							obj.creature.check_life()

						else:
							GAME.current_objects.remove(obj)
						

					else:
						if new_hp == False:
							GAME.current_objects.remove(obj)
						else:
							#object is still in game
							pass

					if obj.ai and data["target"]:
						for possible_target in GAME.current_objects:
							if possible_target.id == data["target"]:
								obj.ai.target = possible_target
								break

					if data["new_effect"]:
						effect_id, params = data["new_effect"]
						dic = effects.effect_dict()
						func = dic.dic[effect_id]

						func(obj, *params)

						
					break


	def Network_ate(self, data):
		PLAYER.player.food += data["amount"]

	def Network_update_tile(self, data):

		if data["map_id"] == GAME.current_map_id:

			x, y, z = data["coords"]

			GAME.current_map[x][y][z].set_critical_properties(data["props"])

	def Network_new_obj(self, data):
		"""when another player causes an object to spawn, then the information is recived and added to this client's game here"""
		used_id = False
		for cmd_id in self.used_obj_command_ids:
			if cmd_id == data["cmd_id"]:
				used_id = True

		if data["id"] != self.id and used_id == False:

			self.used_obj_command_ids.append(data['cmd_id'])

			compressed_obj = data["object"]

			object_simplified = json.loads(zlib.decompress(compressed_obj))


			func, params, obj_x, obj_y, obj_hp, obj_id_old, obj_id_new = object_simplified

			if func:
				func = GEN_DICT.gen_dict[func]
				obj_actor = func(*params)
				obj_actor.id = obj_id_new

				if obj_hp == True:
					#object is item and is still in game
					pass

				else:
					obj_actor.creature.hp = obj_hp

				obj_actor.x = obj_x
				obj_actor.y = obj_y

				if data["map_id"] == GAME.current_map_id:
					GAME.current_objects.append(obj_actor)

					obj_actor.anim_init()

				else:

					map_id = data["map_id"]

					done = False
					for next_map in GAME.all_maps:
						current_map, current_rooms, current_objects, current_map_id, area_level, user_map = next_map

						if current_map_id == map_id:

							obj_actor.animation_destroy()
							current_objects.append(obj_actor)
							done = True
							break


		elif used_id == False:

			compressed_obj = data["object"]

			object_simplified = json.loads(zlib.decompress(compressed_obj))

			func, params, obj_x, obj_y, obj_hp, obj_id_old, obj_id_new = object_simplified


			self.used_obj_command_ids.append(data['cmd_id'])

			for obj in GAME.current_objects:

				if obj.id == obj_id_old:
					obj.id = obj_id_new

			if data["type"] == "player":

				PLAYER.id = obj_id_new

	def Network_death(self, data):


		PLAYER.creature.death_function(PLAYER)

	def get_retro_updates(self):


		mid = GAME.current_map_id
		connection.Send({"action": "get_retro_updates", "id": self.id, "map_id": mid})

class obj_room:
	#used by tunneling map generation class, sets the size of the room and saves some properties
	def __init__(self, coords, size):

		self.x , self.y = coords
		self.w, self.h = size

		self.x2 = self.x + self.w
		self.y2 = self.y + self.h

	@property
	def center(self):

		center_x = int((self.x + self.x2) / 2)
		center_y = int((self.y + self.y2) / 2)

		return (center_x, center_y)

	def intersects(self, other):

		objects_intersect = (self.x <= other.x2 and self.x2 >= other.x and
							 self.y <= other.y2 and self.y2 >= other.y)

		return objects_intersect

class obj_camera:
	"""handles following player and drawing tiles that are onscreen"""
	def __init__(self):

		self.width = constants.CAMERA_WIDTH
		self.height = constants.CAMERA_HEIGHT

		self.x, self.y = (0, 0) # center of camera

		self.speed = .1

	def update(self):
	#moves the camera towards the player's position, gives the camera some smooth movement
		target_x = PLAYER.x * constants.GAME_TILE_SIZE + constants.GAME_TILE_SIZE/2
		target_y = PLAYER.y * constants.GAME_TILE_SIZE + constants.GAME_TILE_SIZE/2

		distance_x, distance_y = self.map_dist((target_x, target_y))

		self.x +=int(distance_x * self.speed) #the further the camera is from the player the faster it moves
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
		#changes from window coords to tile coords, used from things like selecting tile under mouse
		tar_x, tar_y = coords

        #convert window coords to distace from camera
		cam_d_x, cam_d_y = self.cam_dist((tar_x, tar_y))

        #distance from cam -> map coord
		map_p_x = self.x + cam_d_x
		map_p_y = self.y + cam_d_y

		return((map_p_x, map_p_y))

	def map_to_win(self, coords):
		tar_x, tar_y = coords

		#get tiles camera is over
		tile_x, tile_y = self.x / constants.GAME_TILE_SIZE, self.y / constants.GAME_TILE_SIZE

		dx = self.x - (tar_x * constants.GAME_TILE_SIZE)
		dx = constants.CAMERA_WIDTH/2 - dx

		dy = self.y - (tar_y * constants.GAME_TILE_SIZE)
		dy = constants.CAMERA_HEIGHT/2 - dy


		return (dx, dy)


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

class lib():
	#saves the names of the objects with random names and handles renaming 
	def __init__(self):

		self.used_sprites_potions = []
		self.used_sprites_gems = []

		random1, random2 = self.new_sprite_potion()
		self.potion_healing_name = libtcod.namegen_generate("demon male")
		self.potion_healing_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_bleach_name = libtcod.namegen_generate("demon male")
		self.potion_bleach_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_posion_name = libtcod.namegen_generate("demon male")
		self.potion_posion_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_booze_name = libtcod.namegen_generate("demon male")
		self.potion_booze_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_confusion_name = libtcod.namegen_generate("demon male")
		self.potion_confusion_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_luck_name = libtcod.namegen_generate("demon male")
		self.potion_luck_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_strength_name = libtcod.namegen_generate("demon male")
		self.potion_strength_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_dexterity_name = libtcod.namegen_generate("demon male")
		self.potion_dexterity_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_wisdom_name = libtcod.namegen_generate("demon male")
		self.potion_wisdom_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_intelligence_name = libtcod.namegen_generate("demon male")
		self.potion_intelligence_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_fire_resist_name = libtcod.namegen_generate("demon male")
		self.potion_fire_resist_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_posion_resist_name = libtcod.namegen_generate("demon male")
		self.potion_posion_resist_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_lightning_resist_name = libtcod.namegen_generate("demon male")
		self.potion_lightning_resist_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_cold_resist_name = libtcod.namegen_generate("demon male")
		self.potion_cold_resist_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_all_resist_name = libtcod.namegen_generate("demon male")
		self.potion_all_resist_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_magic_nullify_name = libtcod.namegen_generate("demon male")
		self.potion_magic_nullify_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_invincibility_name = libtcod.namegen_generate("demon male")
		self.potion_invincibility_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_hot_name = libtcod.namegen_generate("demon male")
		self.potion_hot_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_full_dmg_hot_name = libtcod.namegen_generate("demon male")
		self.potion_full_dmg_hot_sprite = "POTION_" + random1 + "_" + random2

		random1, random2 = self.new_sprite_potion()
		self.potion_reverse_name = libtcod.namegen_generate("demon male")
		self.potion_reverse_sprite = "POTION_" + random1 + "_" + random2



		



		random1, random2 = self.new_sprite_gem()
		self.gem_diamond_name = "diamond"#libtcod.namegen_generate("demon male")
		self.gem_diamond_sprite = "GEM_" + random1

		random1, random2 = self.new_sprite_gem()
		self.gem_amber_name = "amber"#libtcod.namegen_generate("demon male")
		self.gem_amber_sprite = "GEM_" + random1

		random1, random2 = self.new_sprite_gem()
		self.gem_amethyst_name = "amethyst"#libtcod.namegen_generate("demon male")
		self.gem_amethyst_sprite = "GEM_" + random1

		random1, random2 = self.new_sprite_gem()
		self.gem_aquamarine_name = "aquamarine"#libtcod.namegen_generate("demon male")
		self.gem_aquamarine_sprite = "GEM_" + random1

		random1, random2 = self.new_sprite_gem()
		self.gem_emerald_name = "emerald"#libtcod.namegen_generate("demon male")
		self.gem_emerald_sprite = "GEM_" + random1

		random1, random2 = self.new_sprite_gem()
		self.gem_ruby_name = "ruby"#libtcod.namegen_generate("demon male")
		self.gem_ruby_sprite = "GEM_" + random1

		random1, random2 = self.new_sprite_gem()
		self.gem_sapphire_name = "sapphire"#libtcod.namegen_generate("demon male")
		self.gem_sapphire_sprite = "GEM_" + random1

		random1, random2 = self.new_sprite_gem()
		self.gem_onyx_name = "onyx"#libtcod.namegen_generate("demon male")
		self.gem_onyx_sprite = "GEM_" + random1



		self.lib_dict = {

			"potion_healing" : [self.potion_healing_name, self.potion_healing_sprite],
			"potion_bleach" : [self.potion_bleach_name, self.potion_bleach_sprite],
			"potion_posion" : [self.potion_posion_name, self.potion_posion_sprite],
			"potion_booze" : [self.potion_booze_name, self.potion_booze_sprite],
			"potion_confusion" : [self.potion_confusion_name, self.potion_confusion_sprite],
			"potion_reverse" : [self.potion_reverse_name, self.potion_reverse_sprite],

			"potion_luck" : [self.potion_luck_name, self.potion_luck_sprite],
			"potion_strength" : [self.potion_strength_name, self.potion_strength_sprite],
			"potion_dexterity" : [self.potion_dexterity_name, self.potion_dexterity_sprite],
			"potion_wisdom" : [self.potion_wisdom_name, self.potion_wisdom_sprite],
			"potion_intelligence" : [self.potion_intelligence_name, self.potion_intelligence_sprite],

			"potion_fire_resist" : [self.potion_fire_resist_name, self.potion_fire_resist_sprite],
			"potion_posion_resist" : [self.potion_posion_resist_name, self.potion_posion_resist_sprite],
			"potion_lightning_resist" : [self.potion_lightning_resist_name, self.potion_lightning_resist_sprite],
			"potion_cold_resist" : [self.potion_cold_resist_name, self.potion_cold_resist_sprite],
			"potion_all_resist" : [self.potion_all_resist_name, self.potion_all_resist_sprite],

			"magic_nullify" : [self.potion_magic_nullify_name, self.potion_magic_nullify_sprite],
			"potion_invincibility" : [self.potion_invincibility_name, self.potion_invincibility_sprite],
			"potion_hot" : [self.potion_hot_name, self.potion_hot_sprite],
			"potion_full_dmg_hot" : [self.potion_full_dmg_hot_name, self.potion_full_dmg_hot_sprite],

			"gem_diamond" : [self.gem_diamond_name, self.gem_diamond_sprite],
			"gem_amber" : [self.gem_amber_name, self.gem_amber_sprite],
			"gem_amethyst" : [self.gem_amethyst_name, self.gem_amethyst_sprite],
			"gem_aquamarine" : [self.gem_aquamarine_name, self.gem_aquamarine_sprite],
			"gem_emerald" : [self.gem_emerald_name, self.gem_emerald_sprite],
			"gem_onyx" : [self.gem_onyx_name, self.gem_onyx_sprite],
			"gem_ruby" : [self.gem_ruby_name, self.gem_ruby_sprite],
			"gem_sapphire" : [self.gem_sapphire_name, self.gem_sapphire_sprite]

		}

	def new_sprite_potion(self):
	#gets a potion sprite that is unused
		done = False
		attempts_remaining = 30 #only try to find a unique sprite this many times

		while done == False and attempts_remaining > 0:
			
			random1 = str(libtcod.random_get_int(0, 1, 5)) 
			random2 = str(libtcod.random_get_int(0, 1, 8))
			done = True

			for r1, r2 in self.used_sprites_potions:
				if random1 == r1 and random2 == r2:
					done = False

			attempts_remaining-=1

		self.used_sprites_potions.append((random1, random2))
		return (random1, random2)

	def new_sprite_gem(self):
	#gets a gem sprite that is unused
		done = False
		attempts_remaining = 30 #only try to find a unique sprite this many times

		while done == False and attempts_remaining > 0:
			
			random1 = str(libtcod.random_get_int(0, 1, 8)) 
			random2 = 1
			done = True

			for r1, r2 in self.used_sprites_gems:
				if random1 == r1 and random2 == r2:
					done = False

			attempts_remaining-=1

		self.used_sprites_gems.append((random1, random2))
		return (random1, random2)

	def rename_potion(self, potion_lib_name, new_name):
	#change the display name for all current and future instances of a potion
		global GAME, PLAYER

		potion_old_name = self.lib_dict[potion_lib_name][0]
		self.lib_dict[potion_lib_name][0] = new_name
		for obj in GAME.current_objects:
			if obj.name == potion_old_name:
				obj.name = new_name

		if PLAYER:
			for obj in PLAYER.container.inventory:
				if obj.name == potion_old_name:
					obj.name = new_name



	def rename_gem(self, gem_lib_name, new_name):
	#change the display name for all current and future instances of a gem
		global GAME, PLAYER

		old_gem_name = self.lib_dict[gem_lib_name][0]

		for obj in GAME.current_objects:
			if obj.name == old_gem_name:
				obj.name = new_name

		if PLAYER:
			for obj in PLAYER.container.inventory:
				if obj.name == old_gem_name:
					obj.name = new_name


class tile_dict:
	#converts text into tile object
	def __init__(self):


		self.tile_dict = {
		
		"tile" : tiles.tile,
		"stone_floor" : tiles.stone_floor,
		"stone_wall" : tiles.stone_wall,
		"dirt_floor" : tiles.dirt_floor,
		"dirt_wall" : tiles.dirt_wall,
		"target" : tiles.target,
		"wall_1" : tiles.wall_1,
		"stair" : tiles.stair,
		"stair_down" : tiles.stair_down,
		"stair_up" : tiles.stair_up,
		"campfire" : tiles.campfire,
		"campfire_nearby": tiles.campfire_nearby,
		"p_confused" : tiles.p_confused,
		"p_fire" : tiles.p_fire,
		"p_x" : tiles.p_x,
		"chest" : tiles.chest,
		"trapped_chest": tiles.trapped_chest,
		"hidden_door" : tiles.hidden_door,
		"strange_pool" : tiles.strange_pool,
		"trap_instant_posion_cloud" : tiles.trap_instant_posion_cloud,
		"trap_instant_posion_dart" : tiles.trap_instant_posion_dart,
		"trap_dart" : tiles.trap_dart,
		"trap_floor_spikes" : tiles.trap_floor_spikes,
		"trap_falling_boulder" : tiles.trap_falling_boulder,
		"trap_sound" : tiles.trap_sound,
		"trap_monster" : tiles.trap_monster,
		"trap_block_path" : tiles.trap_block_path,
		"trap_hole" : tiles.trap_hole,
		"trap_collapsing_floor" : tiles.trap_collapsing_floor,
		"hidden_treasure" :tiles. hidden_treasure,
		"burning_tile" : tiles.burning_tile,
		"posion_tile" : tiles.burning_tile,
		"boss_teleport_location" : tiles.boss_teleport_location,
		"boss_wall" : tiles.boss_wall,

		}







class actor:
	#all objects (items, characters, etc. NOT TILES) are an actor class, all the defaults are set to none and then if they are none then changed to default value,
	#this was necessary for allowing mods to create new actors easily
	def __init__(self, x, y, name, animation_key = None, creature = None, ai = None, container = None, item = None,
	 equipment = None, sprite = None, player_com = None, ammo_com = None, ranged_wep_com = None, state = None,
	 potion = None, reagent = None, depth = None, shop_com = None, width = None, height = None, delta_draw_x = None, delta_draw_y = None,
	 create_function = None, create_function_params = None, id = None):
		self.x = x # map address
		self.y = y
		if width:
			self.width = width - 1
		else:
			self.width = 0
		if height:
			self.height = height - 1
		else:
			self.height = 0
		if delta_draw_x:
			self.delta_draw_x = delta_draw_x
		else:
			self.delta_draw_x = 0
		if delta_draw_y:
			self.delta_draw_y = delta_draw_y
		else:
			self.delta_draw_y = 0
		self.name = name
		self.animation_key = animation_key
		self.animation = constants.anim_dict[self.animation_key]
		self.sight_multiplier = 1
		self.state = state
		if depth:
			self.depth = depth
		else:
			self.depth = 5

		if self.animation_key:

			self.anim_speed = .5 #in seconds
			self.flicker_speed = self.anim_speed / len(self.animation)
			self.flicker_timer = 0
			self.sprite_image = 0

		if not isinstance(self.animation, list):

			self.animation = [self.animation]

		self.creature = creature
		if self.creature:
			self.creature.owner = self

		self.ai = ai
		if self.ai:
			self.ai.owner = self

		self.container = container
		if self.container:
			self.container.owner = self

		self.item = item
		if self.item:
			self.item.owner = self

		self.equipment = equipment
		if self.equipment:
			self.equipment.owner = self


		self.player = player_com
		if self.player:
			self.player.owner = self


		self.ammo = ammo_com
		if self.ammo:
			self.ammo.owner = self

		self.ranged_wep_com = ranged_wep_com
		if self.ranged_wep_com:
			self.ranged_wep_com.owner = self

		self.potion = potion
		if self.potion:
			self.potion.owner = self

		self.reagent = reagent
		if self.reagent:
			self.reagent.owner = self

		self.shop = shop_com
		if self.shop:
			self.shop.owner = self

		self.create_function = create_function
		self.create_function_params = create_function_params

		self.active_effects = []

	def draw(self):
	#draws the actors sprite/animation onto the map surface

		is_visable = libtcod.map_is_in_fov(FOV_MAP, self.x, self.y)

		

		if is_visable:

			if constants.DRAW_ACTOR_BACKGROUNDS: #tint behind all actors, used mostly for debugging
				for w in range(self.width + 1):
					for h in range(self.height + 1):
						SURFACE_MAP.blit(constants.S_TINT_RED, ((self.x + w) * constants.GAME_TILE_SIZE, (self.y + h) * constants.GAME_TILE_SIZE))

				if self.width == 1 and self.height == 1: #actor is 2x2
					x, y = self.nearest_corner((PLAYER.x, PLAYER.y))
					SURFACE_MAP.blit(constants.S_BLACK, ((x) * constants.GAME_TILE_SIZE, (y) * constants.GAME_TILE_SIZE))

			if self.animation and len(self.animation) > 1:
			#cycle through animation if enough time has passed
				if CLOCK.get_fps() > 0.0:
					self.flicker_timer += 1 / CLOCK.get_fps()

				if self.flicker_timer >= self.flicker_speed:
					self.flicker_timer = 0.0

					if self.sprite_image >= len(self.animation) - 1:
						self.sprite_image = 0
					else:
					 self.sprite_image +=1

				#for x in range(self.x, self.x + self.width + 1):
					#for y in range(self.y, self.y + self.height + 1):
						#SURFACE_MAP.blit(constants.S_TINT_RED, (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))


				SURFACE_MAP.blit(self.animation[self.sprite_image], ((self.x + self.delta_draw_x) * constants.GAME_TILE_SIZE, (self.y + self.delta_draw_y) * constants.GAME_TILE_SIZE))


			elif self.animation: #if it has animation but animation is only 1 image long
				SURFACE_MAP.blit(self.animation[0], (self.x * constants.GAME_TILE_SIZE, self.y * constants.GAME_TILE_SIZE))
			
			if self.creature and self != PLAYER:
				height = 2
				#Draw healthbar
				coords = ((self.x + self.delta_draw_x) * constants.GAME_TILE_SIZE, (self.y + self.delta_draw_y) * constants.GAME_TILE_SIZE)
				size = (constants.GAME_TILE_SIZE * (self.width+1), height)
				rect = pygame.Rect(coords, size)
				color = constants.COLOR_DARK_GREY
				pygame.draw.rect(SURFACE_MAP, color, rect)

				size = (constants.GAME_TILE_SIZE * (self.width+1) * self.creature.hp / self.creature.maxhp, height)
				rect = pygame.Rect(coords, size)
				color = constants.COLOR_RED
				pygame.draw.rect(SURFACE_MAP, color, rect)

				#Draw attackbar
				coords = ((self.x + self.delta_draw_x) * constants.GAME_TILE_SIZE, 10 + (self.y + self.delta_draw_y) * constants.GAME_TILE_SIZE)
				size = (constants.GAME_TILE_SIZE * (self.width+1), height)
				rect = pygame.Rect(coords, size)
				color = constants.COLOR_DARK_GREY
				pygame.draw.rect(SURFACE_MAP, color, rect)

				size = (constants.GAME_TILE_SIZE * (self.width+1) * min(self.creature.time_past * self.creature.attack_speed, 1), height)
				rect = pygame.Rect(coords, size)
				color = constants.COLOR_YELLOW
				pygame.draw.rect(SURFACE_MAP, color, rect)

	@property
	def display_name(self):

		if self.creature:
			if self.creature.name_instance != self.name: #if creature has unique name, include that as well as genaric name
				return self.creature.name_instance + " (" + self.name + ")"
			else:
				return self.name

		elif self.item and self.equipment and self.equipment.equipped and self.ammo == True:
			return self.name + str(self.ammo.amount) + " (Equipped)"

		elif self.ammo == True:
			return self.name + str(self.ammo.amount)

		elif self.item and self.equipment and self.equipment.equipped == True:
			return self.name + " (Equipped)"

		elif self.item and self.equipment and (self.equipment.strength_req > 0 or self.equipment.dexterity_req > 0):

			text = self.name + " req(" + str(self.equipment.strength_req) + "," + str(self.equipment.dexterity_req) + ")"

			return text.replace("-100", "0") #defult values are -100, but we dont need to inclue this in tooltip

		else:
			return self.name


	def distance_to(self, other):
		#line distance betwenn two points
		dx = other.x - self.x
		dy = other.y - self.y

		return math.sqrt(dx ** 2 + dy ** 2) 

	def animation_destroy(self):
	#removes animation to allow for saving the actor
		self.animation = None

	def anim_init(self):
	#restores animation from animation key
		self.animation = constants.anim_dict[self.animation_key]

		if not isinstance(self.animation, list):

			self.animation = [self.animation]

	def go_down(self):

		GAME.transition_next()

	def go_up(self):

		GAME.transition_previous()

	def level_transition(self, map_id):

		GAME.map_transition_by_id(map_id)

	def nearest_corner(self, coords): #for 2x2 size
	#nearest corner of a 2x2 creature to a coord, necessary for knowing if the creature can attack an actor it is moving towards without checking all nearby tiles
		result_x = None
		reuslt_y = None

		x,y = coords

		center_x = float(self.width/2 + self.x)
		center_y = float(self.height/2 + self.y)

		if y < center_y:
			result_y = self.y
		else:
			result_y = self.y + self.height

		if x < center_x:
			result_x = self.x
		else:
			result_x = self.x + self.width

		

		return (result_x, result_y)

#   _____ ____  __  __ _____   ____  _   _ ______ _   _ _______ _____ 
#  / ____/ __ \|  \/  |  __ \ / __ \| \ | |  ____| \ | |__   __/ ____|
# | |   | |  | | \  / | |__) | |  | |  \| | |__  |  \| |  | | | (___  
# | |   | |  | | |\/| |  ___/| |  | | . ` |  __| | . ` |  | |  \___ \ 
# | |___| |__| | |  | | |    | |__| | |\  | |____| |\  |  | |  ____) |
#  \_____\____/|_|  |_|_|     \____/|_| \_|______|_| \_|  |_| |_____/ 




#### CREATURE TYPES ####
#### CREATURE TYPES ####
#### CREATURE TYPES ####

class creature_type(object):

	"""creature types determine several things about the creature and creature type defaults can be set here,
	such as a natural posion resistance to undead creatures"""

	name = "base_class"

	def __init__(self, owner):

		self.owner = owner

	def take_turn(self):
		pass

class type_undefined(creature_type):
	"""default type with nothing special"""
	
	name = "undefined"


class type_humanoid(creature_type):

	name = "humanoid"


class type_insect(creature_type):

	name = "insect"


class type_demon(creature_type):
#natural fire resistance

	name = "demon"

	def __init__(self, owner):

		super(type_demon, self).__init__(owner)

		self.owner.fire_resistance += .5

class type_undead(creature_type):
#natural posion resistance
	name = "undead"

	def __init__(self, owner):

		super(type_undead, self).__init__(owner)

		self.owner.posion_resistance += .5

class type_beast(creature_type):

	name = "beast"

	def __init__(self, owner):

		super(type_beast, self).__init__(owner)

		self.tame_left = self.owner.level

	def tame(self, amount, trainer):
	#beasts can be tamed, and become pets
		self.tame_left -= 1

		if self.tame_left <= 0:
			ai = ai_pet()
			ai.master = trainer
			ai.owner = self.owner.owner
			self.owner.owner.ai = ai
			self.owner.team = trainer.creature.team
			pass



##### CREATURES #####
##### CREATURES #####
##### CREATURES #####
class com_creature:
	#all enemies, as well as the player have this component
	#handles moving, attacking, taking damage, and death
	def __init__(self, name_instance, level, death_function = None,
	 raw_damage = None, raw_defense = None, raw_evasion = None,
	 vitality = None, dexterity = None, strength = None, intelligence = None, wisdom = None, luck = None,
	 fire_resistance = None, posion_resistance = None, lightning_resistance = None, cold_resistance = None, 
	 attack_function = None, attack_function_occurance = None, team = None, creature_type = None,
	 dead_item_name = None, attack_speed = None, move_speed = None, cast_speed = None):

		self.name_instance = name_instance

		self.level = level

		self.last_location = None

		self.time_past = 0.0 # keeps track of movement points the player has used to determine when this unit can move

		if team:
			self.team = team
		else:
			self.team = 2

		if attack_speed:
			self.attack_speed = float(attack_speed)
		else:
			self.attack_speed = 1.0

		if move_speed:
			self.move_speed = float(move_speed)
		else:
			self.move_speed = 2.0

		if cast_speed:
			self.cast_speed = float(cast_speed)
		else:
			self.cast_speed = 1.0

		if raw_damage:
			self.raw_damage = raw_damage
		else:
			self.raw_damage = 1

		if raw_defense:
			self.raw_defense = raw_defense
		else:
			self.raw_defense = 0

		if raw_evasion:
			self.raw_evasion = raw_evasion
		else:
			self.raw_evasion = 0

		if vitality:
			self.vitality = vitality
		else:
			self.vitality = 5

		if dexterity:
			self.dexterity = dexterity
		else:
			self.dexterity = 1

		if strength:
			self.strength = strength
		else:
			self.strength = 1

		if intelligence:
			self.intelligence = intelligence
		else:
			self.intelligence = 1

		if wisdom:
			self.wisdom = wisdom
		else:
			self.wisdom = 1

		if luck:
			self.luck = luck
		else:
			self.luck = 1

		self.health_multiplier = 1
		self.damage_multiplier = 1
		self.mana_multiplier = 1

		if fire_resistance:
			self.fire_resistance = fire_resistance
		else:
			self.fire_resistance = 0

		if posion_resistance:
			self.posion_resistance = posion_resistance
		else:
			self.posion_resistance = 0

		if lightning_resistance:
			self.lightning_resistance = lightning_resistance
		else:
			self.lightning_resistance = 0

		if cold_resistance:
			self.cold_resistance = cold_resistance
		else:
			self.cold_resistance = 0

		
		self.mana = self.maxmana
		self.active_spells = []
		self.known_spells = []
	
		self.hp = self.maxhp

		if death_function:
			self.death_function = death_function
		else:
			self.death_function = "DEFAULT"

		self.attack_function = attack_function

		if attack_function_occurance:
			self.attack_function_occurance = attack_function_occurance
		else:
			self.attack_function_occurance = .5

		self.active_function = None

		self.move_multiplier_x = 1
		self.move_multiplier_y = 1
		

		if self.death_function == "DEFAULT":
			self.death_function = death_monster

		if creature_type:
			self.type = creature_type(self)
		else:
			self.type = type_undefined(self)





	@property
	def maxmana(self):
		max_mana = int(self.wisdom * 4 * self.mana_multiplier)

		return max_mana

	@property
	def max_active_spells(self):

		max_active_spells = min(int(self.wisdom / 3) + 1, 9) 

		return max_active_spells

	@property
	def maxhp(self):
		maxhp = int(self.vitality * self.health_multiplier * 10 + self.level * 4)

		return maxhp

	@property
	def power(self):
		#physical attack damage
		total_power = self.raw_damage
		if self.owner.container:
			objects = [obj.equipment for obj in self.owner.container.equipped_items]

			for item in objects:
				if item: #add items attack bonus

					if item.attack_min_bonus < item.attack_max_bonus and item.attack_max_bonus >= 1:
						
						total_power+= libtcod.random_get_int(0, item.attack_min_bonus, item.attack_max_bonus)
					elif item.attack_max_bonus:
						total_power += item.attack_max_bonus

					if item.lose_durability == "ON_ATTACK": #remove durability if applicable
						if item.lose_durability_func:
							item.lose_durability_func(item)
						else:
							item.equipment_used()

		if total_power == 0 and self.owner == PLAYER:
			total_power = 1

		return total_power * self.damage_multiplier

	@property
	def hit_chance_roll(self):
	#takes stats into acount then picks a random number within range
		hit_chance = libtcod.random_get_int(0, self.level, self.dexterity + self.level) #random number from level to level + dex

		if self.owner.container: #add hit chance bonuses
			object_bonuses = [obj.equipment.hit_chance_bonus for obj in self.owner.container.equipped_items]

			for bonus in object_bonuses:
				if bonus:
					hit_chance+=bonus


		return hit_chance

	@property
	def dex_roll(self):

		roll = libtcod.random_get_int(0, 0, self.dexterity - self.level)

		return roll

	@property
	def luck_roll(self):

		roll = libtcod.random_get_int(0, 0, self.luck - self.level)

		return roll
	
	@property
	def armor(self):
	#reduces physical damage
		total_armor = self.raw_defense

		if self.owner.container:
			object_bonuses = [obj.equipment.armor_bonus for obj in self.owner.container.equipped_items]

			for bonus in object_bonuses:
				if bonus:
					total_armor+=bonus



		return total_armor

	@property
	def evasion(self):
	#chance to negate melee attack damage
		evasion = self.raw_evasion

		if self.owner.container:
			object_bonuses = [obj.equipment.evade_bonus for obj in self.owner.container.equipped_items]

			for bonus in object_bonuses:
				if bonus:
					evasion+=bonus



		return evasion

	def check_life(self):

		if self.hp <= 0:
			if self.death_function is not None:

				self.death_function(self.owner)

			if self.owner.ai:
				self.owner.ai.end()


	def can_move_to(self, coord):

		tile_is_wall = False

		x1, y1 = coord

		for x in range(x1, x1 + self.owner.width+1):
				for y in range(y1, y1 + self.owner.height+1):
					if (GAME.current_map[x][y][0].block_path == True):
						tile_is_wall = True
						break

					if tile_is_wall == False and GAME.current_map[x][y][1]:
						if GAME.current_map[x][y][1].block_path == True:
							tile_is_wall = True
							break

		if tile_is_wall == False:
			return True

		else:
			return False
	

	#health
	def take_damage(self, dmg, message_player_is_hit = None, message_monster_is_hit = None, color = constants.COLOR_WHITE,
	 fire_damage = 0, posion_damage = 0, lightning_damage = 0, cold_damage = 0, source = "undefined", ignore_armor = False):

	# takes into account all equipment and resists then applies damage

		old_hp = self.hp
		#print("TOOK DAMAGE " + str(dmg) + "+" +str(fire_damage) + "+" +str(posion_damage) + "+" +str(lightning_damage) + "+" +str(cold_damage))
		if ignore_armor == False:
			if self.armor > dmg * 2:
				#take no damage, armor blocks it all
				pass
			else: 
				#take damage - armor ; minimum 1 damage
				self.hp -= util.clamp(dmg - self.armor, 1, None)

			if self.owner.container and dmg >= 1:
				objects = [obj.equipment for obj in self.owner.container.equipped_items]

				for item in objects:
					if item:

						if item.lose_durability == "WHEN_HIT":
							if item.lose_durability_func:
								item.lose_durability_func(item)
							else:
								item.equipment_used()

		else: #don't reduce damage with armor, minimum 0 damage
			self.hp -= util.clamp(dmg, 0, None)


		#take damage from elemental attacks reduced based on resistances, minimum 0 damage
		self.hp -= util.clamp(int(fire_damage * (1 - self.fire_resistance)), 0, None) 
		self.hp -= util.clamp(int(posion_damage * (1 - self.posion_resistance)), 0, None) 
		self.hp -= util.clamp(int(lightning_damage * (1 - self.lightning_resistance)), 0, None) 
		self.hp -= util.clamp(int(cold_damage * (1 - self.cold_resistance)), 0, None) 



		pop_x, pop_y = CAMERA.map_to_win((self.owner.x, self.owner.y))
		pop_x += libtcod.random_get_int(0, 0, constants.GAME_TILE_SIZE/2)
		pop_y += libtcod.random_get_int(0, 0, constants.GAME_TILE_SIZE/2)

		pop_up_text(pop_x, pop_y, str(old_hp - self.hp), color = color, back_color = None)

		if self.owner.name == "Dummy" and old_hp != self.hp: #print debugging messages if attacking target dummy
			
			game_message(str(int(fire_damage * (1 - self.fire_resistance))) + "/" + str(fire_damage) + " fire damage", color = constants.COLOR_RED)
			game_message(str(int(posion_damage * (1 - self.posion_resistance))) + "/" + str(posion_damage) + " posion damage", color = constants.COLOR_GREEN)
			game_message(str(int(lightning_damage * (1 - self.lightning_resistance))) + "/" + str(lightning_damage) + " lightning", color = constants.COLOR_GOLD)
			game_message(str(int(cold_damage * (1 - self.cold_resistance))) + "/" + str(cold_damage) + " cold damage", color = constants.COLOR_BLUE)
			game_message(str(dmg) + " physical damage", color = constants.COLOR_LIGHT_GREY)
			game_message("you hit the target for ")

		if self.owner == PLAYER:
			if message_player_is_hit:
				game_message(message_player_is_hit, color ) 

		else:
			if message_monster_is_hit:
				message_monster_is_hit = message_monster_is_hit.replace("_CREATURE_", self.owner.display_name)

				game_message(message_monster_is_hit, color)

		if NETWORK_LISTENER:
			NETWORK_LISTENER.object_update(self.owner)

		if self.hp <= 0:
			if self.death_function is not None:

				
				self.death_function(self.owner)

		if self.owner.ai:
				self.owner.ai.end()


	def heal(self, amount, message_player_is_hit = None, message_monster_is_hit = None, color = constants.COLOR_WHITE):
	#heal, minimum 0 health
		self.hp = util.clamp(self.hp + amount, 0, self.maxhp)

		#if (self.owner == PLAYER and amount >= 0) :
			#game_message("You feel better, Health~=~" + str(self.hp) + "/" + str(self.maxhp), constants.COLOR_GREEN )
		#else:
			#game_message(self.owner.display_name + " heals", constants.COLOR_GREEN )

		if self.hp <= 0: #if health is still below 0 then die
			if self.death_function is not None:
				self.death_function(self.owner)	

		if self.owner == PLAYER:
			if message_player_is_hit:
				game_message(message_player_is_hit, color ) 

		else:
			if message_monster_is_hit:
				message_monster_is_hit = message_monster_is_hit.replace("_CREATURE_", self.owner.display_name)

				game_message(message_monster_is_hit, color)

		if NETWORK_LISTENER:
			NETWORK_LISTENER.object_update(self.owner)

	def move(self, dx, dy, from_player = False):
	#change actors location by amount, if possible
		dx = dx * self.move_multiplier_x
		dy = dy * self.move_multiplier_y

		if from_player != True or self.owner.ai == None:

			if self.can_move_to((self.owner.x + dx, self.owner.y + dy)) == True:
				tile_is_wall = False

			else:
				tile_is_wall = True


			target = map_check_for_creatures(self.owner.x + dx, self.owner.y + dy, exclude = self.owner)

			if target:
				global TIME_PAST
				if target.shop and self.owner == PLAYER:

					if target.shop.hostile == False and target:
						shop_menu(target)

						TIME_PAST += 1
					else:
						self.attack(target)
						
						TIME_PAST += round(1/self.attack_speed, 3)

				elif target.creature.team != self.team:
					if self.time_past >= 1/self.attack_speed or self.owner == PLAYER:
						self.attack(target)
						self.time_past -= round(1/self.attack_speed, 3)

						if self.owner == PLAYER:
							TIME_PAST += round(1/self.attack_speed, 3)

						return True

				elif from_player == True: # target is a friend, swap places
					self.owner.x += dx
					self.owner.x = util.clamp(self.owner.x, 0, constants.GAME_TILES_X)
					self.owner.y += dy
					self.owner.y = util.clamp(self.owner.y, 0, constants.GAME_TILES_Y)

					target.x += -dx
					target.x = util.clamp(self.owner.x, 0, constants.GAME_TILES_X)
					target.y += -dy
					target.y = util.clamp(self.owner.y, 0, constants.GAME_TILES_Y)

					if self.owner == PLAYER:
						TIME_PAST += round(1/self.move_speed, 3)

					return True

				else:
					self.time_past = 0
					return False

			elif not tile_is_wall:
				global TIME_PAST
				if self.time_past >= 1/self.move_speed or self.owner == PLAYER:
					self.time_past -= round(1/self.move_speed, 3)
					if dx != 0 or dy != 0:
						self.last_location = (util.clamp(self.owner.x, 0, constants.GAME_TILES_X), util.clamp(self.owner.y, 0, constants.GAME_TILES_Y))
					self.owner.x += dx
					self.owner.x = util.clamp(self.owner.x, 0, constants.GAME_TILES_X)
					self.owner.y += dy
					self.owner.y = util.clamp(self.owner.y, 0, constants.GAME_TILES_Y)

					if self.owner == PLAYER:
						TIME_PAST += round(1/self.move_speed, 3)

					if NETWORK_LISTENER:
						NETWORK_LISTENER.object_update(self.owner)

					GAME.current_map[self.owner.x][self.owner.y][0].step_onto(self.owner, PLAYER)

					if GAME.current_map[self.owner.x][self.owner.y][1]:
						GAME.current_map[self.owner.x][self.owner.y][1].step_onto(self.owner, PLAYER)

					if GAME.current_map[self.owner.x][self.owner.y][2]:
						GAME.current_map[self.owner.x][self.owner.y][2].step_onto(self.owner, PLAYER)

					if self.last_location:

						last_x, last_y = self.last_location

						GAME.current_map[last_x][last_y][0].step_off(self.owner, PLAYER)

						if GAME.current_map[last_x][last_y][1]:
							GAME.current_map[last_x][last_y][1].step_off(self.owner, PLAYER)

						if GAME.current_map[last_x][last_y][2]:
							GAME.current_map[last_x][last_y][2].step_off(self.owner, PLAYER)


					return True
				else:
					return False

			else:
				self.time_past = 0
				return False

	def move_towards(self, other):

		dx = other.x - self.owner.x
		dy = other.y - self.owner.y

		if(abs(dx) > abs(dy)) and dx != 0:
			direction = abs(dx) / dx  #results in +1 or -1
			self.move(1*direction,0)
		elif dy != 0:
			direction = abs(dy) / dy  #results in +1 or -1
			self.move(0,1*direction)

	def move_away(self, other):

		dx = other.x - self.owner.x
		dy = other.y - self.owner.y

		if(abs(dx) > abs(dy)) and dx != 0:
			direction = abs(dx) / dx  #results in +1 or -1
			self.move(-1*direction,0)
		elif dy != 0:
			direction = abs(dy) / dy  #results in +1 or -1
			self.move(0,-1*direction)

	def move_away_diagonally(self, other):

			dx = other.x - self.owner.x
			dy = other.y - self.owner.y

			success_x = False
			success_y = False

			if (dx > 0):
				success_x = self.move(-1,0)
			elif success_x == False:
				self.move(1,0)

			if (dy > 0):
				success_y = self.move(0,-1)
			elif success_y == False:
				self.move(0,1)

	def attack(self, target):
	#check to see if actor successfully hits target, if yes deal damage
		#print self.owner.display_name, "attacks", target.display_name

		damage_dealt = int(self.power)
		message = "You attack " + target.display_name
		missed = False

		if self.successful_hit(target) == False:
			damage_dealt = 0
			message+= " and miss"
			missed = True
		else:
			message += " for " + str(damage_dealt)

		if self.owner == PLAYER:
			game_message(message, constants.COLOR_BLACK)
		else:
			game_message(self.owner.display_name + " attacks " + target.display_name)

		target.creature.take_damage(damage_dealt, source = "creature attack")

		if self.owner.container:
			equipped_equipment = [obj.equipment for obj in self.owner.container.equipped_items]


			if missed == False and target.creature:#hit effect handler if we hit and the target didnt die, apply weapon hit effects
				for item in equipped_equipment:

					if item and item.hit_effect_function_temp:

						if item.slot == "right_hand" or item.slot == "left_hand" or item.slot == "both_hands":
							if item.hit_effect_function_params_temp:

								params = [target, self.owner]
								

								for param in item.hit_effect_function_params_temp:
									params.append(param)

								item.hit_effect_function_temp(*params)



							else:
								item.hit_effect_function_temp()


							item.hit_effect_function_temp = None

					if item and item.hit_effect_permenent:
						if item.slot == "right_hand" or item.slot == "left_hand" or item.slot == "both_hands":
							if item.hit_effect_permenent_params:

								params = [target, self.owner]

								for param in item.hit_effect_permenent_params:
									params.append(param)

								item.hit_effect_permenent(*params)

							else:
								item.hit_effect_permenent()


		if self.attack_function:
			rand = libtcod.random_get_float(0, 0, 1)
			if rand <= self.attack_function_occurance:
				self.attack_function(target, self.owner)

	def successful_hit(self, target):

		result = (target.creature.evasion <= self.hit_chance_roll)

		return result

	def message(self, message, color = constants.COLOR_WHITE, font = "FONT_DEFAULT", only_when_player = False):

		if only_when_player == False or self.owner == PLAYER:
			game_message(message, color, font)

#continue comments here
class com_player:
	#the player (and other players in game) has this component
	#handles food, leveling up and health recovery
	def __init__(self):

		self.maxfood = 500
		self.food = 250
		self.starve_turns = 3
		self.heal_turns = 70
		self.exp = 0
		self.stat_points = 1
		self.gold = 0

		self.take_starve_damage = self.starve_turns
		self.turn_until_next_heal = self.heal_turns

	def end_turn(self):

		self.food-= 1
		self.food = util.clamp(self.food, 0, self.maxfood)

		if self.food <= 0:

			game_message("You are starving", color = constants.COLOR_LIGHT_RED)

			self.take_starve_damage -= 1

		if self.take_starve_damage <= 0:

			self.owner.creature.take_damage(1, source = "starvation", ignore_armor = True)
			self.take_starve_damage = self.starve_turns

		self.turn_until_next_heal-= 1
		self.turn_until_next_heal = util.clamp(self.turn_until_next_heal, 0, self.heal_turns)

		if self.turn_until_next_heal <= 0:

			self.owner.creature.heal(1)
			self.turn_until_next_heal = self.heal_turns

		if self.exp > self.next_level():
			self.exp -= self.next_level()
			self.stat_points += 2
			self.owner.creature.level += 1

	def next_level(self):

		if self.owner.creature:

			return self.owner.creature.level * 10

		else: return 0

	def god_mode(self):
		if self.owner.creature.raw_defense != 99901:
			self.owner.creature.old_raw_defense = self.owner.creature.raw_defense
			self.owner.creature.raw_defense = 99901

			self.owner.creature.fire_resistance += 1
			self.owner.creature.cold_resistance += 1
			self.owner.creature.posion_resistance += 1
			self.owner.creature.lightning_resistance += 1

			print "GOD MODE: TRUE"


		else:
			self.owner.creature.raw_defense = self.owner.creature.old_raw_defense

			self.owner.creature.fire_resistance -= 1
			self.owner.creature.cold_resistance -= 1
			self.owner.creature.posion_resistance -= 1
			self.owner.creature.lightning_resistance -= 1
			print "GOD MODE: FALSE"

	def add_random_item(self):

		item = gen_item((self.owner.x, self.owner.y), GAME.area_level)
		item.item.pickup(self.owner)

	def spawn_random_item(self, coords, range):

		x, y = coords
		done = False
		attempts_remaining = 300
		while done == False and attempts_remaining > 0:
			attempts_remaining -= 1
			tiles = util.find_radius(coords, range, False)
			loc = tiles[libtcod.random_get_int(0, 0, len(tiles) - 1)]
			loc_x, loc_y = loc
			if GAME.current_map[loc_x][loc_y][0].block_path == False:
				x,y = loc
				done = True

		item = gen_item((x, y), GAME.area_level)

	def spawn_loot(self, amount = 1, radius = 1):

		for i in range(int(amount)):
			self.spawn_random_item((PLAYER.x, PLAYER.y), int(radius))

	def random_potion_effect(self):

		potion = gen_potion((self.owner.x, self.owner.y), GAME.area_level)

		potion.function(*potion.function_params)

		GAME.remove(potion)

	def spawn_random_monster(self, coords):

		gen_enemy(coords, GAME.area_level)

	def fall_down(self):
		GAME.transition_next()

		done = False
		while done == False:
			
			loc_x = libtcod.random_get_int(0, 0, constants.GAME_TILES_X - 1)
			loc_y = libtcod.random_get_int(0, 0, constants.GAME_TILES_Y - 1)

			if GAME.current_map[loc_x][loc_y][0].block_path == False:
				PLAYER.x = loc_x
				PLAYER.y = loc_y
				done = True

	def network_tile_update(self, coords):

		if NETWORK_LISTENER:
			NETWORK_LISTENER.tile_update(coords)

	def set_haste(self, new_haste = None):
		print "set haste", str(new_haste)
		if new_haste:
			self.owner.creature.haste = float(new_haste)

	def shrine_menu(self, shrine_name, shrine_func):

		yes_no_box("Touch " + str(shrine_name) + "?", shrine_func, None, "Touch", "Do Nothing", [self.owner], None) 



#### ITEM ####
#### ITEM ####
#### ITEM ####
class com_item:
	#used for all items, also a part of creature actor if the actor leaves a corpse item
	def __init__(self, action, size = None, use_function = None, use_params = None, value = None, identify_name = None,
		throw_damage = None, throw_function = None, use_gui = None, use_text = None):

		if action:
			self.action = action
		else:
			error_message("item class called with no action param")
			self.action = "ERROR"

		if size:
			self.size = size
		else:
			self.size = 0.0
		self.use_function = use_function
		self.use_params = use_params

		if value:
			self.value = value
		else:
			self.value = -1

		if use_gui:
			self.use_gui = use_gui
		else:
			self.use_gui = "default_item_use"

		if throw_damage:
			self.throw_damage = throw_damage
		else:
			self.throw_damage = constants.DEFAULT_THROW_DAMAGE

		if throw_function:
			self.throw_function = throw_function
		else:
			self.throw_function = "default_throw"

		self.tooltip_lines = []

		self.identify_name = identify_name

		self.use_text = use_text

	@property
	def throw_range(self):

		if self.current_container:
			throw_range = self.current_container.owner.creature.strength - self.size

		return throw_range
	

		#pickup
	def pickup(self, actor):
		if actor.container:

			if self.owner.name == "Gold" and actor == PLAYER:
				PLAYER.player.gold += self.value
				GAME.current_objects.remove(self.owner)
				self.owner.animation_destroy()

				if NETWORK_LISTENER:
					NETWORK_LISTENER.object_update(self.owner, True)

			elif actor.container.size + self.size <= actor.container.max_size:
				if actor == PLAYER:
					game_message("You found item: " + self.owner.display_name, constants.COLOR_DARK_TEAL)
				
				actor.container.inventory.append(self.owner)
				GAME.current_objects.remove(self.owner)
				self.current_container = actor.container
				self.owner.animation_destroy()

				if NETWORK_LISTENER:
					NETWORK_LISTENER.object_update(self.owner, True)

				if USER_OPTIONS.AUTO_IDENTIFY == True:
					self.identify()

			else:
				game_message("your inventory is full")


		#drop
	def drop(self, new_x, new_y, print_msg = True):

		if self.current_container.owner == PLAYER and print_msg == True:

			game_message("item dropped")

		if self.owner.equipment:
			self.owner.equipment.unequip()

		GAME.current_objects.append(self.owner)
		try:
			self.current_container.inventory.remove(self.owner)
		except:
			pass


		self.owner.x = new_x
		self.owner.y = new_y
		self.current_container = None

		self.owner.anim_init()

		if NETWORK_LISTENER:
			NETWORK_LISTENER.new_obj(self.owner)

		

		#use
	def use(self):

		global PLAYER_TOOK_ACTION

		if self.owner.ranged_wep_com:
			for item in self.owner.item.current_container.equipped_items:

				if item.ammo:
					
					item.ammo.use()
					self.use_function(self.current_container.owner, *self.use_params)
					break
			PLAYER_TOOK_ACTION = self.action

		elif self.owner.equipment:
			self.owner.equipment.toggle_equip()
			PLAYER_TOOK_ACTION = self.action

		elif self.use_function == "POTION":
			potion_action_menu(self.owner)
			#PLAYER_TOOK_ACTION = potion_action_menu(self.owner.potion)
		
		elif self.use_function:

			if self.use_params:
				#try:

				if (self.use_function(self.current_container.owner, self.current_container.owner, *self.use_params)) != False:
					self.current_container.inventory.remove(self.owner)
					PLAYER_TOOK_ACTION = self.action

				else:
					PLAYER_TOOK_ACTION = "FAILED_ACTION"

				# except:
				# 	if (self.use_function(self.current_container.owner, *self.use_params)) != False:
				# 		self.current_container.inventory.remove(self.owner)
				# 		PLAYER_TOOK_ACTION = self.action

				# 	else:
				# 		PLAYER_TOOK_ACTION = "FAILED_ACTION"

			else:

				if (self.use_function()) != False:
					self.current_container.inventory.remove(self.owner)
					PLAYER_TOOK_ACTION = self.action

				else:
					PLAYER_TOOK_ACTION = "FAILED_ACTION"


	def identify(self):
		global LIB

		if self.owner.potion:
			LIB.rename_potion(self.owner.potion.lib_name, self.owner.potion.lib_name)

		elif self.identify_name:

			self.owner.name = self.identify_name

class com_equipment:
	#items the player can equip, owning actor must also have an item component
	def __init__(self, attack_max_bonus = None, attack_min_bonus = None, armor_bonus = None, evade_bonus = None,
	 slot = None, strength_req = None, dexterity_req = None, hit_chance_bonus = None, hit_effect_function_temp = None,
	 hit_effect_function_params_temp = None, equip_effects = None, equip_function_params = None,
	 hit_effect_permenent = None, hit_effect_permenent_params = None, hit_effect_function_chance = None, durability = False,
	 lose_durability = None, lose_durability_func = None):

		self.attack_max_bonus = attack_max_bonus
		self.attack_min_bonus = attack_min_bonus

		self.armor_bonus = armor_bonus
		self.evade_bonus = evade_bonus
		if hit_chance_bonus:
			self.hit_chance_bonus = hit_chance_bonus
		else:
			self.hit_chance_bonus = 0
		self.slot = slot
		self.hit_effect_function_temp = hit_effect_function_temp
		self.hit_effect_params_temp = hit_effect_function_params_temp
		self.equip_effects = equip_effects
		self.equip_function_params = equip_function_params
		self.ongoing_effects = []
		self.hit_effect_permenent = hit_effect_permenent
		self.hit_effect_permenent_params = hit_effect_permenent_params

		if hit_effect_function_chance:
			self.hit_effect_function_chance = hit_effect_function_chance
		else:
			self.hit_effect_function_chance = .5

		if durability:
			self.durability = durability
		else:
			self.durability = False

		if lose_durability:
			self.lose_durability = lose_durability # "ON_ATTACK" or "WHEN_HIT" or function
		else:
			self.lose_durability = "WHEN_HIT"

		self.lose_durability_func = lose_durability_func #takes equipment class as param


		if strength_req:
			self.strength_req = strength_req
		else:
			self.strength_req = -100

		if dexterity_req:
			self.dexterity_req = dexterity_req
		else:
			self.dexterity_req = -100

		self.equipped = False

		if attack_max_bonus and not attack_min_bonus:
			attack_min_bonus = attack_max_bonus

		if attack_min_bonus and not attack_max_bonus:
			attack_max_bonus = attack_min_bonus




	def toggle_equip(self):

		if self.equipped == True:
			self.unequip()
		else:
			self.equip()

	def equip(self):

		if self.owner.item.current_container.owner.creature.strength >= self.strength_req and self.owner.item.current_container.owner.creature.dexterity >= self.dexterity_req:

			if self.owner.item.current_container.equipped_items:
				all_equipped_items = self.owner.item.current_container.equipped_items

				for item in all_equipped_items:
					if item.equipment.slot == "both_hands":
					
						if item.equipment.slot and item.equipment.slot == self.slot:
							#unequip item in that slot
							item.equipment.toggle_equip()

						if item.equipment.slot and item.equipment.slot == "right_hand":
							#unequip item in that slot
							item.equipment.toggle_equip()

						if item.equipment.slot and item.equipment.slot == "left_hand":
							#unequip item in that slot
							item.equipment.toggle_equip()


					elif item.equipment.slot == "right_hand" or item.equipment.slot == "left_hand":

						if item.equipment.slot and item.equipment.slot == self.slot:
							#unequip item in that slot
							item.equipment.toggle_equip()
							
						if item.equipment.slot and item.equipment.slot == "both_hands":
							#unequip item in that slot
							item.equipment.toggle_equip()

					else:

						if item.equipment.slot and item.equipment.slot == self.slot:
							#unequip item in that slot
							item.equipment.toggle_equip()


			self.equipped = True
			if self.equip_effects:
				for index, equip_effect_function in enumerate(self.equip_effects):
					if self.equip_function_params[index]:
						self.ongoing_effects.append(equip_effect_function(self.owner.item.current_container.owner, self.owner.item.current_container.owner, *self.equip_function_params[index]))
					else:
						self.ongoing_effects.append(equip_effect_function(self.owner.item.current_container.owner, self.owner.item.current_container.owner))
					


		else:
			game_message("You do not meet the requirements for this item", constants.COLOR_ORANGE)
	

	def unequip(self):

		self.equipped = False
		for effect in self.ongoing_effects:
			effect.on_end()


	def equipment_used(self):

		if self.durability != False:

			rand = libtcod.random_get_int(0, 0, 10)

			if rand > 4:

				self.durability -= 1

			if self.durability <= 0:

				self.destroy()

	def destroy(self):
		self.unequip()
		self.owner.item.current_container.inventory.remove(self.owner)

class com_ammo:
	#currently only used for arrow, just saves the amount of arrows remaining
	def __init__ (self, amount, hit_effect_function = None, hit_effect_function_params = None):

		if amount:
			self.amount = amount
		else:
			error_message("ammo class created without amount")

		self.hit_effect_function = hit_effect_function

	def use(self):

		self.amount -= 1

		if self.amount <= 0:
			self.owner.item.current_container.inventory.remove(self.owner)

class com_potion:
	#saves properties specific to potions
	def __init__(self, lib_name, function_applied = None, function_params = [None]):

		self.function = function_applied
		self.function_params = function_params
		self.lib_name = lib_name

class com_spell:
	#saves castables spell properties
	# _LEVEL_ can be used in equations that calculate cost and level requirements
	# _LEVEL_ represents level of the spell
	# _PLEVEL_ represents level of the player
	def __init__(self, name, cast_function, cast_function_params, cost_equation, minimum_intel_equation):

		self.cast_function = cast_function
		self.cast_function_params = cast_function_params
		self.level = 1
		self.name = name
		self.cost_equation = cost_equation
		self.minimum_intel_equation = minimum_intel_equation



	@property
	def cost(self):
		string = str(self.cost_equation).replace("_PLEVEL_", str(PLAYER.creature.level))
		return eval( str(string).replace("_LEVEL_", str(self.level)) )



	def minimum_intelligence(self, level_increase = 0):

		string = str(self.cost_equation).replace("_PLEVEL_", str(PLAYER.creature.level))
		return eval( str(string).replace("_LEVEL_", str(self.level + level_increase)) )
	
	
		



	def cast(self):

		if self.owner.creature.mana >= self.cost:
			if self.owner.creature.time_past >= 1/self.owner.creature.cast_speed or self.owner == PLAYER:
				if self.owner == PLAYER:
					global TIME_PAST
					TIME_PAST += round(1/PLAYER.creature.cast_speed, 3)
				else:
					self.owner.creature.time_past -= round(1/self.owner.creature.cast_speed, 3)

				self.owner.creature.mana -= self.cost

				cast_params = list(self.cast_function_params) #using list() here creates a copy of the array rather than a reference

				i = 0
				for param in cast_params:

					changed = False

					if str(param).replace("_LEVEL_", str(self.level)) != str(param):
						param = param.replace("_LEVEL_", str(self.level))
						print "db spell lvl", self.level
						changed = True
					

					if str(param).replace("_PLEVEL_", str(self.level)) != str(param):
						param = param.replace("_PLEVEL_", str(PLAYER.creature.level))
						changed = True

					if changed:
						cast_params[i] = eval(param)

					i += 1
						

				self.cast_function(self.owner, *cast_params)

class com_reagent:
	#currently not used for anything, will be used in crafting later
	def __init__(self, lib_name):

		if lib_name:
			self.lib_name = lib_name
		else:
			error_message("reagent class created without lib_name")

class com_ranged_weapon:
	#used for bows 
	#currently does nothing
	def __init__(self):

		pass

	@property
	def shooter_pos(self):

		pos = (0,0)

		if self.owner:
			pos = (self.owner.x, self.owner.y)

		return pos	

class com_container:
	#used by player and shops,
	#stores all the items in their inventory
	def __init__(self, max_size = 10.0, inventory = []):
		self.inventory = inventory
		self.max_size = max_size
		self.size = 0

		for obj in inventory:
			self.size += obj.item.size



	@property
	def equipped_items(self):

		list_of_equipped = [obj for obj in self.inventory if obj.equipment and obj.equipment.equipped == True]

		return list_of_equipped
	
class com_shop:
	#component used by shop keeper

	def __init__(self, tier):
		self.tier = tier
		self.hostile = False

	def gen_items(self):
		
		rand = libtcod.random_get_int(0, 3, 15)

		for i in range(rand):

			item = gen_item((self.owner.x, self.owner.y), self.tier)
			item.item.pickup(self.owner)



#### AI ####
#### AI ####
#### AI ####

#all ai components must have a take_turn() function this is called whenever the character takes a turn (duh)

class ai_confused:

	def __init__(self, old_ai, num_turns = 10):
		self.old_ai = old_ai
		self.num_turns = num_turns
		self.init = False
		self.partice = None

		self.forced_target = None

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)

	def take_turn(self):

		global PARTICLES

		if self.init == False:
			
			self.partice = (tiles.p_confused(), self.owner, None)
			PARTICLES.append(self.partice)
			self.init = True



		if self.num_turns > 0:
			self.owner.creature.move(libtcod.random_get_int(0, -1,1), libtcod.random_get_int(0, -1,1))
			self.num_turns-=1
			print self.num_turns

		else:
			self.end()

	def end(self):

		if self.owner == PLAYER:
			game_message("You regain your senses", constants.COLOR_GREEN)

		PARTICLES.remove(self.partice)
		self.owner.ai = self.old_ai

class ai_wander:

	def __init__(self, bounds = None):

		if bounds:
			x, y, w, h = bounds
		else:
			x = 0
			y = 0
			w = constants.GAME_TILES_X
			h = constants.GAME_TILES_Y

		self.x = x
		self.y = y
		self.w = w
		self.h = h 

		self.target = None

		self.forced_target = None

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)


	def take_turn(self):

		dx = libtcod.random_get_int(0, -1,1)
		dy = libtcod.random_get_int(0, -1,1)

		if (self.owner.x + dx >= self.x) and (self.owner.x + dx <= self.x + self.w):
			if (self.owner.y + dy >= self.y) and (self.owner.y + dy <= self.y + self.h):
				self.owner.creature.move(dx, dy)

	def end(self):
		pass

class ai_ram_boss:

	def __init__(self,active = True):

		

		self.active = active
		self.last_seen_location = None

		self.last_target = (0,0)
		self.target = (3,3)

		self.set_action = None
		self.set_target = None

		self.particle = None

		self.forced_target = None

		self.teleport_locations = []

		for x in range(constants.GAME_TILES_X):
			for y  in range(constants.GAME_TILES_Y):
				if GAME.current_map[x][y][1] and GAME.current_map[x][y][1].name == "Magic tile":
					self.teleport_locations.append((x,y))

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)

	def take_turn(self):
		global PARTICLES

		monster = self.owner

		nearest_corner = None
		if PLAYER.x <= monster.x:
			if PLAYER.y <= monster.y:
				nearest_corner = (monster.x, monster.y)#top left

			else:
				nearest_corner = (monster.x, monster.y + monster.height)#bottom left

		else:
			if PLAYER.y <= monster.y:
				nearest_corner = (monster.x + monster.width, monster.y)#top right

			else:
				nearest_corner = (monster.x + monster.width, monster.y + monster.height)#bottom left


		if self.set_action == "fire_wall":
			spells.fire_stream(self.owner, 2, (self.owner.x, self.owner.y), True, util.find_line((self.owner.x, self.owner.y), self.target ))

			PARTICLES.remove(self.particle)
			self.particle = None
			self.set_action = None
			self.last_target = self.target

		elif self.set_action == "fire_blast":

			



			spells.fire_blast(self.owner, 2, (self.owner.x, self.owner.y), True, util.find_radius(self.target, 1))
			PARTICLES.remove(self.particle)
			self.particle = None
			self.set_action = None
			self.last_target = self.target


		possible_options = [("fire_wall", 5), ("fire_blast", 5), ("NONE", 15)]#(option, probability)

		x,y = nearest_corner
		libtcod.path_compute(PATH_FINDER, x, y, PLAYER.x, PLAYER.y)
		if libtcod.path_size(PATH_FINDER) <= 2:
			possible_options.append(("teleport_away", 3))
			possible_options.remove(("fire_blast", 5))




		total_value = 0
		for action,amount in possible_options:
			total_value+=amount

		rand_value = libtcod.random_get_int(0, 1, total_value)

		for actionx,amount in possible_options:

			rand_value-=amount
			if rand_value <= 0:
				action = actionx
				break


		if action == "fire_wall":
			self.target = (PLAYER.x, PLAYER.y)
			x,y = self.target
			self.particle = (tiles.p_x(x, y, 1), None, (x,y, 1))
			PARTICLES.append(self.particle)
			self.set_action = "fire_wall"

		elif action == "fire_blast":


			x_move = libtcod.random_get_int(0, 0, 1)
			if x_move == 0:
				y_move = 1
			else:
				y_move = 0

			coin = libtcod.random_get_int(0, 0, 1)

			if coin == 0:
				coin = -1


			self.target = (PLAYER.x + x_move*coin, PLAYER.y + y_move*coin)


			x,y = self.target
			lx,ly = self.last_target

			if x + 2 == lx or x - 2 == lx:
				x+=1
			elif y + 2 == ly or y - 2 == ly:
				y+=1

			if x == PLAYER.x and y == PLAYER.y:
				x-=2 

			self.target = (x,y)

			self.particle = (tiles.p_x(x, y, 1), None, (x,y, 1))
			PARTICLES.append(self.particle)
			self.set_action = "fire_blast"

		elif action == "teleport_away":

			attempts = 300
			done = False
			while done == False:

				attempts -= 1

				new_loc = self.teleport_locations[libtcod.random_get_int(0, 0, len(self.teleport_locations) - 1)]

				new_x, new_y = new_loc	

				if new_x != self.owner.x or new_y != self.owner.y:
					self.owner.x = new_x
					self.owner.y = new_y

				if attempts <= 0:
					done = True
			



		if self.active == False:
			self.owner.ai = None

	def end(self):
		pass

class ai_simple_caster:

	def __init__(self, spell, spell_val, spell_params = None, active = True, attack_occurence = 1):

		self.spell = spell
		self.spell_val = spell_val
		self.spell_params = spell_params
		self.attack_occurence = attack_occurence

		self.active = active
		self.last_seen_location = None

		self.last_target = None
		self.target = None

		self.set_target = None

		self.particle = None

		self.forced_target = None

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)

	def take_turn(self):
		global PARTICLES

		monster = self.owner

		rand = libtcod.random_get_int(0, 1, 100)

		if rand <= self.attack_occurence * 100:

			if self.forced_target:
				tx, ty = self.forced_target
				valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, tx, ty)

				if valid == True:
					self.attack(self.forced_target)



			elif self.target == None:
				self.target = PLAYER

				libtcod.map_is_in_fov(FOV_MAP_MONSTER, monster.x, monster.y) and self.active == True
				valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, self.target.x, self.target.y)
				if valid == True:
					self.attack(self.target)

			elif libtcod.map_is_in_fov(FOV_MAP_MONSTER, monster.x, monster.y) and self.active == True:
					valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, self.target.x, self.target.y)
					if valid == True:
						self.attack(self.target)

						



			elif self.last_seen_location and self.active == True:
				last_x, last_y = self.last_seen_location
				valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, last_x, last_y)
				if valid == True:
					self.attack(self.target)

						

				else:
					self.last_seen_location = None



		if self.active == False:
			self.owner.ai = None

	def attack(self, target_actor):

		coords = (self.target.x, self.target.y)

		if self.spell_params:
			self.spell(self.owner, self.spell_val, (self.owner.x, self.owner.y), True, [coords], *self.spell_params)
		else:
			self.spell(self.owner, self.spell_val, (self.owner.x, self.owner.y), True, [coords])


	def end(self):
		pass

class ai_chase:

	def __init__(self,active = True):

		self.active = active
		self.target = None
		self.last_seen_location = None

		self.forced_target = None

		self.act_again = 0

	def draw(self):
		if pygame.time.get_ticks() > self.act_again:
			self.take_turn()
			self.act_again = pygame.time.get_ticks() + (constants.ACTION_DELAY * 1000)

	def take_turn(self):

		monster = self.owner
		did_something = True

		if self.forced_target:
			tx, ty = self.forced_target
			valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, tx, ty)

			if valid == True and libtcod.path_size(PATH_FINDER) > 0:
				next_tile_x, next_tile_y = libtcod.path_get(PATH_FINDER, 0)
				did_something = self.owner.creature.move(next_tile_x - self.owner.x, next_tile_y - self.owner.y)
				prevent_input(constants.ACTION_DELAY)
			else:
				did_something = False



		elif self.target == None:
			self.target = PLAYER

			libtcod.map_is_in_fov(FOV_MAP_MONSTER, monster.x, monster.y) and self.active == True
			valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, self.target.x, self.target.y)
			if valid == True and libtcod.path_size(PATH_FINDER) > 0:
				next_tile_x, next_tile_y = libtcod.path_get(PATH_FINDER, 0)
				did_something = self.owner.creature.move(next_tile_x - self.owner.x, next_tile_y - self.owner.y)
				prevent_input(constants.ACTION_DELAY)
				self.last_seen_location = (self.target.x, self.target.y)

			else:
				did_something = False

		elif libtcod.map_is_in_fov(FOV_MAP_MONSTER, monster.x, monster.y) and self.active == True:
				valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, self.target.x, self.target.y)
				if valid == True and libtcod.path_size(PATH_FINDER) > 0:
					next_tile_x, next_tile_y = libtcod.path_get(PATH_FINDER, 0)
					did_something = self.owner.creature.move(next_tile_x - self.owner.x, next_tile_y - self.owner.y)
					prevent_input(constants.ACTION_DELAY)
					self.last_seen_location = (self.target.x, self.target.y)

				else:
					did_something = False

					



		elif self.last_seen_location and self.active == True:
			last_x, last_y = self.last_seen_location
			valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, last_x, last_y)
			if valid == True and libtcod.path_size(PATH_FINDER) > 0:
				next_tile_x, next_tile_y = libtcod.path_get(PATH_FINDER, 0)
				if self.owner.x != next_tile_x and self.owner.y != next_tile_y:
					did_something = self.owner.creature.move(next_tile_x - self.owner.x, next_tile_y - self.owner.y)
					prevent_input(constants.ACTION_DELAY)


				else:
					self.last_seen_location = None
					did_something = False

		else:
			did_something = False
		if did_something != True:
			ONGOING_FUNCTIONS.remove(self)

		if self.active == False:
			self.owner.ai = None

	def end(self):
		pass

class ai_pet:

	def __init__(self,active = True):

		self.active = active
		self.target = None
		self.last_seen_location = None

		self.master = None

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)


	def take_turn(self):

		i = 0
		while i < 6:
			i += 1

			monster = self.owner

			if self.master == None:
				self.master = PLAYER
				self.owner.creature.team = self.master.creature.team

			self.target = (self.master.x, self.master.y)

			tx, ty = self.target
			valid = libtcod.path_compute(PATH_FINDER, monster.x, monster.y, tx, ty)

			if libtcod.path_size(PATH_FINDER) < 3:
				#WANDER
				dx = libtcod.random_get_int(0, -1,1)
				dy = libtcod.random_get_int(0, -1,1)

				self.owner.creature.move(dx, dy)
				i = 10000

			else:

				tx, ty = self.target
				valid = libtcod.path_compute(PATH_FINDER, self.owner.x, self.owner.y, tx, ty)

				if valid == True:
					next_tile_x, next_tile_y = libtcod.path_get(PATH_FINDER, 0)
					self.owner.creature.move(next_tile_x - self.owner.x, next_tile_y - self.owner.y)

				

						




			if self.active == False:
				self.owner.ai = None

	def end(self):
		pass

class ai_skiddish:

	def __init__(self,active = True):

		self.active = active

		self.forced_target = None

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)

	def take_turn(self):

		monster = self.owner

		if libtcod.map_is_in_fov(FOV_MAP_MONSTER, monster.x, monster.y) and self.active == True:

				self.owner.creature.move_away_diagonally(PLAYER)

		if self.active == False:
			self.owner.ai = None

	def end(self):
		pass

class ai_dummy:

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)

	def take_turn(self):
		return None

	def end(self):
		pass

class ai_hell_beast:

	def __init__(self,active = True):

		self.active = active
		self.target = None
		self.last_seen_location = None

		self.forced_target = None

	def draw(self):
		self.take_turn()
		ONGOING_FUNCTIONS.remove(self)

	def take_turn(self):

		monster = self.owner


		if self.forced_target:

			x, y = self.nearest_corner(self.forced_target)

			tx, ty = self.forced_target
			valid = libtcod.path_compute(PATH_FINDER, x, y, tx, ty)

			if valid == True and libtcod.path_size(PATH_FINDER) > 0:
				next_tile_x, next_tile_y = libtcod.path_get(PATH_FINDER, 0)
				self.owner.creature.move(next_tile_x - x, next_tile_y - y)



		else:
			if self.target == None:
				self.target = PLAYER

			done = False
			for tile in util.attackable_tiles(self.owner.x, self.owner.y, self.owner.width, self.owner.height):

				x, y = tile
		
				target = map_check_for_creatures(x, y, self.owner)

				if target:
					if target == self.target:
						self.owner.creature.attack(target)
						done = True
						break

				if done == True:
					break


			if done == False:

				x,y = self.owner.nearest_corner((self.target.x, self.target.y))

				libtcod.map_is_in_fov(FOV_MAP_MONSTER, monster.x, monster.y) and self.active == True
				valid = libtcod.path_compute(PATH_FINDER, x, y, self.target.x, self.target.y)
				if valid == True and libtcod.path_size(PATH_FINDER) > 0:
					next_tile_x, next_tile_y = libtcod.path_get(PATH_FINDER, 0)
					self.owner.creature.move(next_tile_x - x, next_tile_y - y)
					self.last_seen_location = (self.target.x, self.target.y)
					


		if self.active == False:
			self.owner.ai = None

	def end(self):
		pass

	def nearest_corner(self, coords): #for 2x2 size

		result_x = None
		reuslt_y = None

		x,y = coords

		center_x = float(self.owner.width/2 + self.owner.x)
		center_y = float(self.owner.height/2 + self.owner.y)

		if y < center_y:
			result_y = self.owner.y
		else:
			result_y = self.owner.y + self.owner.height

		if x < center_x:
			result_x = self.owner.x
		else:
			result_x = self.owner.x + self.owner.width



		return (result_x, result_y)


#### DEATH ####
#### DEATH ####
#### DEATH ####

#takes in actor that dies and does something

def death_monster(monster):#default
	
	game_message(monster.creature.name_instance + " is dead", constants.COLOR_RED)

	PLAYER.player.exp += monster.creature.level
	monster.depth = constants.DEPTH_ITEM

	if monster.item:
		monster.name += (" corpse (" + monster.creature.name_instance + ")")

	if monster.ai:
		monster.ai.active = False
	if monster.creature:
		monster.creature = None
	
	

	rand = libtcod.random_get_int(0, 1, 100)

	if rand >= 90:
		gen_item((monster.x, monster.y), GAME.area_level)

	GAME.current_objects.remove(monster)

def death_shop_owner(monster):#default
	
	game_message(monster.creature.name_instance + " is dead", constants.COLOR_RED)

	items_to_drop = []

	for i in range(0, len(monster.container.inventory)):
		items_to_drop.append(monster.container.inventory[i])
		

	PLAYER.player.exp += monster.creature.level
	monster.depth = constants.DEPTH_ITEM

	if monster.item:
		monster.name += (" corpse (" + monster.creature.name_instance + ")")

	if monster.ai:
		monster.ai.active = False
	if monster.creature:
		monster.creature = None
	
	
	tiles = util.find_radius((monster.x, monster.y), 2)
	good_tiles = []
	for tile in tiles:
		x,y = tile
		if GAME.current_map[x][y][0].block_path == False:
			good_tiles.append(tile)

	if monster.container and len(monster.container.inventory) > 0:
		for actor in items_to_drop:

			randx, randy = good_tiles[libtcod.random_get_int(0, 0, len(monster.container.inventory) - 1)]

			actor.item.drop(randx, randy)
			

	

	GAME.current_objects.remove(monster)

def death_ram_boss(monster):
	
	game_message("Victory achieved", constants.COLOR_GOLD)

	PLAYER.player.exp += 12
	monster.depth = constants.DEPTH_ITEM

	if monster.item:
		monster.name += (" corpse (" + monster.creature.name_instance + ")")

	if monster.ai:
		monster.ai.active = False
	if monster.creature:
		monster.creature = None
	

	GAME.current_objects.remove(monster)

	for x in range(constants.GAME_TILES_X):
		for y in range(constants.GAME_TILES_Y):
			if GAME.current_map[x][y][1] and GAME.current_map[x][y][1].name == "Gate":
				GAME.current_map[x][y][1] = None

def death_hell_beast_boss(monster):

	

	PLAYER.player.exp += 15

	GAME.current_objects.remove(monster)

	another_boss = False
	for obj in GAME.current_objects:
		if obj.display_name.find("(Boss)") != -1:
			another_boss = True

	if another_boss == False:

		game_message("Victory achieved", constants.COLOR_GOLD)

		for x in range(constants.GAME_TILES_X):
			for y in range(constants.GAME_TILES_Y):
				if GAME.current_map[x][y][1] and GAME.current_map[x][y][1].name == "Gate":
					GAME.current_map[x][y][1] = None

				if GAME.current_map[x][y][1] and GAME.current_map[x][y][1].name == "Demon Alter":
					item = gen_weapon_demon_shank((x, y))
					GAME.current_objects.append(item)

def death_humanoid(monster):

	game_message(monster.creature.name_instance + " is dead", constants.COLOR_RED)

	PLAYER.player.exp += monster.creature.level
	monster.depth = constants.DEPTH_ITEM

	if monster.item:
		monster.name += (" corpse (" + monster.creature.name_instance + ")")

	if monster.ai:
		monster.ai.active = False
		monster.creature = None

	if monster.animation:
		monster.animation_key = "CORPSE"
		monster.anim_init()

def player_death(player):

	player.state = "DEAD"

	wait = True

	SURFACE_MAIN.blit(constants.S_RED_FILL, (0,0))

	t_coords = (constants.CAMERA_WIDTH/2, constants.CAMERA_HEIGHT/2)

	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

	#draw_tile_at_coords(tiles.wall_1(0,0), 0, 0)


	#Draw Game
	CAMERA.update()

	display_rect = pygame.Rect( (0,0), (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT) )

	#draw map
	map_draw(GAME.current_map)

	#draw Characters
	for obj in sorted(GAME.current_objects, key = lambda obj :obj.depth, reverse = True):
		obj.draw()

	SURFACE_MAIN.blit(SURFACE_MAP, (0,0), CAMERA.rect)

	pygame.display.flip()


	SURFACE_MAIN.blit(constants.S_RED_FILL, (0,0))

	draw_gui()

	if NETWORK_LISTENER:
		util.draw_text(SURFACE_MAIN, "Your team failed", t_coords, constants.COLOR_WHITE, back_color = None, font = "FONT_MENU", center = True)
		NETWORK_LISTENER.player_died()
		connection.Pump()
		NETWORK_LISTENER.Pump()
	else:
		util.draw_text(SURFACE_MAIN, "You Died", t_coords, constants.COLOR_WHITE, back_color = None, font = "FONT_MENU", center = True)

	pygame.display.update()

	pygame.time.wait(2000)

	if USER_OPTIONS.write_legacy == True:

		#file_name = PLAYER.creature.name_instance + "." + datetime.date.today().strftime("%Y%B%d") + ".txt"
		file_name = "Legacy" + ".txt"

		legacy_file = open(file_name, 'a+')

		for message, color, font in GAME.message_log:

			legacy_file.write(message + "\n")

		legacy_file.write( "*****************END*****************\n")

	x,y = t_coords
	y+=50

	util.draw_text(SURFACE_MAIN, "Click to continue", (x,y), constants.COLOR_WHITE, back_color = None, font = "FONT_DEFAULT", center = True)
	pygame.display.update()

	game_save()

	while wait == True:

		events_list = pygame.event.get()

		for event in events_list:
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					wait = False
					global CLOCK
					CLOCK = None
					Run()

			if event.type == pygame.KEYDOWN:

				if event.key == pygame.K_EQUALS:
					console = open_console()

					if console == "CANCEL":
						wait = False




#  _______ _    _ _____   ______          __
# |__   __| |  | |  __ \ / __ \ \        / /
#    | |  | |__| | |__) | |  | \ \  /\  / / 
#    | |  |  __  |  _  /| |  | |\ \/  \/ /  
#    | |  | |  | | | \ \| |__| | \  /\  /   
#    |_|  |_|  |_|_|  \_\\____/   \/  \/    
                                       



def throw(obj, caster = None, value = -1, origin = "PLAYER", Shoot = False, target = None, m_range = -1):

	global ONGOING_FUNCTIONS

	start_pos = origin
	max_range = obj.item.throw_range
	penetrate_walls = False
	penetrate_characters = False#ignore characters along path = false
	name = throw
	hit_along_path = False#can hit multiple characters
	can_cast_on_self = False
	radius = 0
	caster = caster

	value = obj.item.throw_damage

	if origin == None:
		origin = (caster.x, caster.y)
		start_pos = origin

	elif origin == "PLAYER":
		caster = PLAYER
		origin = (PLAYER.x, PLAYER.y)
		start_pos = origin
	
	if Shoot == False:	
		select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name, [obj, caster, value, start_pos, True, "SELECT_RESULT", radius])

	else:

		x, y = target[-1]

		if obj.equipment:
			obj.equipment.unequip()

		if obj.item.throw_function == "default_throw":
			default_throw(obj, (x,y))
		else:
			obj.item.throw_function(obj, (x, y))
			



		if caster == PLAYER:
			global PLAYER_TOOK_ACTION
			PLAYER_TOOK_ACTION = "THROW"
	
def default_throw(obj, coords):

	x,y = coords

	
	target = map_check_for_creatures(x, y)

	if target:
		target.creature.take_damage(obj.item.throw_damage)

		target_name = "a " + target.display_name

		if target.creature and target.creature.name_instance != target.name:
			target_name = target.display_name

		#game_message("you hit " + target_name + " for " + str(obj.item.throw_damage), constants.COLOR_BLUE) 
		obj.item.drop(x, y, False)

	else:
		#game_message("you hit nothing", constants.COLOR_VERY_DARK_GREY)
		obj.item.drop(x, y, False)
		if isinstance(GAME.current_map[x][y][1], tiles.trap_base):
			GAME.current_map[x][y][1].step_onto(None, PLAYER)

def explosive_throw(obj, coords, radius = 1):
	spells.fire_blast(owner, equipment.attack_max_bonus, coords, True, util.find_radius(coords, 1))	


def bone_throw(obj, coords):

	
	nearby_tiles = util.find_radius(coords, 1)
	found = False
	for tile in nearby_tiles:
		tx, ty = tile
		enemy = map_check_for_creatures(tx, ty)

		if enemy and enemy.creature.type.name == "beast":
			#beast chases after the bone
			found = True
			enemy.ai.forced_target = coords
			enemy.creature.type.tame(1, obj.item.current_container.owner)

	if found == False:
		default_throw(obj, coords)




#  _____  _    _ _____            ____ _____ _      _____ _________     __
# |  __ \| |  | |  __ \     /\   |  _ \_   _| |    |_   _|__   __\ \   / /
# | |  | | |  | | |__) |   /  \  | |_) || | | |      | |    | |   \ \_/ / 
# | |  | | |  | |  _  /   / /\ \ |  _ < | | | |      | |    | |    \   /  
# | |__| | |__| | | \ \  / ____ \| |_) || |_| |____ _| |_   | |     | |   
# |_____/ \____/|_|  \_\/_/    \_\____/_____|______|_____|  |_|     |_|   
                                                                     
                                                          
def durablity_volatile(equipment):
	if libtcod.random_get_int(0, 0, 100) > 10:
		owner = equipment.owner.item.current_container.owner
		coords = (owner.x, owner.y)
		spells.fire_blast(owner, equipment.attack_max_bonus, coords, True, util.find_radius(coords, 1))		

		equipment.destroy()





#  __  __          _____  
# |  \/  |   /\   |  __ \ 
# | \  / |  /  \  | |__) |
# | |\/| | / /\ \ |  ___/ 
# | |  | |/ ____ \| |     
# |_|  |_/_/    \_\_|     
   



def map_draw(map_to_draw):

	camx , camy = CAMERA.map_address

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

				is_visable = libtcod.map_is_in_fov(FOV_MAP, x, y)

				if is_visable:

					if map_to_draw[x][y][0].explored == False:
						map_to_draw[x][y][0].explored = True

						if map_to_draw[x][y][1] and map_to_draw[x][y][1].map_color:
							GAME.user_map[x][y] = map_to_draw[x][y][1].map_color

						elif map_to_draw[x][y][0] and map_to_draw[x][y][0].map_color:
							GAME.user_map[x][y] = map_to_draw[x][y][0].map_color


						new_surface = pygame.Surface((constants.MAP_TILE_SIZE, constants.MAP_TILE_SIZE))
						new_surface.fill(GAME.user_map[x][y])

						GUIDE_MAP.blit(new_surface, (constants.MAP_TILE_SIZE * x, constants.MAP_TILE_SIZE * y))

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

				#else:
					#SURFACE_MAP.blit(constants.S_DARK_GREY, (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

class guide_map():

	def draw(self):

		loc_x, loc_y = (250, 100)

		coords = loc_x, loc_y

		SURFACE_MAIN.blit(GUIDE_MAP, coords)

		player_image = pygame.Surface((constants.MAP_TILE_SIZE, constants.MAP_TILE_SIZE))

		player_image.fill(constants.COLOR_GREEN)

		SURFACE_MAIN.blit(player_image, (loc_x + (PLAYER.x * constants.MAP_TILE_SIZE), loc_y + (PLAYER.y * constants.MAP_TILE_SIZE)))

def remove_blocking():

	for z in range(constants.GAME_TILES_Z):
		for y in range(constants.GAME_TILES_Y):
			for x in range(constants.GAME_TILES_X):
				tile = GAME.current_map[x][y][z]

				if tile:
					tile.block_path = False

def create_map_lighting(map_to_light):

	fov_map = libtcod.map_new(constants.GAME_TILES_X, constants.GAME_TILES_Y)

	for y in range(constants.GAME_TILES_Y):
		for x in range(constants.GAME_TILES_X):
			libtcod.map_set_properties(fov_map, x, y,
				not map_to_light[x][y][0].block_light, not map_to_light[x][y][0].block_path)

		


	for x in range(constants.GAME_TILES_X):
		for y in range(constants.GAME_TILES_Y):
			if map_to_light[x][y][1] and map_to_light[x][y][1].emit_light_radius:
				light_radius = 100
				tiles_to_light = util.find_radius((x,y), map_to_light[x][y][1].emit_light_radius)
				libtcod.map_compute_fov(fov_map, x, y, light_radius, False, constants.FOV_ALGO)

				for coord in tiles_to_light:
					x1, y1 = coord
					is_visable = libtcod.map_is_in_fov(fov_map, x1, y1)
					if is_visable:
						map_to_light[x1][y1][0].light += map_to_light[x][y][1].light / util.clamp( distance_to((x, y), (x1,y1)), 1, None )

	return map_to_light

def tile_dimming(map_to_draw):

	camx , camy = CAMERA.map_address

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

	for x in range(render_min_w, render_max_w):
		for y in range(render_min_h, render_max_h):

			# DIM BASED ON PLAYER DISTANCE #
			is_visable = libtcod.map_is_in_fov(FOV_MAP, x, y)

			if is_visable:
				map_to_draw[x][y][0].explored = True

			if map_to_draw[x][y][0].explored == True:

				s = pygame.Surface((constants.GAME_TILE_SIZE,constants.GAME_TILE_SIZE))
				distance_mod = constants.DISTANCE_DARKENING * distance_to((PLAYER.x, PLAYER.y), (x,y))
				tile_light = map_to_draw[x][y][0].light * 10
				s.set_alpha(distance_mod - tile_light)
				s.fill((0, 0, 0))   
				              
				SURFACE_MAP.blit(s, (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

def map_make_fov(incoming_map):

	global FOV_MAP, FOV_MAP_MONSTER

	FOV_MAP = libtcod.map_new(constants.GAME_TILES_X, constants.GAME_TILES_Y)
	FOV_MAP_MONSTER = libtcod.map_new(constants.GAME_TILES_X, constants.GAME_TILES_Y)


	for y in range(constants.GAME_TILES_Y):
		for x in range(constants.GAME_TILES_X):
			libtcod.map_set_properties(FOV_MAP, x, y,
				not incoming_map[x][y][0].block_light, not incoming_map[x][y][0].block_path)
			libtcod.map_set_properties(FOV_MAP_MONSTER, x, y,
				not incoming_map[x][y][0].block_light, not incoming_map[x][y][0].block_path)

def map_calculate_fov(force = False):
	global FOV_CALCULATE

	if FOV_CALCULATE or force == True:
		FOV_CALCULATE = False
		libtcod.map_compute_fov(FOV_MAP, PLAYER.x, PLAYER.y, int(constants.TORCH_RADIUS * PLAYER.sight_multiplier), constants.FOV_LIGHT_WALLS, constants.FOV_ALGO)
		map_calculate_fov_monster()

def map_calculate_fov_monster():

	#
	#
	#

	libtcod.map_compute_fov(FOV_MAP_MONSTER, PLAYER.x, PLAYER.y, int(constants.TORCH_RADIUS), constants.FOV_LIGHT_WALLS, constants.FOV_ALGO)
	
		#
		#
		#
		#

def is_wall(x, y):

	return GAME.current_map[x][y][0].block_path

def map_check_for_creatures(x, y, exclude = None):

	target = None


	if exclude is not None:
		for object in GAME.current_objects:
				if (object is not exclude
				 and object.x <= x and object.x + object.width >= x 
				 and object.y <= y and object.y + object.height >= y
				 and object.creature and (object.creature.hp > 0 or (object.ai and object.ai.active))):
					
					target = object
					break
	else:
		for object in GAME.current_objects:
				if (object.x <= x and object.x + object.width >= x 
				 and object.y <= y and object.y + object.height >=y
				 and object.creature):
					
					target = object
					break

	return target
	
def map_check_for_item(coords_x, coords_y):
	""" adds all the items at coords"""

	items = []

	for object in GAME.current_objects:
				if (object.x == coords_x and object.y == coords_y
				 and object.item):
					
					items.append(object)
					

	return items



	

	#######MENUS######
	#######MENUS######
	#######MENUS######
	#######MENUS######

def map_create_room(new_map, new_room):

	for x in range(new_room.x, new_room.x2):
		for y in range(new_room.y, new_room.y2):

			new_map[x][y][0] = GAME.tile_floor(x,y, 0)

def map_tunnel(new_map, coords1, coords2):

	x1, y1 = coords1
	x2, y2 = coords2

	coin = libtcod.random_get_int(0, 0, 1) == 1

	if coin == True:

		for x in range(min(x1, x2), max(x1, x2) + 1):
			new_map[x][y1][0] = GAME.tile_floor(x, y1, 0)
		for y in range(min(y1, y2), max(y1, y2) + 1):
			new_map[x2][y][0] = GAME.tile_floor(x1, y, 0)

	else:

		for y in range(min(y1, y2), max(y1, y2) + 1):
			new_map[x1][y][0] = GAME.tile_floor(x1, y, 0)
		for x in range(min(x1, x2), max(x1, x2) + 1):
			new_map[x][y2][0] = GAME.tile_floor(x, y1, 0)

def tile_draw(tile):

	return constants.anim_dict[tile.sprite]
	#
	#
	#

def map_interact(x, y, interacter):

	result = "NONE"

	tile = GAME.current_map[x][y][0]
	tile1 = GAME.current_map[x][y][1]

	objects_at_player = map_check_for_item(x,y)

	if objects_at_player:
			for obj in objects_at_player:
				if obj.item:
					obj.item.pickup(interacter)

					result =  "ITEM_ACTION"


	if result == "NONE":

		result = tile.interact(interacter)

		if result == "NONE" and tile1:

			tile1.interact(interacter)

		

		

	return result

def distance_to(coords1, coords2):

	x1, y1 = coords1
	x2, y2 = coords2

	dx = x1 - x2
	dy = y1 - y2

	return math.sqrt(dx ** 2 + dy ** 2) #returns triangle hypotinuse

def map_create(old_map_id, new_map_id, make_new_player = False):
	
	generator = GAME.dungeon_generator()

	new_map, list_of_rooms = generator.gen_map(old_map_id, new_map_id)

	return (new_map, list_of_rooms)

def map_create_pathfinding():

	global PATH_FINDER, FOV_MAP

	PATH_FINDER = libtcod.path_new_using_map(FOV_MAP, 0.0)

def gen_traps(new_map, list_of_rooms):
	if PLAYER:
		trap_number = libtcod.random_get_int(0, 3, 9) - (PLAYER.creature.luck_roll) * 2
	else:
		trap_number = 4

	trap_number = util.clamp(trap_number, 0, None)

	for num in range(trap_number):

		done = False

		while done == False:

			rand_x = libtcod.random_get_int(0, 0, constants.GAME_TILES_X - 1)
			rand_y = libtcod.random_get_int(0, 0, constants.GAME_TILES_Y - 1)

			if new_map[rand_x][rand_y][0].block_path == False and new_map[rand_x][rand_y][1] == None:

				gen_trap((rand_x, rand_y), new_map)
				done = True



	return(new_map, list_of_rooms)

def draw_tile_at_coords(tile, x, y, require_visability = True):

	if tile.animation:


		if (require_visability == True and libtcod.map_is_in_fov(FOV_MAP, x, y) == True):

					if len(tile.animation) > 1:
						
						if CLOCK.get_fps() > 0.0:
							tile.flicker_timer += 1 / CLOCK.get_fps()

						if tile.flicker_timer >= tile.flicker_speed:
							tile.flicker_timer = 0.0

							if tile.current_anim_index >= len(constants.anim_dict[tile.animation]) - 1:
								tile.current_anim_index = 0
							else:
							 tile.current_anim_index +=1
							

						SURFACE_MAP.blit(constants.anim_dict[tile.animation][tile.current_anim_index], (x * constants.GAME_TILE_SIZE, y * constants.GAME_TILE_SIZE))

					
	elif not tile.animation:

		SURFACE_MAP.blit(constants.anim_dict[tile.sprite], (x*constants.GAME_TILE_SIZE, y*constants.GAME_TILE_SIZE) )

		


		


#  _____  ______ _____ ____  _____  
# |  __ \|  ____/ ____/ __ \|  __ \ 
# | |  | | |__ | |   | |  | | |__) |
# | |  | |  __|| |   | |  | |  _  / 
# | |__| | |___| |___| |__| | | \ \ 
# |_____/|______\_____\____/|_|  \_\
                                   
def gen_campfire(coords, new_map, room):

 	x, y = coords

 	nearby_tiles = util.find_radius((x,y), 1, False)

 	nearby_walls = 0
 	for tx, ty in nearby_tiles:
 		if new_map[tx][ty][0].block_path:
 			nearby_walls+=1

 	if nearby_walls < 1:

	 	fire_range_tiles = []

	 	for tile_coord in nearby_tiles:
		 	x1, y1 = tile_coord
		 	new_map[x1][y1][1] = tiles.campfire_nearby(x, y, 1, (y1-y, x1-x))
		 	#new_map[x1][y1][0].light += 200
		 	fire_range_tiles.append(new_map[x1][y1][1])


	 	new_map[x][y][1] = tiles.campfire(x, y, 1)

		for tile in fire_range_tiles:
			tile.fire = new_map[x][y][1]

	else:

		return False

def gen_shop_keeper(coords, new_map, room):

	tier = GAME.area_level

	x,y = coords

	ai = ai_wander(bounds = (room.x, room.y, room.w, room.h))

	creature_com1 = com_creature("Shop keeper", level = tier, death_function = death_shop_owner,
	 raw_damage = tier+1, raw_defense = 0, raw_evasion = 2 + (tier+1)/2,
	 vitality = 10*(tier+1), team = 3)

	container_com = com_container(10000, [])

	

	A = "SHOP"

	shop_com = com_shop(tier)

	new_shop = actor(x,y, "Shop Keeper", A, creature = creature_com1, container = container_com, depth = constants.DEPTH_CREATURES,
	ai = ai, shop_com = shop_com)
	new_shop.id = GAME.next_id

	rand = libtcod.random_get_int(0, 2, 9)

	for i in range(rand):
		item = gen_item(coords, tier, True)
		
		item.item.pickup(new_shop)



	GAME.current_objects.append(new_shop) 

def no_decor(coords, new_map, room):
	pass
	#
	#

def gen_chest(coords, new_map, room):

	x, y = coords

	rand = libtcod.random_get_int(0, 0, 5)

	if rand == 1:

		new_map[x][y][1] = tiles.trapped_chest(x, y, 1)

	else:

		new_map[x][y][1] = tiles.chest(x, y, 1)

def gen_alter(coords, new_map, room):

	x, y = room.center

	new_map[x][y][1] = tiles.sacraficial_alter(x, y, 1)

def gen_pedestal(coords, new_map, room):

	x, y = room.center

	new_map[x][y][1] = tiles.message_tile(x, y, 1)

	new_map[x][y][1].message = constants.MESSAGES[libtcod.random_get_int(0, 0, len(constants.MESSAGES)-1)]

def gen_trap(coords, new_map):

	trap_list_0 = [(tiles.trap_instant_posion_cloud, 10), (tiles.trap_instant_posion_dart, 10), (tiles.trap_dart, 10), (tiles.trap_floor_spikes, 10),
	 (tiles.trap_falling_boulder, 10), (tiles.trap_sound, 10), (tiles.trap_monster, 10), (tiles.hidden_treasure, 10),
	 (tiles.trap_collapsing_floor, 10)]#(tiles.trap_block_path, 10), (tiles.trap_hole, 10),

	tier = GAME.area_level

	tier_list = [trap_list_0]

	x,y = coords

	total_value = 0
	for trap,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for trap,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:

		rand_value-=amount
		if rand_value <= 0:
			new_map[x][y][1] = trap(x, y, 1)
			break

def gen_shrine(coords, new_map, room):

	shrine_list_0 = [(tiles.shrine_health, 10), (tiles.shrine_strength, 10), (tiles.shrine_fireball, 10), (tiles.shrine_random_stats, 10),
	(tiles.shrine_money, 10), (tiles.shrine_hurt, 10), (tiles.shrine_fire, 10), (tiles.shrine_identify, 10)]

	tier = GAME.area_level

	tier_list = [shrine_list_0]

	x,y = coords

	total_value = 0
	for trap,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for shrine,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:

		rand_value-=amount
		if rand_value <= 0:
			new_map[x][y][1] = shrine(x, y, 1)
			break
	




#   _____ ______ _   _ ______ _____         _______ ____  _____   _____ 
#  / ____|  ____| \ | |  ____|  __ \     /\|__   __/ __ \|  __ \ / ____|
# | |  __| |__  |  \| | |__  | |__) |   /  \  | | | |  | | |__) | (___  
# | | |_ |  __| | . ` |  __| |  _  /   / /\ \ | | | |  | |  _  / \___ \ 
# | |__| | |____| |\  | |____| | \ \  / ____ \| | | |__| | | \ \ ____) |
#  \_____|______|_| \_|______|_|  \_\/_/    \_\_|  \____/|_|  \_\_____/ 
      
def create_loot_tables():
	global tier_0, scroll_list_0, potion_list_0, weapon_list_0, weapon_list_1, weapon_list_2, weapon_list_3, weapon_list_4, r_weapon_list_0
	global r_weapon_list_1, r_weapon_list_2, r_weapon_list_3, r_weapon_list_4, spellbook_list_0, reagent_list_0
	global enemy_list_0, enemy_list_1, enemy_list_2, enemy_list_3, enemy_list_4
	global armor_list_0

	tier_0 = [(gen_scroll, 10), (gen_potion,10), (gen_melee, 15), (gen_ranged, 10), (gen_spellbook, 3), (gen_food, 5), (gen_armor, 10), (gen_gold, 10)]

	scroll_list_0 = [(gen_scroll_lightning,10), (gen_scroll_fireball,10), (gen_scroll_confuse,10), (gen_scroll_identify, 35)]

	potion_list_0 = [(gen_heal_potion, 20), (gen_bleach_potion, 5), (gen_posion_potion, 10), (gen_booze_potion, 10), (gen_confused_potion, 5),
	(gen_luck_potion, 5), (gen_strength_potion, 5), (gen_dexterity_potion, 5), (gen_wisdom_potion, 5), (gen_intelligence_potion, 5), 
	(gen_fire_resist_potion, 5), (gen_posion_resist_potion, 5), (gen_lightning_resist_potion, 5), (gen_cold_resist_potion, 5),
	(gen_all_resist_potion, 5), (gen_magic_nullify_potion, 5), (gen_invincible_potion, 5), (gen_hot_potion, 10), (gen_full_dmg_hot_potion, 5),
	(gen_control_reverse_potion, 5)]

	weapon_list_0 = [(gen_weapon_sword,10), (gen_weapon_sword_cold,5), (gen_weapon_shield,1),
		(gen_weapon_dirk, 10), (gen_broken_bottle, 3), (gen_candle_stick, 15), (gen_weapon_whip, 7)]

	weapon_list_1 = [(gen_weapon_sword,7), (gen_weapon_sword_cold,10), (gen_weapon_shield,3),
		(gen_weapon_dirk, 5), (gen_weapon_pike, 3), (gen_candle_stick, 3), (gen_weapon_whip, 7), (gen_weapon_scimitar,5)]

	weapon_list_2 = [(gen_weapon_sword_cold,3), (gen_weapon_shield,6), (gen_weapon_dirk, 5),
		(gen_weapon_pike,10), (gen_weapon_scimitar,10), (gen_weapon_club, 10)]

	weapon_list_3 = [(gen_weapon_halbard,3), (gen_weapon_shield,6), (gen_weapon_hammer, 5),
		(gen_weapon_pike,15), (gen_weapon_scimitar,15), (gen_weapon_club, 15), (gen_weapon_flail, 5), (gen_weapon_scythe, 5),
		(gen_weapon_executioners_axe, 5)]
		
	weapon_list_4 = [(gen_weapon_halbard,15), (gen_weapon_shield,6), (gen_weapon_hammer, 15),
		(gen_weapon_sword_cold,3), (gen_weapon_pike,5), (gen_weapon_scimitar,5), (gen_weapon_club, 5), (gen_weapon_flail, 10),
		(gen_weapon_scythe, 10), (gen_weapon_executioners_axe, 10)]

	r_weapon_list_0 = [(gen_arrows, 50), (gen_bow, 15)]
	r_weapon_list_1 = [(gen_arrows, 50), (gen_bow, 15)]
	r_weapon_list_2 = [(gen_arrows, 50), (gen_bow, 10), (gen_great_bow, 5)]
	r_weapon_list_3 = [(gen_arrows, 50), (gen_great_bow, 15)]
	r_weapon_list_4 = [(gen_arrows, 50), (gen_great_bow, 15)]

	spellbook_list_0 = [(gen_spellbook_lightning, 15), (gen_spellbook_fireball, 15), (gen_spellbook_blood_bolt, 10), (gen_spellbook_plauge_bomb, 10)]

	reagent_list_0 = [(gen_gem_diamond, 10), (gen_gem_amber, 10), (gen_gem_amethyst, 10), (gen_gem_aquamarine, 10), (gen_gem_emerald, 10),
		(gen_gem_onyx, 10), (gen_gem_ruby, 10), (gen_gem_sapphire, 10)]

	enemy_list_0 = [(gen_skeleton, 15), (gen_bat, 15), (gen_grub, 15), (gen_simple_mage, 5)]

	enemy_list_1 = [(gen_skeleton, 15), (gen_bat, 15), (gen_grub, 5), (gen_worm, 15), (gen_dire_bat, 10), (gen_reaper, 5), (gen_simple_mage, 5)]

	enemy_list_2 = [(gen_dire_bat, 15), (gen_devourer, 5), (gen_scorpion, 5), (gen_wolf, 5), (gen_reaper, 15), (gen_worm, 15), (gen_simple_mage, 10)]

	enemy_list_3 = [(gen_scorpion, 15), (gen_dire_scorpion, 5), (gen_wraith, 5), (gen_spirit, 5), (gen_wanderer, 5), (gen_reaper, 15), (gen_simple_mage, 10)]

	enemy_list_4 = [(gen_fireman, 15), (gen_dire_scorpion, 15), (gen_wraith, 15), (gen_spirit, 15), (gen_wanderer, 15), (gen_simple_mage, 10)]

	armor_list_0 = [(gen_armor_cloak, 15), (gen_armor_bucket_helmet, 15), (gen_armor_broken_crown, 1), (gen_armor_chain_mail, 3), (gen_armor_priest_cassock, 10), (gen_armor_monk_robes, 10)]

	armor_list_1 = [(gen_armor_cloak, 15), (gen_armor_bucket_helmet, 15), (gen_armor_broken_crown, 1), (gen_armor_chain_mail, 5), (gen_armor_lead_armor, 5), (gen_armor_plate_armor, 1), (gen_armor_chromatic_mail, 1), (gen_armor_priest_cassock, 10), (gen_armor_monk_robes, 10)]

	armor_list_2 = [(gen_armor_cloak, 15), (gen_armor_bucket_helmet, 5), (gen_armor_broken_crown, 1), (gen_armor_chain_mail, 15), (gen_armor_lead_armor, 5), (gen_armor_plate_armor, 3), (gen_armor_chromatic_mail, 1), (gen_armor_priest_cassock, 5), (gen_armor_monk_robes, 5)]

	armor_list_3 = [(gen_armor_cloak, 10), (gen_armor_bucket_helmet, 5), (gen_armor_chain_mail, 10), (gen_armor_lead_armor, 5), (gen_armor_plate_armor, 3), (gen_armor_chromatic_mail, 1), (gen_armor_priest_cassock, 3), (gen_armor_monk_robes, 3)]

def create_affix_tables():
	
	global PREFIX_WEAPONS_0

	PREFIX_WEAPONS_0 = [(prefix_sharp, 10), (prefix_simpleton, 10), (prefix_marksman, 10)]


#### ITEMS ####
#### ITEMS ####
#### ITEMS ####
def gen_item(coords, tier, from_map_creation = False):

	tier_list = [tier_0]

	rand = libtcod.random_get_int(0, 1, 10)

	if rand == 10:
		tier -= 2

	elif rand >= 7:
		tier -= 1

	total_value = 0
	for item,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for item,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = item(coords, tier)

			try:
				new_item = gen_item_from_data(new_item)
			except:
				pass

			new_item.id = GAME.next_id
			break

	GAME.current_objects.append(new_item)  

	if from_map_creation == False and NETWORK_LISTENER:
		NETWORK_LISTENER.new_obj(new_item)


	return new_item

def gen_item_from_data(data):

	# { equipment:{}, item:{}, reagent:{}, ammo:{}, potion:{}, actor:{}, coords:(x,y) }

	data = format_data(data, ["equipment", "item", "reagent", "ammo", "potion", "actor", "coords", "ai", "creature"])

	if data["equipment"]:

		equipment_com = com_equipment(**data[equipment])

		# form = ["attack_max_bonus", "attack_min_bonus", "armor_bonus", "evade_bonus",
	 # 			 "slot", "strength_req", "dexterity_req", "hit_chance_bonus", "hit_effect_function_temp", "hit_effect_function_params_temp",
	 # 			 "equip_effects", "equip_function_params",
		# 		 "hit_effect_permenent", "hit_effect_permenent_params", "hit_effect_function_chance", "durability", "lose_durability", "lose_durability_func"]

		# data["equipment"] = format_data(data["equipment"], form)

		# equipment_com = func_from_data(com_equipment, data["equipment"], form)
	else:
		equipment_com = None


	if data["item"]:

		item_com = com_item(**data["item"])

		# form = ["action", "size", "use_function", "use_params", "value", "identify_name",
		# 		 "throw_damage", "throw_function", "use_gui", "use_text"]

		# data["item"] = format_data(data["item"], form)

		# item_com = func_from_data(com_item, data["item"], form)
	else:
		item_com = None


	if data["reagent"]:

		reagent_com = com_reagent(**data["reagent"])

		# form = ["lib_name"]

		# data["reagent"] = format_data(data["reagent"], form)

		# reagent_com = func_from_data(com_reagent, data["reagent"], form)
	else:
		reagent_com = None


	if data["ammo"]:

		ammo_com = com_ammo(**["ammo"])

		# form = ["amount"]

		# data["ammo"] = format_data(data["ammo"], form)

		# ammo_com = func_from_data(com_ammo, data["ammo"], form)
	else:
		ammo_com = None


	if data["potion"]:

		potion_com = com_potion(**data["potion"])

		# form = ["lib_name", "function_applied", "function_params"]

		# data["potion"] = format_data(data["potion"], form)

		# potion_com = func_from_data(com_potion, data["potion"], form)
	else:
		potion_com = None

	if data["creature"]:

		creature_com = com_creature(**data["creature"])

		# form = ["name_instance", "level", "death_function",
		# 	 "raw_damage", "raw_defense", "raw_evasion",
		# 	 "vitality", "dexterity", "strength", "intelligence", "wisdom", "luck",
		# 	 "fire_resistance", "posion_resistance", "lightning_resistance", "cold_resistance", 
		# 	 "attack_function", "attack_function_occurance", "team", "creature_type", "dead_item_name", "haste"]

		# data["creature"] = format_data(data["creature"], form)

		# creature_com = func_from_data(com_creature, data["creature"], form)
	else:
		creature_com = None

	if data["ai"]:

		ai_com = data["ai"]
		
	else:
		ai_com = None

	shop_com = None
	player_com = None
	container_com = None




	form = ["x", "y", "name", "animation_key", "creature", "ai", "container", "item",
	 "equipment", "sprite", "player_com", "ammo_com", "ranged_wep_com", "state",
	 "potion", "reagent", "depth", "shop_com", "width", "height", "delta_draw_x", "delta_draw_y",
	 "create_function", "create_function_params", "id"]

	data["actor"] = format_data(data["actor"], form)

	x, y = data["coords"]

	data["actor"]["x"] = x
	data["actor"]["y"] = y



	if equipment_com:
		data["actor"]["equipment"] = equipment_com
	if ammo_com:
		data["actor"]["ammo_com"] = ammo_com
	if reagent_com:
		data["actor"]["reagent"] = reagent_com
	if item_com:
		data["actor"]["item"] = item_com
	if potion_com:
		data["actor"]["potion"] = potion_com
	if potion_com:
		data["actor"]["potion"] = potion_com
	if shop_com:
		data["actor"]["shop_com"] = shop_com
	if player_com:
		data["actor"]["player_com"] = player_com
	if container_com:
		data["actor"]["container"] = container_com
	if ai_com:
		data["actor"]["ai"] = ai_com
	if creature_com:
		data["actor"]["creature"] = creature_com

	actor_com = actor(**data["actor"])

	#actor_com = func_from_data(actor, data["actor"], form)

	return actor_com

def format_data(data, form):
	#form = ["str1", "str2", "str3"]

	new_data = {}

	for string in form:

		try:
			new_data[string] = data[string]
		except:
			new_data[string] = None


	return new_data

def func_from_data(func, data, form):

	params = []

	for string in form:
		params.append(data[string])

	return func(*params)

def gen_enemy(coords, tier, from_map_creation = False):

	

	rand = libtcod.random_get_int(0, 1, 10)

	if rand == 10:
		tier -= 2
		
	elif rand >= 7:
		tier -= 1

	tier_list = [enemy_list_0, enemy_list_1, enemy_list_2, enemy_list_3, enemy_list_4]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0

	for enemy,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for enemy,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_enemy = enemy(coords)#gen_test_dummy(coords)#

			#new_item = gen_item_from_data(new_enemy)
			try:
				new_enemy = gen_item_from_data(new_enemy)

			except:
				pass

			new_enemy.id = GAME.next_id
			break


	GAME.current_objects.append(new_enemy)  

	if from_map_creation == False and NETWORK_LISTENER:
		NETWORK_LISTENER.new_obj(new_enemy)


# CHILD GENERATORS #
def gen_scroll(coords, tier):


	tier_list = [scroll_list_0]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0
	for scroll,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for scroll,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = scroll(coords)
			break

	return new_item                                     

def gen_potion(coords, tier):

	tier_list = [potion_list_0]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0
	for potion,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for potion,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = potion(coords)
			break

	return new_item

def gen_melee(coords, tier):

	tier_list = [weapon_list_0, weapon_list_1, weapon_list_2, weapon_list_3, weapon_list_4]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0
	for weapon,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for weapon,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = weapon(coords)
			roll_magic_weapon(new_item)
			break

	


	return new_item

def gen_armor(coords, tier):

	tier_list = [armor_list_0]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0
	for weapon,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for weapon,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = weapon(coords)
			break

	


	return new_item

def gen_ranged(coords, tier):

	


	tier_list = [r_weapon_list_0, r_weapon_list_1, r_weapon_list_2, r_weapon_list_3, r_weapon_list_4]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0
	for weapon,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for weapon,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = weapon(coords)
			break

	return new_item

def gen_spellbook(coords, tier):

	


	tier_list = [spellbook_list_0]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0

	for spell,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for spell,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = spell(coords)
			break

	return new_item

def gen_reagent(coords, tier):

	tier_list = [reagent_list_0]

	tier = util.clamp(tier, 0, len(tier_list) - 1)

	total_value = 0
	for reagent,amount in tier_list[tier]:
		total_value+=amount

	rand_value = libtcod.random_get_int(0, 0, total_value)

	for reagent,amount in tier_list[tier]:

		rand_value-=amount
		if rand_value <= 0:
			new_item = reagent(coords)
			break

	return new_item

# SCROLLS #
def gen_scroll_lightning(coords, force_dmg = None, force_range = None):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	if force_dmg:
		damage = force_dmg
	else:
		damage = libtcod.random_get_int(0, 10,30)

	if force_range:
		m_range = force_range

	else:
		m_range = libtcod.random_get_int(0, 3,7)

	item_com = com_item(action = "TARGETED_SPELL", use_function = spells.lightning, use_params = 
		[damage, None, False, None, m_range], value = 100, size = constants.SCROLL_WEIGHT)

	return_object = actor(x, y, "Lightning Scroll", "SCROLL_LIGHTNING", item = item_com, depth = constants.DEPTH_ITEM,
	 create_function = "gen_scroll_lightning", create_function_params = [coords, damage, m_range])

	return return_object

def gen_scroll_fireball(coords, force_radius = None):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	damage = 40

	if force_radius:
		radius = force_radius
	else:
		radius = libtcod.random_get_int(0, 0,1)

	m_range = 5

	item_com = com_item(action = "TARGETED_SPELL", use_function = spells.fireball, use_params = 
		[damage, None, False, None, radius, m_range], value = 100, size = constants.SCROLL_WEIGHT)

	return_object = actor(x, y, "Fireball Scroll", "SCROLL_FIRE", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_scroll_fireball", create_function_params = [coords, radius])

	return return_object

def gen_scroll_confuse(coords, force_radius = None):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	duration = 10

	if force_radius:
		radius = force_radius

	else:
		radius = libtcod.random_get_int(0, 0,1)

	item_com = com_item(action = "TARGETED_SPELL", use_function = spells.confuse, use_params = 
		[duration, None, False, None, radius], value = 75, size = constants.SCROLL_WEIGHT)

	return_object = actor(x, y, "Confue Scroll", "SCROLL_CONFUSE", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_scroll_confuse", create_function_params = [coords, radius])

	return return_object

def gen_scroll_blind(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	duration = 10
	radius = 0

	item_com = com_item(action = "TARGETED_SPELL", use_function = spells.blind, use_params = 
		[duration, None, False, None, radius], value = 30, size = constants.SCROLL_WEIGHT)

	return_object = actor(x, y, "Blinding Scroll", "SCROLL_BLIND", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_scroll_blind", create_function_params = [coords])

	return return_object

def gen_scroll_identify(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	item_com = com_item(action = "IDENTIFY_SCROLL", use_function = identify_scroll, value = 50, size = constants.SCROLL_WEIGHT)

	return_object = actor(x, y, "Identify Scroll", "SCROLL_ID", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_scroll_identify", create_function_params = [coords])

	return return_object

# SPELLBOOKS #
def gen_spellbook_lightning(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Lightning"], value = 175)

	return_object = actor(x, y, "Lightning Spell Book", "RANDOM_BOOK", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_lightning", create_function_params = [coords])

	return return_object

def gen_spellbook_tut_spell(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Tut_Spell"], value = -100)

	return_object = actor(x, y, "Lightning Spell Book", "RANDOM_BOOK", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_tut_spell", create_function_params = [coords])

	return return_object

def gen_spellbook_plauge_bomb(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Plauge_Bomb"], value = 175)

	return_object = actor(x, y, "Plauge Bomb Spell Book", "RANDOM_BOOK", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_plauge_bomb", create_function_params = [coords])

	return return_object

def gen_spellbook_fire_blast(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Fire_Blast"], value = 175)

	return_object = actor(x, y, "Fire Blast Spell Book", "RANDOM_BOOK", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_fire_blast", create_function_params = [coords])

	return return_object

def gen_spellbook_holy_light(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Holy_Light"], value = 175)

	return_object = actor(x, y, "Holy Light Spell Book", "RANDOM_BOOK", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_holy_light", create_function_params = [coords])

	return return_object

def gen_spellbook_blood_bolt(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Blood_Bolt"], value = 175)

	return_object = actor(x, y, "Blood Bolt Spell Book", "RANDOM_BOOK", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_blood_bolt", create_function_params = [coords])

	return return_object

def gen_spellbook_fireball(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)


	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Fireball"], value = 175)

	return_object = actor(x, y, "Fireball Spell Book", "RANDOM_BOOK", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_fireball", create_function_params = [coords])

	return return_object

def gen_spellbook_idiot_speak(coords):

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)


	item_com = com_item(action = "LEARN_SPELL", use_function = spells.learn_spell, size = constants.SPELLBOOK_WEIGHT,
	 use_params = spells.dict["Idiot_Speak"], value = 0)

	return_object = actor(x, y, "Super Secret Spell Book", "MISSING_2", item = item_com, depth = constants.DEPTH_ITEM, 
		create_function = "gen_spellbook_idiot_speak", create_function_params = [coords])

	return return_object

# REAGENTS #
def gen_gem_diamond(coords):

	global LIB

	x,y = coords
	lib_name = "gem_diamond"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com,
	 reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_diamond", create_function_params = [coords])

	return return_object

def gen_gem_amber(coords):

	global LIB

	x,y = coords
	lib_name = "gem_amber"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, 
		reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_amber", create_function_params = [coords])

	return return_object

def gen_gem_amethyst(coords):

	global LIB

	x,y = coords
	lib_name = "gem_amethyst"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com,
	 reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_amethyst", create_function_params = [coords])

	return return_object

def gen_gem_aquamarine(coords):

	global LIB

	x,y = coords
	lib_name = "gem_aquamarine"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com,
	 reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_aquamarine", create_function_params = [coords])

	return return_object

def gen_gem_emerald(coords):

	global LIB

	x,y = coords
	lib_name = "gem_emerald"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, 
		reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_emerald", create_function_params = [coords])

	return return_object

def gen_gem_onyx(coords):

	global LIB

	x,y = coords
	lib_name = "gem_onyx"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com,
	 reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_onyx", create_function_params = [coords])

	return return_object

def gen_gem_ruby(coords):

	global LIB

	x,y = coords
	lib_name = "gem_ruby"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, 
		reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_ruby", create_function_params = [coords])

	return return_object

def gen_gem_sapphire(coords):

	global LIB

	x,y = coords
	lib_name = "gem_sapphire"

	item_com = com_item("NONE", value = 200, size = constants.GEM_WEIGHT)

	reagent_com = com_reagent(lib_name = lib_name)

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, 
		reagent = reagent_com, depth = constants.DEPTH_ITEM, create_function = "gen_gem_sapphire", create_function_params = [coords])

	return return_object


def gen_gold(coords, tier, returns_object = True):

	amount = abs(tier * libtcod.random_get_int(0, 20, 50)) + 40

	x,y = coords

	item_com = com_item("MONEY", value = amount, size = 0)

	return_object = actor(x, y, "Gold", "MONEY", item = item_com, 
		depth = constants.DEPTH_ITEM, create_function = "gen_gold", create_function_params = [coords, amount])

	if return_object == True:
		return return_object
	else:

		new_item = return_object

		try:
			new_item = gen_item_from_data(new_item)
		except:
			pass

		new_item.id = GAME.next_id

		GAME.current_objects.append(new_item)  

		if NETWORK_LISTENER:
			NETWORK_LISTENER.new_obj(new_item)

		return return_object

def gen_food(coords, tier):

	x,y = coords
	item_com = com_item("EAT", use_function = effects.eat, use_params = [150], value = 20, size = .2, use_text = "Eat")
	A = "FOOD"

	enemy = actor(x,y, "Food", A, item = item_com, depth = constants.DEPTH_ITEM, create_function = "gen_food", create_function_params = [coords, tier])

	return enemy

def gen_map_tools(coords):

	global LIB

	x,y = coords

	item_com = com_item("NONE", value = 200, size = .5)

	return_object = actor(x, y, "Cartography tools", "MAP_TOOLS", item = item_com
		, depth = constants.DEPTH_ITEM, create_function = "gen_map_tools", create_function_params = [coords])

	return return_object

# MELEE WEAPONS #
def gen_weapon_toy_sword(coords):#t0

	x,y = coords

	min_a = 0
	max_a = 0


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand")
	item = com_item("EQUIP", value = 5, size = 0, throw_damage = 1)

	return_actor = actor(x, y, "Toy Sword", "SWORD_1", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_toy_sword", create_function_params = [coords])

	return return_actor

def gen_weapon_scepter(coords):#t0

	x,y = coords

	min_a = 7
	max_a = 10


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand", equip_func = effects.luck, equip_function_params = [2])
	item = com_item("EQUIP", value = 300, size = .5, throw_damage = max_a)

	return_actor = actor(x, y, "Scepter", "SCEPTER", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item, 
		create_function = "gen_weapon_scepter", create_function_params = [coords])

	return return_actor

def gen_weapon_sword(coords):#t0

	x,y = coords

	min_a = 15
	max_a = 15


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand")
	item = com_item("EQUIP", value = 50, size = 1, throw_damage = max_a)

	return_actor = actor(x, y, "Short Sword", "SWORD_1", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item, 
		create_function = "gen_weapon_sword", create_function_params = [coords])

	return return_actor

def gen_weapon_demon_shank(coords):#t?

	x,y = coords

	min_a = 20
	max_a = 20


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand", equip_effects = [effects.learn_skill], equip_function_params = [[spells.dict["Demon_Shank"]]])
	item = com_item("EQUIP", value = 500, size = 1, throw_damage = max_a)

	return_actor = actor(x, y, "Demon Shank", "DEMON_BONE", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item, 
		create_function = "gen_weapon_demon_shank", create_function_params = [coords])

	return return_actor

def gen_weapon_volatile_sword(coords):#t?

	x,y = coords

	min_a = 10
	max_a = 20

	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand", lose_durability = "ON_ATTACK", lose_durability_func = durablity_volatile)
	item = com_item("EQUIP", value = 0, size = 1, throw_damage = 35)

	return_actor = actor(x, y, "Volitile Sword", "SWORD_2", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item, 
		create_function = "gen_weapon_volatile_sword", create_function_params = [coords])

	return return_actor

def gen_weapon_sword_cold(coords):#t1

	x,y = coords

	min_a = 3
	max_a = 10

	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand",
	 hit_effect_function_chance = .3, hit_effect_permenent = effects.cold_damage, hit_effect_permenent_params = [15])
	item = com_item("EQUIP", value = 75, size = 1, throw_damage = max_a)

	return_actor = actor(x, y, "Short Sword", "SWORD_1", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item, 
		create_function = "gen_weapon_sword_cold", create_function_params = [coords])

	return return_actor

def gen_weapon_dirk(coords):#t0

	x,y = coords

	min_a = 10
	max_a = 10


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand")
	item = com_item("EQUIP", value = 40, size = .2, throw_damage = max_a)

	return_actor = actor(x, y, "Dirk", "DIRK", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_dirk", create_function_params = [coords])

	return return_actor

def gen_weapon_pike(coords):#t1

	x,y = coords

	min_a = 15
	max_a = 25


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "both_hands")
	item = com_item("EQUIP", value = 60, size = 2.5, throw_damage = max_a)

	return_actor = actor(x, y, "Pike", "PIKE", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_pike", create_function_params = [coords])

	return return_actor

def gen_weapon_scimitar(coords):#t1

	x,y = coords

	min_a = 10
	max_a = 25


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand", dexterity_req = 3, hit_chance_bonus = 2)
	item = com_item("EQUIP", value = 50, size = .7, throw_damage = max_a)

	return_actor = actor(x, y, "Scimitar", "SCIMITAR", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_scimitar", create_function_params = [coords])

	return return_actor

def gen_weapon_flail(coords):#t2

	x,y = coords

	min_a = 30
	max_a = 55


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand", dexterity_req = 3, hit_chance_bonus = -2)
	item = com_item("EQUIP", value = 80, size = 1.5, throw_damage = max_a)

	return_actor = actor(x, y, "Flail", "FLAIL", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_flail", create_function_params = [coords])

	return return_actor

def gen_weapon_scythe(coords):#t2

	x,y = coords

	min_a = 35
	max_a = 50


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "both_hands", dexterity_req = 4, hit_chance_bonus = 0)
	item = com_item("EQUIP", value = 80, size = 2.5, throw_damage = max_a)

	return_actor = actor(x, y, "Scythe", "SCYTHE", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_scythe", create_function_params = [coords])

	return return_actor

def gen_weapon_executioners_axe(coords):#t2

	x,y = coords

	min_a = 35
	max_a = 50


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "both_hands", dexterity_req = 3, strength_req = 3, hit_chance_bonus = 0)
	item = com_item("EQUIP", value = 40, size = 3, throw_damage = max_a)

	return_actor = actor(x, y, "Executioner's Axe", "EXECUTIONERS_AXE", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_executioners_axe", create_function_params = [coords])

	return return_actor

def gen_weapon_whip(coords):#t0

	x,y = coords

	min_a = 8
	max_a = 25


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand", dexterity_req = 3, hit_chance_bonus = 0)
	item = com_item("EQUIP", value = 20, size = .75, throw_damage = max_a)

	return_actor = actor(x, y, "Whip", "WHIP", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_whip", create_function_params = [coords])

	return return_actor

def gen_weapon_club(coords):#t1

	x,y = coords

	min_a = 25
	max_a = 35

	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand", strength_req = 3, hit_chance_bonus = -1)
	item = com_item("EQUIP", value = 10, size = 2, throw_damage = max_a)

	return_actor = actor(x, y, "Club", "CLUB", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_club", create_function_params = [coords])

	return return_actor

def gen_weapon_halbard(coords):#t2

	x,y = coords

	min_a = 25
	max_a = 35


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "both_hands", strength_req = 3, dexterity_req = 3, hit_chance_bonus = 1)
	item = com_item("EQUIP", value = 120, size = 3, throw_damage = max_a)

	return_actor = actor(x, y, "Halbard", "HALBARD", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_halbard", create_function_params = [coords])

	return return_actor

def gen_weapon_hammer(coords):#t2

	x,y = coords

	min_a = 25
	max_a = 35


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "both_hands", strength_req = 5, hit_chance_bonus = 0)
	item = com_item("EQUIP", value = 40, size = 4, throw_damage = max_a)

	return_actor = actor(x, y, "Hammer", "HAMMER", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_hammer", create_function_params = [coords])

	return return_actor

def gen_broken_bottle(coords):#t0

	x,y = coords

	min_a = 8
	max_a = 10


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand")
	item = com_item("EQUIP", value = 2, size = .2, throw_damage = max_a)

	return_actor = actor(x, y, "Broken Bottle", "BROKEN_BOTTLE", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_broken_bottle", create_function_params = [coords])

	return return_actor

def gen_candle_stick(coords):#t0

	x,y = coords

	min_a = 8
	max_a = 10


	equipment_com = com_equipment(attack_max_bonus = max_a, attack_min_bonus = min_a, slot = "right_hand")
	item = com_item("EQUIP", value = 5, size = .5, throw_damage = max_a)

	return_actor = actor(x, y, "Candle Stick", "CANDLE_STICK", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_candle_stick", create_function_params = [coords])

	return return_actor

def gen_weapon_shield(coords):#t1

	x,y = coords

	bonus = 6

	equipment_com = com_equipment(armor_bonus = bonus, slot = "left_hand", strength_req = 3, durability = 30)
	item = com_item("EQUIP", value = 50, size = 2)

	return_actor = actor(x, y, "shield", "SHIELD_1", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_weapon_shield", create_function_params = [coords])

	return return_actor

# ARMOR #
def gen_armor_cloak(coords):#t0

	x,y = coords

	bonus = 1

	equipment_com = com_equipment(evade_bonus = bonus, slot = "chest", dexterity_req = 1)
	item = com_item("EQUIP", value = 40, size = .5)

	return_actor = actor(x, y, "Cloak", "CLOAK", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_cloak", create_function_params = [coords])

	return return_actor

def gen_armor_monk_robes(coords):#t0

	x,y = coords

	equipment_com = com_equipment(evade_bonus = 2, slot = "chest", dexterity_req = 4, equip_effects = [effects.dexterity], equip_function_params = [[1]])
	item = com_item("EQUIP", value = 40, size = .5)

	return_actor = actor(x, y, "Monk Robes", "MONK_ROBES", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_monk_robes", create_function_params = [coords])

	return return_actor

def gen_armor_priest_cassock(coords):#t0

	x,y = coords

	equipment_com = com_equipment(slot = "chest", equip_effects = [effects.wisdom], equip_function_params = [[2]])
	item = com_item("EQUIP", value = 90, size = .5)

	return_actor = actor(x, y, "Priest Cassock", "CASSOCK", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_priest_cassock", create_function_params = [coords])

	return return_actor

def gen_armor_studded_leather(coords):#t0

	x,y = coords


	equipment_com = com_equipment(evade_bonus = 1, armor_bonus = 3, slot = "chest", dexterity_req = 2, strength_req = 2)
	item = com_item("EQUIP", value = 100, size = .75)

	return_actor = actor(x, y, "Studded Leather", "LEATHER_CHEST", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_studded_leather", create_function_params = [coords])

	return return_actor

def gen_armor_chain_mail(coords):#t1

	x,y = coords

	equipment_com = com_equipment(armor_bonus = 6, evade_bonus = -1, slot = "chest", strength_req = 4)
	item = com_item("EQUIP", value = 100, size = .75)

	return_actor = actor(x, y, "Chain Mail", "CHAIN_MAIL", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_chain_mail", create_function_params = [coords])

	return return_actor

def gen_armor_plate_armor(coords):#t2

	x,y = coords

	equipment_com = com_equipment(armor_bonus = 8, evade_bonus = -2, slot = "chest", strength_req = 6, equip_effects = [effects.boost_resistances], equip_function_params = [[(.2, .2, .2, .2)]], durability = 40)
	item = com_item("EQUIP", value = 150, size = .75)

	return_actor = actor(x, y, "Plate Armor", "PLATE_ARMOR", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_plate_armor", create_function_params = [coords])

	return return_actor

def gen_armor_lead_armor(coords):#t1

	x,y = coords

	equipment_com = com_equipment(armor_bonus = 4, evade_bonus = -2, slot = "chest", strength_req = 6, equip_effects = [effects.haste], equip_function_params = [[-.2]])
	item = com_item("EQUIP", value = 100, size = 1.75)

	return_actor = actor(x, y, "Lead Armor", "LEAD_ARMOR", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_lead_armor", create_function_params = [coords])

	return return_actor

def gen_armor_chromatic_mail(coords):#t2

	x,y = coords

	equipment_com = com_equipment(armor_bonus = 6, evade_bonus = -1, slot = "chest", strength_req = 4, equip_effects = [effects.boost_resistances], equip_function_params = [[(.80, .80, .80, .80)]])
	item = com_item("EQUIP", value = 300, size = .75)

	return_actor = actor(x, y, "Chromaitc Mail", "CHROMATIC_MAIL", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_chromatic_mail", create_function_params = [coords])

	return return_actor

def gen_armor_broken_crown(coords):#t0

	x,y = coords

	bonus = 0

	equip_func = effects.reduce_luck

	equipment_com = com_equipment(slot = "head", equip_effects = [equip_func], equip_function_params = [[2]])
	item = com_item("EQUIP", value = 300, size = .5)

	return_actor = actor(x, y, "Broken Crown", "CROWN", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_broken_crown", create_function_params = [coords])

	return return_actor

def gen_armor_bucket_helmet(coords):#t0

	x,y = coords


	equip_func = effects.blind

	equipment_com = com_equipment(slot = "head", equip_effects = [equip_func], equip_function_params = [[-1, .7]], armor_bonus = 6, evade_bonus = -3, durability = 10)
	item = com_item("EQUIP", value = 5, size = 1.5)

	return_actor = actor(x, y, "Bucket Helmet", "BUCKET", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_armor_bucket_helmet", create_function_params = [coords])

	return return_actor

# RINGS #
def gen_sacred_ring(coords):#t0

	x,y = coords

	bonus = 0

	equipment_com = com_equipment(slot = "finger")
	item = com_item("EQUIP", value = 150, size = .2)

	return_actor = actor(x, y, "Sacred Ring", "RANDOM_RING", equipment = equipment_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_sacred_ring", create_function_params = [coords])

	return return_actor

# RANGED WEAPONS #
def gen_arrows(coords):

	x,y = coords

	bonus = 0
	num_of_arrows = libtcod.random_get_int(0, 3, 15)

	equipment_com = com_equipment(attack_min_bonus = 0, slot = "ammo")
	ammo_com = com_ammo(num_of_arrows)
	item = com_item("EQUIP", value = 40, size = .05)

	return_actor = actor(x, y, "arrows", "ARROW", equipment = equipment_com, ammo_com = ammo_com, depth = constants.DEPTH_ITEM, item = item,
		create_function = "gen_arrows", create_function_params = [coords])

	return return_actor

def gen_bow(coords):#t0

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	damage = 20#libtcod.random_get_int(0, 1,2)
	m_range = 4

	ranged_com = com_ranged_weapon()



	item_com = com_item(action = "TARGETED_SPELL", use_function = spells.shoot_wep, use_params = 
		[damage, "PLAYER", False, None, m_range], value = 75, size = 1.25)

	return_object = actor(x, y, "Bow", "BOW", item = item_com, ranged_wep_com = ranged_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_bow", create_function_params = [coords])

	return return_object

def gen_great_bow(coords):#t1

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)

	damage = 30#libtcod.random_get_int(0, 1,2)
	m_range = 6

	ranged_com = com_ranged_weapon()



	item_com = com_item(action = "TARGETED_SPELL", use_function = spells.shoot_wep, use_params = 
		[damage, "PLAYER", False, None, m_range], value = 90, size = 1.75)

	return_object = actor(x, y, "Great Bow", "BOW", item = item_com, ranged_wep_com = ranged_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_great_bow", create_function_params = [coords])

	return return_object

# POTIONS #
def gen_heal_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.heal

	item_com = com_item(action = "POTION", use_function = "POTION", value = 75, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = "potion_healing", function_applied = potion_effect, function_params = [70])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict["potion_healing"][0], LIB.lib_dict["potion_healing"][1], item = item_com, 
		potion = potion_com, depth = constants.DEPTH_ITEM, create_function = "gen_heal_potion", create_function_params = [coords])

	return return_object

def gen_bleach_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.bleach
	tick_damage = 12
	duration = 15
	damage_every_x_turns = 5
	lib_name = "potion_bleach"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 25, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [tick_damage, duration, damage_every_x_turns])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_bleach_potion", create_function_params = [coords])

	return return_object

def gen_posion_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.dot_posion
	tick_damage = 14
	duration = 15
	damage_every_x_turns = 5
	lib_name = "potion_posion"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 50, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [tick_damage, duration, damage_every_x_turns])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_posion_potion", create_function_params = [coords])

	return return_object

def gen_hot_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.hot
	tick_amount = 15
	duration = 15
	damage_every_x_turns = 5
	lib_name = "potion_hot"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 75, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [tick_amount, duration, damage_every_x_turns])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_hot_potion", create_function_params = [coords])

	return return_object

def gen_full_dmg_hot_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.full_dmg_hot
	duration = 15
	lib_name = "potion_full_dmg_hot"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 150, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_full_dmg_hot_potion", create_function_params = [coords])

	return return_object



def gen_luck_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.luck
	amount = 2
	duration = 15
	lib_name = "potion_luck"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 75, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [amount, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_luck_potion", create_function_params = [coords])

	return return_object

def gen_strength_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.strength
	amount = 2
	duration = 15
	lib_name = "potion_strength"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 75, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [amount, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_strength_potion", create_function_params = [coords])

	return return_object

def gen_dexterity_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.dexterity
	amount = 2
	duration = 15
	lib_name = "potion_dexterity"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 75, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [amount, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_dexterity_potion", create_function_params = [coords])

	return return_object

def gen_wisdom_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.wisdom
	amount = 2
	duration = 15
	lib_name = "potion_wisdom"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 75, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [amount, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_wisdom_potion", create_function_params = [coords])

	return return_object

def gen_intelligence_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.intelligence
	amount = 2
	duration = 15
	lib_name = "potion_intelligence"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 75, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [amount, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_intelligence_potion", create_function_params = [coords])

	return return_object


def gen_fire_resist_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.boost_resistances
	resists = (.80,0,0,0)
	duration = 40
	lib_name = "potion_fire_resist"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 100, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [resists, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_fire_resist_potion", create_function_params = [coords])

	return return_object

def gen_posion_resist_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.boost_resistances
	resists = (0,.80,0,0)
	duration = 40
	lib_name = "potion_posion_resist"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 100, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [resists, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_posion_resist_potion", create_function_params = [coords])

	return return_object

def gen_lightning_resist_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.boost_resistances
	resists = (0,0,.80,0)
	duration = 40
	lib_name = "potion_lightning_resist"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 100, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [resists, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_lightning_resist_potion", create_function_params = [coords])

	return return_object

def gen_cold_resist_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.boost_resistances
	resists = (0,0,0,.80)
	duration = 40
	lib_name = "potion_cold_resist"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 100, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [resists, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_cold_resist_potion", create_function_params = [coords])

	return return_object

def gen_all_resist_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.boost_resistances
	resists = (.50,.50,.50,.50)
	duration = 40
	lib_name = "potion_all_resist"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 125, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [resists, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_all_resist_potion", create_function_params = [coords])

	return return_object


def gen_confused_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.confused
	duration = libtcod.random_get_int(0, 12, 20)
	lib_name = "potion_confusion"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 50, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_confused_potion", create_function_params = [coords])

	return return_object

def gen_control_reverse_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.revered_movement
	duration = libtcod.random_get_int(0, 7, 15)
	lib_name = "potion_reverse"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 50, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_control_reverse_potion", create_function_params = [coords])

	return return_object

def gen_booze_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.drunk
	food = 20
	duration = 15
	dex_subtractor = 1
	lib_name = "potion_booze"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 25, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [food, dex_subtractor, duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_booze_potion", create_function_params = [coords])

	return return_object

def gen_magic_nullify_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.magic_nullify
	duration = 15
	lib_name = "magic_nullify"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 100, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_magic_nullify_potion", create_function_params = [coords])

	return return_object

def gen_invincible_potion(coords):

	global LIB

	x,y = coords
	#origin = (self.current_container.owner.x, self.current_container.owner.y)
	potion_effect = effects.invincible
	duration = 15
	lib_name = "potion_invincibility"

	item_com = com_item(action = "POTION", use_function = "POTION", value = 125, size = constants.POTION_WEIGHT, use_gui = potion_action_menu)

	potion_com = com_potion(lib_name = lib_name, function_applied = potion_effect, function_params = [duration])#target will be appended later

	return_object = actor(x, y, LIB.lib_dict[lib_name][0], LIB.lib_dict[lib_name][1], item = item_com, potion = potion_com, depth = constants.DEPTH_ITEM,
		create_function = "gen_invincible_potion", create_function_params = [coords])

	return return_object

#### ENEMIES #####
#### ENEMIES #####
#### ENEMIES ##### 
def gen_test_dummy(coords):

	x,y = coords
	name = "Dummy"#libtcod.namegen_generate("male")
	creature_com = com_creature(name, level = 1, dexterity = 0, vitality = 1, raw_evasion = -1,
		fire_resistance = 0, posion_resistance = .0, lightning_resistance = 0, cold_resistance = .25, death_function = None)
	item_com = com_item("EAT", use_function = effect_eat, use_params = [150])
	ai = ai_dummy()
	A_SKELETON = "DUMMY"

	enemy = actor(x,y, "Dummy", A_SKELETON, creature = creature_com, ai = ai, item = item_com, depth = constants.DEPTH_CREATURES,
		create_function = "gen_test_dummy", create_function_params = [coords])

	return enemy

def gen_skeleton(coords):#t0

	
	x,y = coords
	name = libtcod.namegen_generate("male")
	creature_type = type_undead
	creature_com = com_creature(name, level = 1, dexterity = 1, death_function = death_humanoid, raw_damage = 10, creature_type = creature_type)
	item_com = com_item("NONE", use_function = None, value = 10, size = .1, throw_function = bone_throw)
	ai = ai_chase()
	A_SKELETON = "SKELETON"

	enemy = actor(x,y, "Skeleton", A_SKELETON, creature = creature_com, ai = ai, item = item_com, depth = constants.DEPTH_CREATURES,
		create_function = "gen_skeleton", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_thief(coords):

	
	x,y = coords
	name = libtcod.namegen_generate("male")
	creature_type = type_humanoid
	creature_com = com_creature(name, level = 1, dexterity = 2, death_function = death_humanoid, raw_damage = 7, creature_type = creature_type,
		attack_function = effects.steal_money, attack_function_occurance = .33)
	ai = ai_chase()
	A_THIEF = "THIEF"

	enemy = actor(x,y, "Thief", A_THIEF, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_thief", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_simple_mage(coords):#t0

	
	x,y = coords
	name = libtcod.namegen_generate("male")
	creature_type = type_humanoid
	creature_com = com_creature(name, level = 2, dexterity = 0, death_function = death_monster, raw_damage = 1, creature_type = creature_type)
	ai = ai_simple_caster(spells.fire_blast, 3, 0, attack_occurence = .5)

	enemy = actor(x,y, "Evil Sage", "MAGE", creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_simple_mage", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_fireman(coords):#t2
	
	x,y = coords
	creature_type = type_demon
	creature_com = com_creature("Fire demon", level = 4, raw_evasion = 2, dexterity = 4, raw_damage = 20, vitality = 12, fire_resistance = 1.25, creature_type = creature_type)
	ai = ai_skiddish()
	A_DEMON = "FIREMAN"

	enemy = actor(x,y, "Fireman", A_DEMON, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_fireman", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_bat(coords):#t0
	
	x,y = coords
	creature_type = type_beast
	creature_com = com_creature("Bat", level = 1, raw_evasion = 0, dexterity = 0, raw_damage = 3,
	 vitality = 2, posion_resistance = 1, creature_type = creature_type, attack_speed = 2, move_speed = 3)
	ai = ai_chase()

	ANIM = "BAT"

	enemy = actor(x,y, "Bat", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_bat", create_function_params = [coords])


	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_dire_bat(coords):#t1
	
	x,y = coords
	creature_type = type_beast
	creature_com = com_creature("Dire Bat", level = 2, raw_evasion = 1, dexterity = 0, raw_damage = 13, vitality = 7, 
		attack_function = effects.dire_bat_posion , attack_function_occurance = .1, posion_resistance = 1, creature_type = creature_type)
	ai = ai_chase()
	ANIM = "DIRE_BAT"

	enemy = actor(x,y, "Dire Bat", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_dire_bat", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_grub(coords):#t0
	
	x,y = coords
	creature_com = com_creature("Grub", level = 1, raw_evasion = 1, dexterity = 0, raw_damage = 4, vitality = 2, creature_type = type_insect)
	ai = ai_chase()
	ANIM = "GRUB"

	enemy = actor(x,y, "Grub", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_grub", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_worm(coords):#t0
	
	x,y = coords
	creature_com = com_creature("Worm", level = 1, raw_evasion = 0, dexterity = 1, raw_damage = 0, vitality = 4, attack_function = effects.worm_latch_on , attack_function_occurance = .35, creature_type = type_insect)
	ai = ai_chase()
	ANIM = "MUNCHER"

	enemy = actor(x,y, "Worm", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_worm", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_devourer(coords):#t1
	
	x,y = coords
	creature_com = com_creature("Devourer", level = 2, raw_evasion = 0, dexterity = 1,
	 raw_damage = 10, vitality = 7, attack_function = effects.worm_latch_on , attack_function_occurance = .5, creature_type = type_insect)
	ai = ai_chase()
	ANIM = "GRUB"

	enemy = actor(x,y, "Grub", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_devourer", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_scorpion(coords):#t1
	
	x,y = coords
	creature_com = com_creature("Scorpion", level = 2, raw_evasion = 0, dexterity = 1, raw_damage = 12, vitality = 4, creature_type = type_insect, attack_function = effects.scorpion_posion , attack_function_occurance = .33)
	ai = ai_chase()
	ANIM = "SCORPION"

	enemy = actor(x,y, "Scorpion", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_scorpion", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_dire_scorpion(coords):#t2
	
	x,y = coords
	creature_com = com_creature("Dire Scorpion", level = 3, raw_evasion = 0, dexterity = 1, raw_damage = 15, vitality = 7,
	 attack_function = effect_scorpion_posion , attack_function_occurance = .5, posion_resistance = .5, creature_type = type_insect)
	ai = ai_chase()
	ANIM = "DIRE_SCORPION"

	enemy = actor(x,y, "Dire Scorpion", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_dire_scorpion", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_wolf(coords):#t1
	
	x,y = coords
	creature_type = type_beast
	creature_com = com_creature("Wolf", level = 2, raw_evasion = 0, dexterity = 1, raw_damage = 25, vitality = 7, creature_type = creature_type)
	ai = ai_chase()
	ANIM = "WOLF"

	enemy = actor(x,y, "Wolf", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_wolf", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_reaper(coords):#t1
	
	x,y = coords
	creature_type = type_undead
	creature_com = com_creature("Reaper", level = 2, raw_evasion = 0, dexterity = 1, raw_damage = 0, vitality = 7,
	 attack_function = effects.reaper_cold_damage , attack_function_occurance = 1, cold_resistance = .25, creature_type = creature_type)
	ai = ai_chase()
	ANIM = "REAPER"

	enemy = actor(x,y, "Reaper", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_reaper", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_wraith(coords):#t2
	
	x,y = coords
	creature_type = type_undead
	creature_com = com_creature("Wraith", level = 3, raw_evasion = 2, dexterity = 1, raw_damage = 0, vitality = 7,
	 attack_function = effects.reaper_cold_damage , attack_function_occurance = 1, cold_resistance = .25, creature_type = creature_type)
	ai = ai_chase()
	ANIM = "WRAITH"

	enemy = actor(x,y, "Wraith", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_wraith", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_spirit(coords):#t2
	
	x,y = coords
	creature_type = type_undead
	creature_com = com_creature("Spirit", level = 3, raw_evasion = 4, dexterity = 1, raw_damage = 12, vitality = 4, creature_type = creature_type)
	ai = ai_chase()
	ANIM = "SPIRIT"

	enemy = actor(x,y, "Spirit", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_spirit", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy

def gen_wanderer(coords):#t2
	
	x,y = coords
	creature_type = type_undead
	creature_com = com_creature("Wanderer", level = 3, raw_evasion = 1, dexterity = 0, raw_damage = 10,
	 vitality = 7, attack_function = effects.reaper_cold_damage , attack_function_occurance = 1, creature_type = creature_type)
	ai = ai_chase()
	ANIM = "WANDERER"

	enemy = actor(x,y, "Wanderer", ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES,
		create_function = "gen_wanderer", create_function_params = [coords])

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	return enemy


def gen_boss_ram_mage(coords):#boss 1

	

	x,y = coords
	name = libtcod.namegen_generate("male") + " (Boss)"
	creature_com = com_creature(name, level = 3, raw_evasion = 1, dexterity = 4, raw_damage = 18, vitality = 20, fire_resistance = 1,
	 death_function = death_ram_boss, creature_type = type_demon)
	ai = ai_ram_boss()
	ANIM = "RAM_MAGE"

	enemy = actor(x,y, name, ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES, height = 2, width = 2, delta_draw_x = -.4, delta_draw_y = -.8)
	enemy.id = GAME.next_id

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	#GAME.current_objects.append(enemy)

	return enemy

def gen_boss_hell_beast(coords):#boss

	

	x,y = coords
	name = " Hell Beast (Boss)"
	creature_com = com_creature(name, level = 3, raw_evasion = 1, dexterity = 4, raw_damage = 12, vitality = 10, fire_resistance = 1,
	 death_function = death_hell_beast_boss, creature_type = type_demon)
	ai = ai_hell_beast()
	ANIM = "HELL_BEAST"

	enemy = actor(x,y, name, ANIM, creature = creature_com, ai = ai, depth = constants.DEPTH_CREATURES, height = 2, width = 2, delta_draw_x = .2, delta_draw_y = -.1)
	enemy.id = GAME.next_id

	if NETWORK_LISTENER:
		enemy.health_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER
		enemy.damage_multiplier = NETWORK_LISTENER.players_in_game * constants.DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER

	GAME.current_objects.append(enemy)

	return None


def gen_player(coords = None):

	global PLAYER, LIB

	if coords:
		x,y = coords

	else:
		x = 0
		y = 0
		coords = (0,0)
		for x1 in range(constants.GAME_TILES_X):
			for y1 in range(constants.GAME_TILES_Y):
				if GAME.current_map[x1][y1][1] and GAME.current_map[x1][y1][1].name == "stair":
					if GAME.current_map[x1][y1][1].leads_to == GAME.previous_level:

						x = x1
						y = y1
						coords = (x, y)
						break

	ca = constants.char_dict[USER_OPTIONS.player_class]

	player_com = com_player()
	#name, vitality, dexterity, strength, intelligence, wisdom, luck, items(string), description
	creature_com1 = com_creature(USER_OPTIONS.player_name, level = 1, death_function = player_death,
	 raw_damage = 0, raw_defense = 0, raw_evasion = 1,
	 vitality = ca[1], dexterity = ca[2], strength = ca[3], intelligence = ca[4], wisdom = ca[5], luck = ca[6], team = 1)

	container_com1 = com_container(10, [])
	A_PLAYER = USER_OPTIONS.get_anim_key()
	char_type = constants.char_dict[USER_OPTIONS.player_class][0]




	PLAYER = actor(x,y, char_type, A_PLAYER, creature = creature_com1, container = container_com1, player_com = player_com, depth = constants.DEPTH_PLAYER,
		create_function = "gen_other_player", create_function_params = [(x,y), USER_OPTIONS.player_class, USER_OPTIONS.player_name + " (other player)"])
	PLAYER.sight_multiplier = 1
	PLAYER.id = GAME.next_id
	GAME.current_objects.append(PLAYER) 

	if USER_OPTIONS.player_class == "CHAR_DRUNK":
		starting_items = []

		starting_items.append(gen_broken_bottle(coords))
		starting_items.append(gen_booze_potion(coords))
		starting_items.append(gen_booze_potion(coords))
		starting_items.append(gen_booze_potion(coords))
		

		for item in starting_items:
			item.id = GAME.next_id
			GAME.current_objects.append(item)
			
			item.item.pickup(PLAYER)

			if item == starting_items[0]:
				item.item.use()

		LIB.rename_potion("potion_booze", "Booze")

		if NETWORK_LISTENER:
			PLAYER.creature.damage_multiplier = min(1/NETWORK_LISTENER.players_in_game, .3)
			PLAYER.creature.health_multiplier = NETWORK_LISTENER.players_in_game * 1
			PLAYER.creature.hp = PLAYER.creature.maxhp




	if USER_OPTIONS.player_class == "CHAR_KNIGHT":
		starting_items = []

		starting_items.append(gen_weapon_sword(coords))
		starting_items.append(gen_armor_chain_mail(coords))

		for item in starting_items:
			item.id = GAME.next_id
			GAME.current_objects.append(item)
			
			item.item.pickup(PLAYER)
			item.item.use()

		if NETWORK_LISTENER:
			PLAYER.creature.damage_multiplier = min(3/NETWORK_LISTENER.players_in_game, .5)
			PLAYER.creature.health_multiplier = NETWORK_LISTENER.players_in_game * .7
			PLAYER.creature.hp = PLAYER.creature.maxhp

	if USER_OPTIONS.player_class == "CHAR_ROUGE":
		starting_items = []

		starting_items.append(gen_weapon_dirk(coords))
		starting_items.append(gen_armor_cloak(coords))
		starting_items.append(gen_map_tools(coords))

		for item in starting_items:
			item.id = GAME.next_id
			GAME.current_objects.append(item)
			
			item.item.pickup(PLAYER)
			item.item.use()

		if NETWORK_LISTENER:
			PLAYER.creature.damage_multiplier = max(NETWORK_LISTENER.players_in_game * .7, 2)
			PLAYER.creature.health_multiplier = 1
			PLAYER.creature.hp = PLAYER.creature.maxhp


	if USER_OPTIONS.player_class == "CHAR_KING":
		starting_items = []

		starting_items.append(gen_weapon_scepter(coords))
		starting_items.append(gen_armor_broken_crown(coords))

		for item in starting_items:
			item.id = GAME.next_id
			GAME.current_objects.append(item)
			
			item.item.pickup(PLAYER)

		if NETWORK_LISTENER:
			PLAYER.creature.damage_multiplier = 1
			PLAYER.creature.health_multiplier = 1
			PLAYER.creature.hp = PLAYER.creature.maxhp
			# leadership buff?
			

	if USER_OPTIONS.player_class == "CHAR_CLERIC":
		starting_items = []

		starting_items.append(gen_candle_stick(coords))
		starting_items.append(gen_sacred_ring(coords))
		starting_items.append(gen_spellbook_holy_light(coords))

		for item in starting_items:
			item.id = GAME.next_id
			GAME.current_objects.append(item)
			
			item.item.pickup(PLAYER)
			item.item.use()

		if NETWORK_LISTENER:
			PLAYER.creature.damage_multiplier = max(NETWORK_LISTENER.players_in_game * .7, 2)
			PLAYER.creature.health_multiplier = 1
			PLAYER.creature.mana_multiplier = 2
			PLAYER.creature.hp = PLAYER.creature.maxhp

	if USER_OPTIONS.player_class == "CHAR_IDIOT":
		starting_items = []

		starting_items.append(gen_gem_diamond(coords))
		starting_items.append(gen_armor_bucket_helmet(coords))
		starting_items.append(gen_spellbook_idiot_speak(coords))

		for item in starting_items:
			item.id = GAME.next_id
			GAME.current_objects.append(item)
			
			item.item.pickup(PLAYER)

			if item.reagent:
				LIB.rename_gem(item.reagent.lib_name, "sparklyie dimund")

			else:
				item.item.use()

		if NETWORK_LISTENER:
			PLAYER.creature.damage_multiplier = 1
			PLAYER.creature.health_multiplier = 1
			PLAYER.creature.hp = PLAYER.creature.maxhp

			# support class?

	if USER_OPTIONS.player_class == "CHAR_WARLOCK":

		starting_items = []

		starting_items.append(gen_spellbook_lightning(coords))
		starting_items.append(gen_spellbook_fireball(coords))
		starting_items.append(gen_spellbook_blood_bolt(coords))

		for item in starting_items:
			item.id = GAME.next_id
			GAME.current_objects.append(item)
			
			item.item.pickup(PLAYER)
			item.item.use()

		if NETWORK_LISTENER:
			PLAYER.creature.damage_multiplier = max(NETWORK_LISTENER.players_in_game * .8, 2)
			PLAYER.creature.health_multiplier = .7
			PLAYER.creature.mana_multiplier = 3
			PLAYER.creature.hp = PLAYER.creature.maxhp





	return None

def gen_other_player(coords = None, player_class = "CHAR_KNIGHT", name = "thomas"):

	

	if coords:
		x,y = coords
	else:
		for x1 in range(constants.GAME_TILES_X):
			for y1 in range(constants.GAME_TILES_Y):
				if GAME.current_map[x1][y1][1] and GAME.current_map[x1][y1][1].name == "stair up":
					x = x1
					y = y1
					coords = (x, y)
					break

	ca = constants.char_dict[player_class]

	player_com = com_player()
	#name, vitality, dexterity, strength, intelligence, wisdom, luck, items(string), description
	creature_com1 = com_creature(name, level = 1, death_function = player_death,
	 raw_damage = 0, raw_defense = 0, raw_evasion = 1,
	 vitality = ca[1], dexterity = ca[2], strength = ca[3], intelligence = ca[4], wisdom = ca[5], luck = ca[6], team = 1)

	container_com1 = com_container(10, [])
	A_PLAYER = constants.char_dict[player_class][0]
	char_type = constants.char_dict[player_class][0]




	player = actor(x,y, char_type, A_PLAYER, creature = creature_com1, container = container_com1, player_com = player_com, depth = constants.DEPTH_PLAYER,
		create_function = "gen_other_player", create_function_params = [None, player_class, name])
	player.sight_multiplier = 1
	player.id = GAME.next_id
	
	return player 

class gen_lib:

	def __init__(self):

		self.gen_dict = {

			"gen_scroll_lightning" : gen_scroll_lightning,
			"gen_scroll_fireball" : gen_scroll_fireball,
			"gen_scroll_confuse" : gen_scroll_confuse,
			"gen_scroll_blind" : gen_scroll_blind,
			"gen_scroll_identify" : gen_scroll_identify,

			"gen_spellbook_lightning" : gen_spellbook_lightning,
			"gen_spellbook_tut_spell" : gen_spellbook_tut_spell,
			"gen_spellbook_plauge_bomb" : gen_spellbook_plauge_bomb,
			"gen_spellbook_fire_blast" : gen_spellbook_fire_blast,
			"gen_spellbook_holy_light" : gen_spellbook_holy_light,
			"gen_spellbook_blood_bolt" : gen_spellbook_blood_bolt,
			"gen_spellbook_fireball" : gen_spellbook_fireball,
			"gen_spellbook_idiot_speak" : gen_spellbook_idiot_speak,

			"gen_gem_diamond" : gen_gem_diamond,
			"gen_gem_amber" : gen_gem_amber,
			"gen_gem_amethyst" : gen_gem_amethyst,
			"gen_gem_aquamarine" : gen_gem_aquamarine,
			"gen_gem_emerald" : gen_gem_emerald,
			"gen_gem_onyx" : gen_gem_onyx,
			"gen_gem_ruby" : gen_gem_ruby,
			"gen_gem_sapphire" : gen_gem_sapphire,

			"gen_gold" : gen_gold,
			"gen_food" : gen_food,
			"gen_map_tools" : gen_map_tools,

			"gen_weapon_toy_sword" : gen_weapon_toy_sword,
			"gen_weapon_scepter" : gen_weapon_scepter,
			"gen_weapon_sword" : gen_weapon_sword,
			"gen_weapon_demon_shank" : gen_weapon_demon_shank,
			"gen_weapon_volatile_sword" : gen_weapon_volatile_sword,
			"gen_weapon_sword_cold" : gen_weapon_sword_cold,
			"gen_weapon_dirk" : gen_weapon_dirk,
			"gen_weapon_pike" : gen_weapon_pike,
			"gen_weapon_scimitar" : gen_weapon_scimitar,
			"gen_weapon_flail" : gen_weapon_flail,
			"gen_weapon_scythe" : gen_weapon_scythe,
			"gen_weapon_executioners_axe" : gen_weapon_executioners_axe,
			"gen_weapon_whip" : gen_weapon_whip,
			"gen_weapon_club" : gen_weapon_club,
			"gen_weapon_halbard" : gen_weapon_halbard,
			"gen_weapon_hammer" : gen_weapon_hammer,
			"gen_broken_bottle" : gen_broken_bottle,
			"gen_candle_stick" : gen_candle_stick,
			"gen_weapon_shield" : gen_weapon_shield,

			"gen_armor_cloak" : gen_armor_cloak,
			"gen_armor_monk_robes" : gen_armor_monk_robes,
			"gen_armor_priest_cassock" : gen_armor_priest_cassock,
			"gen_armor_studded_leather" : gen_armor_studded_leather,
			"gen_armor_chain_mail" : gen_armor_chain_mail,
			"gen_armor_plate_armor" : gen_armor_plate_armor,
			"gen_armor_lead_armor" : gen_armor_lead_armor,
			"gen_armor_chromatic_mail" : gen_armor_chromatic_mail, 
			"gen_armor_broken_crown" : gen_armor_broken_crown,
			"gen_armor_bucket_helmet" : gen_armor_bucket_helmet,

			"gen_sacred_ring" : gen_sacred_ring,
			"gen_arrows" : gen_arrows,
			"gen_bow" : gen_bow,
			"gen_great_bow" : gen_great_bow,
			"gen_heal_potion" : gen_heal_potion,
			"gen_bleach_potion" : gen_bleach_potion,
			"gen_posion_potion" : gen_posion_potion,
			"gen_hot_potion" : gen_hot_potion,
			"gen_full_dmg_hot_potion" : gen_full_dmg_hot_potion,
			"gen_luck_potion" : gen_luck_potion,
			"gen_strength_potion" : gen_strength_potion,
			"gen_dexterity_potion" : gen_dexterity_potion,
			"gen_wisdom_potion" : gen_wisdom_potion,
			"gen_intelligence_potion" : gen_intelligence_potion,
			"gen_fire_resist_potion" : gen_fire_resist_potion,
			"gen_posion_resist_potion" : gen_posion_resist_potion,
			"gen_lightning_resist_potion" : gen_lightning_resist_potion,
			"gen_cold_resist_potion" : gen_cold_resist_potion,
			"gen_all_resist_potion" : gen_all_resist_potion,
			"gen_confused_potion" : gen_confused_potion,
			"gen_control_reverse_potion" : gen_control_reverse_potion,
			"gen_booze_potion" : gen_booze_potion,
			"gen_magic_nullify_potion" : gen_magic_nullify_potion,
			"gen_invincible_potion" : gen_invincible_potion,
			"gen_test_dummy" : gen_test_dummy,
			"gen_skeleton" : gen_skeleton,
			"gen_thief" : gen_thief,
			"gen_simple_mage" : gen_simple_mage,
			"gen_fireman" : gen_fireman,
			"gen_bat" : gen_bat,
			"gen_dire_bat" : gen_dire_bat,
			"gen_grub" : gen_grub,
			"gen_worm" : gen_worm,
			"gen_devourer" : gen_devourer,
			"gen_scorpion" : gen_scorpion,
			"gen_dire_scorpion" : gen_dire_scorpion,
			"gen_wolf" : gen_wolf,
			"gen_reaper" : gen_reaper,
			"gen_wraith" : gen_wraith,
			"gen_spirit" : gen_spirit,
			"gen_wanderer" : gen_wanderer,
			"gen_other_player" : gen_other_player,
			"gen_boss_ram_mage" : gen_boss_ram_mage




		}

def console_make_item(func_name):

	func_lib = gen_lib()

	func = func_lib.gen_dict[func_name]

	new_item = func((PLAYER.x, PLAYER.y))

	GAME.current_objects.append(new_item) 

#### MAP ####
#### MAP ####
#### MAP ####
class gen_map_tunneling():

	def __init__(self):
		pass

	def gen_map(self, old_map_id, next_map_id):

		new_map, list_of_rooms = self.map_dig_rooms()

		(new_map, list_of_rooms) = self.map_stairs(new_map, list_of_rooms, old_map_id, next_map_id)


		(new_map, list_of_rooms) = self.decor_rooms(new_map, list_of_rooms)


		(new_map, list_of_rooms) = self.gen_hidden_room(new_map, list_of_rooms)



		new_map = create_map_lighting(new_map)	

		map_make_fov(new_map)

		map_create_pathfinding()




		self.map_populate(list_of_rooms)

		(new_map, list_of_rooms) = gen_traps(new_map, list_of_rooms)

		return (new_map, list_of_rooms)


	def gen_hidden_room(self, new_map, list_of_rooms):

		for room in list_of_rooms:

			if room != list_of_rooms[0] and room != list_of_rooms[-1]:

				x = room.x - 1
				y = room.y - 1

				w = room.w
				h = room.h

				exits = []

				for i in range(w + 1):
					if new_map[x + i][y][0].block_path == False:
						exits.append((x+i, y))

				for i in range(w + 1):
					if new_map[x + i][y+h+1][0].block_path == False:
						exits.append((x+i, y+h+1))

				for i in range(h + 1):
					if new_map[x][y+i][0].block_path == False:
						exits.append((x, y+i))

				for i in range(h + 1):
					if new_map[x+w+1][y+i][0].block_path == False:
						exits.append((x+w+1, y+i))

				if len(exits) == 1:

					for i in range(2):
						
						rand_x = libtcod.random_get_int(0, x+1, x+w-1)
						rand_y = libtcod.random_get_int(0, y+1, y+h-1)

						if new_map[rand_x][rand_y][1] == None:
							new_map[rand_x][rand_y][1] = tiles.chest(rand_x, rand_y, 1)
					
					exit = exits[0]
					exit_x, exit_y = exit
					side = 0

					if exit_x == x:
						side = 3
						dx = -1
						dy = 0
					elif exit_x == x + w + 1:
						side = 1
						dx = 1
						dy = 0
					elif exit_y == y:
						side = 4
						dx = 0
						dy = 1
					elif exit_y == y + h + 1:
						side = 2
						dx = 0
						dy = -1


					if side == 1:
						x,y = exit

						dx = 1
						dy = 0

						done = False

						for i in range(x, constants.GAME_TILES_X-1):

							if new_map[x+1][y+1][0].block_path == False or new_map[x+1][y-1][0].block_path == False:
								new_map[x][y][0] = GAME.tile_wall(x,y, 0)
								new_map[x][y][0].block_path = False
								new_map[x][y][1] = tiles.hidden_door(x,y, 1)

								break

							x+=dx
							y+=dy

					elif side == 2:
						x,y = exit

						dx = 0
						dy = 1

						done = False

						for i in range(x, constants.GAME_TILES_X-1):

							if new_map[x+1][y-1][0].block_path == False or new_map[x-1][y-1][0].block_path == False:
								new_map[x][y][0] = GAME.tile_wall(x,y, 0)
								new_map[x][y][0].block_path = False
								new_map[x][y][1] = tiles.hidden_door(x,y, 1)
								break

							x+=dx
							y+=dy

					elif side == 3:
						x,y = exit

						dx = -1
						dy = 0

						done = False

						for i in range(x, constants.GAME_TILES_X-1):

							if new_map[x-1][y+1][0].block_path == False or new_map[x-1][y-1][0].block_path == False:
								new_map[x][y][0] = GAME.tile_wall(x,y, 0)
								new_map[x][y][0].block_path = False
								new_map[x][y][1] = tiles.hidden_door(x,y, 1)
								break

							x+=dx
							y+=dy

					elif side == 4:
						x,y = exit

						dx = 0
						dy = -1

						done = False

						for i in range(x, constants.GAME_TILES_X-1):

							if new_map[x+1][y+1][0].block_path == False or new_map[x-1][y+1][0].block_path == False:
								new_map[x][y][0] = GAME.tile_wall(x,y, 0)
								new_map[x][y][0].block_path = False
								new_map[x][y][1] = tiles.hidden_door(x,y, 1)
								break

							x+=dx
							y+=dy

					
					break

		return (new_map, list_of_rooms)

	def map_stairs(self, new_map, list_of_rooms, old_map_id, next_map_id):

		newer_map = new_map

		first_room = list_of_rooms[-1]

		min_x = first_room.x
		min_y = first_room.y

		max_x = first_room.x + first_room.w - 1
		max_y = first_room.y + first_room.h - 1

		stair_x = libtcod.random_get_int(0, min_x, max_x)
		stair_y = libtcod.random_get_int(0, min_y, max_y)

		newer_map[stair_x][stair_y][1] = tiles.stair(stair_x, stair_y, 1)

		newer_map[stair_x][stair_y][1].leads_to = next_map_id
		newer_map[stair_x][stair_y][1].super_layer.append("DOWN_ARROW")


		#

		last_room = list_of_rooms[0]

		stair_x, stair_y = last_room.center


		newer_map[stair_x][stair_y][1] = tiles.stair(stair_x, stair_y, 1)

		newer_map[stair_x][stair_y][1].leads_to = old_map_id
		newer_map[stair_x][stair_y][1].super_layer.append("UP_ARROW")

		return (newer_map, list_of_rooms)

	def decor_rooms(self, new_map, list_of_rooms):

		possible_decor_0 = [(gen_campfire, 20), (gen_shop_keeper, 5), (no_decor, 60), (gen_chest, 15), (gen_shrine, 10), (gen_alter, 5), (gen_pedestal, 5)]

		tier_list = [possible_decor_0]
		tier = GAME.area_level

		rooms_to_do = []

		if len(list_of_rooms) >= 3:
			for room in range(1, len(list_of_rooms) - 2):
				rooms_to_do.append(list_of_rooms[room])
		


		for room_to_do in rooms_to_do:

			total_value = 0
			for decor,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:
				total_value+=amount

			rand_value = libtcod.random_get_int(0, 0, total_value)

			for decor,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:

				rand_value-=amount
				if rand_value <= 0:

					for n in range(10): #try and place decor 10 times
					#pick random coords
						x = libtcod.random_get_int(0, room_to_do.x + 1, room_to_do.x2 - 1)
						y = libtcod.random_get_int(0, room_to_do.y + 1, room_to_do.y2 - 1)

						coords = (x, y)
					#make decor
						new_item = decor(coords, new_map, room_to_do)

					#if decor placed successfully, stop attempting to place it
						if new_item != False: 
							break

					break


		return (new_map, list_of_rooms)

	def map_dig_rooms(self):
		#MAP has 3 levels, floor/walls, map interactables, and particles
		new_map = [ [ [None for z in range(0,constants.GAME_TILES_Z)  ] for y in range(0, constants.GAME_TILES_Y)  ] for x in range(0,constants.GAME_TILES_X) ]

		for x in range(constants.GAME_TILES_X):
			for y in range(constants.GAME_TILES_Y):
				new_map[x][y][0] = GAME.tile_wall(x,y, 0)


		#generate new room
		list_of_rooms = []

		for i in range(constants.MAX_ROOMS):

			w = libtcod.random_get_int(0, constants.ROOM_MIN_WIDTH, constants.ROOM_MAX_WIDTH)
			h = libtcod.random_get_int(0, constants.ROOM_MIN_HEIGHT, constants.ROOM_MAX_HEIGHT)

			x =  libtcod.random_get_int(0, 2, constants.GAME_TILES_X - w - 2)
			y = libtcod.random_get_int(0, 2, constants.GAME_TILES_Y - h - 2)

			new_room = obj_room( (x,y), (w,h) )


			#check for intersects
			failed = False

			for other_room in list_of_rooms:
				if new_room.intersects(other_room):
					failed = True
					break

			if not failed:
				#place
				map_create_room(new_map, new_room)

				current_center = new_room.center

				if len(list_of_rooms) != 0:

					#dig tunnel
					previous_center = list_of_rooms[-1].center

					map_tunnel(new_map, current_center, previous_center)


				list_of_rooms.append(new_room)

		return (new_map, list_of_rooms)

	def map_populate(self, room_list):

		global PLAYER

		for room in room_list:


			rand = libtcod.random_get_int(0, -3, 2)
			util.clamp(rand, 0, 3)
			for i in range(rand):

				x = libtcod.random_get_int(0, room.x + 1, room.x2 - 1)
				y = libtcod.random_get_int(0, room.y + 1, room.y2 - 1)

			
				gen_item((x,y), GAME.area_level, True)

			rand = libtcod.random_get_int(0, -3, 2)
			util.clamp(rand, 0, 2)
			for i in range(rand):

				x = libtcod.random_get_int(0, room.x + 1, room.x2 - 1)
				y = libtcod.random_get_int(0, room.y + 1, room.y2 - 1)

				gen_enemy((x,y), GAME.area_level, True)

class gen_map_cellular_automata():

	def __init__(self):
		pass

	def __init__(self):
		self.level = []

		self.iterations = 1000
		self.neighbors = 4 # number of neighboring walls for this cell to become a wall
		self.wallProbability = 0.6 # the initial probability of a cell becoming a wall, recommended to be between .35 and .55

		self.ROOM_MIN_SIZE = 16 # size in total number of cells, not dimensions
		self.ROOM_MAX_SIZE = 500 # size in total number of cells, not dimensions

		self.smoothEdges = True
		self.smoothing =  1

	def gen_map(self, old_map_id, next_map_id):
		# Creates an empty 2D array or clears existing array

		mapWidth = constants.GAME_TILES_X 
		mapHeight = constants.GAME_TILES_Y 

		self.caves = []

		self.level = [[1
			for y in range(mapHeight)]
				for x in range(mapWidth)]

		self.randomFillMap(mapWidth,mapHeight)
		
		self.createCaves(mapWidth,mapHeight)

		self.getCaves(mapWidth,mapHeight)

		self.rooms = []
		for cave in self.caves:
			self.rooms.append(self.cave_to_room(cave))


		self.connectCaves(mapWidth,mapHeight)

		self.cleanUpMap(mapWidth,mapHeight)
		
		#MAP has 3 levels, floor/walls, map interactables, and particles
		self.new_map = [ [ [self.tile_to_make(x, y, z)  for z in range(3)  ] for y in range(0, constants.GAME_TILES_Y)  ] for x in range(0,constants.GAME_TILES_X) ]


		for room in self.rooms:
			x,y = room.center

			passed = False

			for tile in util.find_radius((x,y), 1):

				x1,y1 = tile

				if self.new_map[x1][y1][0].block_path == False:
					passed = True

			if passed == False:
				self.rooms.remove(room)






		self.make_stairs(old_map_id, next_map_id)

		self.decor_rooms()

		self.map_populate()

		self.new_map = create_map_lighting(self.new_map)	

		map_make_fov(self.new_map)

		map_create_pathfinding()

		return (self.new_map, self.rooms)


	def randomFillMap(self,mapWidth,mapHeight):
		for y in range (1,mapHeight-1):
			for x in range (1,mapWidth-1):
				
				if random.random() >= self.wallProbability:
					self.level[x][y] = 0

	def createCaves(self,mapWidth,mapHeight):
		# ==== Create distinct caves ====
		for i in xrange (0,self.iterations):
			# Pick a random point with a buffer around the edges of the map
			tileX = random.randint(1,mapWidth-2) #(2,mapWidth-3)
			tileY = random.randint(1,mapHeight-2) #(2,mapHeight-3)

			# if the cell's neighboring walls > self.neighbors, set it to 1
			if self.getAdjacentWalls(tileX,tileY) > self.neighbors:
				self.level[tileX][tileY] = 1
			# or set it to 0
			elif self.getAdjacentWalls(tileX,tileY) < self.neighbors:
				self.level[tileX][tileY] = 0

		# ==== Clean Up Map ====
		self.cleanUpMap(mapWidth,mapHeight)

	def cleanUpMap(self,mapWidth,mapHeight):
		if (self.smoothEdges):
			for i in xrange (0,5):
				# Look at each cell individually and check for smoothness
				for x in range(1,mapWidth-1):
					for y in range (1,mapHeight-1):
						if (self.level[x][y] == 1) and (self.getAdjacentWallsSimple(x,y) <= self.smoothing):
							self.level[x][y] = 0

	def createTunnel(self,point1,point2,currentCave,mapWidth,mapHeight):
		# run a heavily weighted random Walk 
		# from point1 to point1
		drunkardX = point2[0]
		drunkardY = point2[1]
		while (drunkardX,drunkardY) not in currentCave:
			# ==== Choose Direction ====
			north = 1.0
			south = 1.0
			east = 1.0
			west = 1.0

			weight = 1

			# weight the random walk against edges
			if drunkardX < point1[0]: # drunkard is left of point1
				east += weight
			elif drunkardX > point1[0]: # drunkard is right of point1
				west += weight
			if drunkardY < point1[1]: # drunkard is above point1
				south += weight
			elif drunkardY > point1[1]: # drunkard is below point1
				north += weight

			# normalize probabilities so they form a range from 0 to 1
			total = north+south+east+west
			north /= total
			south /= total
			east /= total
			west /= total

			# choose the direction
			choice = random.random()
			if 0 <= choice < north:
				dx = 0
				dy = -1
			elif north <= choice < (north+south):
				dx = 0
				dy = 1
			elif (north+south) <= choice < (north+south+east):
				dx = 1
				dy = 0
			else:
				dx = -1
				dy = 0

			# ==== Walk ====
			# check colision at edges
			if (0 < drunkardX+dx < mapWidth-1) and (0 < drunkardY+dy < mapHeight-1):
				drunkardX += dx
				drunkardY += dy
				if self.level[drunkardX][drunkardY] == 1:
					self.level[drunkardX][drunkardY] = 0

	def getAdjacentWallsSimple(self, x, y): # finds the walls in four directions
		wallCounter = 0
		
		if (self.level[x][y-1] == 1): # Check north
			wallCounter += 1
		if (self.level[x][y+1] == 1): # Check south
			wallCounter += 1
		if (self.level[x-1][y] == 1): # Check west
			wallCounter += 1
		if (self.level[x+1][y] == 1): # Check east
			wallCounter += 1

		return wallCounter

	def getAdjacentWalls(self, tileX, tileY): # finds the walls in 8 directions
		pass
		wallCounter = 0
		for x in range (tileX-1, tileX+2):
			for y in range (tileY-1, tileY+2):
				if (self.level[x][y] == 1):
					if (x != tileX) or (y != tileY): # exclude (tileX,tileY)
						wallCounter += 1
		return wallCounter

	def getCaves(self, mapWidth, mapHeight):
		# locate all the caves within self.level and stor them in self.caves
		for x in range (0,mapWidth):
			for y in range (0,mapHeight):
				if self.level[x][y] == 0:
					self.floodFill(x,y)

		for set in self.caves:
			for tile in set:
				self.level[tile[0]][tile[1]] = 0

		# check for 2 that weren't changed.
		'''
		The following bit of code doesn't do anything. I 
		put this in to help find mistakes in an earlier 
		version of the algorithm. Still, I don't really 
		want to remove it.
		'''
		for x in range (0,mapWidth):
			for y in range (0,mapHeight):
				if self.level[x][y] == 2:
					print("(",x,",",y,")")

	def floodFill(self,x,y):
		'''
		flood fill the separate regions of the level, discard
		the regions that are smaller than a minimum size, and 
		create a reference for the rest.
		'''
		cave = set()
		tile = (x,y)
		toBeFilled = set([tile])
		while toBeFilled:
			tile = toBeFilled.pop()
			
			if tile not in cave:
				cave.add(tile)
				
				self.level[tile[0]][tile[1]] = 1
				
				#check adjacent cells
				x = tile[0]
				y = tile[1]
				north = (x,y-1)
				south = (x,y+1)
				east = (x+1,y)
				west = (x-1,y)
				
				for direction in [north,south,east,west]:
	
					if self.level[direction[0]][direction[1]] == 0:
						if direction not in toBeFilled and direction not in cave:
							toBeFilled.add(direction)

		if len(cave) >= self.ROOM_MIN_SIZE:
			self.caves.append(cave)

	def connectCaves(self, mapWidth, mapHeight):
		# Find the closest cave to the current cave
		for currentCave in self.caves:
			for point1 in currentCave: break # get an element from cave1
			point2 = None
			distance = None
			for nextCave in self.caves:
				if nextCave != currentCave and not self.checkConnectivity(currentCave,nextCave):
					# choose a random point from nextCave
					for nextPoint in nextCave: break # get an element from cave1
					# compare distance of point1 to old and new point2
					newDistance = self.distanceFormula(point1,nextPoint)
					if (newDistance < distance) or distance == None:
						point2 = nextPoint
						distance = newDistance

			if point2: # if all tunnels are connected, point2 == None
				self.createTunnel(point1,point2,currentCave,mapWidth,mapHeight)

	def distanceFormula(self,point1,point2):
		d = sqrt( (point2[0]-point1[0])**2 + (point2[1]-point1[1])**2)
		return d

	def checkConnectivity(self,cave1,cave2):
		# floods cave1, then checks a point in cave2 for the flood

		connectedRegion = set()
		for start in cave1: break # get an element from cave1
		
		toBeFilled = set([start])
		while toBeFilled:
			tile = toBeFilled.pop()

			if tile not in connectedRegion:
				connectedRegion.add(tile)

				#check adjacent cells
				x = tile[0]
				y = tile[1]
				north = (x,y-1)
				south = (x,y+1)
				east = (x+1,y)
				west = (x-1,y)

				for direction in [north,south,east,west]:
	
					if self.level[direction[0]][direction[1]] == 0:
						if direction not in toBeFilled and direction not in connectedRegion:
							toBeFilled.add(direction)

		for end in cave2: break # get an element from cave2

		if end in connectedRegion: return True

		else: return False

	def tile_to_make(self, x, y, z):

		if z == 0:

			if x == 0 or x == constants.GAME_TILES_X - 2:
				return GAME.tile_wall(x,y, 0)

			elif y == 0 or y == constants.GAME_TILES_Y - 2:
				return GAME.tile_wall(x,y, 0)

			elif self.level[x][y] == 1:
				return GAME.tile_wall(x,y, 0)

			else:
				return GAME.tile_floor(x,y, 0)

		else:
			return None

	def cave_to_room(self, cave_tiles):

		min_x = -1
		max_x = -1

		min_y = -1
		max_y = -1
		
		for x,y in cave_tiles:

			if x < min_x:
				min_x = x

			elif x > max_x:
				max_x = x


			if y < min_y:
				min_y = y

			elif y > max_y:
				max_y = y


		room = obj_room((min_x, min_y), (max_x - min_x, max_y - min_y) )

		return room

	def make_stairs(self, old_map_id, next_map_id):

		self.bad_tiles = []

		

		done = False
		while done == False:

			x = libtcod.random_get_int(0, 1, constants.GAME_TILES_X - 1)
			y = libtcod.random_get_int(0, 1, constants.GAME_TILES_Y - 1)

			if self.new_map[x][y][0].block_path == False:
				self.new_map[x][y][1] = tiles.stair(x,y, 1)
				self.new_map[x][y][1].leads_to = old_map_id
				PLAYER.x = x
				PLAYER.y = y
				self.bad_tiles.append(util.find_radius((x,y), 1))
				done = True

		done = False
		while done == False:

			x1 = libtcod.random_get_int(0, 1, constants.GAME_TILES_X - 1)
			y1 = libtcod.random_get_int(0, 1, constants.GAME_TILES_Y - 1)

			if self.new_map[x1][y1][0].block_path == False and len(util.find_line((x,y), (x1,y1))) > 8:
				self.new_map[x1][y1][1] = tiles.stair(x1,y1, 1)
				self.new_map[x1][y1][1].leads_to = old_map_id
				self.bad_tiles.append(util.find_radius((x1,y1), 1))
				done = True


		


	def decor_rooms(self):

		new_map = self.new_map
		list_of_rooms = self.rooms

		possible_decor_0 = [(gen_campfire, 20), (gen_shop_keeper, 5), (no_decor, 10), (gen_chest, 15)]

		tier_list = [possible_decor_0]
		tier = GAME.area_level


		for i in range(7):		

			done = False
			while done == False:

				x = libtcod.random_get_int(0, 1, constants.GAME_TILES_X - 1)
				y = libtcod.random_get_int(0, 1, constants.GAME_TILES_Y - 1)

				good = True
				for tile in util.find_radius((x,y), 1):
					for bad_tile in self.bad_tiles:
						if tile == bad_tile:
							good = False

				if self.new_map[x][y][0].block_path == False and good == True:
					coords = (x,y)
					done = True


			total_value = 0
			for decor,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:
				total_value+=amount

			rand_value = libtcod.random_get_int(0, 0, total_value)

			for decor,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:

				rand_value-=amount
				if rand_value <= 0:
					x,y = coords
					new_item = decor(coords, self.new_map, obj_room((x-3, y-3), (6,6)) )
					break


		return (new_map, list_of_rooms)

	def map_populate(self):

		global PLAYER

		room_list = self.rooms

		rand = libtcod.random_get_int(0, 8, 12)
		for i in range(rand):		

			done = False
			while done == False:

				x = libtcod.random_get_int(0, 1, constants.GAME_TILES_X - 1)
				y = libtcod.random_get_int(0, 1, constants.GAME_TILES_Y - 1)

				if self.new_map[x][y][0].block_path == False and self.new_map[x][y][1] == None:
					gen_item((x,y), GAME.area_level)
					done = True
				

		rand = libtcod.random_get_int(0, 8, 12)
		for i in range(rand):		

			done = False
			while done == False:

				x = libtcod.random_get_int(0, 1, constants.GAME_TILES_X - 1)
				y = libtcod.random_get_int(0, 1, constants.GAME_TILES_Y - 1)

				if self.new_map[x][y][0].block_path == False and self.new_map[x][y][1] == None:
					gen_enemy((x,y), GAME.area_level)
					done = True


		
#  __  __          _____ _____ _____   _____  _____   ____  _____  ______ _____ _______ _____ ______  _____ 
# |  \/  |   /\   / ____|_   _/ ____| |  __ \|  __ \ / __ \|  __ \|  ____|  __ \__   __|_   _|  ____|/ ____|
# | \  / |  /  \ | |  __  | || |      | |__) | |__) | |  | | |__) | |__  | |__) | | |    | | | |__  | (___  
# | |\/| | / /\ \| | |_ | | || |      |  ___/|  _  /| |  | |  ___/|  __| |  _  /  | |    | | |  __|  \___ \ 
# | |  | |/ ____ \ |__| |_| || |____  | |    | | \ \| |__| | |    | |____| | \ \  | |   _| |_| |____ ____) |
# |_|  |_/_/    \_\_____|_____\_____| |_|    |_|  \_\\____/|_|    |______|_|  \_\ |_|  |_____|______|_____/ 
                                                                                                           
def roll_magic_weapon(item):

	roll = libtcod.random_get_int(0, 0, 100)
	if PLAYER:
		roll += int(3*sqrt(PLAYER.creature.luck))

	if roll > (100 - constants.MAGIC_CHANCE):

		tier_list = [PREFIX_WEAPONS_0]

		rand = libtcod.random_get_int(0, 1, 10)

		tier = GAME.area_level

		if rand == 10:
			tier -= 2

		elif rand >= 7:
			tier -= 1

		total_value = 0
		for affix,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:
			total_value+=amount

		rand_value = libtcod.random_get_int(0, 0, total_value)

		for affix,amount in tier_list[util.clamp(tier, 0, len(tier_list) - 1)]:

			rand_value-=amount

			if rand_value <= 0:
				if item.equipment:
					affix(item)


				error_message("FIX AFFIXES FOR NETWORK_LISTENER")

				break
		



def prefix_sharp(item):

	if item.equipment:
		damage_bonus = 1

		item.item.identify_name = "Sharp " + item.name

		item.item.tooltip_lines.append("damage increased by: " + str(damage_bonus))

		try:
			item.equipment.attack_max_bonus += damage_bonus
			item.equipment.attack_min_bonus += damage_bonus
		except:
			pass

def prefix_berserkers(item):

	if item.equipment:
		damage_bonus = 2

		item.item.identify_name = "Berserker's " + item.name

		item.item.tooltip_lines.append("min damage reduced by: " + str(damage_bonus))
		item.item.tooltip_lines.append("max damage increased by: " + str(damage_bonus))

		try:
			item.equipment.attack_max_bonus += damage_bonus
			item.equipment.attack_min_bonus -= damage_bonus
		except:
			pass

def prefix_marksman(item):

	if item.equipment:

		item.item.identify_name = "Marksman's " + item.name

		accuracy_bonus = 2

		item.item.tooltip_lines.append("hit chance increased by: " + str(accuracy_bonus))

		item.equipment.hit_chance_bonus += accuracy_bonus

def prefix_simpleton(item):

	if item.equipment:

		item.item.identify_name = "Simpleton's " + item.name

		if item.equipment.strength_req > 0:
			item.equipment.strength_req -= 1

		if item.equipment.dexterity_req > 0:
			item.equipment.dexterity_req -= 1

		accuracy_bonus = -1
		min_bonus = -1

		item.item.tooltip_lines.append("reduced requirements")
		item.item.tooltip_lines.append("min damage increased by: " + str(min_bonus))
		item.item.tooltip_lines.append("hit chance increased by: " + str(accuracy_bonus))

		if item.equipment.hit_chance_bonus:
			item.equipment.hit_chance_bonus += accuracy_bonus
		if item.equipment.attack_min_bonus:
			item.equipment.attack_min_bonus += min_bonus




#  _    _ _____      _____ _                _____ _____ ______  _____ 
# | |  | |_   _|    / ____| |        /\    / ____/ ____|  ____|/ ____|
# | |  | | | |     | |    | |       /  \  | (___| (___ | |__  | (___  
# | |  | | | |     | |    | |      / /\ \  \___ \\___ \|  __|  \___ \ 
# | |__| |_| |_    | |____| |____ / ____ \ ____) |___) | |____ ____) |
#  \____/|_____|    \_____|______/_/    \_\_____/_____/|______|_____/ 
                                                                     
     
class ui_button:

	def __init__(self, surface, coords, size, text, click_function = None, click_function_params = None,
	 text_color = constants.COLOR_RED, color_box = constants.COLOR_GREY,
	  color_mouseover = constants.COLOR_LIGHT_GREY, pos_from_center = False, font = "FONT_MENU", sprite = None):

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

		global MOUSE_CLICKED

	

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
		else:

			pygame.draw.rect(self.surface, color, self.rect)
			util.draw_text(self.surface, self.text, self.rect.center, self.text_color, center = True, font = self.font)

		if self.is_highlighted == True:
			if MOUSE_CLICKED == True:

				MOUSE_CLICKED = False

				if self.click_function:
					
					if self.click_function == "RETURN":

						return "END"

					elif self.click_function_params:
						self.click_function(*self.click_function_params)


					else:
						self.click_function()


					return "END"
				else:
					return "END"




		return None

class ui_slider:

	def __init__(self, surface, coords, size, fill = .5, bg_color = constants.COLOR_LIGHT_GREY, fg_color = constants.COLOR_RED,
	 pos_from_center = False, text = "", draw_percent_text = True):

		self.surface = surface
		self.coords = coords
		self.size = size
		self.bg_color = bg_color
		self.fg_color = fg_color
		self.pos_from_center = pos_from_center
		self.fill = fill
		self.text = text
		self.draw_percent_text = draw_percent_text

		if self.text != "":
			self.text = self.text + ": "
		
		self.bg_rect = pygame.Rect((0,0), size)
		self.bg_rect.center = coords

		self.fg_rect = pygame.Rect((0,0), (self.bg_rect.width * self.fill, self.bg_rect.height))
		self.fg_rect.topleft = self.bg_rect.topleft

		if self.pos_from_center == True:
			self.bg_rect.center = self.center(coords)
			self.fg_rect.center = self.center(coords)

			w, h = self.size
			x, y = self.bg_rect.center
			x -= w/2
			y -= h/2

			self.coords = (x,y)

	@property
	def is_highlighted(self):

		x, y = self.coords
		w,h = self.size

		buffer = 20
		return (mouse_in_window(x-buffer, y, w+2*buffer, h) != None)

	def center(self, coords):

		x,y = coords

		x += constants.CAMERA_WIDTH/2
		y += constants.CAMERA_HEIGHT/2

		return (x,y)

	def update(self):

		mouse_down = pygame.mouse.get_pressed()[0]

		mouse_x, mouse_y = pygame.mouse.get_pos()

		if self.is_highlighted and mouse_down:

			dis = (mouse_x - self.bg_rect.left)
			width = (self.bg_rect.width)

			self.fill = util.clamp((float(mouse_x) - float(self.bg_rect.left)) / self.bg_rect.w, 0, 1)
			

			self.fg_rect.width =  self.bg_rect.width * self.fill

		return self.fill


			

	def draw(self):

		pygame.draw.rect(self.surface, self.bg_color, self.bg_rect)
		self.fg_rect.topleft = self.bg_rect.topleft
		pygame.draw.rect(self.surface, self.fg_color, self.fg_rect)

		if self.draw_percent_text:
			util.draw_text(self.surface, self.text + str(int(self.fill * 100)), self.bg_rect.center, constants.COLOR_BLUE, center = True)

		else:
			util.draw_text(self.surface, self.text, self.bg_rect.center, constants.COLOR_BLUE, center = True)

		
		

		return None

class ui_inputbox:

    def __init__(self, x, y, w, h, text='', pos_from_center = False, back_color = constants.COLOR_BLACK):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = constants.COLOR_LIGHT_GREY
        self.text = text
        self.txt_surface = constants.FONT_DEFAULT.render(text, True, self.color)
        self.active = False
        self.pos_from_center = pos_from_center
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.back_surface = pygame.Surface((w - 20, h))
        self.back_surface.fill(back_color)


        if self.pos_from_center == True:


			x += constants.CAMERA_WIDTH/2
			y += constants.CAMERA_HEIGHT/2

			self.rect.center = (x,y)

			x -= w/2
			y -= h/2

			self.x = x
			self.y = y

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
                    
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                # Re-render the text.
                self.txt_surface = constants.FONT_DEFAULT.render(self.text, True, self.color)

    def update(self):
        # Resize the box if the text is too long.
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
		screen.blit(self.back_surface, (self.rect.x, self.rect.y))
		pygame.draw.rect(screen, self.color, self.rect, 2)
		# Blit the text.
		screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y))
		# Blit the rect.
        

#  _____ _   _ _______ ______ _____  ______      _____ ______ 
# |_   _| \ | |__   __|  ____|  __ \|  ____/\   / ____|  ____|
#   | | |  \| |  | |  | |__  | |__) | |__ /  \ | |    | |__   
#   | | | . ` |  | |  |  __| |  _  /|  __/ /\ \| |    |  __|  
#  _| |_| |\  |  | |  | |____| | \ \| | / ____ \ |____| |____ 
# |_____|_| \_|  |_|  |______|_|  \_\_|/_/    \_\_____|______|


def main_menu(message = None, restart_music = False):

	menu_running = True

	offset = 20
	spacer = 60

	new_game_button = ui_button(SURFACE_MAIN, (0,-2*spacer+offset), (270,50), "New Game", pos_from_center = True, click_function = class_selection_menu)
	multiplayer_button = ui_button(SURFACE_MAIN, (0,0*spacer+offset), (270,50), "Multiplayer", pos_from_center = True, click_function = "RETURN")
	quit_button = ui_button(SURFACE_MAIN, (0,2*spacer+offset), (270,50), "Quit", pos_from_center = True, click_function = quit_game)
	load_button = ui_button(SURFACE_MAIN, (0,-1*spacer+offset), (270,50), "Load Game", pos_from_center = True, click_function = game_try_load)
	options_button = ui_button(SURFACE_MAIN, (0,1*spacer+offset), (270,50), "Options", pos_from_center = True, click_function = main_menu_options)

	#rand = libtcod.random_get_int(0, 0, len(constants.TITLE_SCREEN) - 1)

	background = constants.TITLE_SCREEN[0]

	if restart_music == True and USER_OPTIONS.play_music == True:
		pygame.mixer.music.load(constants.MUSIC[0])
		pygame.mixer.music.play(-1)

	center_x = constants.CAMERA_WIDTH/2
	center_y = constants.CAMERA_HEIGHT/2

	title_width = util.helper_text_width(constants.GAME_TITLE, "FONT_TITLE")
	title_height = util.helper_text_height("FONT_TITLE")

	c_x = constants.CAMERA_WIDTH/2
	b_y = constants.CAMERA_HEIGHT - 20
	line = 3
	line_height = 20
	line_color = constants.COLOR_ORANGE
	
	SURFACE_MAIN.blit(background, (0, 0) )
	quit_button.draw()
	new_game_button.draw()
	load_button.draw()
	options_button.draw()
	multiplayer_button.draw()

	util.draw_text(SURFACE_MAIN, "Game made by Thomas Downes", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True)
	line-= 1
	util.draw_text(SURFACE_MAIN, "most of the art comes from free sources on the internet", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True)
	line-= 1
	util.draw_text(SURFACE_MAIN, "credits and sources available in the _Credits.txt file in Data folder", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True)
	SURFACE_MAIN.blit(constants.S_TITLE, ((20, 30)))

	pygame.display.flip()

	for mod in GAME_MODS:
		try:
			mod.menu_start()
		except:
			pass

	while menu_running:

		list_of_events = pygame.event.get()

		for event in list_of_events:

			global MOUSE_CLICKED

			if event.type == pygame.QUIT:
				quit_game()

			MOUSE_CLICKED = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
					#return ("CLICK")
			if event.type == pygame.KEYDOWN:

				if event.key == pygame.K_EQUALS:
					open_console_main_menu()

		#draw menu
		SURFACE_MAIN.blit(background, (0, 0) )

		if quit_button.draw() : menu_running = False

		if new_game_button.draw() : menu_running = False

		if load_button.draw() : menu_running = False

		if options_button.draw() : menu_running = False

		if multiplayer_button.draw() and multiplayer_button.text != "Connected" :
			multiplayer_init()
			multiplayer_button.text = "Connecting..."
			SURFACE_MAIN.blit(constants.S_DARK_FILL, (0,0))
			multiplayer_button.draw()
			
			pygame.display.flip()

			attempts = 20
			mp_done = False
			test_delay_spacer = .5
			while mp_done == False:
				attempts -= 1
				connection.Pump()
				NETWORK_LISTENER.Pump()

				if NETWORK_LISTENER.id:
					mp_done = True
					multiplayer_button.text = "Connected"
					multiplayer_button.color_mouseover = (30,30,30)
					multiplayer_button.color_box = (30,30,30)

				else:
					sleep(.1)

				if attempts <= 0:
					mp_done = True
					multiplayer_button.text = "Failed"


		util.draw_text(SURFACE_MAIN, message, (0,0), constants.COLOR_RED, font = "FONT_MENU", center = True)

		

		#util.draw_text(SURFACE_MAIN, constants.GAME_TITLE, (center_x - title_width/2, 100), constants.COLOR_RED, font = "FONT_TITLE")

		center_x = constants.CAMERA_WIDTH/2
		center_y = constants.CAMERA_HEIGHT/2

		title_width = util.helper_text_width(constants.GAME_TITLE, "FONT_TITLE")
		title_height = util.helper_text_height("FONT_TITLE")

		c_x = constants.CAMERA_WIDTH/2
		b_y = constants.CAMERA_HEIGHT - 20
		line = 3
		line_height = 20
		line_color = constants.COLOR_ORANGE


		bg = constants.COLOR_BLACK

		util.draw_text(SURFACE_MAIN, "Game made by Thomas Downes", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True, back_color = bg)
		line-= 1
		util.draw_text(SURFACE_MAIN, "most of the art comes from free sources on the internet", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True, back_color = bg)
		line-= 1
		util.draw_text(SURFACE_MAIN, "credits and sources available in the _Credits.txt file in Data folder", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True, back_color = bg)

		SURFACE_MAIN.blit(constants.S_TITLE, ((20, 30)))

		#update
		pygame.display.update()

		if NETWORK_LISTENER:
			connection.Pump()
			NETWORK_LISTENER.Pump()

def main_menu_options():

	global USER_OPTIONS

	menu_running = True

	new_button = ui_button(SURFACE_MAIN, (0,-80), (220,50), "Key Binds", pos_from_center = True, click_function = main_menu_key_binds)
	back_button = ui_button(SURFACE_MAIN, (0,80), (220,50), "back", pos_from_center = True, click_function = main_menu)
	sound_slider = ui_slider(SURFACE_MAIN, (0,0), (150,20), pos_from_center = True, fill = USER_OPTIONS.music_volume, text = "Music Volume")
	#options_button = ui_button(SURFACE_MAIN, (0,80), (220,50), "Options", pos_from_center = True, click_function = None)

	background = constants.TITLE_SCREEN[0]

	while menu_running:

		list_of_events = pygame.event.get()

		for event in list_of_events:

			global MOUSE_CLICKED

			if event.type == pygame.QUIT:
				quit_game()

			MOUSE_CLICKED = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
					#return ("CLICK")

		SURFACE_MAIN.blit(background, (0, 0) )

		if new_button.draw() : menu_running = False

		if back_button.draw() : menu_running = False


		USER_OPTIONS.music_volume = sound_slider.update()
		USER_OPTIONS.sound_adjust()
		sound_slider.draw()


		c_x = constants.CAMERA_WIDTH/2
		b_y = constants.CAMERA_HEIGHT - 20
		line = 3
		line_height = 20
		line_color = constants.COLOR_ORANGE

		util.draw_text(SURFACE_MAIN, "Game made by Thomas Downes", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True)
		line-= 1
		util.draw_text(SURFACE_MAIN, "sound and music stolen from the internet", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True)
		line-= 1
		util.draw_text(SURFACE_MAIN, "art mostly stolen from the internet, I made a few tiles myself", (c_x,b_y - line*line_height), line_color, font = "FONT_MAIN_16", center = True)

		#update
		pygame.display.update()

def main_menu_key_binds():

	global USER_OPTIONS

	menu_running = True

	back_button = ui_button(SURFACE_MAIN, (0,80), (220,50), "back", pos_from_center = True, click_function = main_menu_options)

	background = constants.TITLE_SCREEN[0]

	menu_font = "FONT_MAIN_18"
	buff = 3
	line_height = util.helper_text_height(menu_font) + buff

	start_x = constants.CAMERA_WIDTH/2
	start_y = 50

	c_x = constants.CAMERA_WIDTH/2
	b_y = constants.CAMERA_HEIGHT - 20
	line = 3
	line_height_2 = 20
	line_color = constants.COLOR_ORANGE

	while menu_running:

		list_of_events = pygame.event.get()

		GAME_EVENT_LIST = list_of_events

		for event in list_of_events:

			global MOUSE_CLICKED

			if event.type == pygame.QUIT:
				quit_game()

			MOUSE_CLICKED = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
					#return ("CLICK")

		SURFACE_MAIN.blit(background, (0, 0) )

		if back_button.draw() : menu_running = False

		mouse_line_selection = 0


		lines = [

			"Move Up : " + USER_OPTIONS.key_w.upper(),
			"Move Down : " + USER_OPTIONS.key_s.upper(),
			"Move Left : " + USER_OPTIONS.key_a.upper(),
			"Move Right : " + USER_OPTIONS.key_d.upper(),

			"Pass Turn : " + USER_OPTIONS.key_rest.upper(),

			"Interact : " + USER_OPTIONS.key_interact.upper(),
			"Toggle Map (If Available) : " + USER_OPTIONS.key_map.upper(),
			"Drop : " + USER_OPTIONS.key_drop.upper(),
			"Look : " + USER_OPTIONS.key_look.upper(),

		]

		

		#draw lines 

		# due to being unable to pass variables by reference in python...
		# each of these has to have its own code in order to change the correct key in user options
		line = 0
		#up
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_w = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#down
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_s = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#left
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_a = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#right
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_d = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#pass
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_rest = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#interact
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_interact = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#map
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_map = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#drop
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_drop = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1

		#look
		if mouse_in_window(0, start_y - 10 + line * line_height, constants.CAMERA_WIDTH, line_height):
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height - 5), constants.COLOR_WHITE, font = menu_font, center = True, back_color = constants.COLOR_DARK_GREY)
			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:
					if USER_OPTIONS.key_is_bound(event.unicode) == False:
						USER_OPTIONS.key_look = event.unicode
		else:
			util.draw_text(SURFACE_MAIN, lines[line], (start_x, start_y + line*line_height), constants.COLOR_WHITE, font = menu_font, center = True)
		line += 1


		line = 3

		util.draw_text(SURFACE_MAIN, "Game made by Thomas Downes", (c_x,b_y - line*line_height_2), line_color, font = "FONT_MAIN_16", center = True)
		line-= 1
		util.draw_text(SURFACE_MAIN, "sound and music stolen from the internet", (c_x,b_y - line*line_height_2), line_color, font = "FONT_MAIN_16", center = True)
		line-= 1
		util.draw_text(SURFACE_MAIN, "art mostly stolen from the internet, I made a few tiles myself", (c_x,b_y - line*line_height_2), line_color, font = "FONT_MAIN_16", center = True)

		#update
		pygame.display.update()

def load_tutorial():
	message_box("Use WASD keys to move...")
	load_map()

def class_selection_menu():

	done = False

	global MOUSE_CLICKED, USER_OPTIONS

	back_button = ui_button(SURFACE_MAIN, (-80,80), (150,40), "Back", pos_from_center = True, click_function = main_menu)
	name_box = ui_inputbox(0, 0, 220, 20, text=USER_OPTIONS.player_name, pos_from_center = True)
	new_game_button = ui_button(SURFACE_MAIN, (80,80), (150,40), "Start", pos_from_center = True, click_function = "RETURN")
	knight_button = ui_button(SURFACE_MAIN, (-180,-60), (50,50), " ", click_function = "RETURN", pos_from_center = True, sprite = constants.S_KNIGHT)
	cleric_button = ui_button(SURFACE_MAIN, (-120,-60), (50,50), " ", click_function = "RETURN", pos_from_center = True, sprite = constants.S_CLERIC)
	drunk_button = ui_button(SURFACE_MAIN, (-60,-60), (50,50), " ", click_function = "RETURN", pos_from_center = True, sprite = constants.S_DRUNK)
	warlock_button = ui_button(SURFACE_MAIN, (0,-60), (50,50), " ", click_function = "RETURN", pos_from_center = True, sprite = constants.S_WARLOCK)
	idiot_button = ui_button(SURFACE_MAIN, (60,-60), (50,50), " ", click_function = "RETURN", pos_from_center = True, sprite = constants.S_IDIOT)
	rouge_button = ui_button(SURFACE_MAIN, (120,-60), (50,50), " ", click_function = "RETURN", pos_from_center = True, sprite = constants.S_ROUGE)
	king_button = ui_button(SURFACE_MAIN, (180,-60), (50,50), " ", click_function = "RETURN", pos_from_center = True, sprite = constants.S_KING)

	classbuttons = [knight_button, cleric_button, drunk_button, warlock_button, idiot_button, rouge_button, king_button]

	background = constants.TITLE_SCREEN[0]

	current_selection = USER_OPTIONS.player_class

	for button in classbuttons:
		if constants.char_dict[current_selection][11] == button.sprite:
			button.color_box = constants.COLOR_RED


	start_game = False

	while done == False:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit_game()

			name_box.handle_event(event)

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True

		name_box.update()

		SURFACE_MAIN.blit(background, (0, 0) )
		name_box.draw(SURFACE_MAIN)
		if back_button.draw() : done = True
		if new_game_button.draw() :
			done = True
			start_game = True
		if knight_button.draw() :
			current_selection = "CHAR_KNIGHT" 
			for button in classbuttons:
				button.color_box = constants.COLOR_GREY
			knight_button.color_box = constants.COLOR_RED

		if cleric_button.draw() : 
			current_selection = "CHAR_CLERIC"
			for button in classbuttons:
				button.color_box = constants.COLOR_GREY
			cleric_button.color_box = constants.COLOR_RED

		if drunk_button.draw() : 
			current_selection = "CHAR_DRUNK"
			for button in classbuttons:
				button.color_box = constants.COLOR_GREY
			drunk_button.color_box = constants.COLOR_RED

		if warlock_button.draw() : 
			current_selection = "CHAR_WARLOCK"
			for button in classbuttons:
				button.color_box = constants.COLOR_GREY
			warlock_button.color_box = constants.COLOR_RED

		if idiot_button.draw() : 
			current_selection = "CHAR_IDIOT"
			for button in classbuttons:
				button.color_box = constants.COLOR_GREY
			idiot_button.color_box = constants.COLOR_RED

		if rouge_button.draw() : 
			current_selection = "CHAR_ROUGE"
			for button in classbuttons:
				button.color_box = constants.COLOR_GREY
			rouge_button.color_box = constants.COLOR_RED

		if king_button.draw() : 
			current_selection = "CHAR_KING"
			for button in classbuttons:
				button.color_box = constants.COLOR_GREY
			king_button.color_box = constants.COLOR_RED

		#display current selection data
		x = constants.CAMERA_WIDTH/2
		y = constants.MENU_BUFFER * 3

		line_spacer = 25
		line_num = 0
		char = constants.char_dict[current_selection]
		color = constants.COLOR_WHITE
		bg = constants.COLOR_BLACK

         #name, vitality, dexterity, strength, intelligence, wisdom, luck, items(string), description
		line1 = " " + str(char[0]) + " "
		line2 = " " + "Vitality:" + str(char[1]) + ", Dexterity:" + str(char[2]) + ", Strength:" + str(char[3]) + " "
		line3 = " " + "Intelligence:" + str(char[4]) + ", Wisdom:" + str(char[5]) + ", Luck:" + str(char[6]) + " "
		line4 = " " + "Items: " + str(char[7]) + " "
		line5 = " " + str(char[8]) + " "
		line6 = " " + str(char[9]) + " "
		line7 = " " + str(char[10]) + " "

		util.draw_text(SURFACE_MAIN, line1, (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1
		util.draw_text(SURFACE_MAIN, line2, (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1
		util.draw_text(SURFACE_MAIN, line3, (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1
		util.draw_text(SURFACE_MAIN, line4, (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 2
		util.draw_text(SURFACE_MAIN, line5, (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1
		util.draw_text(SURFACE_MAIN, line6, (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1
		if len(line7) > 0:
			util.draw_text(SURFACE_MAIN, line7, (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
			line_num += 1


		line_spacer = 30
		x = constants.CAMERA_WIDTH/2
		y = constants.CAMERA_HEIGHT - line_spacer * 4
		color = constants.COLOR_GOLD
		bg = constants.COLOR_BLACK

		line_num = 0
		util.draw_text(SURFACE_MAIN, "Controls", (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1
		util.draw_text(SURFACE_MAIN, "w,a,s,d to move; x to rest", (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1
		util.draw_text(SURFACE_MAIN, "'g' to interact, 'l' to look, 'f' to drop", (x,y + line_spacer * line_num), color, font = "FONT_MAIN_18", center = True, back_color = bg)
		line_num += 1


		pygame.display.flip()
		MOUSE_CLICKED = False
		
		if NETWORK_LISTENER:
			connection.Pump()
			NETWORK_LISTENER.Pump()

	if start_game == True:
		USER_OPTIONS.player_class = current_selection
		USER_OPTIONS.player_name = name_box.text
		options_save()

		if not NETWORK_LISTENER:
			game_new()
		else:
			GAME.game_start()
			game_main_loop()

def draw_gui():

	inv_menu()
	spell_menu()
	text_box()
	char_box()
	mouseover()
	draw_target_text()
	util.draw_debug(SURFACE_MAIN, CLOCK.get_fps())

def inv_menu():

	global MOUSE_CLICKED

	menu_close = False
	menu_width = constants.MENU_WIDTH
	menu_height = constants.INV_HEIGHT#constants.GAME_TILES_Y * constants.GAME_TILE_SIZE
	menu_font = "FONT_DEFAULT"


	buff = constants.MENU_BUFFER

	coords_x =  0
	coords_y = 0

	inv_surface = pygame.Surface((menu_width, menu_height))

	

	inv_surface.fill(constants.COLOR_BLACK)


	print_list = []
	for obj in PLAYER.container.inventory:
		if len(obj.item.tooltip_lines) != 0 and obj.item.identify_name != obj.name:
			print_list.append("magic " + obj.display_name)

		else:
			print_list.append(obj.display_name)



	util.draw_text(inv_surface, "Inventory:", (buff, buff), constants.COLOR_GOLD)

	mouse_line_selection = 0

	if mouse_in_window(0, 0, menu_width, menu_height):
		rel_x, rel_y = mouse_in_window(0, 0, menu_width, menu_height)
		mouse_line_selection = rel_y / util.helper_text_height(menu_font)
		



	for line, (name) in enumerate(print_list):


		if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
			util.draw_text(inv_surface, name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

			if MOUSE_CLICKED == True and len(ONGOING_FUNCTIONS_GUI) == 0:
				if PLAYER.container.inventory[line].item.use_gui == "default_item_use":
					default_item_use(PLAYER.container.inventory[line])

				else:
					PLAYER.container.inventory[line].item.use_gui(PLAYER.container.inventory[line])

				MOUSE_CLICKED = False

		else:
			util.draw_text(inv_surface, name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE)

		
		line+=1

	SURFACE_MAIN.blit(inv_surface, (0, 0))

def spell_menu():

	global MOUSE_CLICKED

	menu_close = False
	menu_width = constants.MENU_WIDTH
	menu_height = constants.CAMERA_HEIGHT - constants.INV_HEIGHT#constants.GAME_TILES_Y * constants.GAME_TILE_SIZE
	menu_font = "FONT_DEFAULT"


	buff = constants.MENU_BUFFER

	coords_x =  0
	coords_y = 0

	spell_surface = pygame.Surface((menu_width, menu_height))

	

	spell_surface.fill(constants.COLOR_BLACK)

	print_list = [str(spell.name) for spell in PLAYER.creature.active_spells]

	util.draw_text(spell_surface, "Spells:", (buff, buff), constants.COLOR_GOLD)

	mouse_line_selection = 0

	if mouse_in_window(0, constants.INV_HEIGHT, menu_width, menu_height):
		rel_x, rel_y = mouse_in_window(0, constants.INV_HEIGHT, menu_width, menu_height)
		mouse_line_selection = rel_y / util.helper_text_height(menu_font)
		



	for line, (name) in enumerate(print_list):

		spell_display_name = name

		if line < 9 and USER_OPTIONS.spell_key_binds[line]:
			spell_display_name = str(USER_OPTIONS.spell_key_binds[line]) + " : " + str(spell_display_name)

		if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
			util.draw_text(spell_surface, spell_display_name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

			for event in GAME_EVENT_LIST:
				if event.type == pygame.KEYDOWN:

				#remove already bound keys
					for index, bound_key in enumerate(USER_OPTIONS.spell_key_binds):
						if event.unicode == bound_key:
							USER_OPTIONS.spell_key_binds[index] = None
							break

					USER_OPTIONS.spell_key_binds[line] = event.unicode

			if MOUSE_CLICKED == True:
				PLAYER.creature.active_spells[line].cast()
				MOUSE_CLICKED = False

		else:

			spell_display_name = name

			if line < 9 and USER_OPTIONS.spell_key_binds[line]:
				spell_display_name = str(USER_OPTIONS.spell_key_binds[line].upper()) + " : " + str(spell_display_name)

			util.draw_text(spell_surface, spell_display_name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE)

		
		line+=1

	SURFACE_MAIN.blit(spell_surface, (0, constants.INV_HEIGHT))

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

def text_box():

	menu_width = constants.MENU_WIDTH
	menu_height = constants.CAMERA_HEIGHT - constants.MENU_HEIGHT_CHAR
	buff = constants.MENU_BUFFER

	coords_x =  constants.CAMERA_WIDTH #(constants.GAME_TILES_X * constants.GAME_TILE_SIZE)
	coords_y = constants.CAMERA_HEIGHT #constants.GAME_TILES_Y * constants.GAME_TILE_SIZE

	game_height = constants.CAMERA_HEIGHT#constants.GAME_TILES_Y * constants.GAME_TILE_SIZE

	text_surface = pygame.Surface((menu_width, menu_height))
	text_surface.fill(constants.COLOR_DARK_GREY)

	SURFACE_MAIN.blit(text_surface, (coords_x - menu_width, 0))

	util.print_game_messages(GAME.message_log, SURFACE_MAIN, location = (buff + coords_x - menu_width, buff), limit = menu_height )

def char_box():


	menu_width = constants.MENU_WIDTH
	menu_height = constants.MENU_HEIGHT_CHAR
	menu_font = "FONT_DEFAULT"

	buff = constants.MENU_BUFFER

	coords_x = constants.CAMERA_WIDTH - menu_width#constants.GAME_TILES_X * constants.GAME_TILE_SIZE - menu_width
	coords_y = constants.CAMERA_HEIGHT - menu_height#constants.GAME_TILES_Y * constants.GAME_TILE_SIZE - menu_height

	char_surface = pygame.Surface((menu_width, menu_height))
	char_surface.fill(constants.COLOR_BLACK)

	SURFACE_MAIN.blit(char_surface, (coords_x, coords_y))

	button_buffer = 125
	button_size = (10, 10)

	line = 0
	util.draw_text(SURFACE_MAIN, "Health:" + str(PLAYER.creature.hp) + "/" + str(PLAYER.creature.maxhp), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_LIGHT_RED)
	line+=1
	util.draw_text(SURFACE_MAIN, "Mana:" + str(PLAYER.creature.mana) + "/" + str(PLAYER.creature.maxmana), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_LIGHT_BLUE)
	line+=1
	util.draw_text(SURFACE_MAIN, "Food:" + str(PLAYER.player.food) + "/" + str(PLAYER.player.maxfood), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_ORANGE)
	line+=1
	util.draw_text(SURFACE_MAIN, "Strength:" + str(PLAYER.creature.strength), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_TAN)
	if PLAYER.player.stat_points > 0:
		strength_button = ui_button(SURFACE_MAIN, (coords_x+button_buffer, coords_y+buff + (line)*util.helper_text_height(menu_font)), button_size, "+", click_function = "RETURN", color_box = constants.COLOR_BLACK, font = "FONT_MAIN_16")
		
		if strength_button.draw() :
			PLAYER.player.stat_points -= 1
			PLAYER.creature.strength += 1

	line+=1
	util.draw_text(SURFACE_MAIN, "Dexterity:" + str(PLAYER.creature.dexterity), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_TAN)
	if PLAYER.player.stat_points > 0:
		dexterity_button = ui_button(SURFACE_MAIN, (coords_x+button_buffer, coords_y+buff + (line)*util.helper_text_height(menu_font)), button_size, "+", click_function = "RETURN", color_box = constants.COLOR_BLACK, font = "FONT_MAIN_16")
		
		if dexterity_button.draw() :

			PLAYER.player.stat_points -= 1
			PLAYER.creature.dexterity += 1

	line+=1
	util.draw_text(SURFACE_MAIN, "Luck:" + str(PLAYER.creature.luck), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_TAN)
	if PLAYER.player.stat_points > 0:
		luck_button = ui_button(SURFACE_MAIN, (coords_x+button_buffer, coords_y+buff + (line)*util.helper_text_height(menu_font)), button_size, "+", click_function = "RETURN", color_box = constants.COLOR_BLACK, font = "FONT_MAIN_16")
		
		if luck_button.draw() :
			PLAYER.player.stat_points -= 1
			PLAYER.creature.luck += 1

	line+=1
	util.draw_text(SURFACE_MAIN, "Intelligence:" + str(PLAYER.creature.intelligence), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_TAN)
	if PLAYER.player.stat_points > 0:
		intelligence_button = ui_button(SURFACE_MAIN, (coords_x+button_buffer, coords_y+buff + (line)*util.helper_text_height(menu_font)), button_size, "+", click_function = "RETURN", color_box = constants.COLOR_BLACK, font = "FONT_MAIN_16")
		
		if intelligence_button.draw() :
			PLAYER.player.stat_points -= 1
			PLAYER.creature.intelligence += 1

	line+=1
	util.draw_text(SURFACE_MAIN, "Wisdom:" + str(PLAYER.creature.wisdom), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_TAN)
	if PLAYER.player.stat_points > 0:
		wisdom_button = ui_button(SURFACE_MAIN, (coords_x+button_buffer, coords_y+buff + (line)*util.helper_text_height(menu_font)), button_size, "+", click_function = "RETURN", color_box = constants.COLOR_BLACK, font = "FONT_MAIN_16")
		
		if wisdom_button.draw() :
			PLAYER.player.stat_points -= 1
			PLAYER.creature.wisdom += 1

	line+=1
	util.draw_text(SURFACE_MAIN, "Vitality:" + str(PLAYER.creature.vitality), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_TAN)
	if PLAYER.player.stat_points > 0:
		vitality_button = ui_button(SURFACE_MAIN, (coords_x+button_buffer, coords_y+buff + (line)*util.helper_text_height(menu_font)), button_size, "+", click_function = "RETURN", color_box = constants.COLOR_BLACK, font = "FONT_MAIN_16")

		if vitality_button.draw() :
			PLAYER.player.stat_points -= 1
			PLAYER.creature.vitality += 1

	line+=1
	util.draw_text(SURFACE_MAIN, "Level:" + str(PLAYER.creature.level), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_PINK)
	line+=1
	util.draw_text(SURFACE_MAIN, "Exp:" + str(PLAYER.player.exp) + "/" + str( PLAYER.player.next_level()) + "   Points:" + str(PLAYER.player.stat_points) , (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_WHITE)
	line+=1
	util.draw_text(SURFACE_MAIN, "Gold:" + str(PLAYER.player.gold), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_GOLD)
	line+=1
	#util.draw_text(SURFACE_MAIN, "Total Turns:" + str(TOTAL_TURNS), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_LIGHT_GREY)
	util.draw_text(SURFACE_MAIN, "Attack speed:" + str(PLAYER.creature.attack_speed) + " " + str(PLAYER.creature.move_speed), (coords_x+buff, coords_y+buff + (line)*util.helper_text_height(menu_font)), constants.COLOR_LIGHT_GREY)
	

def draw_target_text():

	if TARGET_TEXT:
		util.draw_text(SURFACE_MAIN, TARGET_TEXT, (constants.MENU_WIDTH + 20, constants.CAMERA_HEIGHT - 20), constants.COLOR_WHITE, back_color = constants.COLOR_BLACK)

def identify_scroll():

	global MOUSE_CLICKED

	menu_close = False
	menu_width = constants.MENU_WIDTH
	menu_height = constants.INV_HEIGHT#constants.GAME_TILES_Y * constants.GAME_TILE_SIZE
	menu_font = "FONT_DEFAULT"
	buff = constants.MENU_BUFFER

	display_text = "used scroll of identify, select item"

	menu2_width = util.helper_text_width(display_text, menu_font) + 2*buff
	menu2_height = util.helper_text_height(menu_font) + 2*buff


	

	coords_x =  0
	coords_y = 0

	inv_surface = pygame.Surface((menu_width, menu_height))
	tooltip_surface = pygame.Surface((menu2_width, menu2_height))


	done = False
	while done == False:
		MOUSE_CLICKED = False

		action = game_handle_input()

		if action == "QUIT":
			quit_game()
		elif action == "CLICK":
			
			MOUSE_CLICKED = True

		inv_surface.fill(constants.COLOR_BLACK)
		tooltip_surface.fill(constants.COLOR_BLACK)

		print_list = []
		for obj in PLAYER.container.inventory:
			if len(obj.item.tooltip_lines) != 0:
				print_list.append("magic " + obj.display_name)

			else:
				print_list.append(obj.display_name)

		util.draw_text(inv_surface, "Inventory:", (buff, buff), constants.COLOR_GOLD)

		mouse_line_selection = 0

		if mouse_in_window(0, 0, menu_width, menu_height):
			rel_x, rel_y = mouse_in_window(0, 0, menu_width, menu_height)
			mouse_line_selection = rel_y / util.helper_text_height(menu_font)
			



		for line, (name) in enumerate(print_list):

			if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
				util.draw_text(inv_surface, name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

				if MOUSE_CLICKED == True:
					PLAYER.container.inventory[line].item.identify()
					MOUSE_CLICKED = False
					done = True

			else:
				util.draw_text(inv_surface, name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE)

			
			line+=1


		util.draw_text(tooltip_surface, display_text, (buff, buff), constants.COLOR_WHITE)



		SURFACE_MAIN.blit(inv_surface, (0, 0))


		center_x = constants.CAMERA_WIDTH/2
		center_y = constants.CAMERA_HEIGHT/2

		SURFACE_MAIN.blit(tooltip_surface, (center_x - menu2_width/2, center_y - menu2_height/2))


		pygame.display.flip()

class potion_action_menu():

	def __init__(self, item):


		self.potion = item.potion
		
		self.action_completed = False 
		self.selection_completed = True

		menu_width = constants.POTION_WIDTH
		menu_height = constants.POTION_HEIGHT

		self.coords_x =  constants.CAMERA_WIDTH/2 - menu_width/2 
		self.coords_y = constants.CAMERA_HEIGHT/2 - menu_height/2 

		self.text_surface = pygame.Surface((menu_width, menu_height))
		self.text_surface.fill(constants.COLOR_DARK_GREY)

		button_size_x = 80
		button_size_y = 25

		space = button_size_x * 3 + button_size_y
		space = menu_width - space
		space = space/3

		pos = (self.coords_x + space + button_size_y, self.coords_y + menu_height - button_size_y)
		pos4 = (self.coords_x + 3 * space + button_size_y + 2 * button_size_x, self.coords_y + menu_height - button_size_y)
		pos2 = (self.coords_x + 3 * space + button_size_y + 2 * button_size_x, self.coords_y)
		x3 = self.coords_x
		y3 = self.coords_y
		pos5 = (self.coords_x + 2 * space + button_size_y + button_size_x, self.coords_y + menu_height - button_size_y)
		pos6 = (self.coords_x, self.coords_y + menu_height - button_size_y)

		size = (button_size_x, button_size_y)

		params = []

		params.append(PLAYER)
		params.append(PLAYER)

		for param in self.potion.function_params:
			params.append(param)

		self.potion_old_name = self.potion.owner.display_name

		self.name_box = ui_inputbox(x3, y3, button_size_x, button_size_y, text=self.potion_old_name, pos_from_center = False, back_color = constants.COLOR_DARK_GREY)

		self.drink_button = ui_button(SURFACE_MAIN, pos, size, "Drink", click_function = self.potion.function, click_function_params = params,
		 font = "FONT_DEFAULT")

		self.rename_button = ui_button(SURFACE_MAIN, pos2, size, "Rename", click_function = "RETURN", click_function_params = params,
		 font = "FONT_DEFAULT")


		self.apply_button = ui_button(SURFACE_MAIN, pos4, size, "Use on item", click_function = "RETURN", click_function_params = None,
		 font = "FONT_DEFAULT")

		self.drop_button = ui_button(SURFACE_MAIN, pos5, size, "Drop", click_function = "RETURN", click_function_params = None,
		 font = "FONT_DEFAULT")

		self.cancel_button = ui_button(SURFACE_MAIN, pos6, (button_size_y, button_size_y), "X", click_function = "RETURN", click_function_params = None,
		 font = "FONT_DEFAULT")

		ONGOING_FUNCTIONS_GUI.append(self)

	def draw(self):

		global MOUSE_CLICKED, LIB, ONGOING_FUNCTIONS_GUI

		
		#buff = constants.MENU_BUFFER


		drink_potion = False
		drop_potion = False
		rename_action = False
		cancel_action = False
		
		
		
		events_list = GAME_EVENT_LIST

		#todo process input
		for event in events_list:
			if event.type == pygame.QUIT:
				quit_game()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True

			if self.name_box:
				self.name_box.handle_event(event)



		

		

	#draw buttons and check for user input
		if self.action_completed == False:

			self.name_box.update()
						
			SURFACE_MAIN.blit(self.text_surface, (self.coords_x, self.coords_y))
			
			self.name_box.draw(SURFACE_MAIN)

			if self.cancel_button.draw() == "END" :
				cancel_action = True
				self.action_completed = True
				self.selection_completed = True

			elif self.drink_button.draw() == "END" :
				drink_potion = True

				self.action_completed = True
				self.selection_completed = True
				

			elif self.rename_button.draw() == "END" :
				rename_action = True
				self.action_completed = True
				self.selection_completed = True

			elif self.apply_button.draw() == "END" :
				if len(PLAYER.container.inventory) > 1:
					self.action_completed = True
					self.selection_completed = False

			elif self.drop_button.draw() == "END" :
				drop_potion = True
				self.action_completed = True
				self.selection_completed = True

			
	# open inventory list if selection is needed
		if self.selection_completed == False:

			menu_width = constants.MENU_WIDTH
			menu_height = constants.CAMERA_HEIGHT
			menu_font = "FONT_DEFAULT"

			buff = constants.MENU_BUFFER

			coords_x =  0
			coords_y = 0

			inv_surface = pygame.Surface((menu_width, menu_height))

			location = (constants.CAMERA_WIDTH/2 - menu_width/2, constants.CAMERA_HEIGHT/2 - menu_height/2)


			inv_surface.fill(constants.COLOR_BLACK)

			print_list = [obj.display_name for obj in PLAYER.container.inventory]

			util.draw_text(inv_surface, "Inventory:", (buff, buff), constants.COLOR_GOLD)

			mouse_line_selection = 0

			m_x, m_y = location

			if mouse_in_window(m_x, m_y, menu_width, menu_height):
				rel_x, rel_y = mouse_in_window(m_x, m_y, menu_width, menu_height)
				mouse_line_selection = rel_y / util.helper_text_height(menu_font)
				



			for line, (name) in enumerate(print_list):

				if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
					util.draw_text(inv_surface, name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

					if MOUSE_CLICKED == True:

						if PLAYER.container.inventory[line].ammo:
							PLAYER.container.inventory[line].ammo.hit_effect_function = potion.function
							PLAYER.container.inventory[line].ammo.hit_effect_function_params = potion.function_params 

						elif PLAYER.container.inventory[line].equipment:
							PLAYER.container.inventory[line].equipment.hit_effect_function_temp = potion.function
							PLAYER.container.inventory[line].equipment.hit_effect_function_params_temp = potion.function_params 

						

						MOUSE_CLICKED = False
						selection_completed = True

				else:
					util.draw_text(inv_surface, name, (buff, buff + (line+1)*util.helper_text_height(menu_font)), constants.COLOR_WHITE)

				
				line+=1


			
			SURFACE_MAIN.blit(inv_surface, location)
						


		if rename_action == True and self.action_completed == True and self.selection_completed == True:

			LIB.rename_potion(self.potion.lib_name, self.name_box.text)
			ONGOING_FUNCTIONS_GUI.remove(self)

		elif drink_potion == True and self.action_completed == True and self.selection_completed == True:

			self.potion.owner.item.current_container.inventory.remove(self.potion.owner)
			ONGOING_FUNCTIONS_GUI.remove(self)

		elif drop_potion == True and self.action_completed == True and self.selection_completed == True:

			self.potion.owner.item.drop(PLAYER.x, PLAYER.y)
			ONGOING_FUNCTIONS_GUI.remove(self)

		elif self.action_completed == True and self.selection_completed == True and cancel_action == True:
			ONGOING_FUNCTIONS_GUI.remove(self)

		elif self.action_completed == True and self.selection_completed == True:

			self.potion.owner.item.current_container.inventory.remove(self.potion.owner)

			ONGOING_FUNCTIONS_GUI.remove(self)



		MOUSE_CLICKED = False

class default_item_use():

	def __init__(self, item):


		global MOUSE_CLICKED, ONGOING_FUNCTIONS_GUI

		button_size_x = 70
		button_size_y = 30
		text_height = 0

		self.spacer = 3

		self.item = item

		if self.item.item.identify_name == self.item.name:
			text_height = (len(item.item.tooltip_lines) * (util.helper_text_height() + self.spacer))

		menu_width = constants.POTION_WIDTH 
		menu_height = button_size_y + util.helper_text_height("FONT_MAIN_18") + self.spacer + text_height
		#buff = constants.MENU_BUFFER

		self.coords_x =  constants.CAMERA_WIDTH/2 - menu_width/2 
		self.coords_y = constants.CAMERA_HEIGHT/2 - menu_height/2 

		self.text_surface = pygame.Surface((menu_width, menu_height))
		self.text_surface.fill(constants.COLOR_DARK_GREY)

		space = button_size_x * 3 + button_size_y
		space = menu_width - space
		space = space/3

		pos = (self.coords_x + space + button_size_y, self.coords_y + menu_height - button_size_y)
		pos4 = (self.coords_x + 3 * space + button_size_y + 2 * button_size_x, self.coords_y + menu_height - button_size_y)
		pos2 = (self.coords_x + 3 * space + button_size_y + 2 * button_size_x, self.coords_y)
		x3 = self.coords_x
		y3 = self.coords_y
		pos5 = (self.coords_x + 2 * space + button_size_y + button_size_x, self.coords_y + menu_height - button_size_y)
		pos6 = (self.coords_x, self.coords_y + menu_height - button_size_y)

		size = (button_size_x, button_size_y)

		self.use_text = "Use"
		if self.item.equipment:
			if self.item.equipment.equipped:
				self.use_text = "Unequip"
			else:
				self.use_text = "Equip"

		if self.item.item.use_text:
			self.use_text = self.item.item.use_text

		

		self.use_button = ui_button(SURFACE_MAIN, pos, size, self.use_text, click_function = item.item.use, click_function_params = None,
		 font = "FONT_DEFAULT")

		self.throw_button = ui_button(SURFACE_MAIN, pos4, size, "Throw", click_function = throw, click_function_params = [item],
		 font = "FONT_DEFAULT")

		self.drop_button = ui_button(SURFACE_MAIN, pos5, size, "Drop", click_function = item.item.drop, click_function_params = [PLAYER.x, PLAYER.y],
		 font = "FONT_DEFAULT")

		self.cancel_button = ui_button(SURFACE_MAIN, pos6, (button_size_y, button_size_y), "X", click_function = "RETURN", click_function_params = None,
		 font = "FONT_DEFAULT")

		

		ONGOING_FUNCTIONS_GUI.append(self)


	def draw(self):

						
		SURFACE_MAIN.blit(self.text_surface, (self.coords_x, self.coords_y))

		if self.item.item.identify_name == self.item.name:

			util.draw_text(SURFACE_MAIN, self.item.item.identify_name, (constants.CAMERA_WIDTH/2, self.coords_y + self.spacer*4), constants.COLOR_WHITE, font = "FONT_MAIN_18", center = True)

			for i in range(len(self.item.item.tooltip_lines)):

				util.draw_text(SURFACE_MAIN, self.item.item.tooltip_lines[i], (constants.CAMERA_WIDTH/2, util.helper_text_height("FONT_MAIN_18") + 3 + self.coords_y + i * (util.helper_text_height() + self.spacer)), constants.COLOR_BLUE, center = True)

		else:
			util.draw_text(SURFACE_MAIN, self.item.name, (constants.CAMERA_WIDTH/2, self.coords_y + self.spacer*4), constants.COLOR_WHITE, font = "FONT_MAIN_18", center = True)

		for event in GAME_EVENT_LIST:
			if event.type == pygame.QUIT:
				quit_game()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
		

		if self.use_button.draw() == "END" :
			use_item = True
			if self.item.item.use_function == None and self.item.equipment == None:
				game_message("Nothing happens", color = constants.COLOR_TAN)

			ONGOING_FUNCTIONS_GUI.remove(self)


		elif self.throw_button.draw() == "END" :
			use_item = True
			ONGOING_FUNCTIONS_GUI.remove(self)


		elif self.drop_button.draw() == "END" :
			use_item = True
			ONGOING_FUNCTIONS_GUI.remove(self)

		elif self.cancel_button.draw() == "END":
			use_item = False
			ONGOING_FUNCTIONS_GUI.remove(self)




		MOUSE_CLICKED = False

class yes_no_box():

	def __init__(self, message, yes_function, no_function, yes, no, yes_params = None, no_params = None):

		global MOUSE_CLICKED, ONGOING_FUNCTIONS_GUI

		self.message = message
		self.yes_function = yes_function
		self.no_function = no_function
		self.yes = yes
		self.no = no
		self.yes_params = yes_params
		self.no_params = no_params

		button_size_x = max(util.helper_text_width(self.yes, "FONT_MAIN_18"), util.helper_text_width(self.no, "FONT_MAIN_18"))
		button_size_y = 30
		text_height = 0

		self.spacer = 6

		menu_width = max(200, util.helper_text_width(self.message, "FONT_MAIN_18") + 20) 
		menu_height = button_size_y + util.helper_text_height("FONT_MAIN_18") + self.spacer + text_height
		#buff = constants.MENU_BUFFER

		self.coords_x =  constants.CAMERA_WIDTH/2 - menu_width/2 
		self.coords_y = constants.CAMERA_HEIGHT/2 - menu_height/2 

		self.text_surface = pygame.Surface((menu_width, menu_height))
		self.text_surface.fill(constants.COLOR_DARK_GREY)



		pos = (self.coords_x, self.coords_y + menu_height - button_size_y)
		pos4 = (self.coords_x + menu_width - button_size_x, self.coords_y + menu_height - button_size_y)
		pos2 = (self.coords_x + menu_width - button_size_x, self.coords_y)
		x3 = self.coords_x
		y3 = self.coords_y
		pos5 = (self.coords_x + menu_width/2 - button_size_x/2, self.coords_y + menu_height - button_size_y)

		size = (button_size_x, button_size_y)


		response = False
		drop_item = False


		self.yes_button = ui_button(SURFACE_MAIN, pos4, size, self.yes, click_function = self.yes_function, click_function_params = self.yes_params,
		 font = "FONT_DEFAULT")

		self.no_button = ui_button(SURFACE_MAIN, pos, size, self.no, click_function = self.no_function, click_function_params = self.no_params,
		 font = "FONT_DEFAULT")

		ONGOING_FUNCTIONS_GUI.append(self)


	def draw(self):

						
		SURFACE_MAIN.blit(self.text_surface, (self.coords_x, self.coords_y))

		events_list = GAME_EVENT_LIST

		util.draw_text(SURFACE_MAIN, self.message, (constants.CAMERA_WIDTH/2, self.coords_y + self.spacer*2), constants.COLOR_WHITE, font = "FONT_MAIN_18", center = True)

		for event in events_list:
			if event.type == pygame.QUIT:
				quit_game()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
		

		if self.yes_button.draw() == "END" :
			try:
				ONGOING_FUNCTIONS_GUI.remove(self)
			except:
				print "error here"


		elif self.no_button.draw() == "END" :
			ONGOING_FUNCTIONS_GUI.remove(self)




		MOUSE_CLICKED = False

class message_box():

	def __init__(self, message):

		global MOUSE_CLICKED, ONGOING_FUNCTIONS_GUI

		button_size_x = 70
		button_size_y = 30
		text_height = 0

		word_wrap_length = 350
		self.spacer = 5

		self.msgs = util.wrapline(message, constants.FONT_MAIN_16, word_wrap_length)
		self.msgs.append("")

		menu_width = 400 
		menu_height = button_size_y + (util.helper_text_height("FONT_MAIN_16") * len(self.msgs)) + self.spacer + text_height
		#buff = constants.MENU_BUFFER

		self.coords_x =  constants.CAMERA_WIDTH/2 - menu_width/2 
		self.coords_y = constants.CAMERA_HEIGHT/2 - menu_height/2 

		coords_x = self.coords_x
		coords_y = self.coords_y

		self.text_surface = pygame.Surface((menu_width, menu_height))
		self.text_surface.fill(constants.COLOR_BLACK)



		pos = (coords_x, coords_y + menu_height - button_size_y)
		pos4 = (coords_x + menu_width - button_size_x, coords_y + menu_height - button_size_y)
		pos2 = (coords_x + menu_width - button_size_x, coords_y)
		x3 = coords_x
		y3 = coords_y
		pos5 = (coords_x + menu_width/2 - button_size_x/2, coords_y + menu_height - button_size_y)

		size = (button_size_x, button_size_y)


		response = False
		drop_item = False


		self.ok_button = ui_button(SURFACE_MAIN, pos4, size, "ok", click_function = None, click_function_params = None,
		 font = "FONT_DEFAULT")

		ONGOING_FUNCTIONS_GUI.append(self)


	def draw(self):

						
		SURFACE_MAIN.blit(self.text_surface, (self.coords_x, self.coords_y))


		i = 1
		for msg in self.msgs:
			util.draw_text(SURFACE_MAIN, msg, (constants.CAMERA_WIDTH/2, self.coords_y + self.spacer + i * (util.helper_text_height("FONT_MAIN_18")+2) ), constants.COLOR_WHITE, font = "FONT_MAIN_18", center = True)
			i += 1

		for event in GAME_EVENT_LIST:
			if event.type == pygame.QUIT:
				quit_game()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
		

		if self.ok_button.draw() == "END" :
			ONGOING_FUNCTIONS_GUI.remove(self)




		MOUSE_CLICKED = False

class pop_up_text():

	prevents_action = False

	def __init__(self, x, y, message, back_color = None, color = constants.COLOR_WHITE):

		global MOUSE_CLICKED, ONGOING_FUNCTIONS_GUI

		self.duration = .3
		self.pop_amount = 2

		self.message = message
		self.back_color = back_color
		text_height = 0

		self.spacer = 5

		menu_width = util.helper_text_width(self.message, "FONT_MAIN_16")
		menu_height = 30
		#buff = constants.MENU_BUFFER

		self.coords_x =  x
		self.coords_y = y

		coords_x = self.coords_x
		coords_y = self.coords_y

		

		if self.back_color:
			self.text_surface = pygame.Surface((menu_width, menu_height))
			self.text_surface.fill(self.back_color)
			util.draw_text(self.text_surface, self.message, (menu_width/2, menu_height/2), color, font = "FONT_MAIN_18", center = True)

			
		self.text_surface = util.draw_text(None, self.message, (menu_width/2, menu_height/2), color, font = "FONT_MAIN_18", center = True, return_surface = True)



		ONGOING_FUNCTIONS_GUI.append(self)


	def draw(self):

		if CLOCK.get_fps() > 0:
			self.duration -= 1 / CLOCK.get_fps()

		self.coords_y -= self.duration * self.pop_amount
						
		SURFACE_MAIN.blit(self.text_surface, (self.coords_x, self.coords_y))


		# for event in GAME_EVENT_LIST:
		# 	if event.type == pygame.QUIT:
		# 		quit_game()

		# 	if event.type == pygame.MOUSEBUTTONDOWN:
		# 		if event.button == 1:
		# 			MOUSE_CLICKED = True


		MOUSE_CLICKED = False

		if self.duration <= 0:
			ONGOING_FUNCTIONS_GUI.remove(self)

def message_box_while_loop(message):

	global MOUSE_CLICKED, ONGOING_FUNCTIONS_GUI

	button_size_x = 70
	button_size_y = 30
	text_height = 0

	word_wrap_length = 350
	spacer = 5

	msgs = util.wrapline(message, constants.FONT_MAIN_16, word_wrap_length)
	msgs.append("")


	menu_width = 400 
	menu_height = button_size_y + (util.helper_text_height("FONT_MAIN_16") * len(msgs)) + spacer + text_height
	#buff = constants.MENU_BUFFER

	coords_x =  constants.CAMERA_WIDTH/2 - menu_width/2 
	coords_y = constants.CAMERA_HEIGHT/2 - menu_height/2 

	text_surface = pygame.Surface((menu_width, menu_height))
	text_surface.fill(constants.COLOR_BLACK)



	pos = (coords_x, coords_y + menu_height - button_size_y)
	pos4 = (coords_x + menu_width - button_size_x, coords_y + menu_height - button_size_y)
	pos2 = (coords_x + menu_width - button_size_x, coords_y)
	x3 = coords_x
	y3 = coords_y
	pos5 = (coords_x + menu_width/2 - button_size_x/2, coords_y + menu_height - button_size_y)

	size = (button_size_x, button_size_y)


	response = False
	drop_item = False


	ok_button = ui_button(SURFACE_MAIN, pos4, size, "ok", click_function = None, click_function_params = None,
	 font = "FONT_DEFAULT")



	while True:
					
		SURFACE_MAIN.blit(text_surface, (coords_x, coords_y))

		events_list = pygame.event.get()

		i = 1
		for msg in msgs:
			util.draw_text(SURFACE_MAIN, msg, (constants.CAMERA_WIDTH/2, coords_y + spacer + i * (util.helper_text_height("FONT_MAIN_18")+2) ), constants.COLOR_WHITE, font = "FONT_MAIN_18", center = True)
			i += 1

		for event in events_list:
			if event.type == pygame.QUIT:
				quit_game()

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
		

		if ok_button.draw() == "END" :
			break




		MOUSE_CLICKED = False
		CLOCK.tick()

		pygame.display.flip()

class campfire_menu:

	menu_width = constants.CAMPFIRE_MENU_WIDTH
	menu_height = constants.CAMPFIRE_MENU_HEIGHT

	coords_x =  constants.CAMERA_WIDTH/2 - menu_width/2 
	coords_y = constants.CAMERA_HEIGHT/2 - menu_height/2 

	text = "Requires 30 Food"

	def __init__(self):

		self.text_surface = pygame.Surface((self.menu_width, self.menu_height))
		self.text_surface.fill(constants.COLOR_BLACK)

		button_size_x = 150
		button_size_y = 50	

		pos = (self.coords_x + button_size_x, self.coords_y)
		pos2 = (self.coords_x, self.coords_y)
		
		size = (button_size_x, button_size_y)

		self.leave_button = ui_button(SURFACE_MAIN, pos, size, "Leave", click_function = "RETURN",
		 font = "FONT_DEFAULT")

		self.rest_button = ui_button(SURFACE_MAIN, pos2, size, "Rest", click_function = "RETURN",
		 font = "FONT_DEFAULT")

		self.font = "FONT_DEFAULT"

		self.old_active_spells = []
		for spell in PLAYER.creature.active_spells:
			self.old_active_spells.append(spell)

		self.buff = constants.MENU_BUFFER

		self.refresh_spell_lists()

		ONGOING_FUNCTIONS_GUI.append(self)

	def refresh_spell_lists(self):
	#make surfaces
		self.button_size_x = 150
		self.button_size_y = 50	

		menu_width_2 = constants.CAMPFIRE_MENU_WIDTH/2
		menu_height_2 = constants.CAMPFIRE_MENU_HEIGHT - (self.button_size_y + util.helper_text_height(self.font) * 2)

		self.learned_surface = pygame.Surface((menu_width_2, menu_height_2))
		self.active_surface = pygame.Surface((menu_width_2, menu_height_2))

		self.location1 = (self.coords_x, self.coords_y + self.button_size_y + util.helper_text_height(self.font) + 5)
		self.location2 = (self.coords_x + self.menu_width/2, self.coords_y + self.button_size_y + util.helper_text_height(self.font) + 5)
		
			
		self.learned_surface.fill(constants.COLOR_BLACK)
		self.active_surface.fill(constants.COLOR_BLACK)

		

		x1, y1 = self.location1
		util.draw_text(self.learned_surface, "Learned Spells:", (self.buff, self.buff), constants.COLOR_GOLD)
		x2, y2 = self.location2
		util.draw_text(self.active_surface, "Active Spells: " + str( len(PLAYER.creature.active_spells) ) + "/" + str(PLAYER.creature.max_active_spells), (self.buff, self.buff), constants.COLOR_GOLD)

	#draw player known spells on surfaces, and highlight selection
		print_list = [spell.name for spell in PLAYER.creature.known_spells]

		m_x1, m_y1 = self.location1
		m_x2, m_y2 = self.location2

		mouse_line_selection = 0
		if mouse_in_window(m_x1, m_y1, self.menu_width/2, self.menu_height):
			rel_x1, rel_y1 = mouse_in_window(m_x1, m_y1, self.menu_width/2, self.menu_height)
			mouse_line_selection = rel_y1 / util.helper_text_height(self.font)
			
		global MOUSE_CLICKED

		for line, (name) in enumerate(print_list):

			if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
				util.draw_text(self.learned_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

				if MOUSE_CLICKED == True:
					MOUSE_CLICKED = False
					if len(PLAYER.creature.active_spells) < PLAYER.creature.max_active_spells:
						PLAYER.creature.active_spells.append(PLAYER.creature.known_spells[line])
						PLAYER.creature.known_spells.remove(PLAYER.creature.known_spells[line])

			else:
				util.draw_text(self.learned_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.font)), constants.COLOR_WHITE)

			line+=1

	#draw player active spells on surfaces, and highlight selection
		print_list = [spell.name for spell in PLAYER.creature.active_spells]

		mouse_line_selection = 0
		if mouse_in_window(m_x2, m_y2, self.menu_width/2, self.menu_height):
			rel_x2, rel_y2 = mouse_in_window(m_x2, m_y2, self.menu_width/2, self.menu_height)
			mouse_line_selection = rel_y2 / util.helper_text_height(self.font)
			


		for line, (name) in enumerate(print_list):

			if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
				util.draw_text(self.active_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

				if MOUSE_CLICKED == True:
					MOUSE_CLICKED = False
					PLAYER.creature.known_spells.append(PLAYER.creature.active_spells[line])
					PLAYER.creature.active_spells.remove(PLAYER.creature.active_spells[line])

			else:
				util.draw_text(self.active_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.font)), constants.COLOR_WHITE)	

			
			
			line+=1


	def draw(self):
					

	#draw rest and leave buttons				
		SURFACE_MAIN.blit(self.text_surface, (self.coords_x, self.coords_y))

		if self.leave_button.draw() == "END" :
			ONGOING_FUNCTIONS_GUI.remove(self)


		if self.rest_button.draw() == "END" :
			if PLAYER.player.food < 30:
				self.text = "You do not have enough food"

			else:
			#check for monsters in sight
				monster_nearby = False

				for monster in GAME.current_objects:
					if monster.creature and monster.creature.hp > 0 and monster.creature.team != PLAYER.creature.team:
						is_visable = libtcod.map_is_in_fov(FOV_MAP, monster.x, monster.y)
						if is_visable == True:
							monster_nearby = True
							break

				if monster_nearby == False:
					PLAYER.creature.heal(PLAYER.creature.maxhp)
					PLAYER.creature.mana = PLAYER.creature.maxmana
					PLAYER.player.food -= 30
					ONGOING_FUNCTIONS_GUI.remove(self)

					global TOTAL_TURNS
					TOTAL_TURNS += 1

				else:
					self.text = "A monster is nearby"

		#wrap message text 
		i = 0
		for segment in util.wrapline(self.text, constants.FONT_DEFAULT, self.button_size_x):
			pos3 = (self.coords_x + self.button_size_x/2, 10 + self.coords_y + self.button_size_y + constants.MENU_BUFFER + i * util.helper_text_height(self.font))
			util.draw_text(SURFACE_MAIN, segment, pos3, constants.COLOR_RED, center = True)
			i+=1



	#draw spells menu
		self.refresh_spell_lists()

		SURFACE_MAIN.blit(self.learned_surface, self.location1)
		SURFACE_MAIN.blit(self.active_surface, self.location2)
	

		if self.old_active_spells != PLAYER.creature.active_spells:
			PLAYER_TOOK_ACTION = "CHANGED_SPELLS"

		else:
			PLAYER_TOOK_ACTION = "NONE"
		MOUSE_CLICKED = False

class shop_menu():

	menu_width = constants.MENU_WIDTH * 1.5
	menu_height = constants.INV_HEIGHT#constants.GAME_TILES_Y * constants.GAME_TILE_SIZE
	menu_font = "FONT_DEFAULT"

	

	buff = constants.MENU_BUFFER

	coords_x1 =  constants.CAMERA_WIDTH/2 - (menu_width + constants.GAME_TILE_SIZE/2)
	coords_y1 = constants.CAMERA_HEIGHT/2 - menu_height/2

	coords_x2 =  constants.CAMERA_WIDTH/2 + constants.GAME_TILE_SIZE/2
	coords_y2 = constants.CAMERA_HEIGHT/2 - menu_height/2

	size = (150, 30)
	pos_2 = (0, menu_height/2 + 30)

	def __init__(self, shop_owner):

		self.shop_owner = shop_owner

		size = self.size
		sx,sy = size
		pos = (-(sx*1 + self.buff), self.menu_height/2 + 30)
		pos2 = self.pos_2
		pos_2_slider = (0, self.menu_height/2 + 50)
		pos3 = ((sx*1 + self.buff), self.menu_height/2 + 30)

		food_amount = PLAYER.player.maxfood-PLAYER.player.food
		self.food_slider = ui_slider(SURFACE_MAIN, pos_2_slider, size, pos_from_center = True, fill = .5, text = "", draw_percent_text = False)

		self.attack_button = ui_button(SURFACE_MAIN, pos, size, "Attack", click_function = "RETURN",
		 font = "FONT_DEFAULT", pos_from_center = True)

		self.food_button = ui_button(SURFACE_MAIN, pos2, size, str(food_amount) + " food: " + str(food_amount * constants.GOLD_PER_FOOD),
		 click_function = "RETURN", font = "FONT_DEFAULT", pos_from_center = True)

		self.leave_button = ui_button(SURFACE_MAIN, pos3, size, "Leave", click_function = "RETURN",
		 font = "FONT_DEFAULT", pos_from_center = True)

		self.inv_surface = pygame.Surface((self.menu_width, self.menu_height))
		self.shop_surface = pygame.Surface((self.menu_width, self.menu_height))

		ONGOING_FUNCTIONS_GUI.append(self)

	def refresh(self):

		global MOUSE_CLICKED

		food_amount = int((PLAYER.player.maxfood-PLAYER.player.food) * self.food_slider.fill)
		self.food_button = ui_button(SURFACE_MAIN, self.pos_2, self.size, str(food_amount) + " food: " + str(food_amount * constants.GOLD_PER_FOOD),
		 click_function = "RETURN", font = "FONT_DEFAULT", pos_from_center = True)

	# populate player inventory surface
		self.inv_surface.fill(constants.COLOR_BLACK)

		print_list = [obj.display_name + "  " + str(int(obj.item.value)) for obj in PLAYER.container.inventory]

		util.draw_text(self.inv_surface, "Inventory:", (self.buff, self.buff), constants.COLOR_GOLD)

		mouse_line_selection = 0

		if mouse_in_window(self.coords_x2, self.coords_y2, self.menu_width, self.menu_height):
			rel_x, rel_y = mouse_in_window(self.coords_x2, self.coords_y2, self.menu_width, self.menu_height)
			mouse_line_selection = rel_y / util.helper_text_height(self.menu_font)
			

		for line, (name) in enumerate(print_list):

			if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
				util.draw_text(self.inv_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.menu_font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

				if MOUSE_CLICKED == True:
					PLAYER.player.gold += int(PLAYER.container.inventory[line].item.value)
					self.shop_owner.container.inventory.append(PLAYER.container.inventory[line])
					PLAYER.container.inventory.remove(PLAYER.container.inventory[line])
					MOUSE_CLICKED = False

			else:
				util.draw_text(self.inv_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.menu_font)), constants.COLOR_WHITE)

			line+=1

	# populate shop list
		self.shop_surface.fill(constants.COLOR_BLACK)

		print_list = [obj.display_name + "  " + str(int(obj.item.value * 1.5)) for obj in self.shop_owner.container.inventory]

		util.draw_text(self.shop_surface, "Shop:", (self.buff, self.buff), constants.COLOR_GOLD)

		mouse_line_selection = 0

		if mouse_in_window(self.coords_x1, self.coords_y1, self.menu_width, self.menu_height):
			rel_x, rel_y = mouse_in_window(self.coords_x1, self.coords_y1, self.menu_width, self.menu_height)
			mouse_line_selection = rel_y / util.helper_text_height(self.menu_font)
			

		for line, (name) in enumerate(print_list):

			if (line == mouse_line_selection - 1) and (mouse_line_selection > 0):
				util.draw_text(self.shop_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.menu_font)), constants.COLOR_WHITE, back_color = constants.COLOR_GREY)

				if MOUSE_CLICKED == True:
					if PLAYER.player.gold >= self.shop_owner.container.inventory[line].item.value * 1.5:
						PLAYER.player.gold -= int(self.shop_owner.container.inventory[line].item.value * 1.5)
						PLAYER.container.inventory.append(self.shop_owner.container.inventory[line])
						self.shop_owner.container.inventory[line].item.current_container = PLAYER.container
						self.shop_owner.container.inventory.remove(self.shop_owner.container.inventory[line])
					MOUSE_CLICKED = False

			else:
				util.draw_text(self.shop_surface, name, (self.buff, self.buff + (line+1)*util.helper_text_height(self.menu_font)), constants.COLOR_WHITE)

			
			line+=1

	def draw(self):

		self.refresh()

		SURFACE_MAIN.blit(self.inv_surface, (self.coords_x2, self.coords_y2))
		SURFACE_MAIN.blit(self.shop_surface, (self.coords_x1, self.coords_y1))

		if self.attack_button.draw():
			self.shop_owner.shop.hostile = True
			self.shop_owner.ai = ai_chase()
			self.shop_owner.ai.owner = self.shop_owner
			PLAYER.creature.attack(self.shop_owner)
			ONGOING_FUNCTIONS_GUI.remove(self)

		self.food_slider.update()
		self.food_slider.draw()

		if self.food_button.draw(): pass

		if self.leave_button.draw(): ONGOING_FUNCTIONS_GUI.remove(self)

class select():

	def __init__(self, select_params = [None], on_click_function = None, func_params = [None]):

		self.display_all = USER_OPTIONS.DISPLAY_ALL_TILES_IN_PATH
		
		if select_params != [None]:
			self.origin, self.max_range, self.penetrate, self.penetrate_characters, self.radius, self.hit_along_path, self.can_cast_on_self = select_params
	
		else:
			self.origin  = None
			self.max_range  = None
			self.penetrate  = None
			self.penetrate_characters = None
			self.radius = None
			self.hit_along_path = None
			self.can_cast_on_self = None

		self.on_click_function = on_click_function
		self.func_params = func_params

		ONGOING_FUNCTIONS.append(self)

	def draw(self):
	#turn mouse position into game tile coords
		mouse_x, mouse_y = pygame.mouse.get_pos()

		mapx_pixel, mapy_pixel = CAMERA.win_to_map((mouse_x, mouse_y))

		tile_x = mapx_pixel/constants.GAME_TILE_SIZE
		tile_y = mapy_pixel/constants.GAME_TILE_SIZE

		tile_x = util.clamp(tile_x, 0, constants.GAME_TILES_X-1)
		tile_y = util.clamp(tile_y, 0, constants.GAME_TILES_Y-1)


	#find all tiles in select params
		valid_list_of_tiles = []

		if (self.origin and self.origin != (tile_x, tile_y)): #if the mouse is not over the origin

			origin_x, origin_y = self.origin

		# add tiles in line from origin to mouse
			full_list_of_tiles = util.find_line(self.origin, (tile_x, tile_y)) #get all the tiles between start (player) and mouse

			for i,(x,y) in enumerate(full_list_of_tiles):

				valid_list_of_tiles.append((x,y)) #add tile to return list

			# if we reach a tile we should stop at, break
				if self.max_range and i == self.max_range-1: #reached max range
						break

				elif not self.penetrate and is_wall(x,y) == True: #hit wall
						break

				elif not self.penetrate_characters and map_check_for_creatures(x, y): #hit creature
						break

				# elif not penetrate_characters and not (tile_x == x and tile_y == y): #
				# 	valid_list_of_tiles.remove((x,y))

		# add tiles in radius around endpoint
			if self.radius > 0:
				radius_tiles = util.find_radius(valid_list_of_tiles[-1], self.radius)

				for tile in radius_tiles:
					valid_list_of_tiles.insert(-1, tile)


		else: # no origin, or mouse is over origin
			valid_list_of_tiles = [(tile_x, tile_y)]

	# draw targeting image
		success = False
		if self.display_all == True:

			if self.hit_along_path == True:

				for tilex,tiley in valid_list_of_tiles:
					
					draw_tile_at_coords(tiles.target(tilex,tiley ,1), tilex, tiley)
					success = True

		if success == False and self.display_all == True:
			tilex, tiley = valid_list_of_tiles[-1]
			draw_tile_at_coords(tiles.target(tilex,tiley, 1), tilex, tiley)
			success = True

		if success == False:
			draw_tile_at_coords(tiles.target(tile_x,tile_y, 1), tile_x, tile_y)


	# display tile names if tile is explored
		tile_text = ""
		tile_text += GAME.current_map[tile_x][tile_y][0].name
		if GAME.current_map[tile_x][tile_y][1] != None and GAME.current_map[tile_x][tile_y][1].name != "":
			tile_text += ", "
			tile_text += GAME.current_map[tile_x][tile_y][1].name

		enemy_text = ""

		for i in range (len(GAME.current_objects)):

			if GAME.current_objects[i].x == tile_x and GAME.current_objects[i].y == tile_y:
				enemy_text += (", " + GAME.current_objects[i].name)

		if GAME.current_map[tile_x][tile_y][0].explored == True:
			global TARGET_TEXT
			TARGET_TEXT = tile_text + enemy_text


	# return selected tiles
		if MOUSE_CLICKED == True:

			if self.on_click_function:
				
				params = self.func_params
			#replace SELECT_RESULT keyword with selection results
				i = 0
				for param in params:
					if params[i] == "SELECT_RESULT": 
						params[i] = valid_list_of_tiles
						
					i+=1
					
					
				self.on_click_function(*params)

		# if no func to call (using look action), call tile reveal function
			elif GAME.current_map[tile_x][tile_y][0].hidden == True or (GAME.current_map[tile_x][tile_y][1] and GAME.current_map[tile_x][tile_y][1].hidden):

				PLAYER_TOOK_ACTION = GAME.current_map[tile_x][tile_y][0].reveal()

				if GAME.current_map[tile_x][tile_y][1]:
					PLAYER_TOOK_ACTION = GAME.current_map[tile_x][tile_y][1].reveal()
				

			ONGOING_FUNCTIONS.remove(self)
			TARGET_TEXT = None


		return valid_list_of_tiles		

def mouseover():
	if "CAMERA" in globals():
	
		#turn mouse position into game tile coords
		mouse_x, mouse_y = pygame.mouse.get_pos()

		mapx_pixel, mapy_pixel = CAMERA.win_to_map((mouse_x, mouse_y))

		tile_x = mapx_pixel/constants.GAME_TILE_SIZE
		tile_y = mapy_pixel/constants.GAME_TILE_SIZE

		tile_x = util.clamp(tile_x, 0, constants.GAME_TILES_X-1)
		tile_y = util.clamp(tile_y, 0, constants.GAME_TILES_Y-1)
		
		# display tile names if tile is explored
		tile_text = ""
		tile_text += GAME.current_map[tile_x][tile_y][0].name
		if GAME.current_map[tile_x][tile_y][1] != None and GAME.current_map[tile_x][tile_y][1].name != "":
			tile_text += ", "
			tile_text += GAME.current_map[tile_x][tile_y][1].name

		enemy_text = ""

		for i in range (len(GAME.current_objects)):

			if GAME.current_objects[i].x == tile_x and GAME.current_objects[i].y == tile_y:
				enemy_text += (", " + GAME.current_objects[i].name)

		if GAME.current_map[tile_x][tile_y][0].explored == True:
			global TARGET_TEXT
			TARGET_TEXT = tile_text + enemy_text

	else:
		print("no cam")
#   _____ ____  _____  ______      _____          __  __ ______     ______ _    _ _   _  _____ _______ _____ ____  _   _  _____ 
#  / ____/ __ \|  __ \|  ____|    / ____|   /\   |  \/  |  ____|   |  ____| |  | | \ | |/ ____|__   __|_   _/ __ \| \ | |/ ____|
# | |   | |  | | |__) | |__      | |  __   /  \  | \  / | |__      | |__  | |  | |  \| | |       | |    | || |  | |  \| | (___  
# | |   | |  | |  _  /|  __|     | | |_ | / /\ \ | |\/| |  __|     |  __| | |  | | . ` | |       | |    | || |  | | . ` |\___ \ 
# | |___| |__| | | \ \| |____    | |__| |/ ____ \| |  | | |____    | |    | |__| | |\  | |____   | |   _| || |__| | |\  |____) |
#  \_____\____/|_|  \_\______|    \_____/_/    \_\_|  |_|______|   |_|     \____/|_| \_|\_____|  |_|  |_____\____/|_| \_|_____/ 

def game_new():

	global GAME

	GAME = obj_Game()

	GAME.game_start()

	game_main_loop()	

def game_load():

	global GAME, PLAYER, LIB, GUIDE_MAP

	with gzip.open('Save.pc', 'rb') as file:

		GAME, PLAYER, LIB = pickle.load(file)
		

	map_make_fov(GAME.current_map)
	create_map_lighting(GAME.current_map)
	map_create_pathfinding()

	for x in range(constants.GAME_TILES_X):
			for y in range(constants.GAME_TILES_Y):
				new_surface = pygame.Surface((constants.MAP_TILE_SIZE, constants.MAP_TILE_SIZE))

				new_surface.fill(GAME.user_map[x][y])

				GUIDE_MAP.blit(new_surface, (x * constants.MAP_TILE_SIZE, y * constants.MAP_TILE_SIZE))

	for obj in GAME.current_objects:

		obj.anim_init()

	PLAYER.creature.check_life()

	print("GAME LOADED")

def game_save():

	global GAME

	options_save()

	if GAME:

		for obj in GAME.current_objects:

			obj.animation_destroy()



		with gzip.open('Save.pc', 'wb') as file:
			pickle.dump([GAME, PLAYER, LIB], file)



		for obj in GAME.current_objects:

			obj.anim_init()

def load_map(map_name):
	
	with gzip.open(map_name + ".mp", 'rb') as file:

		loaded_map, objects = pickle.load(file)

		spawn_lib = gen_lib()

		map_tiles = []


		GAME.transition_to(loaded_map)

		for x in range(constants.GAME_TILES_X):
			for y in range(constants.GAME_TILES_Y):
				if objects[x][y] != None:
					print("FOUND AN ACTOR", objects[x][y])
					func = spawn_lib.gen_dict[ objects[x][y] ]
					item = func((x,y))
					print(item)
					GAME.current_objects.append(item)
    
def draw_game():

	global SURFACE_MAIN

	#todo clear
	SURFACE_MAIN.fill(constants.COLOR_DEFAULT_BG)
	SURFACE_MAP.fill(constants.COLOR_DEFAULT_BG)

	CAMERA.map_to_win((PLAYER.x, PLAYER.y))

	#draw_tile_at_coords(tiles.wall_1(0,0), 0, 0)

	CAMERA.update()

	display_rect = pygame.Rect( (0,0), (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT) )

	#todo draw map
	map_draw(GAME.current_map)
	#todo draw Characters
	for obj in sorted(GAME.current_objects, key = lambda obj :obj.depth, reverse = True):
		obj.draw()

		if obj.creature:
			dt = 0
			if CLOCK.get_fps() > 0.0:
				dt = 1 / CLOCK.get_fps()

			GAME.current_map[obj.x][obj.y][0].stand_on_tick(obj, dt)

			if GAME.current_map[obj.x][obj.y][1]:
				GAME.current_map[obj.x][obj.y][1].stand_on_tick(obj, dt)

		

		

	

	

	
	for drawable_class in ONGOING_FUNCTIONS:

		drawable_class.draw()

	for partice in PARTICLES:

		tile_p, target_p, single_target = partice
		if target_p:
			x_p = target_p.x
			y_p = target_p.y
		else:
			try:
				x_p, y_p, z_p = single_target
			except:
				x_p, y_p = single_target

		draw_tile_at_coords(tile_p, x_p, y_p)

	tile_dimming(GAME.current_map)


	SURFACE_MAIN.blit(SURFACE_MAP, (0,0), CAMERA.rect)
	draw_gui()

	for drawable_class in ONGOING_FUNCTIONS_GUI:

		drawable_class.draw()

	#draw_guide_map()

	#todo update display
	pygame.display.flip()

def game_main_loop():

	global MOUSE_CLICKED, PLAYER_TOOK_ACTION, TOTAL_TURNS

	game_quit = False

	player_action = "NONE"
	last_action= "NONE"

	game_message("Hello~and~Welcome: Game~made~by Thomas~Downes Version~" + constants.VERSION, constants.COLOR_GOLD, font = "FONT_DEFAULT")
	game_message("Thomas, Human Knight", font = "FONT_DEFAULT")

	for mod in GAME_MODS:
		mod.game_start()


	while not game_quit:

		MOUSE_CLICKED = False



		if player_action != "NONE":
			last_action = player_action

		literal_last_action = player_action


		if is_action_significant(PLAYER_TOOK_ACTION) == True and PLAYER_TOOK_ACTION != literal_last_action:
			player_action = PLAYER_TOOK_ACTION
			PLAYER_TOOK_ACTION = "NONE"


		else:
			PLAYER_TOOK_ACTION = "NONE"
			player_action = "NONE"

			can_act = True
			for func in ONGOING_FUNCTIONS_GUI:
				if not (hasattr(func, "prevents_action") and func.prevents_action == False):
					can_act = False
					break

			player_action = INPUT_HANDLER(can_act)



			if player_action == "CLICK":
				MOUSE_CLICKED = True

			if PLAYER_TOOK_ACTION != "NONE":
				player_action = PLAYER_TOOK_ACTION

			if player_action == "CLICK":
				MOUSE_CLICKED = True




		if player_action == "QUIT":
			game_quit = True



		if is_action_significant(player_action) == True:
			global TIME_PAST
			PLAYER.player.end_turn()
			TOTAL_TURNS += 1

			print(TIME_PAST)
			for obj in GAME.current_objects:

				for effect in obj.active_effects:	
					effect.each_turn()

				if obj.ai:

					if libtcod.map_is_in_fov(FOV_MAP_MONSTER, obj.x, obj.y) == True or obj.display_name.find("(Boss)") != -1:



						if obj.creature and obj.creature.type:
							
							obj.creature.time_past += TIME_PAST
							ONGOING_FUNCTIONS.append(obj.ai)

						
						map_calculate_fov_monster() 
						map_calculate_fov(True)

			
			

			for x in range(constants.GAME_TILES_X): #reduce the duration of all tiles on map level 2
				for y in range(constants.GAME_TILES_Y):
					if GAME.current_map[x][y][2]:

						try:
							GAME.current_map[x][y][2].duration -= TIME_PAST

							if GAME.current_map[x][y][2].duration <= 0:
								creature = map_check_for_creatures(x, y)
								if creature:
									GAME.current_map[x][y][2].step_off(creature, PLAYER)
								GAME.current_map[x][y][2] = None

						except:
							pass

			TIME_PAST = 0




		#if PLAYER.state == "DEAD":
			#game_quit = True




		map_calculate_fov()

		#todo draw
		draw_game()

		if NETWORK_LISTENER:
			connection.Pump()
			NETWORK_LISTENER.Pump()

		CLOCK.tick(constants.FPS_LIMIT)


	quit_game()

def loading_screen(text = "LOADING", font = "FONT_DEFAULT"):

	SURFACE_MAIN.fill((0, 0, 0))
	util.draw_text(SURFACE_MAIN, text, (constants.CAMERA_WIDTH / 2, constants.CAMERA_HEIGHT / 2), (255, 255, 255), font = font, center = True)

	pygame.display.flip()

def quit_game(save = True):

	print("GAME QUIT")

	loading_screen("GAME CLOSING, PLEASE WAIT", "FONT_MAIN_18")

	if NETWORK_LISTENER:
		connection.Send({"action": "leaveserver", "id": NETWORK_LISTENER.id})

	if save == True:

		options_save()
		game_save()

	pygame.quit()
	sys.exit(0)

def game_init():
	#todo init
	global SURFACE_MAIN, CLOCK, PLAYER, FOV_CALCULATE, MOUSE_CLICKED, ONGOING_FUNCTIONS, LIB, TARGET_TEXT, INPUT_HANDLER
	global ASSETS, PLAYER_TOOK_ACTION, PARTICLES, ACTIVE_EFFECTS, SURFACE_MAP, CAMERA, GAME, USER_OPTIONS, TIME_PAST
	global BURNING_TILES, TOTAL_TURNS, NETWORK_LISTENER, TILE_DICT, GEN_DICT, ONGOING_FUNCTIONS_GUI, GAME_MODS, GUIDE_MAP, INPUT_AGAIN

	pygame.init()
	pygame.display.set_caption(constants.GAME_TITLE)
	pygame.key.set_repeat(200, 70)

	TIME_PAST = 0

	SURFACE_MAIN = pygame.display.set_mode( (constants.CAMERA_WIDTH, constants.CAMERA_HEIGHT) )

	SURFACE_MAP = pygame.Surface((constants.GAME_TILES_X * constants.GAME_TILE_SIZE, constants.GAME_TILES_Y * constants.GAME_TILE_SIZE))

	GUIDE_MAP = pygame.Surface((constants.GAME_TILES_X * constants.MAP_TILE_SIZE, constants.GAME_TILES_X * constants.MAP_TILE_SIZE))

	#ASSETS = anims()

	libtcod.namegen_parse("Data/mingos_demon.cfg")
	libtcod.namegen_parse("Data/jice_norse.cfg")
	libtcod.namegen_parse("Data/jice_norse.cfg")
	libtcod.namegen_parse("Data/mingos_standard.cfg")
	libtcod.namegen_parse("Data/mingos_dwarf.cfg")

	LIB = lib()

	INPUT_HANDLER = game_handle_input

	try:
		options_load()
	except:
		USER_OPTIONS = obj_options()

	USER_OPTIONS.sound_adjust()

	CAMERA = obj_camera()

	CLOCK = pygame.time.Clock()		

	FOV_CALCULATE = True

	MOUSE_CLICKED = False

	PLAYER = None

	PARTICLES = []

	ONGOING_FUNCTIONS = []

	ONGOING_FUNCTIONS_GUI = []

	ACTIVE_EFFECTS = []

	GAME = None

	BURNING_TILES = []

	PLAYER_TOOK_ACTION = "NONE"

	TARGET_TEXT = None

	TOTAL_TURNS = 0

	NETWORK_LISTENER = None

	INPUT_AGAIN = CLOCK.get_time()

	TILE_DICT = tile_dict()
	GEN_DICT = gen_lib()

	create_loot_tables()
	create_affix_tables()

	GAME_MODS = []

	constants.post_init_load()


	#PARTICLES = [(tiles.p_confused(), GAME.current_map[6][1])]

	
	#game_message("Hello~and~Welcome: Game~made~by Thomas~Downes Version~1.0", constants.COLOR_GOLD, font = "FONT_DEFAULT")
	#game_message("Thomas, Human Knight", font = "FONT_DEFAULT")

def multiplayer_init():
	global NETWORK_LISTENER, GAME

	GAME = obj_Game()
	f = open("Address.txt", "r")
	address=f.read()

	if not address:
	    host, port= "localhost", 8000

	else:
		address = address.replace(" ", "")
		host,port=address.split(":")

	NETWORK_LISTENER = obj_network_listener(host, int(port))
	print "attempting connection to host:", host, "port:", port
	#connection.Send({"action": "myaction", "message": "hello client!"})




def game_try_load():

	#try:
	game_load()
	game_main_loop()
	#except:
		#main_menu()
		#util.draw_text(SURFACE_MAIN, "Failed to load game", (0,0), constants.COLOR_RED)

def options_save():

	with gzip.open('Preferences.cfg', 'wb') as file:

			pickle.dump(USER_OPTIONS, file)

def options_load():

	global USER_OPTIONS

	with gzip.open('Preferences.cfg', 'rb') as file:

		USER_OPTIONS = pickle.load(file)

def game_message(message, color = constants.COLOR_WHITE, font = "FONT_DEFAULT"):



	GAME.message_log.append((message, color, font))
	#
	#

def is_action_significant(action):

	result = True

	insignificant_actions = ["NONE", "CLICK", "LOOK", "QUIT", "TARGETED_SPELL", "NEXT_LEVEL", "RENAME", "FAILED_ACTION"] 

	for i_action in insignificant_actions:
		if action == i_action:
			result = False

	return result

class console():

	rect_w = 220
	rect_h = 20

	x_loc = 0
	y_loc = 100

	

	def __init__(self):

		self.commands = {
		"load_boss_1" : (load_map, ["Boss_1"]),
		"tgm" : (PLAYER.player.god_mode, []),
		"kila" : (USER_OPTIONS.toggle_easy, [PLAYER]),
		"not_dead" : (util.easy_return, ["CANCEL"]),
		"down" : (GAME.transition_next, None),
		"up" : (GAME.transition_previous, None),
		"ghost" : (remove_blocking, None),
		"save" : (game_save, None),
		"player_haste" : (PLAYER.player.set_haste, None),
		"loot" : (PLAYER.player.spawn_loot, None),
		"quit" : (quit_game, [False]),
		"target_cheat": (USER_OPTIONS.toggle_target_help, [PLAYER]),
		"gen_item" : (console_make_item, None),
		"load_map" : (load_map, None),
		"learn_magic" : (spells.learn_all_spells, None)
		}

		self.name_box = ui_inputbox(self.x_loc, self.y_loc, self.rect_w, self.rect_h, pos_from_center = True)

		ONGOING_FUNCTIONS_GUI.append(self)

	def draw(self):

		result = "NONE"
		enter = False

	#have text_box handle user input
		for event in GAME_EVENT_LIST:
			
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
					self.name_box.handle_event(event)

			elif event.type == pygame.KEYDOWN:

				if event.key == pygame.K_ESCAPE:
					ONGOING_FUNCTIONS_GUI.remove(self)

				elif event.key == pygame.K_RETURN:
					enter = True
					ONGOING_FUNCTIONS_GUI.remove(self)

				else:
					self.name_box.handle_event(event)


		self.name_box.update()

	#deal with input
		if enter == True:

		#determine if we are using debugging or not
			text = self.name_box.text
			func = None


			ary = text.split('.', 1)

			if ary[0] == "db":
				debug = True

			else:
				debug = False

		#get relevent text from input / remove "db" from input
			text = ary[-1]#elem 1 if debugging, elem 2 if not

		#split text into command, then each parameter
			ary2 = text.split(" ")

			if debug == True: #will crash if command doesnt work, allows reading of crash reports

				if len(ary2) > 1: #if parameters

					text = ary2[0]

					func, params = self.commands[text]
					if not params:
						params = []


					for c in range(1, len(ary2)):#add each of the parameters to params list
						params.append(ary2[c])


				else: #if no user specified parameters
					func, params = self.commands[text]

				if params and len(params) > 0:		
					func(*params)
				else:
					func()


			else: # not debug
				try:

					if len(ary2) > 1: #if parameters

						text = ary2[0]

						func, params = self.commands[text]
						if not params:
							params = []


						for c in range(1, len(ary2)):#add each of the parameters to params list
							params.append(ary2[c])


					else: #if no user specified parameters
						func, params = self.commands[text]


					if params and len(params) > 0:		
						func(*params)
					else:
						func()


				except:
					#there was an invalid command or parameter
					print "Invalid Command", self.name_box.text

		

		

			
		else:
			self.name_box.draw(SURFACE_MAIN)




def open_console_main_menu():

	name_box = ui_inputbox(0, 100, 220, 20, pos_from_center = True)
	result = "NONE"


	if NETWORK_LISTENER:
		commands = {

		"mp" : (multiplayer_init, None),
		"server clear" : (NETWORK_LISTENER.server_clear_cache, None),
		"server close" : (NETWORK_LISTENER.close, None)

		}

	else:
		commands = {

		"mp" : (multiplayer_init, None),

		}



	done = False
	while done == False:


		enter = False

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit_game()

			

			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					MOUSE_CLICKED = True
					name_box.handle_event(event)

			elif event.type == pygame.KEYDOWN:

				if event.key == pygame.K_ESCAPE:
					done = True

				elif event.key == pygame.K_RETURN:
					enter = True
					done = True

				else:
					name_box.handle_event(event)


		name_box.update()

		if enter == True:
		
			try:

				func, params = commands[str(name_box.text)]
				if params:
					result = func(*params)
				else:
					result = func()
			except:
				print("invalid command: " + str( name_box.text ) )
			

		name_box.draw(SURFACE_MAIN)

		CLOCK.tick(constants.FPS_LIMIT)

		pygame.display.flip()

	return result

def error_message(message):
	print "***", message, "***"

def prevent_input(time):
	global INPUT_AGAIN
	INPUT_AGAIN = pygame.time.get_ticks() + (time * 1000)

def game_handle_input(can_act = True):
	#todo player input
	global FOV_CALCULATE, MOUSE_CLICKED, ONGOING_FUNCTIONS, GAME_EVENT_LIST

	player_can_act = False
	if len(ONGOING_FUNCTIONS) == 0:
		player_can_act = True

	#if INPUT_AGAIN > pygame.time.get_ticks():
		#player_can_act = False

	events_list = pygame.event.get()
	GAME_EVENT_LIST = events_list


	#todo process input
	for event in events_list:

		if event.type == pygame.QUIT:
			return "QUIT"

		if event.type == pygame.MOUSEBUTTONDOWN:
			if event.button == 1:
				#MOUSE_CLICKED = True
				return ("CLICK")

				



		if event.type == pygame.KEYDOWN:

			if event.unicode == USER_OPTIONS.key_look and len(ONGOING_FUNCTIONS_GUI) == 0:
				found = False

				for func in ONGOING_FUNCTIONS:
					if func.__class__.name == "select":
						ONGOING_FUNCTIONS.remove(func)
						found = True

				if found == False:
					select()

				GAME_EVENT_LIST.remove(event)
				return "LOOK"

			elif event.unicode == USER_OPTIONS.key_map:


				if len(ONGOING_FUNCTIONS_GUI) == 0:

					for item in PLAYER.container.inventory:
						if item.name == "Cartography tools":
							ONGOING_FUNCTIONS_GUI.append(guide_map())
							GAME_EVENT_LIST.remove(event)
							break

				else:
					
					for obj in ONGOING_FUNCTIONS_GUI:
						print obj.__class__.__name__
						if obj.__class__.__name__ == "guide_map":
							ONGOING_FUNCTIONS_GUI.remove(obj)
							GAME_EVENT_LIST.remove(event)
							break


			if player_can_act == True and can_act == True:

				if event.unicode == USER_OPTIONS.key_rest:
					GAME_EVENT_LIST.remove(event)
					TIME_PAST = min(PLAYER.creature.move_speed, PLAYER.creature.attack_speed)
					return "REST"
				if event.unicode == USER_OPTIONS.key_w:
					PLAYER.creature.move(0,-1, True)
					FOV_CALCULATE = True
					GAME_EVENT_LIST.remove(event)
					return "MOVED"
				elif event.unicode == USER_OPTIONS.key_s:
					PLAYER.creature.move(0,1, True)
					FOV_CALCULATE = True
					GAME_EVENT_LIST.remove(event)
					return "MOVED"
				elif event.unicode == USER_OPTIONS.key_a:
					PLAYER.creature.move(-1,0, True)
					FOV_CALCULATE = True
					GAME_EVENT_LIST.remove(event)
					return "MOVED"
				elif event.unicode == USER_OPTIONS.key_d:
					PLAYER.creature.move(1,0, True)
					FOV_CALCULATE = True
					GAME_EVENT_LIST.remove(event)
					return "MOVED"

				elif event.unicode == USER_OPTIONS.key_interact:

					GAME_EVENT_LIST.remove(event)
					return map_interact(PLAYER.x, PLAYER.y, PLAYER)

					
								
					
				elif event.unicode == USER_OPTIONS.key_drop:
					if len(PLAYER.container.inventory) > 0:
						PLAYER.container.inventory[-1].item.drop(PLAYER.x, PLAYER.y)
						GAME_EVENT_LIST.remove(event)
						return "ITEM_ACTION"




				elif event.unicode == USER_OPTIONS.key_console:
					GAME_EVENT_LIST.remove(event)
					console()

				elif event.unicode == USER_OPTIONS.key_game_info:
					GAME_EVENT_LIST.remove(event)
					print "map id:", GAME.current_map_id

					#for obj in GAME.current_objects:
						#print obj.display_name, ":", obj.id

					print "PLAYER:",  PLAYER.x, PLAYER.y

					try:
						print str(GAME.current_map[PLAYER.x][PLAYER.y][0].get_tile_info())
					except:
						print "Unable to find tile info depth:0"

					try:
						print str(GAME.current_map[PLAYER.x][PLAYER.y][1].get_tile_info())
					except:
						print "Unable to find tile info depth:1"

					print "Area Level:", GAME.area_level


				if mouse_in_window(constants.MENU_WIDTH, 0, constants.CAMERA_WIDTH - constants.MENU_WIDTH * 2, constants.CAMERA_HEIGHT) != None:
				#if inside game window, see if spell is bound to key

					for line, spell_bind in enumerate(USER_OPTIONS.spell_key_binds):
						if event.unicode == spell_bind and len(PLAYER.creature.active_spells) >= line:
							PLAYER.creature.active_spells[line].cast()
							GAME_EVENT_LIST.remove(event)

				




	return "NONE"




















 #  _   _  ____  _   _        ______ _    _ _   _  _____ _______ _____ ____  _   _  _____ 
 # | \ | |/ __ \| \ | |      |  ____| |  | | \ | |/ ____|__   __|_   _/ __ \| \ | |/ ____|
 # |  \| | |  | |  \| |______| |__  | |  | |  \| | |       | |    | || |  | |  \| | (___  
 # | . ` | |  | | . ` |______|  __| | |  | | . ` | |       | |    | || |  | | . ` |\___ \ 
 # | |\  | |__| | |\  |      | |    | |__| | |\  | |____   | |   _| || |__| | |\  |____) |
 # |_| \_|\____/|_| \_|      |_|     \____/|_| \_|\_____|  |_|  |_____\____/|_| \_|_____/ 


def Run():

	try:
		CLOCK.tick()
	except:
		game_init()
		
	main_menu(GAME_MODS, restart_music = True)




	
