from __future__ import annotations


from typing import TYPE_CHECKING, Tuple, Optional
import random

import color
import exceptions

import sound_engine
import animation_engine

if TYPE_CHECKING:
	from engine import Engine
	from entity import Actor, Entity, Item





class Action:
	def __init__(self, entity: Actor) -> None:
		super().__init__()
		self.entity = entity
		self.freeAction = False

	@property
	def engine(self) -> Engine:
		#returns the engine this action belongs to
		return self.entity.gamemap.engine
		"""perform this action with the objects needed to determin scope.

		'self.engine' is the scope this is being performed in.

		'self.entity' is the object performing the action

		this method must be overridden by Action subclasses
		"""
		raise NotImplementedError()

#pickup and item and add it to the inventory, if there is room
class PickupAction(Action):
	def __init__(self, entity: Actor):
		super().__init__(entity)

	def perform(self) -> None:
		actor_location_x = self.entity.x
		actor_location_y = self.entity.y
		inventory = self.entity.inventory

		for item in self.engine.game_map.items:
			if actor_location_x == item.x and actor_location_y == item.y:
				if len(inventory.items) >= inventory.capacity:
					raise exceptions.Impossible("Your inventory is full.")

				self.engine.game_map.entities.remove(item)
				item.parent = self.entity.inventory
				inventory.items.append(item)

				self.engine.message_log.add_message(f"You picked up the {item.name}!",makePing=False)
				self.engine.sound_engine.emitSound(sound_engine.item_pickup)
				self.entity.ailments.ailmentTick()
				return

		raise exceptions.Impossible("There is nothing here to pick up.")




class ItemAction(Action):
	def __init__(
		self, entity: Actor, item: Item, target_xy: Optional[Tuple[int, int]] = None, targetItem: Optional[Item] = None
		):
		super().__init__(entity)
		self.item = item
		self.targetItem = targetItem
		if not target_xy:
			target_xy = entity.x, entity.y
		self.target_xy = target_xy

	@property
	def target_actor(self) -> Optional[Actor]:
		#returns the actor at this actions destianation
		return self.engine.game_map.get_actor_at_location(*self.target_xy)

	#invoke the items ability - this action will be given to provide contrxt
	def perform(self) -> None:
		try:
			self.item.consumable.activate(self)
			self.entity.ailments.ailmentTick()
		except:
			self.item.consumable.activate(self)
		

	

class DropItem(ItemAction):
	def perform(self) -> None:
		self.entity.inventory.drop(self.item)
		self.entity.ailments.ailmentTick()

class LoadItem(ItemAction):
	def perform(self) -> None:
		self.targetItem.mag = self.item.consumable
		self.targetItem.loaded = True
		self.engine.message_log.add_message(
			f"You load the {self.item.name} into the {self.targetItem.parent.name}", makePing=False
			)
		self.item.consumable.consume()
		#self.entity.inventory.items.remove(self.item)

class QuickAccess():
	def __init__(self, quickItem, engine):
		self.quickItem = quickItem
		self.engine = engine
		self.freeAction = True
	def perform(self):
		if self.quickItem != None:
			if self.quickItem in self.engine.player.inventory.items:
				self.quickItem.consumable.get_action(self.engine.player)
			else:
				self.engine.player.inventory.quickItem = None
				raise exceptions.Impossible("This item is no longer in your inventory.")
		else: raise exceptions.Impossible("You have no item bound to the F key.")


class WaitAction(Action):
	def perform(self) -> None:
		self.entity.ailments.ailmentTick()
		pass

class ActionWithDirection(Action):
	def __init__(self, entity: Actor, dx: int, dy: int):
		super().__init__(entity)

		self.dx = dx
		self.dy = dy

	@property
	def dest_xy(self) -> Tuple[int, int]:
		#returns this actions destination
		return self.entity.x + self.dx, self.entity.y + self.dy

	@property
	def blocking_entity(self) -> Optional[Entity]:
		#return the blocking entity at this actions destination
		return self.engine.game_map.get_blocking_entity_at_location(*self.dest_xy)

	@property
	def target_actor(self) -> Optional[Actor]:
		#returns the actor at this actions destination
		return self.engine.game_map.get_actor_at_location(*self.dest_xy)
	
	
	def perform(self) -> None:
		raise NotImplementedError()


class MeleeAction(ActionWithDirection):
	def perform(self) -> None:
		target = self.target_actor
		if not target:
			raise exceptions.Impossible("Nothing to attack.")

		damage = self.entity.fighter.power - target.fighter.defense

		attack_desc = f"{self.entity.name.capitalize()} attacks {target.name}"

		#makes color right
		if self.entity is self.engine.player:
			attack_color = color.player_atk
		else: attack_color = color.enemy_atk

		if damage > 0:
			self.engine.message_log.add_message(
				f"{attack_desc} for {damage} damage.", attack_color, makePing=False
				)

			target.fighter.hp -= damage

			target.fighter.makeHurtSound()

			self.engine.animation_engine.emitAnimation(animation_engine.Highlight(cord=target.xy,color=(255,50,50),duration=3,pulseLength=3))

			#check to see if enemy should bleed
			if target.fighter.max_hp <= damage*3 or target.fighter.hp <= target.fighter.max_hp/4:
				target.bleed(1)

		else:
			self.engine.message_log.add_message(
				f"{attack_desc} but does no damage. ({target.fighter.defense} defense)", attack_color, makePing=False
				)

		self.entity.ailments.ailmentTick()



class MovementAction(ActionWithDirection):
	def perform(self) -> None:
		dest_x, dest_y = self.dest_xy

		if not self.engine.game_map.in_bounds(dest_x, dest_y):
			#out of bounds
			raise exceptions.Impossible("That way is blocked.")
		if not self.engine.game_map.tiles["walkable"][dest_x, dest_y]:
			#Destination is blocked by a tile.
			raise exceptions.Impossible("That way is blocked.")
		if self.engine.game_map.get_blocking_entity_at_location(dest_x, dest_y):
			#destination is blocked by an entity
			raise exceptions.Impossible("That way is blocked.")


		#if if health is low, check if bleed - lower health is higher odds
		if random.randint(self.entity.fighter.hp, self.entity.fighter.max_hp) < self.entity.fighter.max_hp/3:
			self.entity.bleed(1)

		self.entity.move(self.dx, self.dy)
		self.entity.ailments.ailmentTick()

class BumpAction(ActionWithDirection):
	def perform(self) -> None:

		if self.target_actor:
			return MeleeAction(self.entity, self.dx, self.dy).perform()
		else:
			return MovementAction(self.entity, self.dx, self.dy).perform()