import time

import wx
import numpy as np
import pygame.midi
from util import util, song, tree

import os
import serial
import threading


class initFrame(wx.Frame):

    def __init__(self, parent=None, fid=-1):

        wx.Frame.__init__(self, parent, fid, '人-机交互音乐指挥系统 v0.3', size=(770, 630),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.Center()
        self.SetBackgroundColour((240, 240, 240))
        pageBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(pageBoxSizer)
        self.Bind(wx.EVT_CLOSE, self.close)
        img_1 = wx.Image('title_1.png', wx.BITMAP_TYPE_PNG)
        img_1 = img_1.ConvertToBitmap()
        wx.StaticBitmap(self, -1, bitmap=img_1, pos=(210, 0))

        self.paras = list()
        self.paras.append(1.0)
        self.paras.append(0.0)
        self.volume = dict()
        self.panel = wx.Panel(self, pos=(366, 300), size=(330, 220))
        self.graph = util.MPL_Panel(self.panel, pos=(0, 0), size=(330, 220))

        music_lst_1 = [' 所有', ]
        music_lst_2 = [' 天空之城', ]
        wx.StaticText(self, -1, label='设备 :', pos=(60, 120), size=(40, 30))
        wx.StaticText(self, -1, label='作者 :', pos=(60, 160), size=(60, 30))
        wx.StaticText(self, -1, label='曲目 :', pos=(60, 200), size=(60, 30))
        self.cbb_1 = wx.ComboBox(self, -1, pos=(130, 157), size=(190, 30), value=music_lst_1[0],
                                 choices=music_lst_1, style=wx.CB_SORT | wx.CB_READONLY)
        self.cbb_2 = wx.ComboBox(self, -1, pos=(130, 197), size=(190, 30), value=music_lst_2[0],
                                 choices=music_lst_2, style=wx.CB_READONLY)  # wx.CB_SORT |
        self.cbb_5 = None
        self.frame_init()

        set_lst_a = [' COM3']
        set_lst_b = [' 9600', ' 19200', ' 28800', ' 57600', ' 115200']
        self.set_a = wx.ComboBox(self, -1, pos=(130, 117), size=(80, 30), value=' COM3',
                                 choices=set_lst_a, style=wx.CB_READONLY)
        self.set_b = wx.ComboBox(self, -1, pos=(240, 117), size=(80, 30), value=' 9600',
                                 choices=set_lst_b, style=wx.CB_READONLY)
        self.btn_1 = wx.Button(self, id=-1, label='1', pos=(625, 156), size=(28, 28))
        self.btn_1.Bind(wx.EVT_LEFT_DOWN, self.sld)
        self.btn_2 = wx.Button(self, id=-1, label='×', pos=(664, 156), size=(26, 28))
        self.btn_2.Bind(wx.EVT_LEFT_DOWN, self.rmv)
        self.btn_3 = wx.Button(self, id=-1, label='开始', pos=(360, 113), size=(60, 30))
        self.btn_3.Bind(wx.EVT_LEFT_DOWN, self.play)
        self.btn_4 = wx.Button(self, id=-1, label='中止', pos=(440, 113), size=(60, 30))
        self.btn_4.Bind(wx.EVT_LEFT_DOWN, self.kill)
        self.btn_5 = wx.Button(self, id=-1, label='暂停', pos=(520, 113), size=(60, 30))
        self.btn_5.Bind(wx.EVT_LEFT_DOWN, self.stop)
        self.conductor = wx.StaticText(self.panel, -1, label='我', pos=(160, 170), size=(20, 20))
        wx.StaticLine(self, pos=(60, 250), size=(260, -1), style=wx.SL_HORIZONTAL)
        wx.StaticLine(self, pos=(360, 280), size=(330, -1), style=wx.SL_HORIZONTAL)
        wx.StaticText(self, -1, label='演奏进度 :', pos=(365, 200), size=(60, 20))
        wx.StaticText(self, -1, label='总体音量 :', pos=(365, 240), size=(60, 20))
        wx.StaticText(self, -1, label='乐器布局 :', pos=(365, 300), size=(80, 30))
        self.gau_1 = wx.Gauge(self, -1, 100, pos=(440, 200), size=(250, 20), style=wx.GA_HORIZONTAL)
        self.gau_2 = wx.Gauge(self, -1, 127, pos=(440, 240), size=(250, 20), style=wx.GA_HORIZONTAL)

        pygame.midi.init()
        self.output = pygame.midi.Output(pygame.midi.get_default_output_id())
        self.thread, self.player, self.serial = None, None, None
        self.ch_lst, self.ev_lst = None, None
        self.chan_1, self.chan_2 = dict(), dict()
        self.gauges, self.statics = [], []
        self.groups = []
        self.panel_init()
        self.term = True
        self.pause = False
        self.orche = None
        self.angle = 90
        self.display()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for note in range(0, 128):
            for chan in range(0, 16):
                self.output.note_off(note, channel=chan)

    def clear(self):
        for gauge in self.gauges:
            gauge.Destroy()
        for static in self.statics:
            static.Destroy()
        self.gauges, self.statics = [], []

    def panel_init(self):
        music = (self.cbb_2.GetValue()).strip()
        confs = song.songs[music]['confs']
        for i, instr in enumerate(list(confs)):
            pos_r = confs[instr][0]
            pos_a = confs[instr][1] / 180 * np.pi
            pos_x = 160 + pos_r * np.cos(pos_a)
            pos_y = 170 - pos_r * np.sin(pos_a)
            self.groups.append(wx.StaticText(self.panel, -1, label=instr, pos=(pos_x, pos_y), size=(60, 20)))
            # zhu: yuan lai zhe li shi alpha-rho zuo biao xian zai shi rho-alpha zuo biao
            print(i, '+', instr)
            self.chan_1[instr], self.chan_2[i] = i, 2*i
        print(self.chan_1, self.chan_2)

    def frame_init(self):
        music = (self.cbb_2.GetValue()).strip()
        confs = song.songs[music]['confs']
        for conf in list(confs):
            self.volume[conf] = 1
        wx.StaticText(self, -1, label='声道 :', pos=(365, 160), size=(40, 30))
        self.cbb_5 = wx.ComboBox(self, -1, pos=(420, 157), size=(190, 30), value=' ' + list(self.volume)[0],
                                 choices=util.str_list_indent(list(self.volume)), style=wx.CB_READONLY)
        self.cbb_5.Bind(wx.EVT_COMBOBOX, self.volume_func)

    def display(self):
        self.clear()
        instrs = list(self.volume)
        for i, instr in enumerate(instrs):
            self.statics.append(wx.StaticText(self, id=-1, label=instr, pos=(60, 280 + 40 * i), size=(60, 20)))
            self.gauges.append(wx.Gauge(self, id=2*i, range=200, pos=(130, 278 + 40 * i), size=(190, 9)))
            self.gauges.append(wx.Gauge(self, id=2*i+1, range=127, pos=(130, 292 + 40 * i), size=(190, 9)))
            self.chan_2[self.chan_1[instr]] = 2*i

    def volume_func(self, event):
        grp = (self.cbb_5.GetValue()).strip()
        val = self.volume[grp]
        self.btn_1.SetLabel(str(val))

    def sld(self, event):
        grp = (self.cbb_5.GetValue()).strip()
        val = self.volume[grp]
        frame = util.SliderFrame(parent=None, fid=-1, val=val * 100, call=self.callback)
        frame.Show()

    def callback(self, val):
        self.btn_1.SetLabel(str(val))
        grp = (self.cbb_5.GetValue()).strip()
        self.volume[grp] = int(val)

    def rmv(self, event):
        if len(list(self.volume)) == 1:
            return
        ins = (self.cbb_5.GetValue()).strip()
        self.volume.pop(ins)
        self.cbb_5.Destroy()
        self.cbb_5 = wx.ComboBox(self, -1, pos=(420, 157), size=(190, 30), value=' ' + list(self.volume)[0],
                                 choices=util.str_list_indent(list(self.volume)), style=wx.CB_READONLY)
        self.btn_1.SetLabel(str(self.volume[list(self.volume)[0]]))
        for i in range(len(self.groups)):
            label = self.groups[i].GetLabel()
            if label == ins:
                grp_st = self.groups.pop(i)
                grp_st.Destroy()
                break
        self.display()

    def play(self, event):
        if not self.term and self.pause:
            self.pause = False
            return
        if self.term:
            self.pause = False
            self.term = False
            self.play_pre(event)
            self.thread.start()
            time.sleep(2)
            self.player.start()

    def play_pre(self, event):
        self.thread, self.serial = None, None
        self.ch_lst, self.ev_lst = None, None
        self.angle = 90
        self.orche = None
        print('play_pre.1')
        self.gau_1.SetValue(0)
        print('play_pre.2')
        music = (self.cbb_2.GetValue()).strip()
        confs = song.songs[music]['confs']
        events = song.songs[music]['events']
        confs_ = dict()
        list_1 = list(self.volume)
        list_2 = []
        for ins in list_1:
            confs_[ins] = confs[ins]
        for i, ev in enumerate(list(events)):
            list_2.append([i, ev])
        self.ch_lst = [ch for ch in list_2 if ch[1] in list_1]
        self.ev_lst = []
        for ch in self.ch_lst:
            self.ev_lst = self.ev_lst + events[ch[1]]
        self.orche = tree.InstrumentContainer()
        self.orche.create(confs_)
        print(self.orche.ilist)
        self.ev_lst = sorted(self.ev_lst)
        span = self.ev_lst[-1][0] / 800
        print('play_pre.4')
        self.thread = threading.Thread(target=self.mon, args=(span,))
        self.player = threading.Thread(target=self.play_music, args=())
        print('play_pre.5')

    def play_music(self):
        player = self.output
        for ch in self.ch_lst:
            ins = ch[1].split('_')[-1]
            idx = util.instr_2[ins] - 1
            player.set_instrument(idx, channel=ch[0])
        last = 0
        span = self.ev_lst[-1][0]
        for event in self.ev_lst:
            if self.term:
                for note in range(0, 128):
                    for chan in range(0, 16):
                        player.note_off(note, channel=chan)
                self.kill()
                return
            if self.pause:
                for note in range(0, 128):
                    for chan in range(0, 16):
                        player.note_off(note, channel=chan)
                while self.pause:
                    time.sleep(0.01)
                    if self.term:
                        return
                if self.term:
                    return
            if event[0] > last:
                time.sleep((event[0] - last) / 1000)
                last = event[0]
                self.gau_1.SetValue(last / span * 100)
            player.note_on(event[1], event[2], channel=event[3])
            self.gau_2.SetValue(event[1])
            gau_1 = wx.FindWindowById(id=self.chan_2[event[3]])
            gau_2 = wx.FindWindowById(id=self.chan_2[event[3]]+1)
            gau_1.SetValue(1 * 100)
            gau_2.SetValue(event[1])

    def mon(self, span):
        # self.serial = serial.Serial("COM4", 9600, timeout=0.5)  # zhushi
        t0, t1 = time.time(), 0.0
        tmp = []
        ini = dict()
        for i in list(self.volume):
            ini[i] = self.volume[i]
        while t1 < 2.0:
            if self.serial is not None:
                str_ = self.serial.readline()
                try:
                    dic = eval(str_)
                    tmp.append(dic['angle'])
                except Exception:
                    pass
            t1 = time.time() - t0
        # self.angle = int((max(tmp) + min(tmp))/2)  # zhushi
        print('play_mon.1')
        o_lt, n_lt = list(self.volume), []
        k_di = dict()
        t0 = time.time()
        self.paras[1], t1 = 1, 0
        kk_2 = [0, 0, 0, 0, 0]
        print('play_mon.2')
        while t1 < 101:
            # print('play_mon.21')
            # for i, static in enumerate(self.statics):
            #     label = static.GetLabel()
            #     val = self.volume[label]  # * self.paras[0]
            #     self.gauges[i].SetValue(min(val, 126))
            k_1 = 1.0
            # print('play_mon.22')
            if self.serial is not None:
                str_ = self.serial.readline()
                try:
                    dic = eval(str_)
                    k_1 = max(dic['acc_tot'], 1)
                    k_2 = dic['acc_z']
                    k_3 = int(dic['angle']) - self.angle + 80
                    k_4 = dic['curvature'] + 180
                    k_1 = 1 + np.log(1 + np.log(1 + np.log(k_1)))
                    kk_2.append(k_2)
                    kk_2.pop(0)
                    self.paras[0] = max(kk_2) / 100 + 0.6
                    # print(k_4)
                    if k_4 > 0:
                        for i in o_lt:
                            try:
                                self.volume[i] = ini[i]
                            except Exception:
                                pass
                        for i in o_lt:
                            k_di[i] = 1
                        L, R = max(k_3 - 20, 0), min(k_3 + 20, 180)
                        print(L, R)
                        # self.tree.query(L, R)
                        # n_lt = self.tree.A
                        # print(self.tree.A, L, R)
                        for i in n_lt:
                            k_di[i] = k_4 / 10 + 1
                        for i in n_lt:
                            self.volume[i] = min(self.volume[i] * k_di[i], 126)
                        o_lt = n_lt
                        print(n_lt)
                    # else:
                    #     print('?')
                    #     for i in list(ini):
                    #         try:
                    #             self.volume[i] = ini[i]
                    #         except Exception:
                    #             pass
                except Exception:
                    pass
            # print('play_mon.23')
            interval = (time.time() - t0 - self.paras[1]) * k_1
            self.paras[1] = self.paras[1] + interval
            # self.paras[1] = time.time() - t0
            t1 = int(self.paras[1] / span * 100)
            # print('play_mon.24')
        self.paras[1] = 0
        print('play_mon.3')
        for gauge in self.gauges:
            gauge.SetValue(0)
        self.gau_2.SetValue(0)
        # self.serial.close()  # zhushi
        # self.serial.__del__()
        # self.serial = None

    def stop(self, event):
        self.pause = True

    def kill(self, close=False, event=None):
        self.term = True
        self.thread = None
        self.ch_lst, self.ev_lst = None, None
        if self.serial is not None:
            self.serial.close()
            self.serial.__del__()
        self.serial, self.player = None, None
        if not close:
            for gauge in self.gauges:
                gauge.SetValue(0)
            self.gau_1.SetValue(0)
            self.gau_2.SetValue(0)
            self.paras[1] = 0

    def close(self, event):
        self.term = True
        self.kill(event, True)
        self.Destroy()
        os._exit(0)


def gui():
    app = wx.App(False)
    frame = initFrame(parent=None, fid=-1)
    # frame.Bind(wx.EVT_MOUSE_EVENTS, frame.func)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    gui()
