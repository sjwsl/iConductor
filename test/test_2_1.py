from util import util, song
import pygame.midi
import time

# music = song.song['两只老虎']
# pygame.midi.init()
# player = pygame.midi.Output(1)
# player.set_instrument(40)
# for i in range(len(music[0])):
#     val = 63
#     player.note_on(note=music[0][i], velocity=val, channel=0)
#     time.sleep(music[1][i])
#     player.note_off(note=music[0][i], velocity=val, channel=0)
# # player.note_on(note=60, velocity=63, channel=0)
# # time.sleep(10)
# # player.note_off(note=60, velocity=63, channel=0)
# del player

#
# def play_music(music, ins, volumes, paras):
#     global instr_2
#     i = instr_2[ins.split('_')[-1]] - 1
#     pygame.midi.init()
#     # for _ in range(4):
#     #     print(_, pygame.midi.get_device_info(_))
#
#     player = pygame.midi.Output(16)
#     player.set_instrument(i)
#     try:
#         music = song.song[music][ins]
#     except KeyError:
#         music = song.song[music]['else']
#     for i in range(len(music[0])):
#         k = paras[0]
#         val = min(int(volumes[ins] * k), 127)
#         note = music[0][i]
#         if note > 0:
#             secs = music[1][i+1] - music[1][i]  # paras[1]
#             player.note_on(note=note, velocity=val, channel=0)
#             time.sleep(secs if secs > 0 else 0)
#             player.note_off(note=note, velocity=val, channel=0)
#         else:
#             time.sleep(music[1][i + 1] - music[1][i])
#     del player
#     pygame.midi.quit()
#

