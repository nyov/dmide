import wx
import Image

try:
    import psyco
    psyco.full()
except:
    pass


def irange(start, finish):
	if start == finish:
		return [start]
	if start < finish:
		return range(start, finish + 1)
	if start > finish:
		return range(start, finish - 1, -1)


class Draw(object):
	pen = (0, 0, 0, 255)
	brush = (0, 0, 0, 255)

	def __init__(self, image):
		self.image = image.load()
		self.size = image.size

	def within(self, x, y):
		if x < 0 or y < 0 or x >= self.size[0] or y >= self.size[1]:
			return False
		return True

	def ellipse(self, (start_x, start_y), (end_x, end_y), fill=False, (red, green, blue, alpha)=pen):
		drawpen = (red, green, blue, alpha)
		C = 0

		if start_x > end_x:
			C = start_x
			start_x = end_x
			end_x = C
		if start_y > end_y:
			C = start_y
			start_y = end_y
			end_y = C

		a2, b2 = end_x - start_x, end_y - start_y
		x3 = round(start_x + a2 / 2)
		x4 = start_x + end_x - x3
		y3, y4 = start_y, end_y
		ox2, oy2 = a2 % 2, b2
		a2, b2 = a2 + 1, b2 + 1
		a2sq, b2sq = a2 * a2, b2 * b2
		sq = ox2 * b2sq - (oy2 + b2) * a2sq
		a2sq *= 4
		b2sq *= 4

		def drawbound((x1, y1), (x2, y2)):
			try:
				self.image[x1,y1] = drawpen
			except IndexError:
				pass

			try:
				self.image[x2,y1] = drawpen
			except IndexError:
				pass

			try:
				self.image[x1,y2] = drawpen
			except IndexError:
				pass

			try:
				self.image[x2,y2] = drawpen
			except IndexError:
				pass


		def fillbound((x1, y1), (x2, y2), i):
			for i in xrange(y1, y2+1, 1):
				try:
					self.image[x1,i] = drawpen
				except IndexError:
					pass

				try:
					self.image[x2,i] = drawpen
				except IndexError:
					pass

		while x3 > start_x:
			while sq <= 0:
				if fill:
					fillbound((x3, y3), (x4, y4), C)
				else:
					drawbound((x3, y3), (x4, y4))

				x3 -= 1
				x4 += 1
				sq += (ox2 + 1) * b2sq
				ox2 += 2

			y3 += 1
			y4 -= 1

			if y3 <= y4:
				oy2 -= 2
				sq -= (oy2 + 1) * a2sq

			else:
				y3 -= 1
				y4 += 1
				x3 -= 1
				x4 += 1

			if sq > 0 and x3 >= start_x:
				if not fill:
					x3 += 1
					x4 -= 1

					while True:
						drawbound((x3, y3), (x4, y4))
						oy2 -= 2
						sq -= (oy2 + 1) * a2sq
						y3 += 1
						y4 -= 1
						if y3 > y4:
							y3 -= 1
							y4 += 1
							break

						else:
							if sq > 0:
								continue
							else:
								break

					x3 -= 1
					x4 += 1

				else:
					while True:
						oy2 -= 2
						sq -= (oy2 + 1) * a2sq
						y3 += 1
						y4 -= 1

						if y3 > y4:
							y3 -= 1
							y4 += 1
							break

						if sq > 0:
							continue
						else:
							break

		fillbound((start_x, y3), (end_x, y4), C)

	def line(self, (start_x, start_y), (end_x, end_y), (red, green, blue, alpha)=pen):
		points = []
		orig_start_x = start_x
		orig_start_y = start_y

		if abs(end_y - start_y) > abs(end_x - start_x):
			steep = True
		else:
			steep = False

		if steep:
			start_x, start_y = start_y, start_x
			end_x, end_y = end_y, end_x
		if start_x > end_x:
			start_x, end_x = end_x, start_x
			start_y, end_y = end_y, start_y

		deltax = end_x - start_x
		deltay = abs(end_y - start_y)
		error = deltax / 2
		y = start_y
		if start_y < end_y:
			ystep = 1
		else:
			 ystep = -1
		for x in irange(start_x,end_x):
			if steep:
				points.append((y,x))
			else:
				points.append((x,y))
			error = error - deltay
			if error < 0:
				y = y + ystep
				error = error + deltax

		if points[0] != (orig_start_x, orig_start_y):
			points.reverse()

		for x, y in points:
			self.point((x,y), (red, green, blue, alpha))

	def point(self, (x, y), (red, green, blue, alpha)=pen):
##		if x < 0 or y < 0:
##			return
		if not self.within(x, y):
			return

		#try:
		self.image[x,y] = (red, green, blue, alpha)
		#except IndexError:
		#	return

	def rectangle(self, (start_x, start_y), (end_x, end_y), fill=False, (red, green, blue, alpha)=pen):
		if start_x > end_x:
			start_x, end_x = end_x, start_x
		if start_y > end_y:
			start_y, end_y = end_y, start_y

		if not fill:
			for x in xrange(start_x, end_x+1):
				self.point((x,start_y), (red, green, blue, alpha))
				self.point((x,end_y), (red, green, blue, alpha))
			for y in xrange(start_y, end_y+1):
				self.point((start_x,y), (red, green, blue, alpha))
				self.point((end_x,y), (red, green, blue, alpha))

		else:
			for x in xrange(start_x, end_x+1):
				for y in xrange(start_y, end_y+1):
					self.point((x,y), (red, green, blue, alpha))

	def floodfill(self, (start_x, start_y), (red, green, blue, alpha)):
		if not self.within(start_x, start_y):
			return

		edge = [(start_x, start_y)]
		colour = (red, green, blue, alpha)
		replace = self.image[start_x, start_y]
		self.image[start_x, start_y] = colour

		while edge:
			newedge = []
			for (x, y) in edge:
				for (s, t) in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
					if self.within(s, t) and self.image[s, t] == replace:
						self.image[s, t] = colour
						newedge.append((s, t))
			edge = newedge
