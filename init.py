import time

import wx
import numpy as np
import pygame
from util import util, song, tree

import serial
import threading


class initFrame(wx.Frame):

    def __init__(self, parent=None, fid=-1):
        wx.Frame.__init__(self, parent, fid, '人-机交互音乐指挥系统 v0.2', size=(770, 680),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.Center()
        self.SetBackgroundColour((240, 240, 240))
        pageBoxSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(pageBoxSizer)
        self.Bind(wx.EVT_CLOSE, self.close)
        img_1 = wx.Image('title_1.png', wx.BITMAP_TYPE_PNG)
        img_1 = img_1.ConvertToBitmap()
        wx.StaticBitmap(self, -1, bitmap=img_1, pos=(210, 0))
        img_2 = wx.Image('title_2.png', wx.BITMAP_TYPE_PNG)
        img_2 = img_2.ConvertToBitmap()
        wx.StaticBitmap(self, -1, bitmap=img_2, pos=(530, 90))

        self.volume = dict()
        self.coords = dict()
        self.paras = list()
        self.paras.append(1.0)
        self.paras.append(0.0)
        self.volume['1_钢琴'] = 63
        self.volume['1_小提琴'] = 63
        self.coords['1_钢琴'] = [
            int(np.arccos(32/np.sqrt(30**2+32**2))/np.pi*180 + 0.5), np.sqrt(30**2+32**2)]
        self.coords['1_小提琴'] = [
            int(np.arccos(-62/np.sqrt(30**2+62**2))/np.pi*180 + 0.5), np.sqrt(30**2+62**2)]

        music_lst_1 = [' 所有', ]
        music_lst_2 = [' 两只老虎', ' 卡门序曲', ' 打上花火']
        self.instrs = {'钢琴': 1, '小提琴': 1}
        wx.StaticText(self, -1, label='设备 :', pos=(60, 120), size=(40, 30))
        wx.StaticText(self, -1, label='作者 :', pos=(60, 160), size=(60, 30))
        wx.StaticText(self, -1, label='曲目 :', pos=(60, 200), size=(60, 30))
        wx.StaticText(self, -1, label='乐器大类 :', pos=(60, 240), size=(60, 30))
        wx.StaticText(self, -1, label='乐器小类 :', pos=(60, 280), size=(60, 30))
        self.cbb_1 = wx.ComboBox(self, -1, pos=(130, 157), size=(190, 30), value=music_lst_1[0],
                                 choices=music_lst_1, style=wx.CB_SORT | wx.CB_READONLY)
        self.cbb_2 = wx.ComboBox(self, -1, pos=(130, 197), size=(190, 30), value=music_lst_2[1],
                                 choices=music_lst_2, style=wx.CB_READONLY)  # wx.CB_SORT |
        self.cbb_3 = wx.ComboBox(self, -1, pos=(130, 237), size=(190, 30), value=' ' + list(util.instr_1)[0],
                                 choices=util.str_list_indent(list(util.instr_1)), style=wx.CB_READONLY)
        self.cbb_3.Bind(wx.EVT_COMBOBOX, self.type_func)
        self.cbb_4 = wx.ComboBox(self, -1, pos=(130, 277), size=(190, 30), value=' ' + list(util.instr_2)[0],
                                 choices=util.str_list_indent(list(util.instr_2)[0:8]), style=wx.CB_READONLY)
        self.cbb_5 = wx.ComboBox(self, -1, pos=(420, 237), size=(190, 30), value=' ' + list(self.volume)[0],
                                 choices=util.str_list_indent(list(self.volume)), style=wx.CB_READONLY)
        self.cbb_5.Bind(wx.EVT_COMBOBOX, self.volume_func)
        wx.StaticText(self, -1, label='身高 :', pos=(365, 160), size=(40, 30))
        wx.StaticText(self, -1, label='模式 :', pos=(540, 160), size=(40, 30))
        wx.StaticText(self, -1, label='幅度 :', pos=(365, 200), size=(40, 30))
        wx.StaticText(self, -1, label='速度 :', pos=(540, 200), size=(40, 30))
        wx.StaticText(self, -1, label='声道 :', pos=(365, 240), size=(40, 30))
        list_a = [' COM3']
        list_b = [' 9600', ' 19200', ' 28800', ' 57600', ' 115200']
        list_1 = [' 140 cm', ' 150 cm', ' 160 cm',
                  ' 170 cm', ' 180 cm', ' 190 cm', ' 200 cm']
        list_2 = ['   0 cm', '  20 cm', '  40 cm', '  60 cm', '  80 cm',
                  ' 100 cm', ' 120 cm', ' 140 cm', ' 160 cm', ' 180 cm']
        list_3 = [' 很大', ' 大', ' 中', ' 小', ' 很小']
        list_4 = [' 很快', ' 快', ' 中', ' 慢', ' 很慢']
        self.set_a = wx.ComboBox(self, -1, pos=(130, 117), size=(80, 30), value=' COM3',
                                 choices=list_a, style=wx.CB_READONLY)
        self.set_b = wx.ComboBox(self, -1, pos=(240, 117), size=(80, 30), value=' 9600',
                                 choices=list_b, style=wx.CB_READONLY)
        self.set_1 = wx.ComboBox(self, -1, pos=(420, 157), size=(95, 30), value=' 180 cm',
                                 choices=list_1, style=wx.CB_READONLY)
        self.set_2 = wx.ComboBox(self, -1, pos=(595, 157), size=(95, 30), value=' 100 cm',
                                 choices=list_2, style=wx.CB_READONLY)
        self.set_3 = wx.ComboBox(self, -1, pos=(420, 197), size=(95, 30), value=list_3[2],
                                 choices=list_3, style=wx.CB_READONLY)
        self.set_4 = wx.ComboBox(self, -1, pos=(595, 197), size=(95, 30), value=list_4[2],
                                 choices=list_4, style=wx.CB_READONLY)
        self.btn_0 = wx.Button(self, id=-1, label='添加乐器',
                               pos=(155, 317), size=(140, 29))
        self.btn_0.Bind(wx.EVT_LEFT_DOWN, self.add)
        self.btn_1 = wx.Button(self, id=-1, label='63',
                               pos=(625, 236), size=(28, 28))
        self.btn_1.Bind(wx.EVT_LEFT_DOWN, self.sld)
        self.btn_2 = wx.Button(self, id=-1, label='×',
                               pos=(664, 236), size=(26, 28))
        self.btn_2.Bind(wx.EVT_LEFT_DOWN, self.rmv)
        self.btn_3 = wx.Button(self, id=-1, label='开始',
                               pos=(360, 113), size=(60, 30))
        self.btn_3.Bind(wx.EVT_LEFT_DOWN, self.play)
        self.btn_4 = wx.Button(self, id=-1, label='中止',
                               pos=(440, 113), size=(60, 30))
        self.btn_4.Bind(wx.EVT_LEFT_DOWN, self.term)

        self.conductor = wx.StaticText(
            self, -1, label='我', pos=(527, 550), size=(20, 20))  # (182, 530)
        self.grp_s = [wx.StaticText(self, 0, label='1_小提琴', pos=(465, 520), size=(60, 20)),
                      wx.StaticText(self, 1, label='1_钢琴', pos=(559, 520), size=(60, 20))]
        self.grp_n = 0
        for grp in self.grp_s:
            grp.Bind(wx.EVT_LEFT_DOWN, self.grp_func)
        wx.StaticBox(self, pos=(366, 380), size=(330, 220))
        wx.StaticLine(self, pos=(60, 360), size=(
            260, -1), style=wx.SL_HORIZONTAL)
        wx.StaticLine(self, pos=(360, 280), size=(
            330, -1), style=wx.SL_HORIZONTAL)
        wx.StaticText(self, -1, label='演奏进度 :', pos=(365, 300), size=(60, 20))
        wx.StaticText(self, -1, label='总体音量 :', pos=(365, 340), size=(60, 20))
        wx.StaticText(self, -1, label='乐器布局 :', pos=(365, 380), size=(80, 30))
        self.gau_1 = wx.Gauge(self, -1, 100, pos=(440, 297),
                              size=(250, 20), style=wx.GA_HORIZONTAL)
        self.gau_2 = wx.Gauge(self, -1, 127, pos=(440, 337),
                              size=(250, 20), style=wx.GA_SMOOTH)
        self.gauges, self.process, self.statics = [], [], []
        self.thread, self.serial = None, None
        self.btn_5, self.btn_6 = None, None
        self.angle = 90
        self.tree = None
        self.instr_ = 0
        self.display()

    def clear(self):
        for gauge in self.gauges:
            gauge.Destroy()
        for static in self.statics:
            static.Destroy()
        self.gauges, self.statics = [], []

    def display(self):
        self.clear()
        instrs = list(self.volume)[self.instr_:self.instr_ + 6]
        for i, instr in enumerate(instrs):
            self.statics.append(wx.StaticText(
                self, id=i, label=instr, pos=(60, 380 + 40 * i), size=(60, 20)))
            self.gauges.append(wx.Gauge(self, id=i, range=127, pos=(130, 380 + 40 * i), size=(190, 20),
                                        style=wx.GA_SMOOTH))
        self.up_or_dn()

    def up_or_dn(self):
        tot = len(list(self.volume))
        if self.instr_ > 0:
            if self.btn_5 is None:
                self.btn_5 = wx.Button(
                    self, id=-1, label='up', pos=(60, 320), size=(20, 20))
                self.btn_5.Bind(wx.EVT_LEFT_DOWN, self.up)
        else:
            if self.btn_5 is not None:
                self.btn_5.Destroy()
            self.btn_5 = None
        if tot > self.instr_ + 6:
            if self.btn_6 is None:
                self.btn_6 = wx.Button(
                    self, id=-1, label='dn', pos=(100, 320), size=(20, 20))
                self.btn_6.Bind(wx.EVT_LEFT_DOWN, self.dn)
        else:
            if self.btn_6 is not None:
                self.btn_6.Destroy()
            self.btn_6 = None

    def up(self, event):
        self.instr_ = self.instr_ - 1
        instrs = list(self.volume)[self.instr_:self.instr_ + 6]
        for i, instr in enumerate(instrs):
            self.statics[i].SetLabel(instr)
        self.up_or_dn()

    def dn(self, event):
        self.instr_ = self.instr_ + 1
        instrs = list(self.volume)[self.instr_:self.instr_ + 6]
        for i, instr in enumerate(instrs):
            self.statics[i].SetLabel(instr)
        self.up_or_dn()

    def grp_func(self, event):
        grp = event.GetEventObject()
        gid = grp.GetId()
        self.grp_n = gid

    def type_func(self, event):
        idx = util.instr_1[(self.cbb_3.GetValue()).strip()] - 1
        lst = list(util.instr_2)[idx * 8:idx * 8 + 8]
        val = list(util.instr_2)[idx * 8]
        self.cbb_4.Destroy()
        self.cbb_4 = wx.ComboBox(self, -1, pos=(130, 277), size=(190, 30), value=' ' + val,
                                 choices=util.str_list_indent(lst), style=wx.CB_READONLY)

    def volume_func(self, event):
        grp = (self.cbb_5.GetValue()).strip()
        val = self.volume[grp]
        self.btn_1.SetLabel(str(val))

    def sld(self, event):
        grp = (self.cbb_5.GetValue()).strip()
        val = self.volume[grp]
        frame = util.SliderFrame(
            parent=None, fid=-1, val=val, call=self.callback)
        frame.Show()

    def callback(self, val):
        self.btn_1.SetLabel(str(val))
        grp = (self.cbb_5.GetValue()).strip()
        self.volume[grp] = int(val)

    def add(self, event):
        ins = (self.cbb_4.GetValue()).strip()
        try:
            num = self.instrs[ins]
        except KeyError:
            num = 0
        grp = str(num + 1) + '_' + ins
        self.instrs[ins] = num + 1
        self.volume[grp] = 63
        self.coords[grp] = [0, -1]
        self.cbb_5.Destroy()
        name = list(self.volume)[0]
        self.cbb_5 = wx.ComboBox(self, -1, pos=(420, 237), size=(190, 30), value=' ' + name,
                                 choices=util.str_list_indent(list(self.volume)), style=wx.CB_READONLY)
        self.cbb_5.Bind(wx.EVT_COMBOBOX, self.volume_func)
        self.btn_1.SetLabel(str(self.volume[name]))
        self.grp_s.append(wx.StaticText(self, len(self.grp_s),
                                        label=grp, pos=(620, 405), size=(60, 20)))
        self.grp_s[-1].Bind(wx.EVT_LEFT_DOWN, self.grp_func)
        self.display()

    def rmv(self, event):
        in_ = (self.cbb_5.GetValue()).strip()
        ins = in_.split('_')[-1]
        idx = util.text_default_value(in_.split('_')[0], 'int', 0)
        num = self.instrs[ins] = self.instrs[ins] - 1
        if num == 0:
            self.instrs.pop(ins)
            self.volume.pop(in_)
            self.coords.pop(in_)
        else:
            for i in range(idx, num + 1):
                self.volume[str(i) + '_' +
                            ins] = self.volume[str(i + 1) + '_' + ins]
            self.volume.pop(str(num + 1) + '_' + ins)
            self.coords.pop(str(num + 1) + '_' + ins)
        self.cbb_5.Destroy()
        self.cbb_5 = wx.ComboBox(self, -1, pos=(420, 237), size=(190, 30), value=' ' + list(self.volume)[0],
                                 choices=util.str_list_indent(list(self.volume)), style=wx.CB_READONLY)
        self.btn_1.SetLabel(str(self.volume[list(self.volume)[0]]))
        for i in range(len(self.grp_s)):
            label = self.grp_s[i].GetLabel()
            if label == in_:
                grp_st = self.grp_s.pop(i)
                grp_st.Destroy()
                break
        for i in range(len(self.grp_s)):
            label = self.grp_s[i].GetLabel()
            if label.endswith('_' + ins):
                idx_ = int(label.split('_')[0])
                if idx_ > idx:
                    self.grp_s[i].SetLabel(str(idx_-1) + '_' + ins)
        self.display()

    def play(self, event):
        self.term(event)
        self.tree = tree.SegTree()
        self.tree.build(self.coords)
        self.tree.query(0, 180)
        print(self.tree.A)
        str_1 = (self.cbb_2.GetValue()).strip()
        span = song.song[str_1]['time']
        str_list = list(self.volume)
        self.thread = threading.Thread(target=self.pro, args=(span, ))
        self.thread.start()
        # time.sleep(2)
        

        self.play_music(str_1, str_list, self.volume, self.paras)

        # for str_2 in str_list:
        #     process = Process(target=util.play_music, args=(str_1, str_2, self.volume, self.paras))
        #     self.process.append(process)
        # for process in self.process:
        #     process.start()

    def play_music(self, music, instruments, volumes, paras):
        pygame.midi.init()
        player = pygame.midi.Output(16)
        player.set_instrument(0, channel = 1)
        player.set_instrument(0, channel = 2)

        last = 0
        for event in song.events:
            print(event)
            if event[0] > last:
                time.sleep((event[0] - last) / 800)
                last = event[0]
            player.note_on(event[1], event[2], channel=event[3])
    #     # channel = 0
    #     # for ins in instruments:
    #     #     i = util.instr_2[ins.split('_')[-1]] - 1
    #     #     tmp2 = channel
    #     #     channel = channel + 1
    #     #     player.set_instrument(i, channel = tmp2)
    #     #     try:
    #     #         tmp = song.song[music][ins]
    #     #     except KeyError:
    #     #         tmp = song.song[music]['else']
    #     #     threading.Thread(target=self.play_ins, args=(player, ins ,tmp, volumes, paras, tmp2, )).start()

    # def play_ins(self, player, ins, music, vols, paras, chan):
    #     for i in range(len(music[0])):
    #         k = paras[0]
    #         val = min(int(vols[ins] * k), 127)
    #         note = music[0][i]
    #         if note > 0:
    #             secs = music[1][i+1] - music[1][i]  # paras[1]
    #             print(val, chan)
    #             player.note_on(note=note, velocity=val, channel=chan)
    #             time.sleep(secs if secs > 0 else 0)
    #             player.note_off(note=note, velocity=val, channel=chan)
    #         else:
    #             time.sleep(music[1][i + 1] - music[1][i])

    def pro(self, span):
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
        o_lt, n_lt = list(self.volume), []
        k_di = dict()
        t0 = time.time()
        self.paras[1], t1 = 0.0, 0.0
        kk_2 = [0, 0, 0, 0, 0]
        while t1 < 101:
            self.gau_1.SetValue(t1)
            val = int(max(self.volume.values()) * self.paras[0])
            self.gau_2.SetValue(val)
            for i, static in enumerate(self.statics):
                label = static.GetLabel()
                val = int(self.volume[label] * self.paras[0])
                # print(self.volume)
                self.gauges[i].SetValue(min(val, 126))
            k_1 = 1.0
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
                        L, R = max(k_3-20, 0), min(k_3+20, 180)
                        print(L, R)
                        self.tree.query(L, R)
                        n_lt = self.tree.A
                        print(self.tree.A, L, R)
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
            interval = (time.time() - t0 - self.paras[1]) * k_1
            self.paras[1] = self.paras[1] + interval
            # self.paras[1] = time.time() - t0
            t1 = int(self.paras[1] / span * 100)
        time.sleep(2)
        self.paras[1] = 0
        for gauge in self.gauges:
            gauge.SetValue(0)
        self.gau_1.SetValue(0)
        self.gau_2.SetValue(0)
        # self.serial.close()  # zhushi
        # self.serial.__del__()
        # self.serial = None

    def term(self, event):
        while self.thread is not None and self.thread.is_alive():
            util.stop_thread(self.thread)
        self.thread = None
        if self.serial is not None:
            self.serial.close()
            self.serial.__del__()
        self.serial = None
        for process in self.process:
            if process.is_alive():
                process.terminate()
            del process
        self.process = []
        for gauge in self.gauges:
            gauge.SetValue(0)
        self.gau_1.SetValue(0)
        self.gau_2.SetValue(0)
        self.tree = None
        self.paras[1] = 0

    def close(self, event):
        self.term(event)
        self.Destroy()

    def func(self, event):
        if event.Dragging():
            x1, y1 = event.GetPosition()
            if 359 < x1 < 697 and 379 < y1 < 601:
                self.grp_s[self.grp_n].SetPosition((x1 - 30, y1 - 10))
                x0, y0 = self.conductor.GetPosition()
                grp = self.grp_s[self.grp_n].GetLabel()
                rou = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
                alpha = int(np.arccos((x1 - x0) / rou)/np.pi*180 + 0.5)
                if y1 > y0 + 10 and x1 < x0:
                    alpha = 180
                if y1 > y0 + 10 and x1 > x0 + 10:
                    alpha = 0
                self.coords[grp] = [alpha, rou]
                # print(self.coords)
                # self.coords[grp][0] = (y0 - y1) / (x1 - x0)
                # self.coords[grp][1] = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)


def gui():
    app = wx.App(False)
    frame = initFrame(parent=None, fid=-1)
    frame.Bind(wx.EVT_MOUSE_EVENTS, frame.func)
    frame.Show()
    app.MainLoop()


if __name__ == '__main__':
    gui()
