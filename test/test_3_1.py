from util import util, song
import pygame.midi
import time

pygame.midi.init()
player = pygame.midi.Output(1)  # 16
player.set_instrument(0, channel=0)
player.set_instrument(1, channel=1)
music = '天空之城'
events = song.songs[music]['events']
span = events[-1][0]
last = 0
print(events[-1][0])
ch_0, ch_1, ch_2, ch_e = [], [], [], []
for event in events:
    if event[0] > last:
        time.sleep((event[0] - last) / 800)
        last = event[0]
    if event[3] == 0:
        ch_0.append(event)
    elif event[3] == 1:
        ch_1.append(event)
    elif event[3] == 2:
        ch_2.append(event)
    else:
        ch_e.append(event)
    player.note_on(event[1], event[2], channel=event[3])
data = open(".\\data.txt", 'w+')
print('ch_0')
print(ch_0)
print('ch_1')
print(ch_1)
print('ch_2')
print(ch_2)
print('ch_e')
print(ch_e)
data.close()

