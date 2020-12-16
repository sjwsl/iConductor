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

        music_lst_1 = [' 所有', ]
        music_lst_2 = [' 天空之城', ' 我心永恒', ]
        wx.StaticText(self, -1, label='设备 :', pos=(60, 120), size=(40, 30))
        wx.StaticText(self, -1, label='作者 :', pos=(60, 160), size=(60, 30))
        wx.StaticText(self, -1, label='曲目 :', pos=(60, 200), size=(60, 30))
        self.cbb_1 = wx.ComboBox(self, -1, pos=(130, 157), size=(190, 30), value=music_lst_1[0],
                                 choices=music_lst_1, style=wx.CB_SORT | wx.CB_READONLY)
        self.cbb_2 = wx.ComboBox(self, -1, pos=(130, 197), size=(190, 30), value=music_lst_2[0],
                                 choices=music_lst_2, style=wx.CB_READONLY)  # wx.CB_SORT |
        self.cbb_2.Bind(wx.EVT_COMBOBOX, self.music_init)
        self.cbb_5 = None

        self.beat = 900
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
        self.btn_6 = wx.Button(self, id=-1, label='节拍 : ' + str(self.beat), pos=(600, 113), size=(80, 30))
        self.btn_6.Bind(wx.EVT_LEFT_DOWN, self.ctr)
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
        self.chan_0, self.chan_1, self.chan_2 = dict(), dict(), dict()
        self.gauges, self.statics = [], []
        self.panel, self.graph = None, None
        self.value = dict()
        self.groups = []
        self.angle = 90
        self.term = True
        self.pause = False
        self.orche = None
        self.music_init()

    def __exit__(self, exc_type, exc_val, exc_tb):
        for note in range(0, 128):
            for chan in range(0, 16):
                self.output.note_off(note, channel=chan)

    def music_init(self, event=None):
        self.frame_init()
        self.panel_init()
        self.gauge_func()

    def panel_init(self):
        for group in self.groups:
            group.Destroy()
        self.panel = wx.Panel(self, pos=(366, 300), size=(330, 220))
        self.panel.SetBackgroundColour((255, 255, 255))
        wx.StaticText(self.panel, -1, label='我', pos=(160, 170), size=(20, 20))
        self.groups = []
        music = (self.cbb_2.GetValue()).strip()
        confs = song.songs[music]['confs']
        for i, instr in enumerate(list(confs)):
            pos_r = confs[instr][0]
            pos_a = confs[instr][1] / 180 * np.pi
            pos_x = 170 + pos_r * np.cos(pos_a) - 20
            pos_y = 170 - pos_r * np.sin(pos_a) - 10
            self.groups.append(wx.StaticText(self.panel, -1, label=instr, pos=(pos_x, pos_y), size=(60, 20)))
            # zhu: yuan lai zhe li shi alpha-rho zuo biao xian zai shi rho-alpha zuo biao
            self.chan_0[i], self.chan_1[instr], self.chan_2[i] = instr, i, 2 * i

    def frame_init(self):
        music = (self.cbb_2.GetValue()).strip()
        confs = song.songs[music]['confs']
        self.value = dict()
        for conf in list(confs):
            self.value[conf] = 1
        print(self.value)
        wx.StaticText(self, -1, label='声道 :', pos=(365, 160), size=(40, 30))
        if self.cbb_5 is not None:
            self.cbb_5.Destroy()
        self.cbb_5 = wx.ComboBox(self, -1, pos=(420, 157), size=(190, 30), value=' ' + list(self.value)[0],
                                 choices=util.str_list_indent(list(self.value)), style=wx.CB_READONLY)
        self.cbb_5.Bind(wx.EVT_COMBOBOX, self.volume_func)

    def gauge_func(self):
        for gauge in self.gauges:
            gauge.Destroy()
        for static in self.statics:
            static.Destroy()
        self.gauges, self.statics = [], []
        instrs = list(self.value)
        for i, instr in enumerate(instrs):
            self.statics.append(wx.StaticText(self, id=-1, label=instr, pos=(60, 280 + 40 * i), size=(60, 20)))
            self.gauges.append(wx.Gauge(self, id=2 * i, range=200, pos=(130, 278 + 40 * i), size=(190, 9)))
            self.gauges.append(wx.Gauge(self, id=2 * i + 1, range=127, pos=(130, 292 + 40 * i), size=(190, 9)))
            self.chan_2[self.chan_1[instr]] = 2 * i

    def volume_func(self, event):
        grp = (self.cbb_5.GetValue()).strip()
        val = self.value[grp]
        self.btn_1.SetLabel(str(val))

    def sld(self, event):
        grp = (self.cbb_5.GetValue()).strip()
        val = self.value[grp]
        frame = util.SliderFrame(parent=None, fid=-1, val=val, max_=2, scale=100, call=self.sld_callback)
        frame.Show()

    def sld_callback(self, val):
        self.btn_1.SetLabel(str(val))
        grp = (self.cbb_5.GetValue()).strip()
        self.value[grp] = float(val)

    def ctr(self, event):
        frame = util.SliderFrame(parent=None, fid=-1, val=self.beat, max_=2000, call=self.ctr_callback)
        frame.Show()

    def ctr_callback(self, val):
        str_ = '节拍 : ' + str(val).split('.')[0]
        self.btn_6.SetLabel(str_)
        self.beat = val

    def rmv(self, event):
        if len(list(self.value)) == 1:
            return
        ins = (self.cbb_5.GetValue()).strip()
        self.value.pop(ins)
        self.cbb_5.Destroy()
        self.cbb_5 = wx.ComboBox(self, -1, pos=(420, 157), size=(190, 30), value=' ' + list(self.value)[0],
                                 choices=util.str_list_indent(list(self.value)), style=wx.CB_READONLY)
        self.btn_1.SetLabel(str(self.value[list(self.value)[0]]))
        for i in range(len(self.groups)):
            label = self.groups[i].GetLabel()
            if label == ins:
                grp_st = self.groups.pop(i)
                grp_st.Destroy()
                break
        self.gauge_func()

    def play(self, event):
        if not self.term and self.pause:
            self.pause = False
            return
        if self.term:
            self.play_pre(event)
            self.thread.start()
            time.sleep(2)
            self.player.start()

    def play_pre(self, event):
        self.term, self.pause = False, False
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
        list_1 = list(self.value)
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
        span = self.ev_lst[-1][0] / self.beat
        print('play_pre.4')
        self.serial = serial.Serial("COM4", 9600, timeout=0.5)  # zhushi
        self.thread = threading.Thread(target=self.mon, args=(span,))
        self.player = threading.Thread(target=self.play_music, args=())
        print('play_pre.5')

    def play_music(self):
        print(len(self.ev_lst))
        print(self.ev_lst[-1][0])
        player = self.output
        for ch in self.ch_lst:
            ins = ch[1].split('_')[-1]
            idx = util.instr_2[ins] - 1
            player.set_instrument(idx, channel=ch[0])
            gau = wx.FindWindowById(id=self.chan_2[ch[0]])
            gau.SetValue(self.value[self.chan_0[ch[0]]] * 100)
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
                time.sleep((event[0] - last) / self.beat)
                last = event[0]
                self.gau_1.SetValue(last / span * 100)
            value = self.value[self.chan_0[event[3]]]
            val = int(event[2] * value)
            if val != -1:
                player.note_on(event[1], min(val, 127), channel=event[3])
                self.gau_2.SetValue(event[2])
                gau_1 = wx.FindWindowById(id=self.chan_2[event[3]])
                gau_2 = wx.FindWindowById(id=self.chan_2[event[3]] + 1)
                gau_1.SetValue(value * 100)
                gau_2.SetValue(min(val, 127))
        self.term = True

    def mon(self, span):
        start, dura = time.time(), 0.0
        lst_h, lst_v, lst_a = [], [], []
        while dura < 2.0:
            if self.serial is not None:
                str_ = self.serial.readline()
                try:
                    dic = eval(str_)
                    lst_h.append(float(dic['acc_tot']))
                    lst_v.append(float(dic['acc_z']))
                    lst_a.append(float(dic['angle']))
                except Exception:
                    pass
            dura = time.time() - start
        acc_h = np.array(lst_h).mean()
        acc_v = np.array(lst_v).mean()
        self.angle = np.array(lst_a).mean()  # zhushi
        print('play_mon.1')
        acc_h = list(np.zeros(6,))
        acc_v = list(np.zeros(6,))
        val_0, val_e = self.value, 1
        while not self.term and not self.pause:
            try:
                str_ = self.serial.readline()
                dic = eval(str_)
                a_h = dic['acc_tot']
                a_v = dic['acc_z']
                angle = dic['angle'] - self.angle + 90
                curve = dic['curvature']
                acc_h.append(a_h), acc_h.pop(0)
                acc_v.append(a_v), acc_v.pop(0)
                acc_h_, acc_v_ = np.array(acc_h), np.array(acc_v)
                val_s, vel_s = acc_h_.std(), acc_v_.std()
                acc_h_ = (acc_h_ - acc_h_.mean())/val_s + acc_h_.mean()
                acc_v_ = (acc_v_ - acc_v_.mean())/vel_s + acc_v_.mean()
                acc_hv, acc_vh = acc_h_ / acc_v_, acc_v_ / acc_h_
                val_p, vel_p = np.log(acc_vh.mean()+1), np.log(acc_hv.mean()+1)
                val_s, vel_s = min(np.log(val_s+1), 1), min(np.log(vel_s+1), 1)
                print(str(round(val_p, 4)).ljust(7), str(round(vel_p, 4)).ljust(7),
                      str(round(val_s, 4)).ljust(7), str(round(vel_s, 4)).ljust(7), curve)
                for key in list(self.value):
                    val_e = val_e * (1-val_s) + val_p * val_s
                    val_e = val_0[key] * (1-val_s) + val_e * val_s
                    self.value[key] = min(val_e, 2)
                    # val_p is the parameter of horizontal mov, val_s is the weight value
                    # val_0 is the initial value, val_e is the expected value
                    # val(t) = (1-a) val(0) + a(1-a) val(t-1) + a^2 val(^t)
                    # sug: you'd better to maintain a matrix val_es to record N val_e s as a buffer

            except Exception:
                pass
        print('play_mon.3')
        for gauge in self.gauges:
            gauge.SetValue(0)
        self.gau_2.SetValue(0)
        if self.serial is not None:
            self.serial.close()  # zhushi
            self.serial.__del__()
            self.serial = None

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
