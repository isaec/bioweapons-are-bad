#library imports######################################
from __future__ import annotations
from typing import TYPE_CHECKING
######################################################
#tcod imports#########################################
from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov
from tcod import FOV_RESTRICTIVE
######################################################
#my code imports######################################
import exceptions
from input_handlers import MainGameEventHandler
from message_log import MessageLog
from render_functions import render_bar, render_names_at_mouse_location, render_enviroment_hud
import sound_engine
import animation_engine
######################################################

if TYPE_CHECKING:
	from entity import Entity
	from game_map import GameMap
	from input_handlers import EventHandler
	from ailments import Ailments


class Engine:
	game_map: GameMap

	def __init__(self, player: Actor):
		self.event_handler: EventHandler = MainGameEventHandler(self)
		self.message_log = MessageLog(engine=self)
		self.mouse_location = (0, 0)
		self.player = player
		self.sound_engine = sound_engine.SoundEngine()
		self.animation_engine = animation_engine.AnimationEngine(engine=self)

	@property
	def locking(self):
		if self.animation_engine.hasActive: return False
		if self.event_handler.unlock: return False
		return True
	

	def handle_enemy_turns(self) -> None:
		for entity in set(self.game_map.actors) - {self.player}:
			if entity.ai:
				try:
					entity.ai.perform()
				except exceptions.Impossible:
					pass


	#recompute visible area based on players position and view
	#determins if player should be alerted because they revealed somthing
	def update_fov(self) -> None:
		self.game_map.visible[:] = compute_fov(
			self.game_map.tiles["transparent"],
			(self.player.x, self.player.y),
			radius=17,
			algorithm=FOV_RESTRICTIVE
		)
		#if somthing is visible, add it to explored
		self.game_map.explored |= self.game_map.visible

		#makes list of currently visible things, sorts by living ai
		#if this is them being revealed, ping, and flash animation
		for entity in set(self.game_map.actors) - {self.player}:
			if entity.ai:
				if entity.ai.shouldPing():
					self.sound_engine.queueSound("hostile_seen")
					self.animation_engine.emitAnimation(animation_engine.Highlight(cord=entity.xy,color=(255,255,230)))
		self.sound_engine.pushQueue("hostile_seen")

	def render(self, console: Console) -> None:
		self.game_map.render(console)
		self.animation_engine.animateFrame(console)

		#ui and shizz
		console.draw_frame(x=0, y=45, width=22, height=9, title="Condition", fg=(150,150,150), bg=(0,0,0))

		console.print(x=0, y=49,
			string="├────────────────────┤")

		console.draw_frame(x=22, y=45, width=58, height=9, title="Game Log", fg=(150,150,150), bg=(0,0,0))

		console.draw_frame(x=80, y=0, width=16, height=54, title="Enviroment", fg=(150,150,150), bg=(0,0,0))

		console.print(x=80, y=50,
			string="├──────────────┤")


		heatSig = len(set(self.game_map.actors)-{self.player})
		signatureEnding = ""
		if heatSig != 1: signatureEnding = "s"
		console.print(
			x=81,
			y=51,
			string=f"{heatSig} heat \nsignature{signatureEnding}",
			fg=(255,255,255))

		self.message_log.render(console=console, x=23, y=46, width=56, height=7)

		render_bar(
			console=console,
			current_value=self.player.fighter.hp,
			maximum_value=self.player.fighter.max_hp,
			total_width=20,
			x=1,
			y=46)

		console.print(x=1, y=47,
			string=f"{self.player.fighter.defense} Defense\n{self.player.fighter.power} Melee Power")

		render_bar(
			console=console,
			current_value=self.player.ailments.toleranceCountdown,
			maximum_value=self.player.ailments.toleranceCountdownMax,
			total_width=20,
			x=1,
			y=50,
			string="Tolerance: ",
			flipColor=True)


		console.print(x=1, y=51,
			string=f"{self.player.ailments.toleranceLevel} Tolerance")

		console.print(x=1, y=52,
			string=f"{self.player.ailments.stimMod} Stim Modifier")

		render_names_at_mouse_location(console=console, engine=self, x=23, y=53, maxWidth=56)

		visibleEntitiesWithDistance = []
		visibleEntities = []
		for actor in self.game_map.actors:
			if actor != self.player:
				if self.game_map.visible[actor.x, actor.y]:
					visibleEntitiesWithDistance.append((actor, actor.distance(self.player.x, self.player.y)))

		visibleEntitiesWithDistance.sort(key=lambda distance: distance[1])
		for tuple in visibleEntitiesWithDistance:
			visibleEntities.append(tuple[0])

		render_enviroment_hud(console=console, actorsVisible=visibleEntities, engine=self, x=80, y=2, width=16, height=49)
