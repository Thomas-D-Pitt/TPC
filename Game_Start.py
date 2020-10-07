import importlib

import sys


# for module in os.listdir(os.path.dirname("./Mods/.")):
# 	print str(module)

try:

	f = open("Mods/_Load Order.txt", "r")

	full_text=f.read()
	f.close()

	mod_names = full_text.split(",")

	mods = []


	for mod_name in  reversed(mod_names):#reversed ensures that the first item in the load order is run last,
										  #anything it overwrites will be the final result

		mod_name[0]

		mod_name = mod_name.replace(" ", "")#removes spaces from name

		try:
			path = sys.path
			sys.path.append(sys.path[0] + "//Mods")
			imported_mod = (importlib.import_module(mod_name))
			print "Successfully imported:", mod_name, ("id:" + str(imported_mod.Mod_id)), ("v" + str(imported_mod.Mod_version))
			# ^ checks for mod_id and version number, as well as notifying user ^
			mods.append(imported_mod)

		except:
			print "Failed to import mod:", mod_name

except:
	print "No Mods Loaded"
	mods = []

import Game

Game.game_init()

for mod in mods:

	mod.init()


Game.GAME_MODS = mods


Game.Run()