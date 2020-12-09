import wx
import wx.grid as grd
import wx.lib.scrolledpanel as scrolled


# A sample panel with some check box controls to take up space, within a
# static box sizer
class SamplePanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        grid = wx.GridBagSizer()
        for i in (0, 1):
            grid.Add(wx.StaticText(self, label="Blah Blah: "), pos=(i, 0))
            grid.Add(wx.CheckBox(self), pos=(i, 1))

        box = wx.StaticBox(self, -1, "Some Settings: ")
        box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
        box_sizer.Add(grid, 0, wx.ALL)
        self.SetSizer(box_sizer)
        self.Layout()


# A sample "table" of some parameters, let's say
class SampleGrid(grd.Grid):
    def __init__(self, parent):
        grd.Grid.__init__(self, parent)

        self.CreateGrid(20, 4)
        self.SetColLabelValue(0, "Value")
        self.SetColLabelValue(1, "Lo-Bound")
        self.SetColLabelValue(2, "Hi-Bound")
        self.SetColLabelValue(3, "Fit")


# The main panel:
class AnotherPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        # main sizer for everything:
        mainSizer = wx.BoxSizer(wx.VERTICAL)

        # Add a few "sample panels":
        mainSizer.Add(SamplePanel(self), 0, wx.CENTER)
        mainSizer.Add(SamplePanel(self), 0, wx.CENTER)
        mainSizer.Add(SamplePanel(self), 0, wx.CENTER)

        # Create the grid which will be scrollable:
        scrolledPanel = scrolled.ScrolledPanel(self, size=(425, 400))
        table = SampleGrid(scrolledPanel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(table, 1, wx.ALL | wx.EXPAND, 5)
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
