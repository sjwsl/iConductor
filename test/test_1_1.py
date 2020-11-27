import wx

app = wx.App()


def dragEVT(event):
    if event.Dragging():
        panel1.SetPosition(event.GetPosition())
    # elif event.ButtonUp():
    #     panel1.SetPosition(event.GetPosition())
    # elif event.ButtonDown():
    #     panel1.SetPosition(event.GetPosition())


frame = wx.Frame(None, -1, "Hello World")
page1BoxSizer = wx.BoxSizer(wx.HORIZONTAL)
frame.SetSizer(page1BoxSizer)
panel1 = wx.Panel(frame, wx.ID_ANY, size=wx.Size(100, 100))
panel1.SetBackgroundColour("#aa0000")
frame.Bind(wx.EVT_MOUSE_EVENTS, dragEVT)

frame.Show()
app.MainLoop()
