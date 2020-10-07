
import constants
import sys
sys.path.insert(0, '..')
import libtcodpy as libtcod

def clamp(n, min, max = None):

	num = n
	if min != None:
		if num < min:
			num = min
	if max != None:
		if num > max:
			num = max

	return num 



def draw_text(display_surface, text, t_coords, color, back_color = None, font = "FONT_DEFAULT", center = False, return_surface = False):

	text_surf, text_rect = helper_text_objects(text, color, back_color, font)

	if not center:
		text_rect.topleft = t_coords
	else:
		text_rect.center = t_coords

	if return_surface == True or display_surface == None:
		return text_surf
	else:
		display_surface.blit(text_surf, text_rect)




def helper_text_objects(inc_text, inc_color, inc_bg, font1 = "FONT_DEFAULT"):

	font = constants.font_dict[font1]

	if inc_bg:
		Text_surface = font.render(inc_text, False, inc_color, inc_bg)

	else:
		Text_surface = font.render(inc_text, False, inc_color)

	return Text_surface, Text_surface.get_rect()

def helper_text_height(font1 = "FONT_DEFAULT"):

	font = constants.font_dict[font1]

	font_object = font.render('A', False, (0,0,0))
	font_rect = font_object.get_rect()

	return font_rect.height

def helper_text_width(text, font):

	font = constants.font_dict[font]

	font_object = font.render(text, False, (0,0,0))
	font_rect = font_object.get_rect()

	return font_rect.width

def draw_debug(surface, fps):

	draw_text(surface, ("FPS:" + str(int(fps)) + " Target-" + str(int(constants.FPS_LIMIT)) ), (constants.MENU_WIDTH,0), constants.COLOR_RED, constants.COLOR_BLACK )

def print_game_messages( msgs, surface,  color = constants.COLOR_WHITE, 
	 location = (0, 0),
	 bg = None,
	 spacer = "FONT_SPACER",
	 limit = None ):
		
	to_draw = msgs
	
	spacer_height = helper_text_height(spacer)

	start_x, start_y = location

	total_height = 0

	for message,color,mfont in reversed(to_draw):

		text_height = helper_text_height(mfont)

		for msg in wrapline(message, constants.font_dict[mfont], constants.MENU_WIDTH - 25):

			if (not limit) or (limit > text_height + total_height) :
				draw_text(surface, replace(msg),
				 (start_x, (start_y + total_height) ),
					 color, bg, font = mfont)


			total_height+=text_height
		if (not limit) or (limit > text_height + total_height) :
			draw_text(surface, ("_____________________________________________________"), (start_x, (start_y + total_height)),
			 (255,255,255), bg, font = spacer)

			total_height+=spacer_height

def replace(string, old = '~', new = ' '):
	return string.replace(old, new)


def find_radius(coords, radius, include_center = True):

	center_x,center_y = coords

	tile_list = []

	for x in range( int(center_x - radius), int(center_x + radius + 1) ):
		for y in range(int(center_y - radius), int(center_y + radius + 1)):
			tile_list.append((x,y))

	if include_center == False:
		done = False
		while done == False:
			try:
				tile_list.remove(coords)
			except:
				done = True

	return tile_list

def attackable_tiles(given_x, given_y, width, height):

	tiles = []

	for x in range(given_x, given_x + width + 1):
		tiles.append((x, given_y - 1))
		tiles.append((x, given_y + height + 1))

	for y in range(given_y, given_y + height + 1):
		tiles.append((given_x - 1, y))
		tiles.append((given_x + width + 1, y))

	return tiles


def find_line(coords1, coords2):

	x1,y1 = coords1

	x2,y2 = coords2

	libtcod.line_init(x1,y1,x2,y2)

	calc_x, calc_y = libtcod.line_step()

	coord_list = []

	if x1 == x2 and y1 == y2:
		return [x1, y1]

	while (not calc_x is None):
		coord_list.append((calc_x,calc_y))

		calc_x, calc_y = libtcod.line_step()

	return coord_list


def easy_return(value):

	return value


# def math_string_to_int(string):

# 	parts = []

# 	parts = string.split()
# 	numbers = []

# 	for part in parts:
# 		part_is_number = True
# 		for char in part:
# 			if char != "1" and char != "2" and char != "3" and char != "4" and char != "5" and char != "6" and char != "7" and char != "8" and char != "9" and char != "0":
# 			 	part_is_number = False


# 		if part_is_number == True:
# 			numbers.append(float(part))
# 		else:
# 			numbers.append("x")

# 	for part in parts:
# 		if part == "*" or part == "/":
			




	return numbers


########TEXT WRAP##########

from itertools import chain

def truncline(text, font, maxwidth):
        real=len(text)       
        stext=text           
        l=font.size(text)[0]
        cut=0
        a=0                  
        done=1
        old = None
        while l > maxwidth:
            a=a+1
            n=text.rsplit(None, a)[0]
            if stext == n:
                cut += 1
                stext= n[:-cut]
            else:
                stext = n
            l=font.size(stext)[0]
            real=len(stext)               
            done=0                        
        return real, done, stext             
        
def wrapline(text, font, maxwidth): 
    done=0                      
    wrapped=[]                  
                               
    while not done:             
        nl, done, stext=truncline(text, font, maxwidth) 
        stext = stext.strip()
        stext = stext.replace("~", " ")
        
        wrapped.append(stext)                  
        text=text[nl:]                                 
    return wrapped


def wrap_multi_line(text, font, maxwidth):
    """ returns text taking new lines into account.
    """
    lines = chain(*(wrapline(line, font, maxwidth) for line in text.splitlines()))
    return list(lines)























print ("Util.py - Success")



