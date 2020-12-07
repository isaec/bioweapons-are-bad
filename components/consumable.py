from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import math

import actions
import color
import components.inventory
import tile_types
from components.base_component import BaseComponent
from exceptions import Impossible
from input_handlers import SingleRangedAttackHandler, AreaRangedAttackHandler, InventoryLoadHandler
import sound_engine as sa
import animation_engine

if TYPE_CHECKING:
	from entity import Actor, Item
	from ailments import Ailments


class Consumable(BaseComponent):
	parent: Item
	def __init__(self, sound: str):
		self.sound = sound

	@property
	def isAmmo(self):
		return False	

	#try to return an action for item
	def get_action(self, consumer: Actor) -> Optional[actions.Action]:
		return actions.ItemAction(consumer, self.parent)

	#Invoces this items ability
	#action is the context
	def activate(self, actions: actions.ItemAction) -> None:
		raise NotImplementedError()

	def consume(self) -> None:
		#remove consumed item from its containing inventory
		entity = self.parent
		inventory = entity.parent
		#emit its sound		
		if self.sound != None: self.engine.sound_engine.emitSound(self.sound)
		try:
			if isinstance(inventory, components.inventory.Inventory):
				inventory.items.remove(entity)
		except ValueError:
			inventory.quickAccess = None


class HealingConsumable(Consumable):
	def __init__(self, amount: int, tolerance: bool, sound: str):
		super().__init__(sound)
		self.amount = amount
		self.tolerance = tolerance

	def activate(self, action: actions.ItemAction) -> None:
		consumer = action.entity
		if self.tolerance: modifier = consumer.ailments.stimMod
		else: modifier = 0
		amount_recovered = consumer.fighter.heal(self.amount + modifier)

		if amount_recovered > 0:
			self.engine.message_log.add_message(
				f"You use the {self.parent.name}, and recover {amount_recovered} HP!",
				color.health_recovered,
				makePing=False
				)
			self.consume()
			#adds tolerance if needed
			if self.tolerance:
				consumer.ailments.gainTolerance()
		else:
			raise Impossible(f"Your health is already full.")


class HomingGrenadeConsumable(Consumable):
	def __init__(self, damage: int, maximum_range: int, sound: str):
		super().__init__(sound)
		self.damage = damage
		self.maximum_range = maximum_range

	def activate(self, action: actions.ItemAction) -> None:
		consumer = action.entity
		target = None
		closest_distance = self.maximum_range + 1.0

		for actor in self.engine.game_map.actors:
			if actor is not consumer and self.parent.gamemap.visible[actor.x, actor.y]:
				distance = consumer.distance(actor.x, actor.y)

				if distance < closest_distance:
					target = actor
					closest_distance = distance

		if target:
			self.engine.message_log.add_message(
				f"The homing grenade finds the {target.name} and rams them with a violent explosion for {self.damage} damage!",
				color.player_atk,
				makePing=False)
			target.fighter.take_damage(self.damage)
			self.consume()
		else:
			raise Impossible("The homing grenade finds no target and returns to your hand.")

class GrenadeConsumable(Consumable):
	def __init__(self, damage: int, radius: int, sound: str, speedMod: int = None):
		super().__init__(sound)
		self.damage = damage
		self.radius = radius
		if speedMod == None: self.speedMod = int(radius*1.5)
		else: self.speedMod = speedMod

	def get_action(self, consumer: Actor) -> Optional[actions.Action]:
		self.engine.message_log.add_message(
			"Select a target location for your grenade.", color.needs_target
		)
		self.engine.event_handler = AreaRangedAttackHandler(
			self.engine,
			radius=self.radius,
		    callback=lambda xy: actions.ItemAction(consumer, self.parent, xy),
		)
		return None

	def activate(self, action: actions.ItemAction) -> None:
		target_xy = action.target_xy

		if not self.engine.game_map.visible[target_xy]:
			raise Impossible("You cannot throw your grenade that far.")

		targets_hit = False
		for actor in self.engine.game_map.actors:
			if actor.distance(*target_xy) <= self.radius:
				self.engine.message_log.add_message(
					f"The {actor.name} is caught in the blast, taking {self.damage} damage!",
					color.player_atk,
					makePing=False
				)
				actor.fighter.take_damage(self.damage)
				targets_hit = True

		if not targets_hit:
			raise Impossible("There are no heat signatures in the blast radius")

		radius = self.radius
		x, y = target_xy[0], target_xy[1]
		targetx, targety = x - radius, y - radius
		for targetx in range(x - radius, x + radius + 1):
			for targety in range(y - radius, y + radius + 1):
				try:
					if (math.sqrt((targetx - x) ** 2 + (targety - y) ** 2) <= radius and
					self.engine.game_map.tiles[targetx, targety] == tile_types.wall):
						self.engine.game_map.tiles[targetx, targety] = tile_types.floor
				except IndexError: pass
		self.engine.animation_engine.emitAnimation(animation_engine.Explosion(cord=target_xy,radius=self.radius,color=self.parent.color, speedMod=self.speedMod))
		self.consume()



class ZipGunConsumable(Consumable):
	def __init__(self, damage: int, sound: str):
		super().__init__(sound)
		self.damage = damage

	def get_action(self, consumer: Actor) -> Optional[actions.Action]:
		self.engine.message_log.add_message(
			f"Select somthing to shoot with the {self.parent.name}.", color.needs_target
		)
		self.engine.event_handler = SingleRangedAttackHandler(
			self.engine,
			callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
		)
		return None

	def activate(self, action: actions.ItemAction) -> None:
		consumer = action.entity
		target = action.target_actor

		if not self.engine.game_map.visible[action.target_xy]:
			raise Impossible("You cannot shoot somthing you cannot see.")
		if not target:
			raise Impossible("You need to select somthing to shoot.")
		if target is consumer:
			raise Impossible("Please refrain from shooting yourself.")

		self.engine.message_log.add_message(
			f"The {self.parent.name} erupts in flame, spraying {target.name} with lead for {self.damage} damage!",
			color.player_atk,
			makePing=False)
		target.fighter.take_damage(self.damage)
		self.engine.animation_engine.emitAnimation(animation_engine.MuzzleFlash(cordStart=consumer.xy,cordEnd=target.xy))
		self.consume()
		

#I know I should make a new base class for this but I cant be fucking bothered
#I understand how to use the consumables I have set up, and I dont really feel like making things more complex
class BallisticGun(Consumable):
	def __init__(self, fireRate: int, damage: int, sound: str):
		super().__init__(sound)
		self.damage, self.fireRate = damage, fireRate
		self.mag = None
		self.loaded = False

	def get_action(self, consumer: Actor) -> Optional[actions.Acton]:
		if self.loaded == False:
			self.engine.message_log.add_message(
				f"Please load a magazine into the {self.parent.name}.", color.empty_clip)

			self.engine.event_handler = InventoryLoadHandler(
				self.engine,
				targetItem = self)
		else:
			self.engine.message_log.add_message(
			f"Select somthing to shoot with the {self.parent.name}.", color.needs_target)
			self.engine.event_handler = SingleRangedAttackHandler(
			self.engine,
			callback = lambda xy: actions.ItemAction(consumer, self.parent, xy),
		)
		return None

	def activate(self, action: actions.ItemAction) -> None:
		consumer = action.entity
		target = action.target_actor

		if not self.engine.game_map.visible[action.target_xy]:
			raise Impossible("You cannot shoot somthing you cannot see.")
		if not target:
			raise Impossible("You need to select somthing to shoot.")
		if target is consumer:
			raise Impossible("Please refrain from shooting yourself.")

		if self.mag.useAmmo(self):

			self.engine.message_log.add_message(
				f"The {self.parent.name} pierces {target.name} for {self.damage} damage!",
				color.player_atk,
				makePing=False)
			target.fighter.take_damage(self.damage)
			self.engine.sound_engine.emitSound("hand_gun")
			self.engine.animation_engine.emitAnimation(animation_engine.MuzzleFlash(cordStart=consumer.xy,cordEnd=target.xy))
			#self.engine.animation_engine.emitAnimation(animation_engine.Projectile(cordStart=consumer.xy,cordEnd=target.xy,speedMod=2))

		else:

			self.engine.message_log.add_message(
				f"Your {self.parent.name} dry fires. Your out!",
				color.impossible,
				makePing=False)
			self.engine.sound_engine.emitSound("gun_empty")


class MagazineConsumable(Consumable):
	def __init__(self, magSize: int, sound: str):
		super().__init__(sound)
		self.magSize = magSize
		self.ammo = magSize

	@property
	def isAmmo(self):
		return True
	

	def get_action(self, consumer: Actor) -> None:
		self.engine.message_log.add_message(
			f"You hold the {self.parent.name}. You need to load it into a firearm to use it.")

	def useAmmo(self, firearm: BallisticGun) -> bool:
		if self.ammo > 0:
			self.ammo -= 1
			return True
		if self.ammo <= 0:
			firearm.loaded = False
			return False
