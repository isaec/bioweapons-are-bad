from __future__ import annotations

from typing import TYPE_CHECKING

import color

import render_order

if TYPE_CHECKING:
	from tcod import Console
	from engine import engine
	from game_map import GameMap

def get_names_at_location(x: int, y: int, game_map: GameMap) -> str:
	if not game_map.in_bounds(x, y) or not game_map.visible[x, y]:
		return ""

	names = ", ".join(
		entity.name for entity in game_map.entities if entity.x == x and entity.y == y
		)

	return names#.capitalize()


def render_bar(
	console: Console, current_value: int, maximum_value: int, total_width: int, x: int = 0, y: int = 45, string: str = "HP: ", flipColor: bool = False
	) -> None:
	try: bar_width = int(float(current_value) / maximum_value * total_width)
	except ZeroDivisionError: bar_width = 0

	if flipColor:
		console.draw_rect(x, y, width=total_width, height=1, ch=1, bg=color.bar_filled)
		if bar_width > 0:
			console.draw_rect(
				x, y, width=bar_width, height=1, ch=1, bg=color.bar_empty
				)
	else:
		console.draw_rect(x, y, width=total_width, height=1, ch=1, bg=color.bar_empty)

		if bar_width > 0:
			console.draw_rect(
				x, y, width=bar_width, height=1, ch=1, bg=color.bar_filled
				)

	console.print(
		x+1, y, string=string+f"{current_value}/{maximum_value}", fg=color.bar_text
		)

def render_names_at_mouse_location(
	console: Console, engine: Engine, x: int, y: int, maxWidth: int 
	) -> None:
	mouse_x, mouse_y = engine.mouse_location

	names_at_mouse_location = get_names_at_location(
		x=mouse_x, y=mouse_y, game_map=engine.game_map
		)

	names_at_mouse_location = names_at_mouse_location[:maxWidth]

	console.print(x=x, y=y, string=names_at_mouse_location, fg=(0,0,0), bg=(200,200,200))

def render_enviroment_hud(
	console: Console, actorsVisible, engine: Engine, x: int, y: int, width: int, height: int):
		yy = y
		for actor in actorsVisible:
			if yy+4 in range(y, y+height):
				mouse_x, mouse_y = engine.mouse_location
				if engine.game_map.get_actor_at_location(mouse_x, mouse_y) == actor:
					console.draw_frame(x, yy, width=width, height=4, title=actor.name, fg=(200,255,200), bg=(0,0,0))
				else:
					console.draw_frame(x, yy, width=width, height=4, title=actor.name, fg=(200,200,200), bg=(0,0,0))
				render_bar(
					console=console, current_value=actor.fighter.hp, maximum_value=actor.fighter.max_hp,total_width=width-2,x=x+1,y=yy+1)
				console.print(x+1, yy+2, f"{actor.fighter.power} pwr {actor.fighter.defense} dfnse", fg=(200,200,200))

				yy+=4