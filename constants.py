
import pygame
import libtcodpy as libtcod

import Game

pygame.init()

class obj_spriteSheet():

	def __init__(self, file_name, height = None, width = None):
		self.sprite_sheet = pygame.image.load(file_name)
		self.tile_dict = {'a':1, 'b':2, 'c':3, 'd':4, 'e':5, 'f':6, 'g':7, 'h':8, 'i':9, 'j':10, 'k':11, 'l':12, 'm':13, 'n':14, 'o':15, 'p':16, 'q':17, 'r':18, 's':19,
						  0:0, 1:1, 2:2, 3:3, 4:4, 5:5, 6:6, 7:7, 8:8, 9:9, 10:10, 11:11, 12:12, 13:13, 14:14, 15:15, 16:16}


		self.height = height
		self.width = width


	def get_image(self, column, row, width = 16, height = 16, scale = (32,32), color_key = (0,0,0)):#scale = tuple


		image_list = []

		image = pygame.Surface([width, height])
		image.blit(self.sprite_sheet, (0,0), (self.tile_dict[column]*width, row*height, width, height ))
		if color_key:
			image.set_colorkey(color_key)

		if scale:
			(new_w, new_h) = scale

			image = pygame.transform.scale(image, (new_w, new_h))

		image_list.append(image)

		return image_list

	def get_anim(self, column, row, num_sprites = 2, width = 16, height = 16, scale = (32,32), color_key = (0,0,0)):#scale = tuple


		image_list = []

		for i in range(num_sprites):

			image = pygame.Surface([width, height])
			image.blit(self.sprite_sheet, (0,0), (self.tile_dict[column]*width+width*i, row*height, width, height ))
			if color_key:
				image.set_colorkey(color_key)

			if scale:
				(new_w, new_h) = scale

				image = pygame.transform.scale(image, (new_w, new_h))

			image_list.append(image)
		#print(len(image_list))

		return image_list

def image(path):
	img = pygame.image.load(path)
	img = pygame.transform.scale(img, (32, 32))
	return img


#Game Size
#GAME_WIDTH = 800
#GAME_HEIGHT = 600

GAME_TITLE = "The Profaned Cathedral"
VERSION = "Jan 2 2020"

GAME_TILES_X = 50
GAME_TILES_Y = 50
GAME_TILES_Z = 3
GAME_TILE_SIZE = 32
MAP_TILE_SIZE = 8
FPS_LIMIT = 30
ACTION_DELAY = .3

CAMERA_WIDTH = 1000
CAMERA_HEIGHT = 600

DRAW_ACTOR_BACKGROUNDS = False

#MAP
MAX_ROOMS = 50

ROOM_MIN_WIDTH = 3
ROOM_MIN_HEIGHT = 3

ROOM_MAX_WIDTH = 7
ROOM_MAX_HEIGHT = 7

DISPLAY_ALL_TILES_IN_PATH = True
DISTANCE_DARKENING = 35

FALSE = False
TRUE = True

DEFAULT_HEALTH_MULTIPLIER_PER_PLAYER = 1
DEFAULT_DAMAGE_MULTIPLIER_PER_PLAYER = .6

#MENUS
MENU_WIDTH = 200
MENU_HEIGHT_CHAR = 260
MENU_BUFFER = 5

POTION_WIDTH = 280
POTION_HEIGHT = 60

POTION_WEIGHT = .5
SCROLL_WEIGHT = .25
SPELLBOOK_WEIGHT = .75
GEM_WEIGHT = .1

CAMPFIRE_MENU_WIDTH = 300
CAMPFIRE_MENU_HEIGHT = 300

INV_HEIGHT = 400

MAGIC_CHANCE = 200 #in percent
GOLD_PER_FOOD = 2

DEFAULT_THROW_DAMAGE = 8

#Colors Definitions
COLOR_BLACK = (0,0,0)
COLOR_WHITE = (254, 254, 254)
COLOR_GREY = (100, 100, 100)
COLOR_LIGHT_GREY = (175, 175, 175)
COLOR_DARK_GREY = (50, 50, 50)
COLOR_VERY_DARK_GREY = (20, 20, 20)
COLOR_RED = (130,0,0)
COLOR_LIGHT_RED = (255,0,0)
COLOR_VERY_LIGHT_RED = (255, 100, 100)
COLOR_GOLD = (255,223,0)
COLOR_PINK = (255,105,180)
COLOR_GREEN = (124,252,0)
COLOR_DARK_TEAL = (0, 153, 153)
COLOR_LIGHT_BLUE = (65, 105, 225)
COLOR_BLUE = (0, 102, 204)
COLOR_DARK_BLUE = (0, 0, 175)
COLOR_BRIGHT_PINK = (255,0,255)
COLOR_ORANGE = (255,165,0)
COLOR_RED_TINT = (255,0,0,.9)
COLOR_INDIGO = (75,0,130)
COLOR_PURPLE = (138,43,226)
COLOR_BROWN = (139,69,19)
COLOR_BROWN_2 = (170,100,40)
COLOR_LIGHT_BROWN = (205,133,63)
COLOR_TAN = (210, 180, 140)
COLOR_YELLOW = (255, 255, 0)
#Game Colors
COLOR_DEFAULT_BG = COLOR_DARK_GREY
COLOR_DEFAULT_MISSING = COLOR_BRIGHT_PINK


#FOV
TORCH_RADIUS = 10
FOV_LIGHT_WALLS = True
FOV_ALGO = libtcod.FOV_BASIC

#MESSAGES
MG_NUM = 100

# S
font_const = 4
font_loc = "Data/TypographerRotunda.otf"
#font_loc = "Data/DIABLO_H.ttf"
FONT_MAIN = pygame.font.Font(font_loc, 16 +font_const)
FONT_MAIN_16 = pygame.font.Font(font_loc, 16+font_const)
FONT_MAIN_18 = pygame.font.Font(font_loc, 18+font_const)
FONT_MAIN_32 = pygame.font.Font(font_loc, 32+font_const)
FONT_MAIN_48 = pygame.font.Font(font_loc, 48+font_const)
FONT_MAIN_12 = pygame.font.Font(font_loc, 12+font_const)
FONT_MAIN_8 = pygame.font.Font(font_loc, 8+font_const)
FONT_MAIN_24 = pygame.font.Font(font_loc, 24+font_const)
FONT_GUTHEN_24 = pygame.font.Font("Data/underworld.ttf", 24+font_const)

FONT_DEFAULT = FONT_MAIN_12
FONT_SPACER = pygame.font.Font(font_loc, 2)
FONT_MENU = FONT_MAIN_32
FONT_TITLE = FONT_MAIN_48


#SPRITES

DEMONS = obj_spriteSheet("Data/Characters/Demons.png")
PLANT = obj_spriteSheet("Data/Characters/Plant.png")
PLAYER = obj_spriteSheet("Data/Characters/Player.png")
UNDEAD = obj_spriteSheet("Data/Characters/Undead.png")
AQUATIC = obj_spriteSheet("Data/Characters/Aquatic.png")
AVIAN = obj_spriteSheet("Data/Characters/Avian.png")
HUMANOID = obj_spriteSheet("Data/Characters/Humanoid.png")
PEST = obj_spriteSheet("Data/Characters/Pest.png")
QUADRAPED = obj_spriteSheet("Data/Characters/Quadraped.png")
REPTILE = obj_spriteSheet("Data/Characters/Reptile.png")
RODENT = obj_spriteSheet("Data/Characters/Rodent.png")
SLIME = obj_spriteSheet("Data/Characters/Slime.png")

WALLS = obj_spriteSheet("Data/Objects/Wall.png")
FLOORS = obj_spriteSheet("Data/Objects/Floor.png")
DOORS = obj_spriteSheet("Data/Objects/Door.png")
GROUND = obj_spriteSheet("Data/Objects/Ground.png")
TILES = obj_spriteSheet("Data/Objects/Tile.png")
EFFECTS = obj_spriteSheet("Data/Objects/Effect.png")
DECOR = obj_spriteSheet("Data/Objects/Decor.png")
WEP = obj_spriteSheet("Data/Items/MedWep.png")
WEP2 = obj_spriteSheet("Data/Items/LongWep.png")
WEP3 = obj_spriteSheet("Data/Items/ShortWep.png")
WAND = obj_spriteSheet("Data/Items/Wand.png")
SHIELD = obj_spriteSheet("Data/Items/Shield.png")
SCROLL = obj_spriteSheet("Data/Items/Scroll.png")
FLESH = obj_spriteSheet("Data/Items/Flesh.png")
AMMO = obj_spriteSheet("Data/Items/Ammo.png")
POTIONS = obj_spriteSheet("Data/Items/Potion.png")
MUSIC_SHEET = obj_spriteSheet("Data/Items/Music.png")
LIGHT = obj_spriteSheet("Data/Items/Light.png")
ARMOR = obj_spriteSheet("Data/Items/Armor.png")
HAT = obj_spriteSheet("Data/Items/Hat.png")
GEMS = obj_spriteSheet("Data/Gems.png")
RINGS = obj_spriteSheet("Data/Items/Ring.png")
BOOKS = obj_spriteSheet("Data/Items/Book.png")
CHESTS = obj_spriteSheet("Data/Items/Chest.png")
TOOL = obj_spriteSheet("Data/Items/Tool.png")
FOODS = obj_spriteSheet("Data/Items/Food.png")
TRAPS = obj_spriteSheet("Data/Objects/Trap.png")
MONEY = obj_spriteSheet("Data/Items/Money.png")

FIRE = obj_spriteSheet("Data/fire.png")

TORCH_1 = pygame.image.load("Data/fire_013.png")
TORCH_1 = pygame.transform.scale(TORCH_1, (32, 32))
TORCH_2 = pygame.image.load("Data/fire_014.png")
TORCH_2 = pygame.transform.scale(TORCH_2, (32, 32))
TORCH_3 = pygame.image.load("Data/fire_015.png")
TORCH_3 = pygame.transform.scale(TORCH_3, (32, 32))
TORCH_4 = pygame.image.load("Data/fire_016.png")
TORCH_4 = pygame.transform.scale(TORCH_4, (32, 32))

TORCH_5 = pygame.image.load("Data/fire_017.png")
TORCH_5 = pygame.transform.scale(TORCH_5, (32, 32))
TORCH_6 = pygame.image.load("Data/fire_018.png")
TORCH_6 = pygame.transform.scale(TORCH_6, (32, 32))
TORCH_7 = pygame.image.load("Data/fire_019.png")
TORCH_7 = pygame.transform.scale(TORCH_7, (32, 32))
TORCH_8 = pygame.image.load("Data/fire_020.png")
TORCH_8 = pygame.transform.scale(TORCH_8, (32, 32))
 
HOT_BARS = obj_spriteSheet("Data/hot_floor.png")
HOT_BARS = HOT_BARS.get_anim(1,0, 15, 32, 32)

RAM_MAGE = obj_spriteSheet("Data/spritesheets/gnu.png")


color = (0,254,0)
temp = RAM_MAGE.get_anim(0,0,5, 120, 100, (96,96), color_key = color)
temp2 = reversed(RAM_MAGE.get_anim(0,0,5, 120, 100, (96,96), color_key = color))

RAM_MAGE = temp
for img in temp2:
	RAM_MAGE.append(img)

HELL_BEAST = obj_spriteSheet("Data/gothicvania  collection/Hell-Beast-Files/PNG/with-stroke/hell-beast-idle2.png")

HELL_BEAST = HELL_BEAST.get_anim(0,0, 6, 55, 67, scale = (55,67))

#Sprites
S_LOGO = pygame.image.load("Data/Logo.png")
S_BOOK = pygame.image.load("Data/Book.png")
S_TITLE = pygame.image.load("Data/Title.png")
S_TITLE = pygame.transform.scale(S_TITLE, (CAMERA_WIDTH - 30, CAMERA_HEIGHT/4 - 30))
#S_PLAYER = pygame.image.load("Data/Knight.png")
S_SKELETON = pygame.image.load("Data/Skeleton_Knight.png")
#S_PRIEST = pygame.image.load("Data/Priest.png")
#S_GOBLIN = pygame.image.load("Data/Goblin.png")
S_REAPER = pygame.image.load("Data/Reaper.png")
S_SKELETON_KNIGHT = pygame.image.load("Data/Skeleton_Knight.png")
S_WALL = pygame.image.load("Data/StoneWall.png")
S_SEWAGE = pygame.image.load("Data/sewage.png")
S_DIRT_FLOOR = pygame.image.load("Data/dirt_floor.png")
S_DIRT_WALL = pygame.image.load("Data/dirt_wall.png")
S_ROCK_FLOOR = pygame.image.load("Data/RockFloor.png")
S_DOOR_OPEN = pygame.image.load("Data/Door_open.png")
S_DOOR_CLOSED = pygame.image.load("Data/Door_Closed.png")
S_TINT_RED = pygame.image.load("Data/tint.png")
S_TINT_DARK = pygame.image.load("Data/tint_dark.png")
S_BLACK = pygame.image.load("Data/Black.png")
S_DARK_GREY = pygame.image.load("Data/Dark_grey.png")
S_TARGET = pygame.image.load("Data/Target.png")
S_CONFUSED_1 = pygame.image.load("Data/P_Confusion_1.png")
S_CONFUSED_2 = pygame.image.load("Data/P_Confusion_2.png")
S_CONFUSED_3 = pygame.image.load("Data/P_Confusion_3.png")
S_CORPSE = FLESH.get_image('a', 1)[0]
S_BR_FILL = pygame.image.load("Data/black_red_fill.png")

S_DEMON_BONE = pygame.image.load("Data/Items/Demon Bone.png")
S_DEMON_BONE = pygame.transform.scale(S_DEMON_BONE, (32, 32))

#S_PLUS = pygame.image.load("Data/plus.png")
X = pygame.image.load("Data/x.png")
X = pygame.transform.scale(X, (32, 32))

GUI = obj_spriteSheet("Data/GUI/GUI.png")

S_DOWN_ARROW = GUI.get_image('a', 7)
S_UP_ARROW = [pygame.transform.rotate(S_DOWN_ARROW[0], 180)]

CAMP_FIRE_GLOW_1_1 = pygame.image.load("Data/campfire_glow_1_1.png")
CAMP_FIRE_GLOW_1_2 = pygame.image.load("Data/campfire_glow_1_2.png")
CAMP_FIRE_GLOW_1_3 = pygame.image.load("Data/campfire_glow_1_3.png")

CAMP_FIRE_GLOW_2_1 = pygame.image.load("Data/campfire_glow_2_1.png")
CAMP_FIRE_GLOW_2_2 = pygame.image.load("Data/campfire_glow_2_2.png")
CAMP_FIRE_GLOW_2_3 = pygame.image.load("Data/campfire_glow_2_3.png")

CAMP_FIRE_GLOW_3_1 = pygame.image.load("Data/campfire_glow_3_1.png")
CAMP_FIRE_GLOW_3_2 = pygame.image.load("Data/campfire_glow_3_2.png")
CAMP_FIRE_GLOW_3_3 = pygame.image.load("Data/campfire_glow_3_3.png")

BUCKET = pygame.image.load("Data/bucket.png")

FLOOR_MARKER = pygame.image.load("Data/floor_marker.png")

#GAS_CLOUD = EFFECTS.get_image('e', 25)[0]
GAS_CLOUD_SS = obj_spriteSheet("Data/Objects/gas cloud.png")
GAS_CLOUD = GAS_CLOUD_SS.get_anim(0, 0)

S_NONE = S_LOGO

HIDDEN = obj_spriteSheet("Data/sparkle.png")

HIDDEN = HIDDEN.get_anim(0, 0, 16)
HIDDEN_FLICKER_SPEED = .3

BLOOD = obj_spriteSheet("Data/blood splatter/blood splatter 96x96.png")

S_BLOOD_1 = pygame.image.load("Data/blood splatter/blood splatter (1).png")
S_BLOOD_2 = pygame.image.load("Data/blood splatter/blood splatter (4).png")
S_BLOOD_3 = pygame.image.load("Data/blood splatter/blood splatter (7).png")

S_BLOOD_4 = pygame.image.load("Data/blood splatter/blood splatter (2).png")
S_BLOOD_5 = pygame.image.load("Data/blood splatter/blood splatter (5).png")
S_BLOOD_6 = pygame.image.load("Data/blood splatter/blood splatter (8).png")

S_BLOOD_7 = pygame.image.load("Data/blood splatter/blood splatter (3).png")
S_BLOOD_8 = pygame.image.load("Data/blood splatter/blood splatter (6).png")
S_BLOOD_9 = pygame.image.load("Data/blood splatter/blood splatter (9).png")

BLOOD = ["S_BLOOD_1", "S_BLOOD_2", "S_BLOOD_3", "S_BLOOD_4", "S_BLOOD_5", "S_BLOOD_6", "S_BLOOD_7", "S_BLOOD_8", "S_BLOOD_9"]

#BLANK = S_GOBLIN

S_RED_FILL = pygame.transform.scale(S_TINT_RED, (CAMERA_WIDTH, CAMERA_HEIGHT))
S_DARK_FILL = pygame.transform.scale(S_TINT_DARK, (CAMERA_WIDTH, CAMERA_HEIGHT))


A_CONFUSION = [S_CONFUSED_1, S_CONFUSED_2, S_CONFUSED_3]



#AUDIO
try:
	#sometimes I dont upload sound files due to having very slow internet and sound takes up most of the game size
	#therfore this ensures that audio files are present and should be used

	pygame.mixer.music.load("Data/Music/oppressive-gloom-by-kevin-macleod.mp3")#if music files are there, then load the rest of them

	MUSIC_1 = "Data/Music/oppressive-gloom-by-kevin-macleod.mp3"
	MUSIC_2 = "Data/Music/the-dread-by-kevin-macleod.wav"


	MUSIC = [MUSIC_1, MUSIC_2]

	MUSIC_FOUND = True

except:
	MUSIC_FOUND = False



#Title screen
TITLE_IMG_1 = pygame.image.load("Data/background_3.png")
TITLE_IMG_2 = pygame.image.load("Data/background_3.png")
TITLE_IMG_3 = pygame.image.load("Data/background_3.png")
#TITLE_IMG_2 = pygame.image.load("Data/background_image_2.jpg")
#TITLE_IMG_3 = pygame.image.load("Data/background_image_3.jpg")

TITLE_IMG_1 = pygame.transform.scale(TITLE_IMG_1, (CAMERA_WIDTH, CAMERA_HEIGHT))
TITLE_IMG_2 = pygame.transform.scale(TITLE_IMG_2, (CAMERA_WIDTH, CAMERA_HEIGHT))
TITLE_IMG_3 = pygame.transform.scale(TITLE_IMG_3, (CAMERA_WIDTH, CAMERA_HEIGHT))

TITLE_SCREEN = [TITLE_IMG_3, TITLE_IMG_2, TITLE_IMG_1]


#def set_music_volume(value):

#	for song in MUSIC:

#		song.set_volume(value)

CAMPFIRE = obj_spriteSheet("Data/CampFire.png")

anim_dict = {
	
	"FIREMAN" : DEMONS.get_anim('a', 2),
	"FIREMAN_DEAD" : DEMONS.get_anim('a', 2, 1),
	#"PLANT" PLANT,
	"PLAYER" : PLAYER.get_anim('c', 12),
	"MAGE" : PLAYER.get_anim('m', 4),
	"THIEF" : PLAYER.get_anim('e', 5),
	"SHOP" : PLAYER.get_anim('i', 12),
	"SKELETON" : UNDEAD.get_anim('a', 3),
	"BAT" : AVIAN.get_anim('a', 12),
	"DIRE_BAT" : AVIAN.get_anim('a', 2),
	'GRIFFIN' : AVIAN.get_anim('c', 10),
	"GARGOYLE" : AVIAN.get_anim('e', 12),
	"GRUB" : PEST.get_anim('a', 4),
	"MUNCHER" : PEST.get_anim('c', 4),
	"DEVOURER" : PEST.get_anim('i', 4),
	"SCORPION" : PEST.get_anim('i', 3),
	"DIRE_SCORPION" : PEST.get_anim('k', 3),
	"SLIME_MONSTER" : PLANT.get_anim('c', 7),
	"DARK_RAM" : QUADRAPED.get_anim('k', 3),
	"DARK_RAM_LEADER" : QUADRAPED.get_anim('e', 8),
	"WOLF" : QUADRAPED.get_anim('m', 1),
	"REAPER" : UNDEAD.get_anim('a', 6),
	"WRAITH" : UNDEAD.get_anim('a', 7),
	"GREATER_WRAITH" : UNDEAD.get_anim('c', 7),
	"WANDERER" : UNDEAD.get_anim('e', 6),
	"SPIRIT" : UNDEAD.get_anim('c', 9),
	"PIG_MAN" : UNDEAD.get_anim('a', 10),
	"YOUNG_DEVIL" : DEMONS.get_anim('c', 2),
	"RED_DEVIL" : DEMONS.get_anim('e', 2),
	"GREATER_DEMON" : DEMONS.get_anim('g', 2),
	"RED_COLOSSUS" : DEMONS.get_anim('i', 2),
	"DEMON_WITCH" : DEMONS.get_anim('m', 1),
	"LESSER_DEMON" : DEMONS.get_anim('e', 4),
	"RAM_MAGE" : RAM_MAGE,
	"HELL_BEAST" : HELL_BEAST,

	"DUMMY" : DEMONS.get_anim('a', 4),

	"HIDDEN" : HIDDEN,
	"MISSING" : GUI.get_image('c',1),
	"MISSING_2" : GUI.get_anim('g',1),
	#"BLANK" : BLANK,
	"X" : X,
	"FLOOR_MARKER" : FLOOR_MARKER,
	"TITLE" : S_TITLE,
	"FLOOR_MARKER_scaled" : pygame.transform.scale(FLOOR_MARKER, (32,32)),

	



	"UP_ARROW" : S_UP_ARROW[0],
	"DOWN_ARROW" : S_DOWN_ARROW[0],


	"SCEPTER" : WAND.get_image('c', 4),
	"SWORD_1" : WEP.get_image('a', 1),
	"SWORD_2" : WEP.get_image('c', 1),
	"PIKE" : WEP2.get_image('a', 3),
	"SCIMITAR" : WEP2.get_image('e', 2),
	"DIRK" : WEP3.get_image('b', 1),
	"CLUB" : WEP2.get_image('c', 5),
	"HALBARD" : WEP2.get_image('a', 5),
	"HAMMER" : WEP2.get_image('a', 7),
	"ARROW" : AMMO.get_image('d', 3),
	"BOW" : AMMO.get_image('a', 2),
	"BROKEN_BOTTLE" : MUSIC_SHEET.get_image('b', 2),
	"CLOAK" : ARMOR.get_image('b', 6),
	"MONK_ROBES" : ARMOR.get_image('a', 8),
	"CASSOCK" : ARMOR.get_image('h', 5),
	"LEATHER_CHEST" : ARMOR.get_image('a', 7),
	"CHAIN_MAIL" : ARMOR.get_image('h', 1),
	"PLATE_ARMOR" : ARMOR.get_image('c', 7),
	"LEAD_ARMOR" : ARMOR.get_image('e', 9),
	"CHROMATIC_MAIL" : ARMOR.get_image('d', 2),
	"CROWN" : HAT.get_image('b', 4),
	"CANDLE_STICK" : LIGHT.get_image('c', 1),
	"FLAIL" : WEP3.get_image('b', 5),
	"SCYTHE" : WEP2.get_image('d', 5),
	"EXECUTIONERS_AXE" : WEP2.get_image('b', 5),
	"WHIP" : WEP2.get_image('b', 6),
	"DEMON_BONE" : [S_DEMON_BONE],

	"RANDOM_RING" : RINGS.get_image(libtcod.random_get_int(0, 1,8), libtcod.random_get_int(0, 1, 6)),

	"RANDOM_BOOK" : BOOKS.get_image(libtcod.random_get_int(0, 1,8), libtcod.random_get_int(0, 1, 5)),

	"GEM_1" : GEMS.get_image('a', 1),
	"GEM_2" : GEMS.get_image('b', 1),
	"GEM_3" : GEMS.get_image('c', 1),
	"GEM_4" : GEMS.get_image('d', 1),
	"GEM_5" : GEMS.get_image('e', 1),
	"GEM_6" : GEMS.get_image('f', 1),
	"GEM_7" : GEMS.get_image('g', 1),
	"GEM_8" : GEMS.get_image('h', 1),

	"POTION_1_1" : POTIONS.get_image('a', 1),
	"POTION_1_2" : POTIONS.get_image('b', 1),
	"POTION_1_3" : POTIONS.get_image('c', 1),
	"POTION_1_4" : POTIONS.get_image('d', 1),
	"POTION_1_5" : POTIONS.get_image('e', 1),
	"POTION_1_6" : POTIONS.get_image('f', 1),
	"POTION_1_7" : POTIONS.get_image('g', 1),
	"POTION_1_8" : POTIONS.get_image('h', 1),

	"POTION_2_1" : POTIONS.get_image('a', 2),
	"POTION_2_2" : POTIONS.get_image('b', 2),
	"POTION_2_3" : POTIONS.get_image('c', 2),
	"POTION_2_4" : POTIONS.get_image('d', 2),
	"POTION_2_5" : POTIONS.get_image('e', 2),
	"POTION_2_6" : POTIONS.get_image('f', 2),
	"POTION_2_7" : POTIONS.get_image('g', 2),
	"POTION_2_8" : POTIONS.get_image('h', 2),

	"POTION_3_1" : POTIONS.get_image('a', 3),
	"POTION_3_2" : POTIONS.get_image('b', 3),
	"POTION_3_3" : POTIONS.get_image('c', 3),
	"POTION_3_4" : POTIONS.get_image('d', 3),
	"POTION_3_5" : POTIONS.get_image('e', 3),
	"POTION_3_6" : POTIONS.get_image('f', 3),
	"POTION_3_7" : POTIONS.get_image('g', 3),
	"POTION_3_8" : POTIONS.get_image('h', 3),

	"POTION_4_1" : POTIONS.get_image('a', 4),
	"POTION_4_2" : POTIONS.get_image('b', 4),
	"POTION_4_3" : POTIONS.get_image('c', 4),
	"POTION_4_4" : POTIONS.get_image('d', 4),
	"POTION_4_5" : POTIONS.get_image('e', 4),
	"POTION_4_6" : POTIONS.get_image('f', 4),
	"POTION_4_7" : POTIONS.get_image('g', 4),
	"POTION_4_8" : POTIONS.get_image('h', 4),

	"POTION_5_1" : POTIONS.get_image('a', 5),
	"POTION_5_2" : POTIONS.get_image('b', 5),
	"POTION_5_3" : POTIONS.get_image('c', 5),
	"POTION_5_4" : POTIONS.get_image('d', 5),
	"POTION_5_5" : POTIONS.get_image('e', 5),
	"POTION_5_6" : POTIONS.get_image('f', 5),
	"POTION_5_7" : POTIONS.get_image('g', 5),
	"POTION_5_8" : POTIONS.get_image('h', 5),

	"S_BLOOD_1" : S_BLOOD_1,
	"S_BLOOD_2" : S_BLOOD_2,
	"S_BLOOD_3" : S_BLOOD_3,

	"S_BLOOD_4" : S_BLOOD_4,
	"S_BLOOD_5" : S_BLOOD_5,
	"S_BLOOD_6" : S_BLOOD_6,

	"S_BLOOD_7" : S_BLOOD_7,
	"S_BLOOD_8" : S_BLOOD_8,
	"S_BLOOD_9" : S_BLOOD_9,

	#"WEP2" : WEP2
	#"WEP3" : WEP3
	"SHIELD_1" : SHIELD.get_image('a', 1),
	"SCROLL_LIGHTNING" : SCROLL.get_image('e', 1),
	"SCROLL_FIRE" : SCROLL.get_image('c', 2),
	"SCROLL_CONFUSE" : SCROLL.get_image('e', 4),
	"SCROLL_BLIND" : SCROLL.get_image('e', 5),
	"SCROLL_ID" : SCROLL.get_image('a', 1),
	#"FLESH" : FLESH
	"CORPSE" : FLESH.get_image('a', 1)[0],
	"FOOD" : FOODS.get_image('c', 5),
	"MAP_TOOLS" : TOOL.get_image('g', 1),

	"WALL_1" : S_WALL,
	"DIRT_WALL" : S_DIRT_WALL,
	"DIRT_FLOOR" : S_DIRT_FLOOR,
	"WALL_2" : WALLS.get_image('d', 13)[0],
	"ROCK_FLOOR" : S_ROCK_FLOOR,
	"TARGET" : S_TARGET,
	"NONE" : S_LOGO,
	"BLACK" : S_BLACK,
	"CONFUSION" : [S_CONFUSED_1, S_CONFUSED_2, S_CONFUSED_3],
	"S_TINT_RED" : S_TINT_RED,
	"CHEST_CLOSED" :  CHESTS.get_image('c',1)[0],
	"CHEST_OPENED" :  CHESTS.get_image('d',1)[0],
	"WOOD_DOOR" :  DOORS.get_image('a',1)[0],
	"GRASS_1" :  GROUND.get_anim('a',2),
	"GRASS_2" :  GROUND.get_anim('a',1),
	"FENCE" :  WALLS.get_image('k',10)[0],
	"FENCE_2" :  image("Data/Objects/fence_vert.png"),
	"FENCE_3" :  image("Data/Objects/half_fence.png"),
	"FENCE_4" :  image("Data/Objects/dark_fence.png"),

	"DARK_GRASS_1" :  FLOORS.get_image('h',13)[0],
	"DARK_GRASS_2" :  FLOORS.get_image('i',13)[0],
	"DARK_GRASS_3" :  FLOORS.get_image('j',13)[0],

	"DARK_GRASS_4" :  FLOORS.get_image('h',14)[0],
	"DARK_GRASS_5" :  FLOORS.get_image('i',14)[0],
	"DARK_GRASS_6" :  FLOORS.get_image('j',14)[0],

	"DARK_GRASS_7" :  FLOORS.get_image('h',15)[0],
	"DARK_GRASS_8" :  FLOORS.get_image('i',15)[0],
	"DARK_GRASS_9" :  FLOORS.get_image('j',15)[0],

	"DARK_PATH_1" :  FLOORS.get_image('r',13)[0],
	"DARK_PATH_2" :  FLOORS.get_image('r',14)[0],
	"DARK_PATH_3" :  FLOORS.get_image('r',15)[0],

	"BOOK_PEDESTAL" :  S_BOOK,


	"LOGO" : S_LOGO,
	"STAIR_DOWN" : TILES.get_image('f', 4)[0],
	"STAIR_UP" : TILES.get_image('f', 3)[0],
	"EXPLOSION" : EFFECTS.get_image('c', 25)[0],
	"CAMPFIRE" : CAMPFIRE.get_anim(1, 1, 4, width = 32,height = 32),
	"GAS_CLOUD" : GAS_CLOUD,
	"SPIKES" : TRAPS.get_image('d', 4)[0],
	"BARS" : TRAPS.get_image('e', 4)[0],
	"PIT" : TRAPS.get_image('k', 3)[0],
	"HOLE" : TRAPS.get_image('i', 3)[0],
	"MONEY" : MONEY.get_image('a', 2),
	"HOT_BARS" : HOT_BARS,
	#"FIRE_1" : FIRE.get_anim(1, 1, 4, width = 32, height = 32, scale = (32,32), color_key = (0, 0, 0)),



	"FIRE_1" : [TORCH_1, TORCH_2, TORCH_3, TORCH_4, TORCH_5, TORCH_6, TORCH_7, TORCH_8],


	"CAMP_FIRE_GLOW_1_1" : CAMP_FIRE_GLOW_1_1,
	"CAMP_FIRE_GLOW_1_2" : CAMP_FIRE_GLOW_1_2,
	"CAMP_FIRE_GLOW_1_3" : CAMP_FIRE_GLOW_1_3,

	"CAMP_FIRE_GLOW_2_1" : CAMP_FIRE_GLOW_2_1,
	"CAMP_FIRE_GLOW_2_2" : CAMP_FIRE_GLOW_2_2,
	"CAMP_FIRE_GLOW_2_3" : CAMP_FIRE_GLOW_2_3,

	"CAMP_FIRE_GLOW_3_1" : CAMP_FIRE_GLOW_3_1,
	"CAMP_FIRE_GLOW_3_2" : CAMP_FIRE_GLOW_3_2,
	"CAMP_FIRE_GLOW_3_3" : CAMP_FIRE_GLOW_3_3,

	"SHRINE" : EFFECTS.get_image('n', 25)[0],
	"SHRINE_USED" : EFFECTS.get_image('l', 25)[0],
	"SACRAFICIAL_ALTER" : pygame.image.load("Data/Objects/Alter.png"),
	"BLOODY_ALTER" : pygame.image.load("Data/Objects/Alter Bloody.png"),

	"BUCKET": HAT.get_image('a', 1),

	"Knight" : PLAYER.get_anim('c', 4),
	"Cleric" : PLAYER.get_anim('a', 5),
	"Town Drunk" : PLAYER.get_anim('a', 12),
	"Warlock" : PLAYER.get_anim('o', 4),
	"Village Idiot" : PLAYER.get_anim('a', 4),
	"Rouge" : PLAYER.get_anim('e', 2),
	"King" : PLAYER.get_anim('e', 12),

}

spritesheet_dict = { 
#spritesheets used by the map maker, all spritesheets must have height and width added to be used
#additionally apritesheets should have each image added to the 
	"PENTAGRAM" : obj_spriteSheet("Data/pentagram/pentagram9x9.png", width = 9, height = 9),
}
for x in range(9):
	for y in range(9):
		if x != 0 and y*9 != 0:
			anim_dict["PENTAGRAM_" + str(x) + "_" + str(y)] = pygame.image.load("Data/pentagram/tile0" + str(x + y*9) + ".png")
		elif x == 0 and y > 1:
			anim_dict["PENTAGRAM_" + str(x) + "_" + str(y)] = pygame.image.load("Data/pentagram/tile0" + str(y*9) + ".png")
		elif y == 0:
			anim_dict["PENTAGRAM_" + str(x) + "_" + str(y)] = pygame.image.load("Data/pentagram/tile00" + str(x) + ".png")
		else:
			anim_dict["PENTAGRAM_" + str(x) + "_" + str(y)] = pygame.image.load("Data/pentagram/tile00" + str(y*9) + ".png")


S_KNIGHT = PLAYER.get_image('c', 4)[0]
S_CLERIC = PLAYER.get_image('a', 5)[0]
S_DRUNK = PLAYER.get_image('a', 12)[0]
S_WARLOCK = PLAYER.get_image('o', 4)[0]
S_IDIOT = PLAYER.get_image('a', 4)[0]
S_ROUGE = PLAYER.get_image('e', 2)[0]
S_KING = PLAYER.get_image('e', 12)[0]


font_dict = {
	
	"FONT_MAIN" : FONT_MAIN,
	"FONT_MAIN_16" : FONT_MAIN_16,
	"FONT_MAIN_12" : FONT_MAIN_12,
	"FONT_MAIN_8" : FONT_MAIN_8,
	"FONT_SPACER" : FONT_SPACER,
	"FONT_GUTHEN_24" : FONT_GUTHEN_24,
	"FONT_MENU" : FONT_MENU,
	"FONT_MAIN_32" : FONT_MAIN_32,
	"FONT_DEFAULT" : FONT_MAIN_12,
	"FONT_MAIN_24" : FONT_MAIN_24,
	"FONT_TITLE" : FONT_TITLE,
	"FONT_MAIN_18" : FONT_MAIN_18

}


#### CHARACTER DATA ####

S_KNIGHT = PLAYER.get_image('c', 4)[0]
S_CLERIC = PLAYER.get_image('a', 5)[0]
S_DRUNK = PLAYER.get_image('a', 12)[0]
S_WARLOCK = PLAYER.get_image('o', 4)[0]
S_IDIOT = PLAYER.get_image('a', 4)[0]
S_ROUGE = PLAYER.get_image('e', 2)[0]
S_KING = PLAYER.get_image('e', 12)[0]

#   name, vitality, dexterity, strength , intelligence , wisdom , luck, items(string), description(1-3), image
# 	(affects health),(affects hit chance and item req),(affects damage and item req),(spell req),(max mana)
#                                                               = 18

#KNIGHT Pride
CHAR_KNIGHT = ["Knight", 8, 1, 4, 1, 2, 2, "Sword, Chain Mail", "Has come seeking glory, and belives he will be the one", "to clense the cathedral of all it's evil.",  "Belives that he can conqer any demon that dares stand in his way", S_KNIGHT]
#CLERIC Greed
CHAR_CLERIC = ["Cleric", 8, 1, 1, 2, 4, 2, "Candle Stick, Sacred Ring, and Holy Light spell", "Knows of valuable artifacts left behind when the cathedral was lost.", "Artifacts such as these could gain him influence over the other clergymen,", "as well as fetch heaps of gold at auction", S_CLERIC]
#DRUNK Sloth
CHAR_DRUNK = ["Town Drunk", 12, 0, 3, 0, 1, 2, "Broken Bottle, Booze", "Spent the last of his inheritance at the tavern last night,", "woke up locked in the cathedral with no recollection of what happened", "", S_DRUNK]
#WARLOCK Wrath
CHAR_WARLOCK = ["Warlock", 6, 0, 0, 4, 6, 1, "Lightning, Fireball, and Blood Bolt spells", "Hopes to make a deal with the vile demons below", "The aid of such creatures will give him the power to crush his enemies", "and bring great suffering the witch hunters who have caused him so much grief", S_WARLOCK]
#IDIOT Lust
CHAR_IDIOT = ["Village Idiot", 9, 1, 1, 0, 0, 7, "sparklyie dimund", "Was looking for shiny rocks so princess will talk to him again. But he fell", "down hole instead. This however doesn't bother him, he hopes to find new", "princess that will spend time with him, and one that doesn't smell so bad", S_IDIOT]
#ROUGE Envy
CHAR_ROUGE = ["Rouge", 7, 4, 2, 1, 2, 2, "Dirk, Cloak", "Jealous of the wealthy kings, and dashing knights, seeks fame to overshadow all", "those who who were born lucky. Ledgends tell of the glory", "thats befalls the one who returns from the depths of the cathedral", S_ROUGE]
#KING Gluttony
CHAR_KING = ["King", 8, 1, 2, 2, 2, 3, "Broken Crown", "Thrown into the cathedral by his angry subjects rioting over his unjust", "treatment. Half the village starved while the king stuffed his face. The king", "allowed his subjects to suffer and die while he benefited from their hard work", S_KING]





char_dict = {
	
	"CHAR_KNIGHT" : CHAR_KNIGHT,
	"CHAR_CLERIC" : CHAR_CLERIC,
	"CHAR_DRUNK" : CHAR_DRUNK,
	"CHAR_WARLOCK" : CHAR_WARLOCK,
	"CHAR_IDIOT" : CHAR_IDIOT,
	"CHAR_ROUGE" : CHAR_ROUGE,
	"CHAR_KING" : CHAR_KING


}


DEPTH_PLAYER = -100
DEPTH_CREATURES = 1
DEPTH_ITEM = 2



MESSAGES = [
	
	"The cows hide secrets",
	"The mysterious shopkeepers seem to be aware the effects and value of the potions scattered about",
	"\"...I would later find that the magically enchanted blade had a terrible curse upon it...\"",
	"\"...the wretched catacombs beneath the cathedral draws sinners like moths to a flame...\"",
	"\"The enchanted bonfire seems to have accelerated the rate at which I recover from my wounds, but the infection remains...\"",
	"\"... yet another failed attempt to sacrafice an undead, I'll need to find a fresh corpse if I am to have any more success\"",


]



def post_init_load():

	pass







print("constants.py - Success")

