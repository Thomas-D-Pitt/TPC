import Game
import constants

Mod_id = 5556
Mod_version = 1.0

def test2():

	print "Test2"
	
	
def init():

	#since Game.Run is assigned in both test from test_mod and test2 from test_mod2,
	#it will be replaced with whichever is first in the Mod_Load_Order.txt
	#Game.Run = test2
	pass

