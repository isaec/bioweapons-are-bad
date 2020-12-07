from __future__ import annotations

from typing import Callable, Tuple, Optional, TYPE_CHECKING
import tcod
import math

import actions
from actions import (
	Action,
	BumpAction,
	PickupAction,
	WaitAction,
	QuickAccess
	)

import color
import exceptions
import sound_engine
import animation_engine



if TYPE_CHECKING:
	from engine import Engine
	from entity import Item
	from components import consumable


MOVE_KEYS = {
	# Arrow keys.
	tcod.event.K_UP: (0, -1),
	tcod.event.K_DOWN: (0, 1),
	tcod.event.K_LEFT: (-1, 0),
	tcod.event.K_RIGHT: (1, 0),
	tcod.event.K_HOME: (-1, -1),
	tcod.event.K_END: (-1, 1),
	tcod.event.K_PAGEUP: (1, -1),
	tcod.event.K_PAGEDOWN: (1, 1),
	# Numpad keys.
	tcod.event.K_KP_1: (-1, 1),
	tcod.event.K_KP_2: (0, 1),
	tcod.event.K_KP_3: (1, 1),
	tcod.event.K_KP_4: (-1, 0),
	tcod.event.K_KP_6: (1, 0),
	tcod.event.K_KP_7: (-1, -1),
	tcod.event.K_KP_8: (0, -1),
	tcod.event.K_KP_9: (1, -1),
	# Vi keys.
	tcod.event.K_h: (-1, 0),
	tcod.event.K_j: (0, 1),
	tcod.event.K_k: (0, -1),
	tcod.event.K_l: (1, 0),
	tcod.event.K_y: (-1, -1),
	tcod.event.K_u: (1, -1),
	tcod.event.K_b: (-1, 1),
	tcod.event.K_n: (1, 1),
}


WAIT_KEYS = {
	tcod.event.K_PERIOD,
	tcod.event.K_KP_5,
	tcod.event.K_CLEAR,
}

CONFIRM_KEYS = {
	tcod.event.K_RETURN,
	tcod.event.K_KP_ENTER,
}


class EventHandler(tcod.event.EventDispatch[Action]):
	def __init__(self, engine: Engine):
		self. engine = engine
		self.unlock = False

	def handle_events(self, event: tcod.event.Event) -> None:
		self.handle_action(self.dispatch(event))

	def handle_action(self, action: Optional[Action]) -> bool:
		#handles the actions returned from event methods
		#returns true if they advance a turn
		if action is None:
			return False

		try:
			action.perform()
		except exceptions.Impossible as exc:
			self.engine.message_log.add_message(exc.args[0], color.impossible, makePing=False)
			self.engine.sound_engine.emitSound(sound_engine.error_sound)
			return False

		if action.freeAction:
			return False

		self.engine.handle_enemy_turns()

		self.engine.update_fov()
		return True

	def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
		if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
			self.engine.mouse_location = event.tile.x, event.tile.y

	def ev_quit(self, event: tcod.event.Quit) -> Optional[Action]:
		raise SystemExit()

	def on_render(self, console: tcod.Console) -> None:
		self.engine.render(console)

"""Handles the user events that need special input"""
class AskUserEventHandler(EventHandler):
	#returns to main event handler if valid action
	def handle_action(self, action: Optional[Action]) -> bool:
		if super().handle_action(action):
			self.engine.event_handler = MainGameEventHandler(self.engine)
			return True
		return False

	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
		"""By default any key will exit this"""
		if event.sym in { #ignore the modifier keys
		tcod.event.K_LSHIFT,
		tcod.event.K_RSHIFT,
		tcod.event.K_LCTRL,
		tcod.event.K_RCTRL,
		tcod.event.K_LALT,
		tcod.event.K_RALT,
		}:
			return None
		return self.on_exit()

	def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
		return self.on_exit() #by default a mouse click will exit

	def on_exit(self) -> Optional[Action]:
		"""Called when user is trying to exit or cancel action-
		defaults to returning to main event handler
		"""
		self.engine.event_handler = MainGameEventHandler(self.engine)
		return None


class InventoryEventHandler(AskUserEventHandler):
	"""This handler lets the user select an item-
	what happens next comes down to the subclass"""
	TITLE = "<missing title>"
	FOREGROUND = (255, 255, 255)

	def on_render(self, console: tcod.Console) -> None:
		"""Render and inventory item menu - displaying such, and letter to select them
		Moves to different position based on where the player is located so the player can always
		see where they are"""
		super().on_render(console)
		number_of_items_in_inventory = len(self.engine.player.inventory.items)

		height = number_of_items_in_inventory+2

		if height <= 3: height = 3

		if self.engine.player.x <= 30: x=40
		else: x = 0

		y = 0

		width = len(self.TITLE) + 4

		console.draw_frame(
			x=x,
			y=y,
			width=width,
			height=height,
			title=self.TITLE,
			clear=True,
			fg=self.FOREGROUND,
			bg=(0, 0, 0))

		self.x, self.y, self.width, self.height, self.console = x, y, width, height, console

		if number_of_items_in_inventory > 0:
			for i, item in enumerate(self.engine.player.inventory.items):
				item_key = chr(ord("a")+i)
				console.print(x + 1, y + i + 1, f"({item_key})")
				console.print(x + 1 + len(f"({item_key})"),
					y + i + 1, f">{item.char}<", fg=item.color)
				console.print(x + 1 + len(f"({item_key})>{item.char}<"), y + i + 1, item.name)
		else:
			console.print(x + 1, y + 1, "Empty")

	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
		player = self.engine.player
		key = event.sym
		index = key - tcod.event.K_a

		if 0 <= index <= 26:
			try:
				selected_item = player.inventory.items[index]
			except IndexError:
				self.engine.message_log.add_message("Invalid entry.", color.invalid)
				return None
			return self.on_item_selected(selected_item)
		return super().ev_keydown(event)


	def on_item_selected(self, item: Item) -> Optional[Action]:
		raise NotImplementedError()

class InventoryActivateHandler(InventoryEventHandler):
	#deals with useing an inventory item
	TITLE = "Select an item to use"

	def on_item_selected(self, item: Item) -> Optional[Action]:
		#returns action for selected item
		return item.consumable.get_action(self.engine.player)



class InventoryDropHandler(InventoryEventHandler):
	#handles item droppage

	TITLE = "Select an item to drop"

	def on_item_selected(self, item: Item) -> Optional[Action]:
		#drop this item
		return actions.DropItem(self.engine.player, item)

class InventoryLoadHandler(InventoryEventHandler):
	def __init__(self, engine: Engine, targetItem: Item):
		super().__init__(engine)
		self.targetItem = targetItem
	TITLE = "Select an item to load"
	FOREGROUND = (255, 240, 240)

	def on_item_selected(self, item: Item) -> Optional[Action]:
		if item.consumable.isAmmo:
			return actions.LoadItem(self.engine.player, item, targetItem=self.targetItem)
		else:
			self.engine.message_log.add_message(f"You cannot load {item.name} into {self.targetItem.parent.name}.", color.invalid)

class QuickAccessHandler(InventoryEventHandler):
	TITLE = "Select an item to bind to F key"
	FOREGROUND = (240, 255, 240)

	def on_item_selected(self, item: Item) -> None:
		self.engine.player.inventory.quickAccess = item
		self.engine.event_handler = MainGameEventHandler(self.engine)
		self.engine.message_log.add_message(f"{item.name} bound to F key.")

			




class SelectIndexHandler(AskUserEventHandler):
	"""handles asking user for index (location) on map"""

	def __init__(self, engine: Engine):
		"""sets cursor to player when handler is made"""
		super().__init__(engine)
		player = self.engine.player
		engine.mouse_location = player.x, player.y
		self.color = 255
		self.flipColor = True
		self.unlock = True

	def on_render(self, console: tcod.Console) -> None:
		#highlight cursor tile
		super().on_render(console)
		x, y = self.engine.mouse_location
		clampColor = max(min(self.color, 255), 0)
		console.tiles_rgb["bg"][x, y] = (clampColor,clampColor,clampColor)
		console.tiles_rgb["fg"][x, y] = color.black
		if self.flipColor: self.color -= 1
		else: self.color += 1
		if self.color >= 255: self.flipColor = True
		if self.color <= 230: self.flipColor = False

	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Actions]:
		#check for key movement or confermation keys
		key = event.sym
		if key in MOVE_KEYS:
			modifier = 1 #holding modifier speeds up movement
			if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
				modifier *= 5
			if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
				modifier *= 10
			if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
				modifier *= 20

			x, y = self.engine.mouse_location
			dx, dy = MOVE_KEYS[key]
			x += dx * modifier
			y += dy * modifier
			# cursor indax clamped to map size

			x = max(0, min(x, self.engine.game_map.width - 1))
			y = max(0, min(y, self.engine.game_map.height - 1))
			self.engine.mouse_location = x, y
			return None

		elif key in CONFIRM_KEYS:
			return self.on_index_selected(*self.engine.mouse_location)
		return super().ev_keydown(event)

	def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
		if self.engine.game_map.in_bounds(*event.tile):
			if event.button == 1:
				return self.on_index_selected(*event.tile)
		return super().ev_mousebuttondown(event)

	def on_index_selected(self, x: int, y: int) -> Optional[Action]:
		raise NotImplementedError()

class LookHandler(SelectIndexHandler):
	"""lets player look around via keyboard"""
	def on_index_selected(self, x: int, y: int) -> None:
		"""return to main handler"""
		self.engine.event_handler = MainGameEventHandler(self.engine)

class SingleRangedAttackHandler(SelectIndexHandler):
	"""Handles attacking one enemy- only the selected will be affected"""
	def __init__(
		self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
		):

		super().__init__(engine)

		self.callback = callback

	def on_index_selected(self, x:int, y:int) -> Optional[Action]:
		return self.callback((x, y))

class AreaRangedAttackHandler(SelectIndexHandler):
	"""Handles targeting area with given radius - anthing in the area is affected."""
	def __init__(
		self,
		engine: Engine,
		radius: int,
		callback: Callable[[Tuple[int, int]], Optional[Action]],
		):
		super().__init__(engine)

		self.radius = radius
		self.callback = callback
		self.color = 230
		self.flipColor = True
		self.unlock = True

	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console)

		x, y = self.engine.mouse_location
		clampColor = max(min(self.color, 255), 0)

		#draw the effected area with pulsing red so player can see what is affected
		radius = self.radius
		targetx, targety = x - radius, y - radius
		for targetx in range(x - radius, x + radius + 1):
			for targety in range(y - radius, y + radius + 1):
				if math.sqrt((targetx - x) ** 2 + (targety - y) ** 2) <= radius:
					if self.engine.game_map.in_bounds(targetx, targety):
						console.tiles_rgb["bg"][targetx, targety] = (clampColor, 0, 0)
						console.tiles_rgb["fg"][targetx, targety] = color.black
		console.tiles_rgb["bg"][x, y] = color.white
		console.tiles_rgb["fg"][x, y] = color.black
		if self.flipColor: self.color -= 1
		else: self.color += 1
		if self.color >= 255: self.flipColor = True
		if self.color <= 230: self.flipColor = False


	def on_index_selected(self, x: int, y: int) -> Optional[Action]:
		return self.callback((x, y))			


class MainGameEventHandler(EventHandler):
	def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[Action]:
		action: Optional[Action] = None


		key = event.sym

		player = self.engine.player


		if key in MOVE_KEYS:
			dx, dy = MOVE_KEYS[key]
			action = BumpAction(player, dx, dy)
		elif key in WAIT_KEYS:
			action = WaitAction(player)
		elif key == tcod.event.K_ESCAPE:
			raise SystemExit()
		elif key == tcod.event.K_v:
			self.engine.event_handler = HistoryViewer(self.engine)
		elif key == tcod.event.K_g:
			action = PickupAction(player)

		elif key == tcod.event.K_i:
			self.engine.event_handler = InventoryActivateHandler(self.engine)
		elif key == tcod.event.K_d:
			self.engine.event_handler = InventoryDropHandler(self.engine)
		elif key == tcod.event.K_SLASH:
			self.engine.event_handler = LookHandler(self.engine)
		elif key == tcod.event.K_f:
			action = QuickAccess(player.inventory.quickAccess, self.engine)
		elif key == tcod.event.K_r:
			self.engine.event_handler = QuickAccessHandler(self.engine)


		#no vaild key is pressed
		return action

	def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[Action]:
		action: Optional[Action] = None


		if not self.engine.game_map.in_bounds(*event.tile):
			return super().ev_mousebuttondown(event)
		if not (event.button == 1 or event.button == 3):
			return super().ev_mousebuttondown(event)


		player = self.engine.player

		mouseOnPlayerBool = bool(event.tile[0] == player.x and event.tile[1] == player.y)

		path = False
		#left click
		if event.button == 1:
			if mouseOnPlayerBool:
				action = PickupAction(player)
			else:
				path = player.ai.get_path_to(
							event.tile[0], event.tile[1], cheat = False)
				for tuple in path:
					self.engine.animation_engine.emitAnimation(animation_engine.Highlight(cord=tuple, color=(255,200,200)))
				
		#right click
		if event.button == 3:
			if mouseOnPlayerBool:
				self.engine.event_handler = InventoryActivateHandler(self.engine)

		if path:
			#if len(path) < 1: return super().ev_mousebuttondown(event)
			action = BumpAction(player, path[0][0]-player.x, path[0][1]-player.y)
		elif path != False: self.engine.message_log.add_message("You cannot find a way to get there.", color.impossible)

		return action


class GameOverEventHandler(EventHandler):
	def ev_keydown(self, event: tcod.event.KeyDown) -> None:
		if event.sym == tcod.event.K_ESCAPE:
			raise SystemExit()
		elif event.sym == tcod.event.K_v:
			self.engine.event_handler = HistoryViewer(self.engine)



CURSOR_Y_KEYS = {
	tcod.event.K_UP: -1,
	tcod.event.K_DOWN: 1,
	tcod.event.K_PAGEUP: -10,
	tcod.event.K_PAGEDOWN: 10,
}

class HistoryViewer(EventHandler):
	#print the history on a larger window

	def __init__(self, engine: Engine):
		super().__init__(engine)
		self.log_length = len(engine.message_log.messages)
		self.cursor = self.log_length - 1

	def on_render(self, console: tcod.Console) -> None:
		super().on_render(console) #draw main state as background

		log_console = tcod.Console(console.width - 6, console.height - 6)

		#draw the frame with custom banner title
		log_console.draw_frame(0, 0, log_console.width, log_console.height)
		log_console.print_box(
			0, 0, log_console.width, 1, "┤Message History├", alignment=tcod.CENTER
			)

		#render the message log with the cursor
		self.engine.message_log.render_messages(
			log_console,
			1,
			1,
			log_console.width - 2,
			log_console.height - 2,
			self.engine.message_log.messages[: self.cursor + 1],
			)
		log_console.blit(console, 3, 3)

	def ev_keydown(self, event: tcod.event.KeyDown) -> None:
		if event.sym in CURSOR_Y_KEYS:
			adjust = CURSOR_Y_KEYS[event.sym]
			if adjust < 0 and self.cursor == 0:
				#only move from the top to the bottem when your at the edge
				self.cursor = self.log_length - 1
			elif adjust > 0 and self.cursor == self.log_length - 1:
				self.cursor = 0

			else:
				#move but stay in bounds of history
				self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))
		elif event.sym == tcod.event.K_HOME:
			self.cursor = 0 #go to top
		elif event.sym == tcod.event.K_END:
			self.cursor = self.log_length - 1#last message
		else: #any other key
			if self.engine.player.ai == None:
				self.engine.event_handler = GameOverEventHandler(self.engine)
			else:
				self.engine.event_handler = MainGameEventHandler(self.engine)