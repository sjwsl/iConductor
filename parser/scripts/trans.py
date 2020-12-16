import pygame.midi
import time

events = list()

last = 0

chan = -1

while True:
    try:
        li = input().strip().split()
    except EOFError:
        break

    if len(li) == 0:
        last = 0
        chan = chan + 1
        continue

    tick, note, vol = map(int, li)

    tick = tick + last
    last = tick
    events.append((tick, note, vol, chan))

events.sort()

print(events)

# last = 0
# for event in events:
#     print(event)
#     if event[0] > last:
#         time.sleep((event[0] - last) / 800)
#         last = event[0]
#     player.note_on(event[1], event[2], channel=event[3])