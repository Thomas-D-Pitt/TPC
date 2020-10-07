
import Game
import constants
import pygame

Mod_id = 5555 #a mod_id and version must be declared in order for the mod to load
Mod_version = 1.0 #the variables are case sensative and must be spelled exactly as they are here

def effect_heal_caster(target, caster, value):

	#you can write your own function, however some have specific variables that they must recive
	#in this case it must recive target and caster as parameters followed by whatever you save to the objects hit_effect_permenent_params
	return Game.effect_heal(caster, caster, value)

def gen_mod_sword(coords):

	x,y = coords
	#any of the parameters for creating an object can be set like this: (unless I forget to update the list at some point)
	equipment_com = {"attack_max_bonus":2, "attack_min_bonus":2, "slot":"right_hand",
	 "hit_effect_permenent": effect_heal_caster, "hit_effect_permenent_params":[5], "not a param":"will be ignored"}
	#hit_effect_permenent_params must be None or an array
	#hit_effect_permenent can be a function in this file or it can be a function in the game ex) Game.effect_heal
	item = {"action":"EQUIP", "value":50, "size":1}

	actor = {"name":"Mod Sword", "animation_key":"GEM_1", "depth":constants.DEPTH_ITEM}

	return {"equipment":equipment_com, "item":item, "actor":actor, "coords":coords}
	#equipment:{}, item:{}, reagent:{}, ammo:{}, potion:{}, actor:{}, coords:(x,y)

def gen_mod_skelly(coords):

	x,y = coords

	creature_com = {"name_instance":"mod skelly", "level":2,}
	ai = Game.ai_chase()

	actor = {"name":"Mod skelly", "animation_key":"your_bosses_anim_key", "depth":constants.DEPTH_CREATURES}

	return {"creature":creature_com, "actor":actor, "ai":ai, "coords":coords}
	#equipment:{}, item:{}, reagent:{}, ammo:{}, potion:{}, actor:{}, coords:(x,y)

def test():

	print "test"

def init():

	#items can be added to spawn lists like this:

	# Game.tier_0 += [(Game.gen_melee, 1500)]#changes drops to ~99% melee weapons
	# Game.weapon_list_0 += [(gen_mod_sword, 3000)]#changes gen_melee() to call gen_mod_sword() ~99% of the time 
	# Game.weapon_list_1 += [(gen_mod_sword, 3000)]
	# Game.weapon_list_2 += [(gen_mod_sword, 3000)]
	# Game.weapon_list_3 += [(gen_mod_sword, 3000)]
	# Game.weapon_list_4 += [(gen_mod_sword, 3000)]

	Game.enemy_list_0 += [(gen_mod_skelly, 3000)]
	Game.enemy_list_1 += [(gen_mod_skelly, 3000)]

	#Game functions can be overwritten like this:
	#Game.Run = test

	constants.anim_dict["your_bosses_anim_key"] = [pygame.image.load("Data/Logo.png")]

def game_start():
	
	print "game started"

