from typing import Tuple

import numpy as np


#Tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = np.dtype(
	[
		("ch", np.int32), #unicode codepoint, whatever that is
		("fg", "3B"), #3 unsigned bytes that make RGB colors
		("bg", "3B"), #same here
	]
)



#Tile structure for all the static tile data
tile_dt = np.dtype(
	[
		("walkable", np.bool), #true if it can be walked over
		("transparent", np.bool), #true if it doesnt block fov
		("dark", graphic_dt), #graphic if not in fov
		("light", graphic_dt), #graphic if it is in fov
	]
)


def new_tile(
	*, #mandates keywords so order is irrelevent
	walkable: int,
	transparent: int,
	dark: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]],
	light: Tuple[int, Tuple[int, int, int], Tuple[int, int, int]]
	) -> np.ndarray:
	#helper function for defineing tile types
	return np.array((walkable, transparent, dark, light), dtype=tile_dt)

#SHROUD is fog of war tiles
SHROUD = np.array((ord("?"), (24,24,24), (0,0,0)), dtype=graphic_dt)


floor = new_tile(
	walkable = True,
	transparent=True,
	dark=(ord("."), (128, 128, 128), (64, 64, 64)),
	light=(ord("."), (196,196,196), (160, 172, 172)), #(196,196,196), (160, 172, 172)
)

bloodyFloor = new_tile(
	walkable = True,
	transparent=True,
	dark=(ord("~"), (64, 0, 0), (32, 0, 0)),
	light=(ord("~"), (255,0,0), (128, 0, 0)), #(255,0,0), (128, 0, 0)
)

wall = new_tile(
	walkable = False,
	transparent=False,
	dark=(ord("#"), (96, 96, 96), (32, 32, 32)),
	light=(ord("#"), (0, 255, 255), (0, 196, 196)),
)