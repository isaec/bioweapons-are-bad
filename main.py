 #!/usr/bin/env python3
#library import##################
import tcod
import copy
import traceback
import time
###############################
#more of my code imports
###################################################
from engine import Engine
import entity_factories
from procgen import generate_dungeon
from sound_engine import error_sound
import color

import animation_engine

###################################################

def main() -> None:
	#game settings
	screen_width = 96 
	screen_height = 54 

	map_width = 80
	map_height = 45

	room_max_size = 10
	room_min_size = 6
	max_rooms = 15
	min_rooms = 12

	max_monsters_per_room = 4 #4
	min_monsters_per_room = 2 #2
	max_items_per_room = 3 #2 3
	min_items_per_room = 0

	#TARGET_FPS = 600


	#tileset
	tileset = tcod.tileset.load_tilesheet(
		"dejavu16x16_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD
	)

	player = copy.deepcopy(entity_factories.player)

	engine = Engine(player=player)

	engine.game_map = generate_dungeon(
		max_rooms=max_rooms,
		min_rooms=min_rooms,
		room_min_size=room_min_size,
		room_max_size=room_max_size,
		map_width=map_width,
		map_height=map_height,
		max_monsters_per_room=max_monsters_per_room,
		min_monsters_per_room=min_monsters_per_room,
		max_items_per_room=max_items_per_room,
		min_items_per_room=min_monsters_per_room,
		engine=engine
		)

	engine.update_fov()

	engine.message_log.add_message(
		"This is pre alpha gameplay, and subject to change. Welcome!", color.welcome_text, makePing = False)


	with tcod.context.new_terminal(
		screen_width,
		screen_height,
		tileset=tileset,
		title="bioweapons are bad",
		vsync=True
	) as context:
		root_console = tcod.Console(screen_width, screen_height, order="F")




		while True:

			root_console.clear()
			engine.event_handler.on_render(console=root_console)
			context.present(root_console)

			if engine.locking: eventHolder = tcod.event.wait()
			else: eventHolder = tcod.event.get()

			try:
				for event in eventHolder: #used to be wait instead of get
					context.convert_event(event)
					engine.event_handler.handle_events(event)
			except Exception:
				traceback.print_exc()
				#makes error noise
				engine.sound_engine.emitSound(error_sound)
				#print the error to the message log
				engine.message_log.add_message(traceback.format_exc(), color.error, makePing = False)


			

#bottem of program
if __name__ == "__main__":
    main()


#shops between levels, ranged enemie, reduce enemies?, all shopkeepers are same person, optional dialoge.
#slow regen for enemies? on last floor enemies can res.