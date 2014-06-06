import math
import os
import re
import spectrum
from PIL import Image
import numpy
from collections import deque
import movieMaker

# THIS CLASS REPRESENTS A CELL ON A GRID
class Cell:
	def __init__(self, xtl, ytl, width, height, img = None):
		self.xtl = xtl
		self.ytl = ytl
		self.width = width
		self.height = height
		self.xc = xtl + (width / 2)
		self.yc = ytl + (width / 2)
		self.level = None

	#THIS FUNCTION GETS THE Z VALUE OF THE MIDDLE OF THE CELL GIVEN A FUNCTION STRING
	def getZ(self, origin, fnStr, h = 1):
		if fnStr == 'cosSurf':
			(z, minZ, maxZ) = cosSurf(self.xc - origin[0], self.yc - origin[1], h)	
		if fnStr == 'sincosSurf':
			(z, minZ, maxZ) = sincosSurf(self.xc - origin[0], self.yc - origin[1], h)	
		return (z, minZ, maxZ)
	#GIVEN THE Z VALUE, NUMBER OF LEVELS, AND Z BOUNDARIES, THIS FUNCTION RETURNS THE LEVEL OF A CELL 
	def getLevel(self, z, levels, minZ, maxZ):
		step = (maxZ - minZ) / float(levels)	
		height = z - minZ
		level = int(height / step)
		self.level = level

# THIS CLASS REPRESENTS THE CARTESIAN PLANE DIVIDED UP INTO SQUARES (CELLS)
class Grid:
	def __init__(self, depth, dim, spectrum, fnStr, origin = 'auto'):
		self.depth = depth
		self.dim = dim
		self.activeCells = deque()
		self.xn = depth
		self.yn = depth
		self.spectrum = spectrum
		self.fnStr = fnStr
		if origin == 'auto':
			self.origin = (dim[0] / 2, dim[1] / 2)
		else:
			self.origin = origin

		self.totalXSideImgs = dim[0] / self.xn
		self.totalYSideImgs = dim[1] / self.yn
		extraXPix = dim[0] % self.totalXSideImgs
		extraYPix = dim[1] % self.totalYSideImgs
		self.xBuf = extraXPix / 2
		self.yBuf = extraYPix / 2
		
		self.img = Image.new('RGB', dim, 'white')
		#print self.spectrum.colors, len(self.spectrum.colors)
		#print [x.name for x in self.spectrum.imgs]

	#GIVEN A HEIGHT (MAGNITUDE COEFFICEINT), THIS FUNCTION FINDS THE CORRECT IMAGE CELLS TO PASTE ONTO THE IMAGE, AND SAVES THEIR IMAGEINFO CLASSES IN A QUEUE TO BE CYCLED THROUGH BY MAKEIMG()
	def getImgCells(self, h):
		for y in range(0, self.totalYSideImgs):
			for x in range(0, self.totalXSideImgs):
				cell = Cell((x * self.xn) + self.xBuf, (y * self.yn) + self.yBuf, self.xn, self.yn)
				(z, minZ, maxZ) = cell.getZ(self.origin, self.fnStr, h)	
				cell.getLevel(z, len(self.spectrum.colors), minZ, maxZ)
				if cell.level != None:
					self.activeCells.appendleft(cell)	
					
	#TAKES ALL THE CELLS FROM THE ACTIVECELLS QUEUE, AND PASTES THE APPROPRIATE IMAGE ONTO THE GRID'S IMAGE FOR EACH ONE	
	def makeImg(self, outputName):
		i = 0
		while len(self.activeCells) > 0:
			cell = self.activeCells.pop()
			tmpImg = Image.open(self.spectrum.lilImgDir + self.spectrum.imgs[int(cell.level)].name)
			tmpImg = tmpImg.resize((self.xn, self.yn), Image.ANTIALIAS)
			self.img.paste(tmpImg, (cell.xtl, cell.ytl))	
		self.img.save(outputName + '.png')
	# SAVES IMAGES IN ORDER IN MOVDIR TO PRODUCE THE FRAMES OF THE MOVIE
	def makeAnim(self, movDir, outputName, frame):
		for i in range(-20, 20):
			self.getImgCells(0.05 * i)
			self.makeImg(movDir + outputName + movieMaker.getFrameStr(frame,4))
			frame += 1
		return frame
			
		
#RETURNS Z-VALUE  AND Z BOUNDS, GIVEN X AND Y VALUES
def cosSurf(x, y, h):
	z = h * math.cos((x**2 + y**2)/(220.0**2))
	return (z, -1, 1)
def sincosSurf(x, y, h):
	z = h * math.cos((x + y)/100.0) * math.sin((x - y)/100.0)
	return (z, -1, 1)

# THIS FUNCTION TAKES AN INPUT DIRECTORY, AND WRITES A NEW DIRECTORY WHERE THE FIRST HALF OF THE IMAGES ARE COPIED IN ORDER FROM THE INPUT DIRECTORY, AND THE SECOND HALF IS IN REVERSE ORDER, CREATING A FORWARD - REVERSE LOOP.
def reverseLoop(inputDir, outputDir):
	movieMaker.wipeDir(outputDir)
	imgs = os.listdir(inputDir)
	imgs.sort()
	frames = (len(imgs) * 2) - 1
	for img in imgs:
		numMatch = re.search('\d+', img)
		num = int(numMatch.group())
		newNum = num + frames 
		newNumStr = movieMaker.getFrameStr(newNum, 4)
		nameStrMatch = re.search('\D+', img)
		nameStr = nameStrMatch.group()
		os.system('cp ' + inputDir + img + ' ' + outputDir + img)
		os.system('cp ' + inputDir + img + ' ' + outputDir + nameStr + newNumStr + '.png')	
	#	print 'cp ' + inputDir + img + ' ' + outputDir + nameStr + newNumStr     + '.png'
		frames -= 2



#THIS FUNCTION WRITES THE INPUT DIRECTORY REPEATED IN ORDER 'LOOPS' NUMBER OF TIMES INTO THE OUTPUT DIRECTORY
def loopify(inputDir, outputDir, loops):
	movieMaker.wipeDir(outputDir)
	imgs = os.listdir(inputDir)
	frames = len(imgs)
	for img in imgs:
		for loop in range(0, loops):
			numMatch = re.search('\d+', img)
			num = int(numMatch.group())
			newNum = num + (loop * frames)
			newNumStr = movieMaker.getFrameStr(newNum, 4)
			nameStrMatch = re.search('\D+', img)
			nameStr = nameStrMatch.group()
			os.system('cp ' + inputDir + img + ' ' + outputDir + nameStr + newNumStr + '.png')
	
def tempMain():
#	ywbSpec = spectrum.Spectrum(5, ((255,255,0), (240,240,240), (0,160,255)), 'emoji/')
#	gwrSpec = spectrum.Spectrum(5, ((0,200,0), (240,240,240), (200,0,0)), 'emoji/')
#	ywbSpec.disp()
#	gwrSpec.disp()
#	spec2d = spectrum.make2dSpectrum(10, ywbSpec, gwrSpec, 'emoji/')
#	spectrum.disp2d(spec2d)
	spec1 = spectrum.Spectrum(10, ((255,255,200),(255,255,100)), 'emoji/')
	spec2 = spectrum.Spectrum(10, ((200,200,255),(100,100,255)), 'emoji/')
	spec3 = spectrum.Spectrum(10, ((255,200,200),(255,100,100)), 'emoji/')
	spec2d = spectrum.make2dSpectrum(10, spec1, spec2, 'emoji/')
	spectrum.disp2d(spec2d)
	
##	g = Grid(8, (1280,720), s, 'cosSurf')
#	g1 = Grid(28, (1280,720), ywbSpec, 'cosSurf')
#	g2 = Grid(28, (1280,720), gwrSpec, 'sincosSurf')
#	movieMaker.wipeDir('movgb0/')
#	movieMaker.wipeDir('movgb1/')
##	g.getImgCells(0.5)
#	frame = g1.makeAnim('movgb0/', 'testsc', frame = 1)
#	frame = g2.makeAnim('movgb1/', 'testc', frame = 1)
#	reverseLoop('movgb0/', 'movgbr0/')
#	reverseLoop('movgb1/', 'movgbr1/')
#	loopify('movgbr0/', 'movgbl0/', 10)
#	loopify('movgbr1/', 'movgbl1/', 10)
#	movieMaker.framesToMpg('testsc','movgbl0/')
#	movieMaker.framesToMpg('testc','movgbl1/')
	
tempMain()
