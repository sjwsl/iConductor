import wx
import wx.grid as grd
import wx.lib.scrolledpanel as scrolled


# A sample "table" of some parameters, let's say
class GaugeBox(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.gauges = []
        self.i = 0
        for i in range(10):
            self.add()

    def add(self, event=None):
        self.gauges.append(wx.Gauge(self, id=-1, range=127, pos=(20, 20 + 40 * self.i), size=(190, 9)))
        self.gauges.append(wx.Gauge(self, id=-1, range=200, pos=(20, 35 + 40 * self.i), size=(190, 9)))
        self.i = self.i + 1
        self.Fit()


# The main panel:
class AnotherPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        # main sizer for everything:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Create the grid which will be scrollable:
        scrolledPanel = scrolled.ScrolledPanel(self, size=(425, 400))
        self.table = GaugeBox(scrolledPanel)

        self.btn_5 = wx.Button(self, id=-1, label='暂停')
        mainSizer.Add(self.btn_5, 0, wx.CENTER)
        self.btn_5.Bind(wx.EVT_LEFT_DOWN, self.table.add)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.table, 1, wx.ALL, 5)
        scrolledPanel.SetSizer(sizer)
        scrolledPanel.Layout()
        scrolledPanel.SetupScrolling(scroll_x=False)

        # Put the scrolled panel into a static box:
        box = wx.StaticBox(self, -1, "Parameters: ")
        sizer2 = wx.StaticBoxSizer(box, wx.VERTICAL)
        sizer2.Add(scrolledPanel, 1, wx.EXPAND)

        mainSizer.Add(sizer2, 1, wx.EXPAND)
        self.SetSizer(mainSizer)
        self.Fit()


# The main frame:
class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, -1, title=title, size=(850, 500))

        # Put 2 panels side by side:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(AnotherPanel(self), 1, wx.EXPAND)
        sizer.Add(AnotherPanel(self), 1, wx.EXPAND)

        self.SetSizer(sizer)
        self.SetAutoLayout(1)


# And, the app and mainloop:
app = wx.App(False)
frame = MainFrame(None, "Scroll Test")
frame.Show(True)
app.MainLoop()
