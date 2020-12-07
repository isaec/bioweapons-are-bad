from typing import Optional, Tuple, Type, List, Dict, TypeVar, TYPE_CHECKING, Union
import math
import numpy
from tcod import los

class AnimationEngine:
	def __init__(self, engine) -> None:
		self.activeAnimations = []
		self.engine = engine
		self.didFrame = True

	@property
	def hasActive(self):
		if len(self.activeAnimations) > 0:
			self.didFrame = True 
			return True
		if self.didFrame:
			self.didFrame = False
			return True
		return False

	def emitAnimation(self, AnimationObject):
		self.activeAnimations.append(AnimationObject)


	def animateFrame(self, console):
		for AnimationObject in self.activeAnimations:
			if AnimationObject.stepFrame(console, self.engine) == "done":
				self.activeAnimations.remove(AnimationObject)

	

class AnimationObject():
	def __init__():
		self.animationList = []
		self.frame = 0
		self.totalFrames = 0

	def stepFrame(self, console, engine):
		for dict in self.animationList[self.frame]:
			#console.tiles_rgb["bg"][x, y] = color.white
			try:
				if engine.game_map.visible[dict["cord"][0]][dict["cord"][1]]:
					if dict["bg"] != None: console.tiles_rgb["bg"][dict["cord"]] = dict["bg"]
					if dict["fg"] != None: console.tiles_rgb["fg"][dict["cord"]] = dict["fg"]
					if dict["ch"] != None: console.tiles_rgb["ch"][dict["cord"]] = ord(dict["ch"])
			except IndexError: pass
		self.frame += 1
		if self.frame == self.totalFrames:
			return "done"


class MuzzleFlash(AnimationObject):
	def __init__(self, cordStart: Tuple[int, int], cordEnd: Tuple[int, int]):
		self.cordStart = cordStart
		self.cordEnd = cordEnd
		self.frame = 0
		animationList = []
		lineBres = los.bresenham(cordStart, cordEnd)
		lineBresList = []
		for i in range(len(lineBres)-1):
			lineBresList.append((lineBres[i][0],lineBres[i][1]))
		lineBresList.pop(0)
		while len(lineBresList) < 3:
			lineBresList.append(cordEnd)

		animationList.append([{"cord":lineBresList[0],"bg":(255,255,255),"fg":None,"ch":" "}])
		animationList.append([{"cord":lineBresList[0],"bg":(255,255,255),"fg":None,"ch":" "},
			{"cord":lineBresList[1],"bg":(255,255,255),"fg":None,"ch":None}])
		animationList.append([{"cord":lineBresList[1],"bg":(255,255,255),"fg":None,"ch":" "}])
		self.animationList = animationList
		self.totalFrames = len(animationList)


class Explosion(AnimationObject):
	def __init__(self, cord: Tuple[int, int], radius: int, color: int, speedMod: int = 1):
		self.cord = cord
		self.radius = radius
		self.frame = 0
		animationList = []
		x, y = cord

		frame = []
		#calculates the squares to be animated on.


		for i in range(radius+1):
			iMin = max(1,i)
			frame = []
			#calculates the squares to be animated on.
			targetx, targety = x - i, y - i
			for targetx in range(x - i, x + i + 1):
				for targety in range(y - i, y + i + 1):
					if i-2 < math.sqrt((targetx - x) ** 2 + (targety - y) ** 2) <= i:
						frame.append({"cord":(targetx, targety),"bg":(color[0]/iMin,color[1]/iMin,color[2]/iMin),"fg":None,"ch":" "})
			for ii in range(speedMod):
				animationList.append(frame)

		animationListReversed = animationList.copy()
		animationListReversed.reverse()
		animationList = animationListReversed + animationList

		self.animationList = animationList
		self.totalFrames = len(animationList)

		

class Highlight(AnimationObject):
	def __init__(self,cord: Tuple[int, int], color: Tuple[int, int, int] = (255,255,255), duration: int = 9, pulseLength: int = 3):
		self.cord = cord
		self.color = color
		self.duration = duration
		self.pulseLength = pulseLength
		self.frame = 0
		animationList = []
		i, ii, iii = 0, 1, 0
		while i in range(duration):
			if ii <= pulseLength:
				animationList.append([{"cord":cord,"bg":color,"fg":None,"ch":None}])
				ii += 1
			else:
				animationList.append([{"cord":cord,"bg":None,"fg":None,"ch":None}])
				iii += 1
				if iii == pulseLength:
					ii, iii = 1, 0

			i += 1

		self.animationList = animationList
		self.totalFrames = len(animationList)


class Projectile(AnimationObject):
	def __init__(self, cordStart: Tuple[int, int], cordEnd: Tuple[int, int], char: str = "*", color: Tuple[int, int, int] = (0, 0, 0), speedMod: int = 1):
		self.cordStart = cordStart
		self.cordEnd = cordEnd
		self.char = char
		self.color = color
		self.frame = 0
		animationList = []
		lineBres = los.bresenham(cordStart, cordEnd)
		lineBresList = []
		for i in range(len(lineBres)-1):
			lineBresList.append((lineBres[i][0],lineBres[i][1]))
		lineBresList[-1:1]
		for i in range(len(lineBresList)-1):
			for ii in range(speedMod):
				animationList.append([{"cord":lineBresList[i],"bg":None,"fg":color,"ch":char}])
		self.animationList = animationList
		self.totalFrames = len(animationList)


class FrameLight(AnimationObject):
	def __init__(self, mapSizeTuple: Tuple[int, int] = (80, 45), color: Tuple[int, int, int] = (150, 150, 150),
		duration: int = 15, pulseLength: int = 5, sides = {"t":True, "b":True, "r":True, "l":True}):

		self.color = color
		self.duration = duration
		self.pulseLength = pulseLength
		self.mapSizeTuple = mapSizeTuple
		self.frame = 0
		animationList = []
		i, ii, iii = 0, 1, 0

		activeFrame = []
		inactiveFrame = [{"cord":(0,0),"bg":None,"fg":None,"ch":None}]
		for x in range(mapSizeTuple[0]):
			if sides["t"]: activeFrame.append({"cord":(x,0),"bg":color,"fg":None,"ch":" "})
			if sides["b"]: activeFrame.append({"cord":(x,mapSizeTuple[1]-1),"bg":color,"fg":None,"ch":" "})
		for y in range(mapSizeTuple[1]):
			if sides["l"]: activeFrame.append({"cord":(0,y),"bg":color,"fg":None,"ch":None})
			if sides["r"]: activeFrame.append({"cord":(mapSizeTuple[0]-1,y),"bg":color,"fg":None,"ch":" "})


		while i in range(duration):
			if ii <= pulseLength:
				animationList.append(activeFrame)
				ii += 1
			else:
				animationList.append(inactiveFrame)
				iii += 1
				if iii == pulseLength:
					ii, iii = 1, 0

			i += 1

		self.animationList = animationList
		self.totalFrames = len(animationList)