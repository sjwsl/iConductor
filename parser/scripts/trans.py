import time

events = dict()

last = 0

chan = -1

ins = ['1_钢琴', '1_无品贝司', '2_钢琴', '3_钢琴', '1_弦',  '2_弦', '1_方波', '1_钢鼓']

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

    if vol == -1:
        continue

    try:
        events[ins[chan]].append((tick, note, vol, chan))
    except KeyError:
        events[ins[chan]] = []

print(events)

# last = 0
# for event in events:
#     print(event)
#     if event[0] > last:
#         time.sleep((event[0] - last) / 800)
#         last = event[0]
#     player.note_on(event[1], event[2], channel=event[3])
