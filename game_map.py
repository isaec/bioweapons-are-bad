from __future__ import annotations

from typing import Iterable, Iterator, Optional, TYPE_CHECKING

import numpy as np
from tcod.console import Console

from entity import Actor, Item
import tile_types

if TYPE_CHECKING:
	from engine import Engine
	from entity import Entity

class GameMap:
	def __init__(
		self, engine: Engine, width: int, height: int, entities: Iterable[Entity] = ()
		):
		self.engine = engine
		self.width, self.height = width, height
		self.entities = set(entities)
		self.tiles = np.full((width, height), fill_value=tile_types.wall, order="F")
		self.rooms = None

		self.visible = np.full(
		(width, height), fill_value=False, order="F"
		) #Tiles player can see
		self.explored = np.full(
		(width, height), fill_value=False, order="F"
		) #Tiles player has seen

	@property
	def gamemap(self) -> GameMap:
		return self
	

	#iterates over maps living actors
	@property
	def actors(self) -> Iterator[Actor]:
		yield from (
			entity
			for entity in self.entities
			if isinstance(entity, Actor) and entity.is_alive)
		
	@property
	def items(self) -> Iterator[Item]:
		yield from (entity for entity in self.entities if isinstance(entity, Item))
	

	def get_blocking_entity_at_location(
		self, location_x: int, location_y: int,
		) -> Optional[Entity]:

		for entity in self.entities:
			if (entity.blocks_movement
			and entity.x == location_x
			and entity.y == location_y):
				return entity

		return None

	def get_actor_at_location(self, x: int, y: int) -> Optional[Actor]:
		for actor in self.actors:
			if actor.x == x and actor.y == y:
				return actor

		return None


	def in_bounds(self, x: int, y: int) -> bool:
		#true if x and y are in bounds of map
		return 0 <= x < self.width and 0 <= y < self.height

	def render(self, console: Console) -> None:
		"""
		Renders the map.

		If a title is in the visible array then draw it with the light colors
		If it isnt but is in the explored array, draw it dark - 
		Otherwise, draw it with shroud.
		"""
		console.tiles_rgb[0 : self.width, 0 : self.height] = np.select(
			condlist=[self.visible, self.explored],
			choicelist=[self.tiles["light"], self.tiles["dark"]],
			default=tile_types.SHROUD,
		)

		entities_sorted_for_rendering = sorted(
			self.entities, key=lambda x: x.render_order.value)

		#renders each entity
		for entity in entities_sorted_for_rendering:
			#only print entities in FOV(Make true for ai debug)
			if self.visible[entity.x, entity.y]:
				console.print(
					x=entity.x, y=entity.y, string=entity.char, fg=entity.color)