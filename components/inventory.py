from __future__ import annotations

from typing import List, TYPE_CHECKING

from components.base_component import BaseComponent

if TYPE_CHECKING:
	from entity import Actor, Item


class Inventory(BaseComponent):
	parent: Actor

	def __init__(self, capacity: int):
		self.capacity = capacity
		self.items: List[Item] = []
		self.quickAccess = None

	

	def drop(self, item:Item) -> None:
		#removes item from inventory and puts it on map, at players location
		self.items.remove(item)
		item.place(self.parent.x, self.parent.y, self.gamemap)

		self.engine.message_log.add_message(f"You dropped the {item.name}.")