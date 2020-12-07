from components.ai import HostileEnemy
from components import consumable
from components.fighter import Fighter
from components.inventory import Inventory

from entity import Actor, Item
from ailments import Ailments

import sound_engine

player = Actor(
	char="@",
	color=(255, 255, 255),
	name="Player",
	ai_cls=HostileEnemy,
	aiConfig={"blockCost":0,"corpseCost":0},
	fighter=Fighter(hp=30, defense=2, power=5, hurtSound=sound_engine.playerHurt, deathSound=sound_engine.playerDead),
	inventory=Inventory(capacity=26),
	ailments=Ailments()
	)

infected = Actor(
	char="i",
	color=(64, 64, 128),
	name="Infected",
	ai_cls=HostileEnemy,
	aiConfig={"blockCost":10,"corpseCost":3},
	fighter=Fighter(hp=10, defense=0, power=3, hurtSound=sound_engine.infectedHurt, deathSound=sound_engine.infectedDead),
	inventory=Inventory(capacity=0),
	ailments=Ailments()
	)

infectedGunner = Actor(char="I",
	color=(32, 32, 128),
	name="Infected Brute",
	ai_cls=HostileEnemy,
	aiConfig={"blockCost":30,"corpseCost":15},
	fighter=Fighter(hp=16, defense=1, power=4, hurtSound=sound_engine.infectedHurt, deathSound=sound_engine.infectedDead),
	inventory=Inventory(capacity=0),
	ailments=Ailments()
	)


stim_stick = Item(
	char="/",
	color=(127, 0, 255),
	name="Stim Stick",
	consumable= consumable.HealingConsumable(amount=4, tolerance=True, sound=sound_engine.stim_stick))

homing_grenade = Item(
	char="*",
	color=(255,255,0),
	name="Homing Grenade",
	consumable = consumable.HomingGrenadeConsumable(damage=20, maximum_range=9, sound=sound_engine.homing_grenade))

zip_gun = Item(
	char="l",
	color=(255,255,0),
	name="Zip Gun",
	consumable = consumable.ZipGunConsumable(damage=12, sound=sound_engine.zip_gun))

zip_cannon = Item(
	char="l",
	color=(255,200,0),
	name="Zip Cannon",
	consumable = consumable.ZipGunConsumable(damage=24, sound=sound_engine.zip_cannon))

hand_grenade = Item(
	char="*",
	color=(255,0,100),
	name="Hand Grenade",
	consumable = consumable.GrenadeConsumable(damage=7, radius=2, sound=sound_engine.hand_grenade, speedMod=3))

nitroglyn_grenade = Item(
	char="*",
	color=(100, 0, 255),
	name="NitroGlyn Grenade",
	consumable = consumable.GrenadeConsumable(damage=16, radius=4, sound=sound_engine.nitroglyn_grenade, speedMod=4))

hand_gun = Item(
	char="f",
	color=(70, 70, 200),
	name="SemiAuto HandGun",
	consumable = consumable.BallisticGun(fireRate=1, damage=5, sound="hand_gun"))

small_magazine = Item(
	char="]",
	color=(230, 0, 0),
	name="Small Magazine",
	consumable = consumable.MagazineConsumable(magSize=10, sound="reloaded_sound"))

medium_magazine = Item(
	char="]",
	color=(230, 230, 0),
	name="Medium Magazine",
	consumable = consumable.MagazineConsumable(magSize=20, sound="reloaded_sound"))

large_magazine = Item(
	char=")",
	color=(0, 230, 0),
	name="Large Magazine",
	consumable = consumable.MagazineConsumable(magSize=40, sound="reloaded_sound"))




"""
LOOT TABLE
30% stim stick
15% zip gun
15% hand grenade
5% zip cannon
7% homing grenade
3% nitroglyn grenade
20% small mag
4% medium mag
1% large mag
-----
100%
"""


standeredLootTable = []
standeredLootTable.extend([stim_stick]*30)
standeredLootTable.extend([zip_gun]*15)
standeredLootTable.extend([hand_grenade]*15)
standeredLootTable.extend([zip_cannon]*5)
standeredLootTable.extend([homing_grenade]*7)
standeredLootTable.extend([nitroglyn_grenade]*3)
standeredLootTable.extend([small_magazine]*20)
standeredLootTable.extend([medium_magazine]*4)
standeredLootTable.extend([large_magazine]*1)