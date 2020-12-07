from exceptions import Impossible
import color
from message_log import MessageLog

class Ailments():
	def __init__(self, tolerance: int = 0, toleranceCountdown = 0):
		self.tolerance = tolerance
		if tolerance == 0:
			self.toleranceCountdown = toleranceCountdown
		else:
			self.toleranceCountdown = self.toleranceCountdownMax

	@property
	def toleranceLevel(self):
		toleranceLevelLabels = ["No","Low","Medium","High"]
		if 0 <= self.tolerance <= 3: return toleranceLevelLabels[self.tolerance]
		else: raise Impossible("Tolerance out of Range")

	@property
	def stimMod(self):
		stimModLevels = [0,-1,-2,-3]
		if 0 <= self.tolerance <= 3: return stimModLevels[self.tolerance]
		else: raise Impossible("Tolerance out of Range")

	@property
	def toleranceCountdownMax(self):
		toleranceMaxLabels = [0,20,60,120]
		if 0 <= self.tolerance <= 3: return toleranceMaxLabels[self.tolerance]
		else: raise Impossible("Tolerance out of Range")
	


	def gainTolerance(self):
		if 0 <= self.tolerance < 3:
			self.tolerance += 1
			self.toleranceCountdown = self.toleranceCountdownMax
			if self.parent.name == "Player": self.parent.gamemap.engine.message_log.add_message(text=f"Stimulant Stick tolerance increased to {self.toleranceLevel}", fg=color.tolerance_increased, makePing=False)
		elif self.tolerance == 3:
			self.toleranceCountdown = self.toleranceCountdownMax
			if self.parent.name == "Player": self.parent.gamemap.engine.message_log.add_message(text=f"Stimulant Stick tolerance maxed at {self.toleranceLevel}", fg=color.tolerance_increased)

	def ailmentTick(self):
		if self.toleranceCountdown > 0:
			self.toleranceCountdown -= 1
		elif self.toleranceCountdown == 0 and self.tolerance != 0:
			self.tolerance = 0
			if self.parent.name == "Player": self.parent.gamemap.engine.message_log.add_message(text=f"Stimulant Stick tolerance has run its course", fg=color.tolerance_reduced)
	
	