import ctypes
import inspect
import wx
import time
import pygame.midi
from util import song
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure


instr_1 = {'钢琴类': 1, '其他类': 2, '风琴类': 3, '吉他类': 4, '贝斯类': 5, '弦乐器': 6,
           '合唱组': 7, '铜管乐器': 8, '簧片乐器': 9, '管鸣乐器': 10, '合成领奏': 11,
           '合成长音': 12, '合成效果': 13, '民间乐器': 14, '打击乐器': 15, '音响效果': 16}
instr_2 = {'钢琴': 1, '立式钢琴': 2, '电钢琴': 3, '酒吧钢琴': 4, '电子琴': 5, '电子琴+合唱': 6, '羽管键琴': 7, '古钢琴': 8,
           '钢片琴': 9, '钟琴': 10, '音乐盒': 11, '电颤琴': 12, '马林巴琴': 13, '木琴': 14, '管钟': 15, '洋琴': 16,
           '击杆风琴': 17, '打击风琴': 18, '摇滚风琴': 19, '教堂风琴': 20, '簧风琴': 21, '手风琴': 22, '口琴': 23, '小手风琴': 24,
           '尼龙丝吉他': 25, '钢丝吉他': 26, '爵士吉他': 27, '清音吉他': 28, '弱音吉他': 29, '过载吉他': 30, '失真吉他': 31, '吉他泛音': 32,
           '原声贝斯': 33, '手弹贝斯': 34, '拨片贝斯': 35, '无品贝斯': 36, '拍击贝斯1': 37, '拍击贝斯2': 38, '合成贝斯1': 39, '合成贝斯2': 40,
           '小提琴': 41, '中提琴': 42, '大提琴': 43, '低音提琴': 44, '颤音弦': 45, '拨弦': 46, '竖琴': 47, '定音鼓': 48,
           '弦': 49, '慢弦': 50, '合成弦1': 51, '合成弦2': 52, '人声合唱啊': 53, '人声嘟': 54, '合成人声': 55, '管弦乐齐奏': 56,
           '小号': 57, '长号': 58, '大号': 59, '弱音小号': 60, '圆号': 61, '铜管': 62, '合成铜管1': 63, '合成铜管2': 64,
           '高音萨克斯': 65, '中音萨克斯': 66, '次中音萨克斯': 67, '上低音萨克斯': 68, '双簧管': 69, '英国管': 70, '巴松管': 71, '单簧管': 72,
           '短笛': 73, '长笛': 74, '竖笛': 75, '排箫': 76, '瓶木管': 77, '尺八': 78, '口哨': 79, '奥卡雷那': 80,
           '方波': 81, '锯齿波': 82, '汽笛风琴': 83, '领奏': 84, '沙朗主奏': 85, '人声独唱': 86, '五度管乐': 87, '贝斯主奏': 88,
           '幻想曲': 89, '温暖背景': 90, '复合成': 91, '太空音': 92, '弧形波': 93, '金属背景': 94, '光晕背景': 95, '曲线波背景': 96,
           '冰雨': 97, '电影声效': 98, '水晶': 99, '气氛': 100, '轻柔': 101, '地精': 102, '回声滴答': 103, '星辰大海': 104,
           '西塔琴': 105, '班卓琴': 106, '三弦琴': 107, '十三弦古筝': 108, '克林巴琴': 109, '苏格兰风笛': 110, '古提琴': 111, '山奈': 112,
           '铃铛': 113, '摇摆舞铃': 114, '钢鼓': 115, '木块': 116, '太鼓': 117, '通通鼓': 118, '合成鼓': 119, '铜钹': 120,
           '吉他杂音': 121, '呼吸音': 122, '海浪': 123, '鸟': 124, '电话': 125, '直升机': 126, '掌声': 127, '枪射击': 128}


def str_list_indent(lst):
    for i in range(len(lst)):
        lst[i] = ' ' + lst[i]
    return lst


def text_default_value(text, data_type, default):
    try:
        if isinstance(text, wx.TextCtrl):
            return eval(data_type)(text.GetLineText(0))
        elif isinstance(text, wx.StaticText):
            return eval(data_type)(text.GetLabel())
        else:
            return eval(data_type)(text)
    except ValueError:
        return default


class SliderFrame(wx.Frame):

    def __init__(self, call, val, max_, scale=1, parent=None, fid=-1):
        wx.Frame.__init__(self, parent, fid, '', size=(245, 140),
                          style=wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.Center()
        self.call = call
        self.panel = wx.Panel(self)
        self.slider = wx.Slider(self.panel, value=val*scale, id=-1, minValue=0, maxValue=max_*scale, pos=(10, 20), size=(210, -1))
        self.sl_txt = wx.StaticText(self.panel, -1, label=str(val), pos=(90, 50), size=(50, 25), style=wx.TE_CENTER)
        self.min = wx.StaticText(self.panel, id=1, label='0', pos=(20, 50), size=(50, 25), style=wx.TE_LEFT)
        self.max = wx.StaticText(self.panel, id=2, label=str(max_), pos=(160, 50), size=(50, 25), style=wx.TE_RIGHT)
        self.scale = scale
        self.sl_val = val

        self.slider.Bind(wx.EVT_SLIDER, self.slider_fun)

    def slider_fun(self, event):
        rb = event.GetEventObject()
        self.sl_val = rb.GetValue()/self.scale
        self.sl_txt.SetLabel(str(self.sl_val))
        self.call(self.sl_val)


class MPL_Panel(wx.Panel):

    def __init__(self, parent, pos, size, style=wx.TE_CENTER | wx.EXPAND):
        wx.Panel.__init__(self, parent=parent, size=size, pos=pos, style=style, id=-1)
        tmp = (list(size)[0] / 100 + 0.1, list(size)[1] / 100 + 0.1)
        self.Figure = matplotlib.figure.Figure(figsize=tmp)
        self.axes = self.Figure.add_axes([0, 0, 0, 0])  #
        self.FigureCanvas = FigureCanvas(self, -1, self.Figure)

        self.SubBoxSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.TopBoxSizer = wx.BoxSizer(wx.VERTICAL)
        self.TopBoxSizer.Add(self.SubBoxSizer, proportion=-1, border=2, flag=wx.ALL | wx.EXPAND)
        self.TopBoxSizer.Add(self.FigureCanvas, proportion=-10, border=2, flag=wx.ALL | wx.EXPAND)

        self.SetSizer(self.TopBoxSizer)


def _async_raise(tid, exc):
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exc):
        exc = type(exc)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        tid, ctypes.py_object(exc))
    if res == 0:
        return
        # raise ValueError("invalid thread id")
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
