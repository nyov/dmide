import wx
import wx.lib.filebrowsebutton as wxfile
import Image
import math
import re



def read_info(info):
	icon_states = [] #(name, dirs, frames)

	if len(info) < 11: return -1
	if info[0:11] != '# BEGIN DMI': return -2

	groups = re.findall('(.+) = (.+)', info)
	if not groups or not len(groups): return -3

	for x in xrange(len(groups)):
		index, value = groups[x]
		if index == 'version' and value != '4.0': return -4

		if index == 'state':
			state = value
			dirs = int(groups[x + 1][1])
			frames = int(groups[x + 2][1])
			icon_states.append( (state, dirs, frames) )
			x += 2

	return icon_states




class Window(wx.Frame):
	def __init__(self, *args, **kwargs):
		wx.Frame.__init__(self, *args, **kwargs)

		self.initBackground()
		self.initLoadDMI()
		self.initDisplay()

		self.initLayout()


	def initBackground(self):
		self.background = wx.Panel(self, wx.ID_ANY)

	def initLoadDMI(self):
		self.load_dmi_button = wxfile.FileBrowseButton(self.background, wx.ID_ANY, size = (350, -1), fileMask = 'DMI Icons(*.dmi)|*.dmi|All Files(*.*)|*.*', changeCallback = self.LoadDMIButton)

	def initDisplay(self):
		self.display = wx.Panel(self.background, wx.ID_ANY, style = wx.SIMPLE_BORDER)
		self.display.SetBackgroundColour(wx.WHITE)

	def initLayout(self):
		sizer1 = wx.BoxSizer(wx.VERTICAL)
		sizer2 = wx.BoxSizer(wx.VERTICAL)

		sizer2.Add(self.load_dmi_button, 0, wx.EXPAND, 0)
		sizer2.Add(self.display, 1, wx.EXPAND, 0)

		self.background.SetSizer(sizer2)
		sizer1.Add(self.background, 1, wx.EXPAND, 0)

		self.SetSizerAndFit(sizer1)
		self.Layout()


	def LoadDMIButton(self, event):
		self.UpdateDisplay(self.LoadDMI(event.GetString()))

	def LoadDMI(self, dmi):
		dmi = Image.open(dmi)
		dmis = []

		width, height = dmi.size

		for x in xrange(0, width, height):
			new = dmi.crop((x, 0, x + height, height))
			new_image = wx.EmptyImage(new.size[0], new.size[1])
			new_image.SetData(new.convert('RGB').tostring())
			new_image.SetAlphaData(new.convert('RGBA').tostring()[3::4])
			new_bitmap = wx.BitmapFromImage(new_image)
			dmis.append(new_bitmap)

		return dmis, read_info(dmi.info['Description'])

	def UpdateDisplay(self, dmis):
		sizer = wx.GridBagSizer(12, 22)

		width = 10
		def linear_to_coords(i):
			return (i / width, i % width)

		for i, dmi in enumerate(dmis[0]):
			
			sizer.Add( IconDisplay(self.display, wx.ID_ANY, dmi, dmis[1][i]), linear_to_coords(i) )

		self.display.SetSizerAndFit(sizer)
		self.Fit()



class IconDisplay(wx.Panel):
	def __init__(self, root, id, image, state):
		wx.Panel.__init__(self, root, id)

		self.image = wx.StaticBitmap(self, wx.ID_ANY, image, size = (32, 32))
		self.state = wx.StaticText(self, wx.ID_ANY, state[0])

		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.image, 0, wx.EXPAND, wx.CENTER)
		sizer.Add(self.state, 0, wx.EXPAND, wx.CENTER)
		self.SetSizerAndFit(sizer)



if __name__ == '__main__':
	app = wx.App(0)
	Window(None, wx.ID_ANY, title = 'DMI').Show(True)
	app.MainLoop()