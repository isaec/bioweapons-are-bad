from typing import Iterable, List, Reversible, Tuple
import textwrap

import tcod

import color

import sound_engine

import animation_engine

class Message:
	def __init__(self, text: str, fg: Tuple[int, int, int]):
		self.plain_text = text
		self.fg = fg
		self.count = 1

	@property
	def full_text(self) -> str:
		#the full text of this message, including a count if necisary
		if self.count > 1:
			return f"{self.plain_text} (x{self.count})"
		return self.plain_text
	
class MessageLog:
	def __init__(self, engine) -> None:
		self.messages: List[Message] = []
		self.parent = engine

	def add_message(
		self, text: str, fg: Tuple[int, int, int] = color.white, *, stack: bool = True, makePing: bool = True,
		) -> None:
		"""Add a message to this log.
		'text' is the message text, fg is the color
		if 'stack' is true then the message can stack with a previous message
		of the same text.
		"""
		if stack and self.messages and text == self.messages[-1].plain_text:
			self.messages[-1].count += 1
		else:
			self.messages.append(Message(text, fg))

		#self.parent.animation_engine.emitAnimation(animation_engine.FrameLight(color=fg, sides={"t":False,"b":False,"l":True,"r":True}))

		#makes ping to alert player to new message
		if makePing:
			self.parent.sound_engine.emitSound(sound_engine.new_message)

	def render(
		self, console: tcod.Console, x: int, y: int, width: int, height: int,
		) -> None:
		"""Render this log over the given area. 
		'x', 'y', 'width', 'height' is the rect region to render onto
		the console.
		"""
		self.render_messages(console, x, y, width, height, self.messages)

	#returns the message, wrapped
	@staticmethod
	def wrap(string: str, width: int) -> Iterable[str]:
		for line in string.splitlines():
			yield from textwrap.wrap(
				line, width, expand_tabs=True
				)

	@classmethod
	def render_messages(
		cls,
		console: tcod.Console,
		x: int,
		y: int,
		width: int,
		height: int,
		messages: Reversible[Message],
		) -> None:
		"""Render the messages provided.
		the 'messages' are rendered starting at the last message and working backwords
		"""
		y_offset = height - 1

		for message in reversed(messages):
			for line in reversed(list(cls.wrap(message.full_text, width))):
				console.print(x=x, y=y + y_offset, string=line, fg=message.fg)
				y_offset -= 1
				if y_offset < 0:
					return #out of space to print lines
