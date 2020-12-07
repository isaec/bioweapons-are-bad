from pygame import mixer as mixer

mixer.init(
	frequency=44100,
	size=-16, channels=2,
	buffer=512,
	allowedchanges=0)

niceNoise = mixer.Sound("sounds/General_Sounds/Fanfares/sfx_sounds_fanfare2.wav")

#mixer.set_num_channels(16)

primaryChannel = mixer.Channel(0)

print(mixer.get_num_channels())

niceNoise.play(loops=100)


input()