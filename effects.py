import constants
import Game
#  ______ ______ ______ ______ _____ _______ _____    __  _____  _    _ _____         _______ _____ ____  _   _  __  
# |  ____|  ____|  ____|  ____/ ____|__   __/ ____|  / / |  __ \| |  | |  __ \     /\|__   __|_   _/ __ \| \ | | \ \ 
# | |__  | |__  | |__  | |__ | |       | | | (___   | |  | |  | | |  | | |__) |   /  \  | |    | || |  | |  \| |  | |
# |  __| |  __| |  __| |  __|| |       | |  \___ \  | |  | |  | | |  | |  _  /   / /\ \ | |    | || |  | | . ` |  | |
# | |____| |    | |    | |___| |____   | |  ____) | | |  | |__| | |__| | | \ \  / ____ \| |   _| || |__| | |\  |  | |
# |______|_|    |_|    |______\_____|  |_| |_____/  | |  |_____/ \____/|_|  \_\/_/    \_\_|  |_____\____/|_| \_|  | |

#effects duration   
# must be passed a target

class blind():
	#only works on player, reduces field of view
	#yes i know theres a scroll that uses this i left it in there for testing ill take it out later
	def __init__(self, target, caster, duration, sight_reduce_by):

		self.duration = duration
		self.sight_subtractor = sight_reduce_by
		self.target = target
		self.caster = caster

		self.id = "blind"


		self.on_start()

	def on_start(self):
		self.target.sight_multiplier -= self.sight_subtractor
		
		Game.FOV_CALCULATE = True
		self.target.active_effects.append(self)

	def each_turn(self):
		if self.duration != -1:
			self.duration-=1

		if self.duration != -1 and self.duration <= 0:
			self.on_end()
			pass



	def on_end(self):
		self.target.sight_multiplier+=self.sight_subtractor
		Game.FOV_CALCULATE = True
		try:
			self.target.active_effects.remove(self) # all effects must be passed a target#
		except:
			pass



	def get_critical_properties(self):
		return [self.duration, self.sight_subtractor]

class dot_posion():
	#deals damage over time
	def __init__(self, target, caster, tick_damage, duration, damage_every_x_turns = 3, source_id = None):

		self.duration = duration
		self.tick_damage = tick_damage
		self.target = target
		self.damage_every_x_turns = damage_every_x_turns
		self.turns_until_tick = self.damage_every_x_turns
		self.id = "effects.dot_po"
		self.caster = caster

		self.source_id = source_id

		self.on_start()



	def on_start(self):

		if self.source_id:
			for effect in self.target.active_effects:
				if effect.id == "dot_posion" and self.source_id == effect.source_id:
					effect.on_end()

		self.target.active_effects.append(self)
		self.target.creature.message("You are Posioned", color = constants.COLOR_GREEN, only_when_player = True)

	def each_turn(self):
		self.duration-=1

		if self.duration <= 0:
			self.on_end()

		self.turns_until_tick -=1

		if self.turns_until_tick <= 0:
			if self.target and self.target.creature:
				self.target.creature.take_damage(0, posion_damage = self.tick_damage, source = "posion (dot)")
				self.turns_until_tick = self.damage_every_x_turns
			else:
				self.on_end()



	def on_end(self):
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.tick_damage, self.duration, self.damage_every_x_turns]

class bleach():
	#if the player drinks it, it does a large amount of damage, otherwise does a small amount of posion damage over time
	def __init__(self, target, caster, tick_damage = 8, duration = 4, damage_every_x_turns = 3):

		self.duration = duration
		self.tick_damage = tick_damage
		self.target = target
		self.damage_every_x_turns = damage_every_x_turns
		self.turns_until_tick = self.damage_every_x_turns
		self.id = "bleach"
		self.caster = caster

		self.on_start()

		

	def on_start(self):

		self.target.active_effects.append(self)

		if self.target == PLAYER:
			self.target.creature.take_damage(self.tick_damage*5, "It was bleach...", source = "bleach (instant)")

	def each_turn(self):
		self.duration-=1

		if self.duration <= 0:
			self.on_end()

		self.turns_until_tick -=1

		if self.turns_until_tick <= 0 and self.target and self.target.creature:
			self.target.creature.take_damage(0, posion_damage = self.tick_damage, source = "bleach (dot)")
			self.turns_until_tick = self.damage_every_x_turns



	def on_end(self):
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.tick_damage, self.duration, self.damage_every_x_turns]

class drunk():
	#gives some food and reduces dexterity
	def __init__(self, target, caster, food, dex_subtractor, duration):

		self.duration = duration
		self.food = food
		self.target = target
		self.dex_subtractor = dex_subtractor
		self.caster = caster

		self.id = "drunk"

		self.on_start()

	def on_start(self):

		duplicate = False

		for active_effect in self.target.active_effects:
			if active_effect.id == "drunk":
				active_effect.duration += self.duration
				duplicate = True
				break

		if duplicate == False:

			self.target.active_effects.append(self)

			self.target.creature.dexterity -= self.dex_subtractor

			if self.target == PLAYER:
					self.target.creature.message("You are drunk", color = constants.COLOR_PINK, only_when_player = True)

					eat(self.target, self.caster, self.food)


		elif self.target == PLAYER:
			self.target.player.food += self.food



	def each_turn(self):
		self.duration-=1

		if self.duration <= 0:
			self.on_end()




	def on_end(self):
		if self.target and self.target.creature:
			self.target.creature.dexterity += self.dex_subtractor
			self.target.creature.message( "You feel sober", color = constants.COLOR_PINK, only_when_player = True)
			self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.food, self.dex_subtractor, self.duration]

class reduce_luck():
	#you should be able to figure this one out youself, go ahead buddy you can get it
	def __init__(self, target, caster, amount, duration = None):

		self.duration = duration
		self.target = target
		self.amount = amount
		self.id = "reduce_luck"
		self.caster = caster

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.luck -= self.amount

	def each_turn(self):
		if self.duration:
			self.duration-=1

		if self.duration and self.duration <= 0:
			self.on_end()




	def on_end(self):
		self.target.creature.luck += self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.amount, self.duration]

class hot():
	#restores health over time
	def __init__(self, target, caster, tick_amount, duration, heal_every_x_turns = 3):

		self.duration = duration
		self.tick_amount = tick_amount
		self.target = target
		self.heal_every_x_turns = heal_every_x_turns
		self.turns_until_tick = self.heal_every_x_turns
		self.id = "hot"
		self.caster = caster

		self.on_start()



	def on_start(self):

		self.target.active_effects.append(self)
		self.target.creature.message("You feel good", color = constants.COLOR_GOLD, only_when_player = True)

	def each_turn(self):
		self.duration-=1

		if self.duration <= 0:
			self.on_end()

		self.turns_until_tick -=1

		if self.turns_until_tick <= 0:
			if self.target and self.target.creature:
				self.target.creature.heal(self.tick_amount)
				self.turns_until_tick = self.heal_every_x_turns
			else:
				self.on_end()

	def on_end(self):
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.tick_amount, self.duration, self.heal_every_x_turns]

class on_fire():
	#restores health over time
	def __init__(self, target, caster, tick_amount, duration, damage_every_x_turns = 1, source_id = None):

		self.duration = duration
		self.tick_damage = tick_amount
		self.target = target
		self.damage_every_x_turns = damage_every_x_turns
		self.turns_until_tick = self.damage_every_x_turns
		self.id = "on_fire"
		self.caster = caster
		self.source_id = source_id

		self.on_start()



	def on_start(self):

		self.target.active_effects.append(self)
		self.target.creature.message("You are on fire", color = constants.COLOR_RED, only_when_player = True)

	def each_turn(self):
		if self.duration:

			self.duration-=1

			if self.duration <= 0:
				self.on_end()

		self.turns_until_tick -=1

		if self.turns_until_tick <= 0:
			if self.target and self.target.creature:
				self.target.creature.take_damage(0, fire_damage = self.tick_damage, source = "on fire")
				self.turns_until_tick = self.damage_every_x_turns
			else:
				self.on_end()

	def on_end(self):
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.tick_amount, self.duration, self.damage_every_x_turns]

class full_dmg_hot():
	#reduces target health to 1 then heals over time
	def __init__(self, target, caster, duration, heal_every_x_turns = 3):

		self.duration = duration
		
		self.target = target

		self.id = "full_dmg_hot"
		self.caster = caster

		if self.target.creature:

			self.tick_amount = self.target.creature.maxhp / (self.duration / heal_every_x_turns)

			self.heal_every_x_turns = heal_every_x_turns
			self.turns_until_tick = self.heal_every_x_turns

			self.on_start()
		



	def on_start(self):
		self.target.active_effects.append(self)
		self.target.creature.message("You're feel sick", color = constants.COLOR_BLUE, only_when_player = True) 

		if self.target.creature and self.target.player:
			self.target.creature.take_damage(self.target.creature.hp - 1, source = "damage from full_dmg_hot")

		elif self.target.creature:
			self.target.creature.take_damage(self.target.creature.hp / 2, source = "damage from full_dmg_hot")

	def each_turn(self):
		self.duration-=1

		if self.duration <= 0:
			self.on_end()

		self.turns_until_tick -=1

		if self.turns_until_tick <= 0:
			if self.target and self.target.creature:
				self.target.creature.heal(self.tick_amount)
				self.turns_until_tick = self.heal_every_x_turns
			else:
				self.on_end()

	def on_end(self):
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.duration, self.heal_every_x_turns]

class weakness():
	#increases target's luck
	def __init__(self, target, caster, percent_reduction, duration = None):

		self.duration = duration
		self.target = target
		self.amount = percent_reduction
		self.id = "weakness"
		self.caster = caster

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.damage_multiplier -= self.amount

	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()

	def on_end(self):
		self.target.creature.damage_multiplier += self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.amount, self.duration]

class haste():
	#increases target's luck
	def __init__(self, target, caster, haste_change, duration = None):

		self.duration = duration
		self.target = target
		self.amount = percent_reduction
		self.id = "haste"
		self.caster = caster

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.haste += self.amount

	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()

	def on_end(self):
		self.target.creature.haste -= self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.amount, self.duration]

class luck():
	#increases target's luck
	def __init__(self, target, caster, amount, duration = None):

		self.duration = duration
		self.target = target
		self.amount = amount
		self.id = "luck"
		self.caster = caster

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.luck += self.amount

	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()

	def on_end(self):
		self.target.creature.luck -= self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.amount, self.duration]

class strength():

	def __init__(self, target, caster, amount, duration = None):

		self.duration = duration
		self.target = target
		self.amount = amount
		self.id = "strength"
		self.caster = caster

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.Strength += self.amount



	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()


	def on_end(self):
		self.target.creature.str -= self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.amount, self.duration]

class dexterity():

	def __init__(self, target, caster, amount, duration = None):

		self.duration = duration
		self.target = target
		self.amount = amount
		self.id = "dexterity"
		self.caster = caster

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.dexterity += self.amount



	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()


	def on_end(self):
		self.target.creature.dexterity -= self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.amount, self.duration]

class wisdom():

	def __init__(self, target, caster, amount, duration = None):

		self.duration = duration
		self.target = target
		self.amount = amount
		self.id = "wisdom"
		self.caster = caster

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.wisdom += self.amount



	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()


	def on_end(self):
		self.target.creature.wisdom -= self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target #

	def get_critical_properties(self):
		return [self.amount, self.duration]

class revered_movement():
	#movement input is reversed
	def __init__(self, target, caster, duration = None):

		self.duration = duration
		self.target = target
		self.caster = caster

		self.id = "revered_movement"

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		if self.target == PLAYER:
			self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.move_multiplier_x = self.target.creature.move_multiplier_x * -1
		self.target.creature.move_multiplier_y = self.target.creature.move_multiplier_y * -1



	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()


	def on_end(self):

		self.target.creature.move_multiplier_x = self.target.creature.move_multiplier_x * -1
		self.target.creature.move_multiplier_y = self.target.creature.move_multiplier_y * -1

		self.target.active_effects.remove(self) # all effects must be passed a target #

	def get_critical_properties(self):
		return [self.amount, self.duration]

class intelligence():

	def __init__(self, target, caster, amount, duration = None):

		self.duration = duration
		self.target = target
		self.amount = amount
		self.id = "intelligence"
		self.caster = caster
		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.intelligence += self.amount



	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()


	def on_end(self):
		self.target.creature.intelligence -= self.amount
		self.target.active_effects.remove(self) # all effects must be passed a target #

	def get_critical_properties(self):
		return [self.amount, self.duration]

class boost_resistances():
	#takes in resistances as tuple and adjusts targets resistences accordingly
	def __init__(self, target, caster, (fire, posion, lightning, cold), duration = None):

		self.duration = duration
		self.target = target
		self.fire, self.posion, self.lightning, self.cold = (fire, posion, lightning, cold)
		self.id = boost_resistances
		self.caster = caster
		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.object_update(self.target, new_effect = self)

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		self.target.creature.fire_resistance += self.fire
		self.target.creature.posion_resistance += self.posion
		self.target.creature.lightning_resistance += self.lightning
		self.target.creature.cold_resistance += self.cold



	def each_turn(self):

		if self.duration:
			self.duration-=1

			if self.duration <= 0:
				self.on_end()


	def on_end(self):
		self.target.creature.fire_resistance -= self.fire
		self.target.creature.posion_resistance -= self.posion
		self.target.creature.lightning_resistance -= self.lightning
		self.target.creature.cold_resistance -= self.cold
		self.target.active_effects.remove(self) # all effects must be passed a target #

	def get_critical_properties(self):
		return [(self.fire, self.posion, self.lightning, self.cold), self.duration]

class dire_bat_posion():
	#posion damage over time
	def __init__(self, target, caster, tick_damage = 8, duration = 12, damage_every_x_turns = 3):

		self.duration = duration
		self.tick_damage = tick_damage
		self.target = target
		self.damage_every_x_turns = damage_every_x_turns
		self.turns_until_tick = self.damage_every_x_turns
		self.caster = caster
		self.id = "dire_bat_posion"

		self.on_start()

	def on_start(self):
		self.target.active_effects.append(self)
		self.target.creature.message("You are Posioned", color = constants.COLOR_GREEN, only_when_player = True)

	def each_turn(self):
		self.duration-=1

		if self.duration <= 0:
			self.on_end()

		self.turns_until_tick -=1

		if self.turns_until_tick <= 0:
			self.target.creature.take_damage(0, posion_damage = self.tick_damage, source = "bat posion")
			self.turns_until_tick = self.damage_every_x_turns



	def on_end(self):
		self.target.active_effects.remove(self) # all effects must be passed a target#

	#def get_critical_properties(self):
		#pass

class worm_latch_on():

	def __init__(self, target, caster, tick_damage = 8, duration = 3, damage_every_x_turns = 1):

		self.duration = duration
		self.tick_damage = tick_damage
		self.target = target
		self.damage_every_x_turns = damage_every_x_turns
		self.turns_until_tick = self.damage_every_x_turns
		self.caster = caster

		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)
		self.target.creature.take_damage(1, "The worm latches onto you", color = constants.COLOR_GREEN, source = "worm latch (instant)")


	def each_turn(self):
		self.duration-=1

		if self.duration <= 0:
			self.on_end()

		self.turns_until_tick -=1

		if self.turns_until_tick <= 0:
			if self.target.creature and self.caster.creature:
				self.target.creature.take_damage(self.tick_damage, source = "worm latch (dot)")

			if self.caster.creature:
				self.caster.creature.heal(self.tick_damage)
			self.turns_until_tick = self.damage_every_x_turns






	def on_end(self):
		self.target.active_effects.remove(self) # all effects must be passed a target#

class magic_nullify():
	#reduces target mana
	def __init__(self, target, caster, duration = 3):

		self.duration = duration
		self.target = target
		self.id = "magic_nullify"
		self.caster = caster
		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)
		self.target.creature.message("your magic weakens", color = constants.COLOR_PINK, only_when_player = True)
		self.characters_old_mana = self.target.creature.mana
		self.target.creature.mana = 0


	def each_turn(self):
		pass

	def on_end(self):
		self.target.creature.mana = self.characters_old_mana
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.duration]

class invincible():
	#greatly increases armor 
	def __init__(self, target, caster, duration = 3):

		self.duration = duration
		self.target = target
		self.id = "invincible"
		self.caster = caster
		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)
		self.target.creature.message("you feel unstoppable", color = constants.COLOR_PINK, only_when_player = True)
		self.characters_old_armor = self.target.creature.raw_defense
		self.target.creature.raw_defense = 999


	def each_turn(self):
		
		self.duration-= 1

		if self.duration <= 0:
			self.on_end()


	def on_end(self):

		if self.target and self.target.creature:
			self.target.creature.raw_defense = self.characters_old_armor
			
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.duration]

class burning_tile():
	#deals damage when stading on tile that is in its damaging phase
	def __init__(self, target, caster, coord, damage = 10):

		self.caster = caster
		self.target = target
		self.x, self.y = coord

		for tile in Game.BURNING_TILES:
			if tile.x == self.x and tile.y == self.y:
				tile.on_end()

		Game.BURNING_TILES.append(self)

		self.damage = damage
		self.duration = 2
		self.anim = tiles.p_fire(self.x, self.y, 1)

		#if self.tile.block_path == False:
		self.on_start()

	def on_start(self):
		global PARTICLES
		if self.target:
			self.target.active_effects.append(self)
		

		Game.PARTICLES.append((self.anim, None, (self.x, self.y)))

		hit = Game.map_check_for_creatures(self.x, self.y)
		if hit:
			hit.creature.take_damage(0, fire_damage = self.damage, source = "burning tile")


	def each_turn(self):

		self.duration -= 1

		hit = Game.map_check_for_creatures(self.x, self.y)

		if hit:
			hit.creature.take_damage(0, fire_damage = self.damage, source = "burning tile")

		if self.duration <= 0:
			self.on_end()


	def on_end(self):
		try:
			self.target.active_effects.remove(self) # all effects must be passed a target #
		except:
			pass

		try:
			Game.PARTICLES.remove((self.anim, None, (self.x, self.y)))
		except:
			pass

class learn_skill():
	
	def __init__(self, target, caster, spell_params, duration = None):

		self.duration = duration
		self.target = target
		self.id = "learn_skill"
		self.caster = caster
		self.spell_params = spell_params
		self.spell_name = spell_params[0]
		self.on_start()

	def on_start(self):

		self.target.active_effects.append(self)

		learn_spell(self.target, self.caster, *self.spell_params)


	def each_turn(self):

		if self.duration:
			self.duration-= 1

			if self.duration <= 0:
				self.on_end()


	def on_end(self):

		unlearn_spell(self.target, self.caster, self.spell_name)
			
		self.target.active_effects.remove(self) # all effects must be passed a target#

	def get_critical_properties(self):
		return [self.duration]

def worm_latch_on(target, caster):

	effect = worm_latch_on(target, caster)

class dict:

	def __init__(self):

		dic = {


		"blind" : blind,
		"dot_posion" : dot_posion,
		"bleach" : bleach,
		"drunk" : drunk,
		"reduce_luck" : reduce_luck,
		"hot" : hot,
		"on_fire" : on_fire,
		"full_dmg_hot" : full_dmg_hot,
		"weakness" : weakness,
		"haste" : haste,
		"luck" : luck,
		"strength" : strength,
		"dexterity" : dexterity,
		"wisdom" : wisdom,
		"intelligence" : intelligence,
		"boost_resistances" : boost_resistances,
		"magic_nullify" : magic_nullify,
		"invincible" : invincible,
		"learn_skill" : learn_skill,


		}

#  ______ ______ ______ ______ _____ _______ _____    __  _____ _   _  _____ _______       _   _ _______  __  
# |  ____|  ____|  ____|  ____/ ____|__   __/ ____|  / / |_   _| \ | |/ ____|__   __|/\   | \ | |__   __| \ \ 
# | |__  | |__  | |__  | |__ | |       | | | (___   | |    | | |  \| | (___    | |  /  \  |  \| |  | |     | |
# |  __| |  __| |  __| |  __|| |       | |  \___ \  | |    | | | . ` |\___ \   | | / /\ \ | . ` |  | |     | |
# | |____| |    | |    | |___| |____   | |  ____) | | |   _| |_| |\  |____) |  | |/ ____ \| |\  |  | |     | |
# |______|_|    |_|    |______\_____|  |_| |_____/  | |  |_____|_| \_|_____/   |_/_/    \_\_| \_|  |_|     | |
#                                                    \_\                                                  /_/ 
    # effects instant


# must be passed a target and caster as first & second params

def heal(target, caster, value):
	#heals target
	
	target.creature.heal(value)

	return True

def eat(target, caster, value):
	#if the target is a player, give it food
	if target.player:

		target.player.food+=value

		if Game.NETWORK_LISTENER:
			Game.NETWORK_LISTENER.player_ate(value)

def instant_posion(target, caster, value):
	#deals instant posion damage to target
	target.creature.take_damage(0, "ITS POSION", "", posion_damage = value, source = "posion (instant)")

	return True

def scorpion_posion(target, caster, value = 15):

	target.creature.take_damage(0, "The scorpion posions you", posion_damage = value, source = "scorpion posion (instant)")

	return True

def steal_money(target, caster, value = 15):
	if target.player:
		target.player.gold -= value
		target.creature.message("The " + caster.name + " stole your gold", color = constants.COLOR_RED)

	return True

def reaper_cold_damage(target, caster, value = 15):

	target.creature.take_damage(0, cold_damage = value, source = "reaper damage")

	return True

def cold_damage(target, caster, value = 8):
	#deals instant cold damage
	target.creature.take_damage(0, cold_damage = value, source = "cold damage effect")

	return True

def confused(target, caster, value):
	#replaces ai with confused ai for (value) number of turns
	game_message(target.name + " is confused", constants.COLOR_PINK)
	old_ai = target.ai
	target.ai = ai_confused(old_ai = old_ai, num_turns = value)
	target.ai.owner = target

