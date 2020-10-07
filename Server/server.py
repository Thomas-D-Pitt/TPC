import PodSixNet, time
import pygame

from PodSixNet.Channel import Channel
from PodSixNet.Server import Server

import json
import zlib

from time import sleep

class ClientChannel(Channel):

	def Network(self, data):#Whenever the client does connection.Send(mydata), the Network() method will be called. 
		# print data
		# global PRINT
		# PRINT.append(str(data))
		pass
	
	def Network_myaction(self, data):#
		self._server.send_myaction(data)
		#print "myaction:", data
		#The method Network_myaction() will only be called if your data has a key called 'action' with a value of "myaction". 
		#my action can be replaced with any keyword
		#In other words if it looks something like this: data = {"action": "myaction", "blah": 123, ... }

	#def Network_leaveserver(self, data):
		#self._server.remove_player(data["id"])

	def Network_playermoved(self, data):
		self._server.update_pos(data)

	def Network_close(self, data):
		exit()

	def Network_new_map(self, data):
		self._server.share_map(data)

	def Network_leaveserver(self, player_id):

		self._server.remove_player(player_id)

	def Network_clear_cache(self, data):

		self._server.maps = []
		self._server.channels = []
		self._server.channel_player_info = []

	def Network_obj_update(self, data):
		self._server.obj_update(data)

	def Network_ate(self, data):
		self._server.ate(data)


	def Network_tile_update(self, data):

		self._server.tile_update(data)

	def Network_new_object(self, data):

		self._server.new_obj(data)

	def Network_get_retro_updates(self, data):

		#print "MID:", data["map_id"]

		self._server.send_retro_updates(data["id"], data["map_id"])

	def Network_death(self, data):

		self._server.death(data)

	def Network_game_start(self, data):

		self._server.no_new_clients()

class MyServer(Server):
	
	channelClass = ClientChannel
	#Set channelClass to the channel class that you created above.


	def __init__(self, *args, **kwargs):
		Server.__init__(self, *args, **kwargs)

		self.channels = []
		self.channel_player_info = []

		self.maps = []

		self.next_id_object = 0

		self.saved_map_id = 0
		self.saved_obj_id = 0

		self.retro_updates_objs = []
		self.retro_updates_tiles = []

		self.player_count = 0

		self.new_channels = True

	@property
	def next_map_id(self):

		self.saved_map_id += 5

		return self.saved_map_id

	@property
	def next_obj_id(self):

		self.saved_obj_id += 5

		return self.saved_obj_id
	
	def Connected(self, channel, addr):
		global PRINT

		if self.new_channels == True:

			new_id = len(self.channels)

			channel.Send({"action": "joinedserver", "id": new_id})

			for saved_map in self.maps:
				channel.Send(saved_map)

			self.channels.append(channel)
			self.channel_player_info.append({"id": new_id, "x": 0, "y": 0, "class": "CHAR_KNIGHT", "name": "thomas"})
			print 'new connection:', channel


			self.player_count += 1
			print "total players:", self.player_count

			PRINT.append("new connection:" + str(channel))

			#The method Connected() will be called whenever a new client connects to your server.
			#You need to call Server.Pump() every now and then, probably once per game loop.

			for client in self.channels:
				client.Send({"action": "player_count", "player_count": self.player_count})



	def send_myaction(self, data):
		for client in self.channels:
			client.Send(data)

	def send_to_all(self, data):
		for client in self.channels:
			client.Send(data)

	def remove_player(self, player_id):
		i = 0
		for c_id in self.channel_player_info:
			if c_id == player_id:
				self.channels[i] = None
				self.channel_player_info[i] = None

			i+=1

		other_ids = []

		i = 0
		for client in self.channels:
			other_ids.append(self.channel_player_info[i])	

			i+=1

		for client in self.channels:
			client.Send({"action": "playerschanged", "other_players": other_ids})

	def update_pos(self, data):

		for info in self.channel_player_info:

			if info["id"] == data["id"]:
				info["x"] = data["x"]
				info["y"] = data["y"]

	def share_map(self, data):

		data["action"] = "setmap"
		#data["map_id"] = self.next_map_id

		compressed_objs = data["objects"]
		objects_simplified = json.loads(zlib.decompress(compressed_objs))

		new_objs = []
		for simple_obj in objects_simplified:
			func, params, obj_x, obj_y, obj_hp, obj_id_old = simple_obj
			new_objs.append((func, params, obj_x, obj_y, obj_hp, obj_id_old, self.next_obj_id))

		data["objects"] = zlib.compress(json.dumps(new_objs))

		self.maps.append(data)

		for client in self.channels:
			client.Send(data)

		print "sent out new map from:", data["id"], "with map id:", data["map_id"]

	def obj_update(self, data):

		#example data: {"action": "obj_update", "obj": (obj_id, x, y, hp), "map_id": GAME.current_map_id, "delete": delete, "id": self.id}

		data["action"] = "update_object"

		found_saved_object = False
		for i in range(len(self.retro_updates_objs)):
			d_packet = self.retro_updates_objs[i]
			packet_id, packet_x, packet_y, packet_hp = d_packet["obj"]
			obj_id, x, y, hp = data["obj"]

			
			if packet_id == obj_id:
				self.retro_updates_objs[i] = data
				found_saved_object = True
				#print "overwrote id:", obj_id, "for map:", data["map_id"]
				break


		if found_saved_object == False:
			self.retro_updates_objs.append(data)
			#print "new packet:", data
			
			

		for client in self.channels:
			client.Send(data)

	def tile_update(self, data):

		data["action"] = "update_tile"

		found_saved_object = False
		for i in range(len(self.retro_updates_tiles)):
			coords = self.retro_updates_tiles[i]
			if coords == data["coords"]:

				self.retro_updates_tiles[i] = data
				found_saved_object = True
				break


		if found_saved_object == False:
			self.retro_updates_tiles.append(data)

		for client in self.channels:
			client.Send(data)

	def send_retro_updates(self, target_id, map_id):
		#print "trying to sent retro update"
		for client in self.channels:

	 		for packet in self.retro_updates_objs:
	 			#print "trying to sent retro update map_id", map_id, "?", packet["map_id"]

	 			if packet["map_id"] == map_id:
	 				temp_packet = packet
	 				temp_packet["retro"] = True
	 				client.Send(temp_packet)

	 		for packet in self.retro_updates_tiles:

	 			if packet["map_id"] == map_id:
	 				temp_packet = packet
	 				temp_packet["retro"] = True
	 				client.Send(temp_packet)

	def send_next_id_object(self):

		for client in self.channels:
			client.Send({"action": "next_id", "id": self.next_id_object})

	def new_obj(self, data):

		data["action"] = "new_obj"
		#data["obj_id"] = self.next_map_id

		compressed_obj = data["object"]
		simple_obj = json.loads(zlib.decompress(compressed_obj))

		
		func, params, obj_x, obj_y, obj_hp, obj_id_old = simple_obj

		new_obj = (func, params, obj_x, obj_y, obj_hp, obj_id_old, self.next_obj_id)

		data["object"] = zlib.compress(json.dumps(new_obj))


		for client in self.channels:
			client.Send(data)

		#print "sent out new obj from:", data["id"], "with map id:", data["map_id"]

	def death(self, data):
		for client in self.channels:
			client.Send({"action": "death"})

		self.channels = []
		self.channel_player_info = []

		self.maps = []

		self.next_id_object = 0

		self.saved_map_id = 0
		self.saved_obj_id = 0

		self.retro_updates_objs = []
		self.retro_updates_tiles = []

	def no_new_clients(self):

		self.new_channels = False
		global PRINT
		PRINT.append("Game started, no new clients can connect")

	def ate(self, data):

		for client in self.channels:
			client.Send(data)

def handle_input():

	events_list = pygame.event.get()


	#todo process input
	for event in events_list:
		if event.type == pygame.QUIT:
			return "QUIT"

def draw_text(display_surface, text, t_coords, color, font, back_color = None, center = False):

	text_surf, text_rect = helper_text_objects(text, color, back_color, font)

	if not center:
		text_rect.topleft = t_coords
	else:
		text_rect.center = t_coords

	display_surface.blit(text_surf, text_rect)

def helper_text_objects(inc_text, inc_color, inc_bg, font1):

	font = font1

	if inc_bg:
		Text_surface = font.render(inc_text, False, inc_color, inc_bg)

	else:
		Text_surface = font.render(inc_text, False, inc_color)

	return Text_surface, Text_surface.get_rect()

def helper_text_height(font1):

	font = font1

	font_object = font.render('A', False, (0,0,0))
	font_rect = font_object.get_rect()

	return font_rect.height

def helper_text_width(text, font):

	font = font

	font_object = font.render(text, False, (0,0,0))
	font_rect = font_object.get_rect()

	return font_rect.width

def main():
	global PRINT
	pygame.init()
	pygame.display.set_caption('TPC Server')
	SURFACE_MAIN = pygame.display.set_mode( (600, 400) )
	SURFACE_MAIN.fill((0, 0, 140))
	FONT = pygame.font.Font("LibreBaskerville-Bold.ttf", 12)

	PRINT = []
	menu_font = FONT
	buff = 5
	color = (255,255,255)
	line = 0
	draw_text(SURFACE_MAIN, "STARTING SERVER ON LOCALHOST", (0+buff, 0+buff + (line)*helper_text_height(menu_font)), color, menu_font)
	line+=1

	f = open("Address_Server.txt", "r")
	address=f.read()#raw_input("Host:Port (localhost:8000): ")
	if not address:
		
	    host, port= "localhost", 8000

	else:

		address = address.replace(" ", "")
		host,port=address.split(":")


	server = MyServer(localaddr=(host, int(port)))

	print "Host:", host, "Port:", port


	draw_text(SURFACE_MAIN, ("Host: " + str(host) + " Port: " + str(port)), (0+buff, 0+buff + (line)*helper_text_height(menu_font)), color, menu_font)
	line+=1
	#draw_text(SURFACE_MAIN, "PLAYERS:" + str(server.player_count), (0+buff, 0+buff + (line)*helper_text_height(menu_font)), color, menu_font)
	#line+=1 #for the player count message

	pygame.display.flip()

	while True:

		action = handle_input()
		if action == "QUIT":
			break

		server.Pump()

		SURFACE_MAIN.fill((0, 0, 140))

		line = 0
		draw_text(SURFACE_MAIN, ("Host: " + str(host) + " Port: " + str(port)), (0+buff, 0+buff + (line)*helper_text_height(menu_font)), color, menu_font)
		line+=1
		draw_text(SURFACE_MAIN, "PLAYERS:" + str(server.player_count), (0+buff, 0+buff + (line)*helper_text_height(menu_font)), color, menu_font)
		line+=1 #for the player count message

		for msg in PRINT:
			draw_text(SURFACE_MAIN, msg, (0+buff, 0+buff + (line)*helper_text_height(menu_font)), color, menu_font)
			line+=1


		pygame.display.flip()

		sleep(.0001)

	pygame.quit()
	#exit()

#When you want to send data to a specific client/channel, use the Send method of the Channel class:
#channel.Send({"action": "hello", "message": "hello client!"})

print "STARTING SERVER ON LOCALHOST"
main()
# f = open("Address_Server.txt", "wt")
# f.write("localhost:3000")
# f.close()


