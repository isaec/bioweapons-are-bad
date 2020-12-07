from __future__ import annotations

import copy
import math
import random
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING, Union

from render_order import RenderOrder

import tile_types

if TYPE_CHECKING:
	from components.ai import BaseAI
	from components.consumable import Consumable
	from components.fighter import Fighter
	from components.inventory import Inventory
	from game_map import GameMap
	from ailments import Ailments

T = TypeVar("T", bound="Entity")


class Entity:
	"""
	A genaric object to represent players, enemies, items - anything that can move -
	"""

	parent: Union[GameMap, Inventory]


	def __init__(
		self,
		parent: Optional[GameMap] = None,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str ="<Unnamed>",
		blocks_movement: bool = False,
		render_order: RenderOrder = RenderOrder.CORPSE
		):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.name = name
		self.blocks_movement = blocks_movement
		self.render_order = render_order
		self.could_live = False
		if parent:
			#if this is false, then it will be set later
			self.parent = parent
			parent.entities.add(self)


	@property
	def is_alive(self):
		return False
	
	@property
	def gamemap(self) -> GameMap:
		return self.parent.gamemap
	
	@property
	def xy(self):
		return (self.x, self.y)
	

	#makes copy of instance at given point
	def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
		clone = copy.deepcopy(self)
		clone.x = x
		clone.y = y
		clone.parent = gamemap
		gamemap.entities.add(clone)
		return clone

	#place this entity at new location, handles movine across GameMaps
	def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
		self.x = x
		self.y = y
		if gamemap:
			#may be unintilized
			if hasattr(self, "parent"):
				if self.parent is self.gamemap:
					self.gamemap.entities.remove(self)

			self.parent = gamemap
			gamemap.entities.add(self)

	#returns distance between self and x,y
	def distance(self, x: int, y: int) -> float:
		return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

	def move(self, dx: int, dy: int) -> None:
		#moves by amount
		self.x += dx
		self.y += dy


class Actor(Entity):
	def __init__(
		self,
		*,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: Tuple[int, int, int] = (255, 255, 255),
		name: str = "<Unnamed>",
		ai_cls: Type[BaseAI],
		aiConfig: dict,
		fighter: Fighter,
		inventory: Inventory,
		ailments: Ailments,
		):
		super().__init__(
			x=x,
			y=y,
			char=char,
			color=color,
			name=name,
			blocks_movement=True,
			render_order=RenderOrder.ACTOR,
			)

		self.ai: Optional[BaseAI] = ai_cls(self, blockCost=aiConfig["blockCost"], corpseCost=aiConfig["corpseCost"])

		self.fighter = fighter
		self.fighter.parent = self

		self.inventory = inventory
		self.inventory.parent = self

		self.ailments = ailments
		self.ailments.parent = self

		self.could_live = True

	@property
	def is_alive(self) -> bool:
		#returns true as long as this actor can perform actions
		return bool(self.ai)

	@property
	def locTuple(self) -> Tuple(self.x, self.y):
		return (self.x, self.y)
	

	#makes bloodyFloor around actor
	def bleed(self, amount: int >= 1 = 1):
		#first blood
		if amount > 0:
			#makes sure there isnt already blood under actor, so it can go next to
			if not self.gamemap.tiles[self.x, self.y] in [tile_types.bloodyFloor, tile_types.wall]:
				self.gamemap.tiles[self.x, self.y] = tile_types.bloodyFloor
				amount -= 1

		#iteration variable to prevent cpu overuse
		iteration = 0
		#all the rest fo the blood
		while amount > 0:
			#picks random modifier
			stainX = random.choice((+1,0,-1))
			stainY = random.choice((+1,0,-1))

			#tests if its a valid space for blood
			if not self.gamemap.tiles[self.x+stainX, self.y+stainY] in [tile_types.bloodyFloor, tile_types.wall]:
				#if it is, put blood, and reduce amount by 1
				self.gamemap.tiles[self.x+stainX, self.y+stainY] = tile_types.bloodyFloor
				amount -= 1

			iteration += 1
			if iteration > 100: return #stops trying after 100 attempts


class Item(Entity):
	def __init__(
		self,
		*,
		x: int = 0,
		y: int = 0,
		char: str = "?",
		color: tuple[int, int, int] = (255, 255, 255),
		name: str = "<Unnamed>",
		consumable: Consumable,
		):
		super().__init__(
			x=x,
			y=y,
			char=char,
			color=color,
			name=name,
			blocks_movement=False,
			render_order=RenderOrder.ITEM,
			)

		self.consumable = consumable
		self.consumable.parent = self


		
	