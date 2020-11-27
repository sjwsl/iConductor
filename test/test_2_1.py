from util import util, song
import pygame.midi
import time

music = song.song['两只老虎']
pygame.midi.init()
player = pygame.midi.Output(1)
player.set_instrument(40)
for i in range(len(music[0])):
    val = 63
    player.note_on(note=music[0][i], velocity=val, channel=0)
    time.sleep(music[1][i])
    player.note_off(note=music[0][i], velocity=val, channel=0)
# player.note_on(note=60, velocity=63, channel=0)
# time.sleep(10)
# player.note_off(note=60, velocity=63, channel=0)
del player
