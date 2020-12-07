from __future__ import annotations

from typing import List, Tuple, TYPE_CHECKING

import numpy as np # type: ignore
import tcod
import random

from actions import Action, MeleeAction, MovementAction, WaitAction
import tile_types
import sound_engine
import animation_engine

if TYPE_CHECKING:
	from entity import Actor


class BaseAI(Action):

	def perform(self) -> None:
		raise NotImplementedError()

	def shouldPing(self) -> None:
		raise NotImplementedError()

	def get_path_to(self, dest_x: int, dest_y: int, blockCost: int = 0, corpseCost: int = 0, cheat: bool = True) -> List[Tuple[int, int]]:
		"""Compute and retrun a path to the target position.

		if there is no valid path then retrun an empty list.
		"""
		#makes a copy of the array of walkable places, only uses visible if cheating is false
		if cheat: cost = np.array(self.entity.gamemap.tiles["walkable"], dtype=np.int8)
		else: cost = np.where(self.entity.gamemap.explored, self.entity.gamemap.tiles["walkable"], 1)


			


		for entity in self.entity.gamemap.entities:
			#check that an entity blocks movement and the cost isnt zero(blocking)
			if entity.blocks_movement and cost[entity.x, entity.y]:
				""" Add to the cost of a blocked position.
				Low number will mean they will croud together to take shortest route
				High number will encorage longer paths to surround the player
				"""
				cost[entity.x, entity.y] += blockCost
			try:
				if entity.is_alive == False and cost[entity.x, entity.y] and entity.could_live:
					"""Adds to cost of position with a corpse.
					Low corpse cost will have ai walk over corspes.
					High cost will have ai avoid corpses, maybe avoiding traps."""
					cost[entity.x, entity.y] += corpseCost
			#if entity doesnt have this method
			except AttributeError:
				print(entity.name+" lacks a method - no biggie (ai.py)")

		#create a graph from the cost array and pass that graph to a new pathfinder
		graph = tcod.path.SimpleGraph(cost=cost, cardinal=2, diagonal=3)
		pathfinder = tcod.path.Pathfinder(graph)


		pathfinder.add_root((self.entity.x, self.entity.y)) #start position

		#computes path to destination and removes the starting point
		path: List[List[int]] = pathfinder.path_to((dest_x, dest_y))[1:].tolist()

		#convirt from list in a list full of ints to list with tuples
		return [(index[0], index[1]) for index in path]



class HostileEnemy(BaseAI):
	def __init__(self, entity: Actor, blockCost: int = 10, corpseCost: int = 0):
		super().__init__(entity)
		self.path: List[Tuple[int, int]] = []
		self.justSeen = False
		self.seenPlayer = False
		self.blockCost, self.corpseCost = blockCost, corpseCost
		self.lastLocation = self.entity.locTuple


	def perform(self) -> None:
		target = self.engine.player
		dx = target.x - self.entity.x
		dy = target.y - self.entity.y
		distance = max(abs(dx), abs(dy)) #Chebyshev distance


		#if i am visible
		if self.engine.game_map.visible[self.entity.x, self.entity.y]:
			self.seenPlayer = True#I have seen player

			#if in range to attack, melee action
			if distance <= 1:
				return MeleeAction(self.entity, dx, dy).perform()

			#otherwise path to player
			self.path = self.get_path_to(
				target.x, target.y, blockCost=self.blockCost, corpseCost=self.corpseCost)

		#If i am at the last place I saw the player
		if self.seenPlayer and not self.path:
			#attempts to keep going in same direction
			changeX = self.entity.x - self.lastLocation[0]
			changeY = self.entity.y - self.lastLocation[1]

			#print(f"fancy search - vector{(changeX, changeY)} currentLoc{self.entity.locTuple} - lastLoc{self.lastLocation}")
			if (changeX, changeY) == (0, 0):
				self.seenPlayer = False
				return

			searchX, searchY = self.entity.locTuple
			while self.engine.game_map.tiles[searchX, searchY]["walkable"]:
				searchX += changeX
				searchY += changeY
			searchX -= changeX
			searchY -= changeY

			if (searchX, searchY) != self.entity.locTuple:
				self.path = self.get_path_to(
					searchX, searchY, blockCost=self.blockCost, corpseCost=self.corpseCost)
				#print(f"resolved - {(searchX, searchY)}")
			self.seenPlayer = False
				


		#if i have a path, follow it
		if self.path:
			self.lastLocation = self.entity.locTuple
			dest_x, dest_y = self.path.pop(0)
			return MovementAction(
				self.entity, dest_x - self.entity.x, dest_y - self.entity.y
				).perform()



		#patrolling could be toggled here
		if True:
			#random patrols, but no big distances - iterations prevents hang
			iterations = 0
			while not self.path:
				roomTarget = self.engine.game_map.rooms[
				random.randint(0,len(self.engine.game_map.rooms)-1)]
				(roomTargetX, roomTargetY) = roomTarget.center
				roomDX = roomTargetX - self.entity.x
				roomDY = roomTargetY - self.entity.y
				roomDistance = max(abs(roomDX), abs(roomDY))
				#if target is not spawn room, and is within 10
				if roomDistance < 10 and roomTarget != self.engine.game_map.rooms[0]:
					self.path = self.get_path_to(
						roomTargetX, roomTargetY, blockCost=self.blockCost, corpseCost=self.corpseCost)
				else:
					iterations += 1
					if iterations > 100:
						break

		
		#if there is noting better to do, wait
		return WaitAction(self.entity).perform()

	def shouldPing(self) -> bool:
		if self.engine.game_map.visible[self.entity.x, self.entity.y]:
			if not self.justSeen:
				self.justSeen = True
				return True

			else:
				return False

		self.justSeen = False
		return False
