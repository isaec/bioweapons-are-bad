#import simpleaudio as sa
#import wave
#import pydub
from pygame import mixer as mixer


mixer.init(
	frequency=44100,
	size=-16, channels=2,
	buffer=512,
	allowedchanges=0)

mixer.set_num_channels(16)

class SoundEngine:
	def __init__(self) -> None:
		mixer.init()
		self.queue = {}

	def emitSound(self, soundName: str, loops: int = 0) -> None:
		soundDict[soundName].play(loops=loops)

	def queueSound(self, queueId: str) -> None:
		if queueId in self.queue:
			self.queue[queueId] += 1
		else:
			self.queue[queueId] = 0

	def pushQueue(self, queueId: str, soundName: str = None):
		if soundName == None: soundName = queueId
		if queueId in self.queue:
			self.emitSound(soundName, self.queue[queueId])
			self.queue.pop(queueId)
		






soundDict = {}


def waveLoader(location: str, name: str, volume=1):
	soundDict[name] = mixer.Sound(location)
	soundDict[name].set_volume(volume)
	return name


#easy sounds for items
zip_gun = waveLoader('sounds/Weapons/Single_Shot_Sounds/sfx_weapon_singleshot7.wav', "zip_gun")
zip_cannon = waveLoader('sounds/Weapons/Cannon/sfx_wpn_cannon2.wav', "zip_cannon")
hand_gun = waveLoader('sounds/Weapons/Single_Shot_Sounds/sfx_weapon_singleshot3.wav', "hand_gun")
stim_stick = waveLoader("sounds/General_Sounds/Weird_Sounds/sfx_sound_noise.wav", "stim_stick")
homing_grenade = waveLoader("sounds/Explosions/Short/sfx_exp_short_hard3.wav", "homing_grenade")
hand_grenade = waveLoader("sounds/Explosions/Short/sfx_exp_short_hard13.wav", "hand_grenade")
nitroglyn_grenade = waveLoader("sounds/Explosions/Medium_Length/sfx_exp_medium8.wav", "nitroglyn_grenad")
item_pickup = waveLoader("sounds/General_Sounds/Coins/sfx_coin_cluster3.wav", "item_pickup")

#easy sounds for actors
playerHurt = waveLoader("sounds/General_Sounds/Negative_Sounds/sfx_sounds_damage1.wav", "playerHurt", volume = .6)
playerDead = [waveLoader("sounds/General_Sounds/Weird_Sounds/sfx_sound_shutdown1.wav", "playerDead")]
infectedHurt = waveLoader("sounds/General_Sounds/Impacts/sfx_sounds_impact3.wav", "infectedHurt")
infectedDead = [] #8 sounds long
for i in range(6, 14):
	waveLoader(f"sounds/Death_Screams/Human/sfx_deathscream_human{i}.wav", f"infectedDead{i}")
	infectedDead.append(f"infectedDead{i}")

#other sounds
new_message = waveLoader("sounds/General_Sounds/Coins/sfx_coin_single5.wav", "new_message")
hostile_seen = waveLoader("sounds/General_Sounds/Neutral_Sounds/sfx_sound_neutral11.wav", "hostile_seen", volume=.4)
error_sound = waveLoader("sounds/General_Sounds/Simple_Bleeps/sfx_sounds_Blip9.wav", "error_sound", volume = .4)

reloaded_sound = waveLoader("sounds/General_Sounds/Positive Sounds/sfx_sounds_powerup4.wav", "reloaded_sound")
gun_empty = waveLoader("sounds/Weapons/Out of Ammo/sfx_wpn_reload.wav", "gun_empty")
