from __future__ import annotations

import random
from typing import Iterator, Tuple, TYPE_CHECKING

import entity_factories
from game_map import GameMap
import tile_types
from tile_types import new_tile

import tcod

if TYPE_CHECKING:
	from engine import Engine



class RectangularRoom:
	def __init__(self, x: int, y: int, width: int, height: int):
		self.x1 = x
		self.y1 = y
		self.x2 = x + width
		self.y2 = y + height

	@property
	def center(self) -> Tuple[int, int]:
		center_x = int((self.x1 + self.x2) / 2)
		center_y = int((self.y1 + self.y2) / 2)

		return center_x, center_y

	@property
	def inner(self) -> Tuple[slice, slice]:
		#return inner area of room as 2D array index
		return slice(self.x1 +1, self.x2), slice(self.y1 + 1, self.y2)

	def intersects(self, other: RectangularRoom) -> bool:
		#return true if this room overlaps another rectangular room
		return (
			self.x1 <= other.x2
			and self.x2 >= other.x1
			and self.y1 <= other.y2
			and self.y2 >= other.y1
		)
		
def place_entities(
	room: RectangularRoom, dungeon: GameMap,  maximum_monsters: int,  maximum_items: int, minimum_items: int = 0, minimum_monsters: int = 0, forceSpawn: List[Items] = None
	) -> None:
	number_of_monsters = random.randint(minimum_monsters, maximum_monsters)
	number_of_items = random.randint(minimum_items, maximum_items)

	i = 0
	while i in range(number_of_monsters):
		x = random.randint(room.x1 + 1, room.x2 -1)
		y = random.randint(room.y1 + 1, room.y2 - 1)

		if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
			if random.random() < 0.8:
				entity_factories.infected.spawn(dungeon, x, y)
				i += 1
			else:
				entity_factories.infectedGunner.spawn(dungeon, x, y)
				i += 1
	i = 0
	while i in range(number_of_items):
		x = random.randint(room.x1 + 1, room.x2 -1)
		y = random.randint(room.y1 + 1, room.y2 - 1)
		if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
			random.choice(entity_factories.standeredLootTable).spawn(dungeon, x, y)
			i += 1

	if forceSpawn == None: return

	for Item in forceSpawn:
		spawned = False
		while spawned == False:
			x = random.randint(room.x1 + 1, room.x2 -1)
			y = random.randint(room.y1 + 1, room.y2 - 1)
			if not any(entity.x == x and entity.y == y for entity in dungeon.entities):
				Item.spawn(dungeon, x, y)
				spawned = True

def blood_stains(new_room: RectangularRoom, dungeon: GameMap):

	#rolls to add bloodstains to rooms floor
	if random.randint(0,6) == 0:

		stainX = random.randint(new_room.x1+1, new_room.x2-1)
		stainY = random.randint(new_room.y1+1, new_room.y2-1)

		dungeon.tiles[stainX, stainY] = tile_types.bloodyFloor

		bloodSplatter = 0
		while bloodSplatter in range(0,random.randint(2,4)):
			stainModX = random.choice((+1,0,-1))
			stainModY = random.choice((+1,0,-1))
			if not dungeon.tiles[stainX+stainModX,stainY+stainModY] in [tile_types.bloodyFloor, tile_types.wall]:
				dungeon.tiles[stainX+stainModX,stainY+stainModY] = tile_types.bloodyFloor
				bloodSplatter += 1


def tunnel_between(
	start: Tuple[int, int], end: Tuple[int, int],
	size = "1x", order = "ran"
) -> Iterator[Tuple[int, int]]:
	#if size is random, pick a random size
	if size == "ra":
		size = random.choice(("1x","2xT","2xB","3x"))

	#if order is random, pick one
	if order == "ran":
		order = random.choice(("htv", "vth"))


	x1, y1 = start
	x2, y2 = end


	#if its a default 1 wide tunnel
	if size == "1x":
		#Returns an L shape tunnel between two points

		if order == "htv":
			#Go horizontally then virtically
			corner_x, corner_y = x2, y1
		else:
			#go virticaly then horezontally
			corner_x, corner_y = x1, y2

		#Genereate tunnel cordenents
		for x, y in tcod.los.bresenham((x1, y1), (corner_x, corner_y)).tolist():
			yield x, y
		for x, y in tcod.los.bresenham((corner_x, corner_y), (x2, y2)).tolist():
			yield x, y

		#skips the rest of checks to save cpu
		return

	if size == "2xT":
		for x, y in tunnel_between(start, end, "1x", order):
			yield x, y
			yield x+1, y+1

		if order == "htv":
			corner_x, corner_y = x2, y1
		else:
			corner_x, corner_y = x1, y2

		#yield corner_x, corner_y
		yield corner_x+1, corner_y

		yield corner_x, corner_y+1
		yield corner_x+1, corner_y+1

	if size == "2xB":
		for x, y in tunnel_between(start, end, "1x", order):
			yield x, y
			yield x-1, y-1

		if order == "htv":
			corner_x, corner_y = x2, y1
		else:
			corner_x, corner_y = x1, y2

		#yield corner_x, corner_y
		yield corner_x-1, corner_y

		yield corner_x, corner_y-1
		yield corner_x-1, corner_y-1


	if size == "3x":
		for x, y in tunnel_between(start, end, "1x", order):
			yield x, y
			yield x+1, y+1
			yield x-1, y-1

		if order == "htv":
			corner_x, corner_y = x2, y1
		else:
			corner_x, corner_y = x1, y2

		yield corner_x, corner_y+1
		yield corner_x+1, corner_y+1
		yield corner_x-1, corner_y+1

		yield corner_x, corner_y-1
		yield corner_x+1, corner_y-1
		yield corner_x-1, corner_y-1

		yield corner_x, corner_y
		yield corner_x+1, corner_y
		yield corner_x-1, corner_y


		



def generate_dungeon(
	max_rooms: int,
	min_rooms: int,
	room_min_size: int,
	room_max_size: int,
	map_width: int,
	map_height: int,
	max_monsters_per_room: int,
	min_monsters_per_room: int,
	max_items_per_room: int,
	min_items_per_room: int,

	engine: Engine,
	) -> GameMap:
	#makes a dungeon map
	player = engine.player
	dungeon = GameMap(engine, map_width, map_height, entities=[player])

	rooms: List[RectangularRoom] = []

	bonusAttempts = 0
	r = 0
	while r in range(max_rooms) or len(rooms) < min_rooms:
		room_width = random.randint(room_min_size, room_max_size)
		room_height = random.randint(room_min_size, room_max_size)

		x = random.randint(0, dungeon.width - room_width - 1)
		y = random.randint(0, dungeon.height - room_height - 1)

		#our rect room class to make this easy
		new_room = RectangularRoom(x, y, room_width, room_height)

		#see if new room idea intersects with an old one
		if any(new_room.intersects(other_room) for other_room in rooms):
			continue # if this happens it intersects
		#otherwise its valid

		#dig out inner area
		dungeon.tiles[new_room.inner] = tile_types.floor

		#if this is the first room, set spawn
		if len(rooms) == 0:
			player.place(*new_room.center, dungeon)

			place_entities(room=new_room, dungeon=dungeon, maximum_monsters=0, minimum_items=0, maximum_items=1, 
				forceSpawn=[entity_factories.hand_gun, entity_factories.small_magazine, entity_factories.stim_stick, entity_factories.hand_grenade])

		else:
			#dig a tunnel between this room and last one
			for x, y in tunnel_between(rooms[-1].center, new_room.center, "ra"):
				dungeon.tiles[x, y] = tile_types.floor

			#rolls to add bloodstains
			blood_stains(dungeon=dungeon, new_room=new_room)

			#adds all the entities
			place_entities(room=new_room, dungeon=dungeon, minimum_monsters=min_monsters_per_room, maximum_monsters=max_monsters_per_room, maximum_items=max_items_per_room)
		

		#append new room to list
		rooms.append(new_room)

	

		r+=1


	#prints room number
	# for i in range(len(rooms)):
	# 	dungeon.tiles[rooms[i].center] = new_tile(
	# 		walkable = True,
	# 		transparent=True,
	# 		dark=(ord(chr(65 + i)), (128, 128, 128), (64, 64, 64)),
	# 		light=(ord(chr(65 + i)), (255, 255, 255), (160, 172, 172)))

	dungeon.rooms = rooms
	return dungeon