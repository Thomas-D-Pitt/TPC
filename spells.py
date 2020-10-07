import Game
import constants
import tiles
import effects

#   _____ _____  ______ _      _       _____ 
#  / ____|  __ \|  ____| |    | |     / ____|
# | (___ | |__) | |__  | |    | |    | (___  
#  \___ \|  ___/|  __| | |    | |     \___ \ 
#  ____) | |    | |____| |____| |____ ____) |
# |_____/|_|    |______|______|______|_____/ 
 
#the method for making spells is bad and will most likely be changed eventually if im ever not feeling lazy
#until then im not even gonna try and expain how it works

def lightning(caster = None, value = 10, origin = None, Shoot = False, target = None, m_range = 5):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = lightning
    hit_along_path = True#can hit multiple characters
    can_cast_on_self = False
    radius = 0
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", m_range])    
        
    else:

        list_of_tiles = target



        for x,y in list_of_tiles:

            hit = Game.map_check_for_creatures(x,y)


            if hit and ((x,y) != origin or can_cast_on_self == True):

                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                value = value * caster.creature.damage_multiplier
                hit.creature.take_damage(0, "Lightning arcs through your body", "ZZzzt", lightning_damage = value, source = "lightning spell", color = constants.COLOR_BLUE)

        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def blood_bolt(caster = None, value = 10, origin = None, Shoot = False, target = None, m_range = 5, percent_self_damage = 1.0):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = blood_bolt
    hit_along_path = True#can hit multiple characters
    can_cast_on_self = False
    radius = 0
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self],
         name, [caster, value, start_pos, True, "SELECT_RESULT", m_range, percent_self_damage])


    else:

        list_of_tiles = target

        caster.creature.take_damage(int(value * percent_self_damage))

        effects.weakness(caster, caster, .1, 80)

        for x,y in list_of_tiles:

            hit = Game.map_check_for_creatures(x,y)


            if hit and ((x,y) != origin or can_cast_on_self == True):

                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                value = value * caster.creature.damage_multiplier
                hit.creature.take_damage(value, "You are hit by a magical blood bolt", "Your life force impales _CREATURE_", lightning_damage = value, source = "blood bolt spell", color = constants.COLOR_LIGHT_RED)

        if caster == Game.PLAYER:

            Game.PLAYER_TOOK_ACTION = "SPELL"

def holy_light(caster = None, value = 10, origin = None, Shoot = False, target = None, m_range = 5):


    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = holy_light
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = True
    radius = 0
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", m_range])

    else:

        list_of_tiles = target



        for x,y in list_of_tiles:

            hit = Game.map_check_for_creatures(x,y)


            if hit and ((x,y) != origin or can_cast_on_self == True):
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                value = value * caster.creature.damage_multiplier

                if hit.creature.type.name == "undead":
                    hit.creature.take_damage(0, "Holy light heals your wounds", "A blinding flash of light envelops _CREATURE_", lightning_damage = value * 2, source = "holy light spell", color = constants.COLOR_GOLD)
                    
                    confuse_chance = libtcod.random_get_int(0, 1, 100)

                    if confuse_chance <= 20:

                        old_ai = hit.ai
                        hit.ai = ai_confused(old_ai = old_ai, num_turns = 3)
                        hit.ai.owner = hit
                        Game.game_message(hit.name + " is disoriented", constants.COLOR_PINK)

                else:
                    hit.creature.heal(value, "Holy light heals your wounds", "A blinding flash of light envelops _CREATURE_")

        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def fireball(caster = None, value = 10, origin = None, Shoot = False, target = None, radius = 1, m_range = 5):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = fireball
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = True
    caster = caster

    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", radius])


    else:

        list_of_tiles = target





        for x,y in list_of_tiles:

            hit = Game.map_check_for_creatures(x,y)


            if hit and ((x,y) != origin or can_cast_on_self == True):
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####

                value = value * caster.creature.damage_multiplier
                hit.creature.take_damage(0, "Your skin is burned by a fireball", "the flame burns the _CREATURE_", fire_damage = value, source = "fireball spell")

        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def confuse(caster = None, value = 10, origin = None, Shoot = False, target = None, radius = 0):

    start_pos = origin
    max_range = 7
    penetrate_walls = False
    penetrate_characters = True#ignore characters along path = false
    name = confuse
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = True
    caster = caster

    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", radius])


    else:

        

        list_of_tiles = target


        for x,y in list_of_tiles:
            
            hit = Game.map_check_for_creatures(x,y)


            if hit and ((x,y) != origin or can_cast_on_self == True):

                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####

                old_ai = hit.ai
                hit.ai = ai_confused(old_ai = old_ai, num_turns = value)
                hit.ai.owner = hit

                Game.game_message(hit.name + " is confused", constants.COLOR_PINK)

        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def blind(caster = None, value = 10, origin = None, Shoot = False, target = None, radius = 0):

    start_pos = origin
    max_range = 3
    penetrate_walls = False
    penetrate_characters = False#ignore characters on path = false
    name = blind
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = True
    caster = caster
    blind_amount = .7

    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", radius])


    else:

        

        list_of_tiles = target




        for x,y in list_of_tiles:
            
            hit = Game.map_check_for_creatures(x,y)


            if hit and ((x,y) != origin or can_cast_on_self == True):

                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                effect = effects.blind(hit, caster, value, blind_amount)


        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def shoot_wep(caster = None, value = 10, origin = None, Shoot = False, target = None, m_range = 5):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = shoot_wep
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = False
    radius = 0
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin

    elif origin == "Game.PLAYER":
        caster = Game.PLAYER
        origin = (Game.PLAYER.x, Game.PLAYER.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", m_range])

    else:

        list_of_tiles = target



        for x,y in list_of_tiles:



            hit = Game.map_check_for_creatures(x,y)


            if hit and ((x,y) != origin or can_cast_on_self == True):

                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####
                ####ACUTAL AFFECT####

                value = value * caster.creature.damage_multiplier
                hit.creature.take_damage(value, "bow attack hits you", "bow attack", source = "shoot weapon")

                if caster.container:
                    objects = [obj.equipment for obj in caster.container.equipped_items]

                    for item in objects:

                        if item.owner.ammo and item.owner.ammo.hit_effect_function:

                            if item.owner.ammo.hit_effect_function_params:

                                params = [hit]

                                for param in item.owner.ammo.hit_effect_function_params:
                                    params.append(param)

                                item.owner.ammo.hit_effect_function(*params)

                            else:
                                item.owner.ammo.hit_effect_function()

                            


        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def fire_stream(caster = None, value = 10, origin = None, Shoot = False, target = None, m_range = 5):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = fire_stream
    hit_along_path = True#can hit multiple characters
    can_cast_on_self = False
    radius = 0
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", m_range])

    else:

        list_of_tiles = target
        



        for x,y in list_of_tiles:

            
            fire_tile = tiles.fire_tile(x, y, 2)
            fire_tile.caster = caster
            fire_tile.tick_damage = value
            fire_tile.damage_every_x_turns = 1
            fire_tile.source_id = "fire_stream_spell"

            Game.GAME.current_map[x][y][2] = fire_tile

            hit = Game.map_check_for_creatures(x,y)

            if hit and ((x,y) != origin or can_cast_on_self == True):

                Game.GAME.current_map[x][y][2].step_onto(hit, Game.PLAYER)


        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def plauge_bomb(caster = None, value = 10, origin = None, Shoot = False, target = None, radius = 0, m_range = 5):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = plauge_bomb
    hit_along_path = True#can hit multiple characters
    can_cast_on_self = True
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", radius])

    else:
        list_of_tiles = target
        

        for x,y in list_of_tiles:

            posion_tile = tiles.posion_tile(x, y, 2)
            posion_tile.caster = caster
            posion_tile.tick_damage = value
            posion_tile.duration = 5
            posion_tile.damage_every_x_turns = 1
            posion_tile.source_id = str(caster) + "plauge_bomb_spell"

            Game.GAME.current_map[x][y][2] = posion_tile

            hit = Game.map_check_for_creatures(x,y)

            if hit and ((x,y) != origin or can_cast_on_self == True):

                Game.GAME.current_map[x][y][2].step_onto(hit, Game.PLAYER)

                #needs network code

            

        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def fire_blast(caster = None, value = 10, origin = None, Shoot = False, target = None, radius = 1, m_range = 5):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = fire_blast
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = True
    radius = radius
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", radius])

    else:

        list_of_tiles = target
        



        for x,y in list_of_tiles:

            fire_tile = tiles.fire_tile(x, y, 2)
            fire_tile.caster = caster
            fire_tile.tick_damage = value
            fire_tile.damage_every_x_turns = 1
            fire_tile.source_id = "fire_blast_spell"

            Game.GAME.current_map[x][y][2] = fire_tile

            hit = Game.map_check_for_creatures(x,y)

            if hit and ((x,y) != origin or can_cast_on_self == True):

                Game.GAME.current_map[x][y][2].step_onto(hit, Game.PLAYER)

        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def idiot_speak(caster = None, value = 10, origin = None, Shoot = False, target = None, radius = 0, m_range = 1):

    start_pos = origin
    max_range = m_range
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = idiot_speak
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = False
    radius = radius
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin
    
    if Shoot == False:    
        Game.select([start_pos, max_range, penetrate_walls, penetrate_characters, radius, hit_along_path, can_cast_on_self], name,
         [caster, value, start_pos, True, "SELECT_RESULT", radius])

    else:

        list_of_tiles = target
        



        for x,y in list_of_tiles:

            hit = Game.map_check_for_creatures(x,y)

            if hit and ((x,y) != origin or can_cast_on_self == True):

                if hit.creature.type.name == "humanoid" or hit.creature.type.name == "undead" or hit.creature.type.name == "demon":

                    rand = libtcod.random_get_int(0, 1, 100)

                    if rand < 50 - caster.creature.intelligence * 15:

                        old_ai = hit.ai
                        hit.ai = ai_confused(old_ai = old_ai, num_turns = value)
                        hit.ai.owner = hit

                        Game.game_message(hit.name + " is confused", constants.COLOR_PINK)

        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"

def desperate_prayer(caster = None, value = 1, origin = None, Shoot = False, target = None):

    start_pos = origin
    max_range = 0
    penetrate_walls = False
    penetrate_characters = False#ignore characters along path = false
    name = desperate_prayer
    hit_along_path = False#can hit multiple characters
    can_cast_on_self = False
    radius = 0
    caster = caster
    if origin == None:
        origin = (caster.x, caster.y)
        start_pos = origin    

        rand = libtcod.random_get_int(0, 0, 100)

        if rand <= value * 20:
            
            #HEAL
            caster.creature.heal(caster.creature.maxhp)

            #Brimstone
            nearby = util.find_radius((caster.x, caster.y), 4, False)
            for coord in nearby:
                x, y = coord
                if Game.GAME.current_map[x][y][0].block_path == False:

                    fire_tile = tiles.fire_tile(x, y, 2)
                    fire_tile.caster = caster
                    fire_tile.tick_damage = caster.creature.level * 10
                    fire_tile.damage_every_x_turns = 1
                    fire_tile.source_id = "fire_blast_spell"

                    Game.GAME.current_map[x][y][2] = fire_tile

                    hit = Game.map_check_for_creatures(x,y)

                    if hit:

                        Game.GAME.current_map[x][y][2].step_onto(hit, Game.PLAYER)



        else:
            Game.game_message("Your prayer goes unanswered")

        unlearn_spell(caster, caster, "Desperate Prayer", 5)



        if caster == Game.PLAYER:
            Game.PLAYER_TOOK_ACTION = "SPELL"



def learn_all_spells(levels = 1):

    for elem in dict:
        learn_spell(Game.PLAYER, Game.PLAYER, *dict[elem][0:5], force_learn = True)

def learn_spell(actor, caster, spellname, func, func_params, cost_function, minimum_intelligence, force_learn = False):
    print(spellname)
    found_spell = False
    for spell in actor.creature.known_spells:
        if spell.name == spellname:

            if spell.minimum_intelligence(1) <= actor.creature.intelligence or force_learn == True:
                spell.level += 1
                Game.game_message(spellname + " rank increased to " + str(spell.level), constants.COLOR_TAN)
                found_spell = True
            else:
                Game.game_message("You do not meet the requirements for this spell", constants.COLOR_TAN)
                return False

    for spell in actor.creature.active_spells:

        if spell.name == spellname:

            if spell.minimum_intelligence(1) <= actor.creature.intelligence:
                spell.level += 1
                Game.game_message(spellname + " rank increased to " + str(spell.level), constants.COLOR_TAN)
                found_spell = True
            else:
                Game.game_message("You do not meet the requirements for this spell", constants.COLOR_TAN)
                return False


    if found_spell == False:
        com = Game.com_spell(spellname, func, func_params, cost_function, minimum_intelligence)

        if com.minimum_intelligence(1) <= actor.creature.intelligence or force_learn == True:

            if force_learn == True or Game.TOTAL_TURNS == 0:
                actor.creature.active_spells.append(com)
            else:
                actor.creature.known_spells.append(com)

            com.owner = actor
            try:
                Game.game_message( str(actor.display_name) + " learned spell " + str(spellname) )
            except:
                pass

        else:
            Game.game_message("You do not meet the requirements for this spell", constants.COLOR_TAN)
            return False

def unlearn_spell(target, caster, name, levels = 1):

    for n in range(levels):

        for spell in target.creature.known_spells:
            if spell.name == self.name:

                if spell.level > 1:
                    spell.level -= 1


                else:
                    target.creature.known_spells.remove(spell)
                    break

        for spell in target.creature.active_spells:
            if spell.name == name:

                if spell.level > 1:
                    spell.level -= 1

                else:
                    target.creature.active_spells.remove(spell)
                    break

dict = {
        #    ["name", function, [value (probably damage), None, False, None, any other spell variables ex)range/radius], cost, minimum intelligence
"Fireball" : ["Fireball", fireball, ["15 * _LEVEL_", None, False, None, "_LEVEL_ / 3 + 1"], "_LEVEL_", "_LEVEL_ * 2" ],
"Plauge_Bomb" : ["Plauge Bomb", plauge_bomb, ["10 * _LEVEL_", None, False, None], "_LEVEL_", 0 ],
"Fire_Blast" : ["Fire Blast", fire_blast, ["5 + 2 * (_LEVEL_ - 1)", None, False, None, "_LEVEL_ - 1"], "_LEVEL_ * 3", "3 * _LEVEL_ + 2" ],
"Lightning" : ["Lightning", lightning, ["20 * _LEVEL_", None, False, None, "_LEVEL_ + 1"], "_LEVEL_", "_LEVEL_ * 2" ],
"Tut_Spell" : ["Lightning (tutorial)", lightning, ["20 * _LEVEL_", None, False, None, "_LEVEL_ + 1"], 0, 0, True ],
"Holy_Light" : ["Holy Light", holy_light, ["10 * _LEVEL_ * _PLEVEL_", None, False, None, "_LEVEL_ + 1"], "_LEVEL_", "_LEVEL_" ],
"Blood_Bolt" : ["Blood Bolt", blood_bolt, ["20 * _PLEVEL_", None, False, None, 5, ".5 / _LEVEL_"], "0", "_LEVEL_ * 2" ],
"Idiot_Speak" : ["Idiot Speak", idiot_speak, [3, None, False, None, 5], 0, 0],
"Demon_Shank" : ["Demon Shank", fire_blast, ["5 + 2 * (_LEVEL_ - 1)", None, False, None, "_LEVEL_ - 1"], 2, 0, True],
"Desperate_Prayer" : ["Desperate Prayer", desperate_prayer, ["_LEVEL_", None, False, None], 0, 0],
}