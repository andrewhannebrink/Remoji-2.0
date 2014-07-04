#!/usr/bin/python

import os
import sys
import getopt
import math
from PIL import Image
import ImageDraw
import movieMaker
from multiprocessing import Process, Pool
import time
import preProc

#THIS FUNCITON RETURNS THE AVERAGE INTENSITY OF THE SUPPLIED COLOR STRING WITHIN THE IMAGE 
def getAvgColor(imageFile, colorStr, skip = 5):
	imgPixels = imageFile.load()
	xi, yi = imageFile.size
	intensityList = []
	if colorStr is 'r':
		for x in range(0, xi / skip):
			for y in range(0, yi / skip):
				if len(imgPixels[x,y]) == 2:
					break
				(r,g,b) = imgPixels[x*skip, y*skip]
				intensityList.append(r)
	if colorStr is 'g':
		for x in range(0, xi / skip):
			for y in range(0, yi / skip):
				if len(imgPixels[x*skip,y*skip]) == 2:
					break
				(r,g,b) = imgPixels[x*skip, y*skip]
				intensityList.append(g)
	if colorStr is 'b':
		for x in range(0, xi / skip):
			for y in range(0, yi / skip):
				if len(imgPixels[x*skip,y*skip]) == 2:
					break
				(r,g,b) = imgPixels[x*skip, y*skip]
				intensityList.append(b)
	avg = sum(intensityList) / sum( [1 for n in intensityList] )
	return avg
				

#THIS FUNCTION RETURNS THE AVERAGE RED, GREEN, AND BLUE VALUES OF AN IMAGE IN A LIST
def getAvgRGB(imageFile):
	r = getAvgColor(imageFile, 'r')
	g = getAvgColor(imageFile, 'g')
	b = getAvgColor(imageFile, 'b')
	return (r, g, b)

#THIS FUNCTION REMOVES TRANSPARENCY IN THE IMG LIBRARY BY TAKING EVERY IMAGE IN THE GIVEN DIRECTORY, FINDS PIXELS WITH AN ALPHA VALUE OF 0, AND CONVERTS THE RGBA VALUES TO (255,255,255) FOR EVERY ONE OF THOSE PIXELS, AND SAVES THE IMAGES TO THEIR ORIGINAL NAMES AS RGB PNGS RATHER THAN RGBA PNGS
def changeLittleImgs(dbDir):
	littleImgNames = os.listdir(dbDir)
	i = 0
	for imgName in littleImgNames:
		i += 1
		print i, imgName
		tempImgFile = Image.open(dbDir + imgName).convert('RGBA')
		x, y = tempImgFile.size
		tempPix = tempImgFile.load()
		for xi in range(0, x):
			for yi in range(0,y):
				(r,g,b,a) = tempPix[xi,yi]
				if a == 0:
					tempPix[xi,yi] = (255,255,255,1)
		tempImgFile.convert('RGB')
		tempImgFile.save(dbDir + imgName)

#THIS CLASS HOLDS INFORMATION ABOUT AN IMAGE WITH A GIVEN NAME WITHOUT LEAVING THE IMAGE FILE OPEN
class ImageInfo:
	def __init__(self, imgName, imageFile):
		self.name = imgName
		self.width, self.height = imageFile.size
		self.avgRGB = getAvgRGB(imageFile)
		self.mult = 1
	def disp(self):
		print '----------------------'
		print 'name: ', self.name
		print 'width: ', self.width
		print 'height: ', self.height
		print 'avgRGB: ', self.avgRGB
		print 'mult: ', self.mult
		print '----------------------'

#MAKES AND RETURNS A LIST OF IMAGEINFO CLASSES OF EVERY EMOJI IN THE 'IMAGES/' DIRECTORY
def getLittleImgs(directory):
	littleImgs = []
	littleImgNames = os.listdir(directory)
	for imgName in littleImgNames:
		imgFile = Image.open(directory + imgName).convert('RGB')
		try:
			imgInfo = ImageInfo(imgName, imgFile)
			littleImgs.append(imgInfo)
		except:
			print 'skipping image: ' + imgName
	return littleImgs

#DO LEAST SQUARES APPROXIMATION TO FIND THE IMAGE THAT HAS THE CLOSEST COLOR TO ORIGTILE
def getClosestImg(origTile, littleImgs, colorMap, lilImgDir, oneColor = False):
	ogAvgRGB = ''
	if oneColor == True:
		ogAvgRGB = preProc.compressColor(origTile)
	else:
		ogAvgRGB = preProc.compressColor(origTile.avgRGB)
	#print colorMap
	#SET MINSQUAREDIS TO JUST ABOVE THE MAXIMUM SQUARE DISTANCE OF ANY TWO IMAGES
	minSquareDis = 3*(266*266)
	closestImg = None
	if colorMap != None:
		if (ogAvgRGB, lilImgDir) in colorMap:
			#print 'found object in color map'
			return colorMap[(ogAvgRGB, lilImgDir)]
		else:
			for littleImg in littleImgs:
				if oneColor == False:
					dis = (littleImg.avgRGB[0] - origTile.avgRGB[0])* (littleImg.avgRGB[0] - origTile.avgRGB[0]) + (littleImg.avgRGB[1] - origTile.avgRGB[1])*(littleImg.avgRGB[1] - origTile.avgRGB[1]) + (littleImg.avgRGB[2] - origTile.avgRGB[2])* (littleImg.avgRGB[2] - origTile.avgRGB[2])
				else:
					dis = (littleImg.avgRGB[0] - ogAvgRGB[0])* (littleImg.avgRGB[0] - ogAvgRGB[0]) + (littleImg.avgRGB[1] - ogAvgRGB[1])*(littleImg.avgRGB[1] - ogAvgRGB[1]) + (littleImg.avgRGB[2] - ogAvgRGB[2])* (littleImg.avgRGB[2] - ogAvgRGB[2])
				if dis < minSquareDis:
					minSquareDis = dis
					closestImg = littleImg.name
			#print 'adding object to colormap'
			colorMap[(ogAvgRGB, lilImgDir)] = closestImg
		return closestImg
	# IF COLORMAP == NONE, DONT KEEP A COLOR MAP DURING PIXEL ITERATION
	else:
		for littleImg in littleImgs:
			if oneColor == False:
				dis = (littleImg.avgRGB[0] - origTile.avgRGB[0])* (littleImg.avgRGB[0] - origTile.avgRGB[0]) + (littleImg.avgRGB[1] - origTile.avgRGB[1])*(littleImg.avgRGB[1] - origTile.avgRGB[1]) + (littleImg.avgRGB[2] - origTile.avgRGB[2])* (littleImg.avgRGB[2] - origTile.avgRGB[2])
			else:
				dis = (littleImg.avgRGB[0] - ogAvgRGB[0])* (littleImg.avgRGB[0] - ogAvgRGB[0]) + (littleImg.avgRGB[1] - ogAvgRGB[1])*(littleImg.avgRGB[1] - ogAvgRGB[1]) + (littleImg.avgRGB[2] - ogAvgRGB[2])* (littleImg.avgRGB[2] - ogAvgRGB[2])
			if dis < minSquareDis:
				minSquareDis = dis
				closestImg = littleImg.name
		return closestImg
			

#THIS FUNCTION FINDS THE SCALE AND IMAGE OF THE TILES IN NEWTILES
def getNewTiles(origTiles, littleImgs, colorMap, lilImgDir):
	newTiles = []
	for y in range(0, len(origTiles)):
		newTiles.append([])
		for x in range(0, len(origTiles[0])):
			newTile = getClosestImg(origTiles[y][x], littleImgs, colorMap, lilImgDir)
			newTiles[y].append(newTile)
	return newTiles
		
#THIS FUNCTION CONSTRUCTS AND RETURNS THE FINAL MOSAIC IMAGE
def getFinalImg(xt, yt, xBuf, yBuf, newTiles, directory):
	finalImg = Image.new('RGB', (int(xt), int(yt)), (0,0,0))
	tileWidth = int(xt / len(newTiles[0]))
	tileHeight = int(yt / len(newTiles))
	#print 'newTiles:', newTiles
	for y in range(0, len(newTiles)):
		for x in range(0, len(newTiles[0])):
			newImg = Image.open(directory + newTiles[y][x]).convert('RGB')
			newImg = newImg.resize((tileWidth, tileHeight), Image.ANTIALIAS)
			finalImg.paste(newImg, (x*tileWidth + xBuf, y*tileHeight + yBuf))	
	return finalImg	

#GIVEN THE ORIGINAL IMAGE, SCALE, AND DEPTH (PIXEL WIDTH OF SINGLE MOSAIC TILE), THIS FUNCTION BUILDS AND SAVES THE FINAL IMAGE FROM START TO FINISH
def makeMosaic(targetImgName, scale, depth, littleImgs, outputName, colorMap, lilImgDir):
	print 'started: ' + outputName
#	if direc is 'emoji/':
#		targetImg = Image.open('emoji/' + targetImgName).convert('RGB')
#	else:
	targetImg = Image.open(targetImgName).convert('RGB')
	if scale == 'autoScale':
		[xt, yt] = [1920, 1080]
	else:
		[xt, yt] = [ l * scale for l in targetImg.size ] 
	[xi, yi] = targetImg.size
	xt = int(xt)
	yt = int(yt)
	xn = depth
	totalXSideImgs = int(xt) / int(xn)
	yn = xn
	totalYSideImgs = int(yt) / int(yn)
	extraXPix = xt % totalXSideImgs
	extraYPix = yt % totalYSideImgs
	#XBUF AND YBUF ARE THE NUMBER OF PIXELS NECESSARY ON EITHER SIDE FOR CENTERING THE IMAGE
	xBuf = extraXPix / 2
	yBuf = extraYPix / 2
	#INFLATE TARGET IMG TO FINAL SIZE
	if scale == 'autoScale':
		bigTargetImg = targetImg.resize((1920,1080), Image.ANTIALIAS)
	else:
		bigTargetImg = targetImg.resize(((int(xi*scale)), int(yi*scale)), Image.ANTIALIAS)
	#BREAK TARGET IMG INTO SMALLER PIECES THAT WILL BE REPLACED BY ONE EMOJI AND PUT THEM INTO A LIST OF LISTS CORRESPONDING TO TILE POSITION
	origTiles = []
	for y in range(0, totalYSideImgs):
		origTiles.append([])
		for x in range(0, totalXSideImgs):
			tempImg = bigTargetImg.crop((x*xn + xBuf, y*yn + yBuf, (x+1)*xn - 1 + xBuf, (y+1)*yn - 1 + yBuf))
			origTiles[y].append(ImageInfo('tempTile', tempImg))
	newTiles = getNewTiles(origTiles, littleImgs, colorMap, lilImgDir)
	#MAKE NEW FRAME AND FILL IT OUT WITH TILES FORM NEWTILES. THIS FUNCTION RETURNS THE FINAL IMAGE
	finalImg = getFinalImg(xt, yt, xBuf, yBuf, newTiles, lilImgDir)
	finalImg.save(outputName)
	print 'finished: ' + outputName
	return
	
#ANIMATION OF ONE TARGET IMAGE WITH 1-9 RESOLUTION FRAMES SAVED AS <FRAMENUM>.PNG, <FRAMENUM + 1>.PNG, <FRAMENUM + 2>.PNG IN THE FRAMES DIRECTORY...
def blurAnim(targetImgName, scale, startingFrameNum, littleImgs, directoryName):
	for depth in range(1,9):
		outputName = directoryName + '/' + str(startingFrameNum) + '.png'	
		makeMosaic(targetImgName, scale, depth, littleImgs, outputName)
		startingFrameNum += 1
	return

			
#THIS FUNCTION CALLS BLUR ANIM FOR EVERY IMAGE IN LITTLEIMGS
def getAllBlurAnims(littleImgs, scale):
	frameNum = 0
	for img in littleImgs:
		targetImgName = img.name
		blurAnim(targetImgName, scale, frameNum, littleImgs)
		frameNum += 9
	return

#CONVERTS GIFFRAMES TO IMAGE FILES OF THE NAME <NAMESTR>0.PNG, <NAMESTR>1.PNG IN THE RELATIVE 'FRAMES/' DIRECTORY. IF AUTO IS TRUE, THIS FUNCTION AUTOMATICALLY FLOPS THE IMAGE TO FIT THE 16:9 ASPECT RATIO
def convertGif(inputGifName, framesDB, auto = False):
	longInputGifName = 'gifs/' + inputGifName
	totFrames = movieMaker.getTotFrames(longInputGifName)
	if auto is False:
		for i in range(0, totFrames):
			os.system('convert ' + longInputGifName + '.gif[' + str(i) + '] ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + '.png')
	else:
		for i in range(0, totFrames):
			os.system('convert ' + longInputGifName + '.gif[' + str(i) + '] ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + 'l.png')
			os.system('convert -flop ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + 'l.png ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + 'r.png')
			os.system('convert +append ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + 'l.png ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + 'r.png ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + '.png')
			os.system('rm ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + 'l.png')
			os.system('rm ' + framesDB + inputGifName + movieMaker.getFrameStr(i,3) + 'r.png')
			unCroppedImg = Image.open(framesDB + inputGifName + movieMaker.getFrameStr(i,3) + '.png').convert('RGB')
			[xi, yi] = unCroppedImg.size
			xn = int( (yi*16) / 9.0 )
			xBuf = (xi - xn) / 2
			croppedImg = unCroppedImg.crop((xBuf, 0, xi - xBuf - 1, yi))	
			croppedImg.save(framesDB + inputGifName + movieMaker.getFrameStr(i,3) + '.png')
	return totFrames	

#THIS FUNCTION EXTRACTS THE GIF FRAMES, MAKES, AND SAVES MOSAICS OF EACH FRAME AT THE GIVEN SCALE AND DEPTH INTO THE OUTPUTNAMESTR PATH 
def makeLoopsFromFrames(inputDirectory, scale, littleImgs, outputNameStr):
	inputFrameNames = os.listdir(inputDirectory)
	inputFrameNames.sort()
	pool = Pool(processes = 4)
	for i in range(0, len(inputFrameNames)):
		d = 0
		for depthPix in range(6,46,2):
			dStr = movieMaker.getFrameStr(d, 2) + '_'
			if scale is 'autoScale':
				pool.apply_async(makeMosaic, [inputDirectory + '/' + inputFrameNames[i], scale, depthPix, littleImgs, outputNameStr + dStr + movieMaker.getFrameStr(i,3) + '.png', 'arbitraryDir/'])
			d += 1
	pool.close()
	pool.join()
#			else:
#				targetImg = Image.open(inputDirectory + '/' + inputFrameNames[i]).convert('RGB')
#				targetImg.save(outputNameStr + movieMaker.getFrameStr(i,3) + '.png')
#				p = Process(target = makeMosaic, args = (outputNameStr + movieMaker.getFrameStr(i,3) + '.png', scale, depthPix, littleImgs, outputNameStr + movieMaker.getFrameStr(i,3) + '.png', 'arbitraryDir/'))
#				p.start()
		#makeMosaic(outputNameStr + movieMaker.getFrameStr(i,3) + '.png', scale, depth, littleImgs, outputNameStr + movieMaker.getFrameStr(i,3) + '.png', 'pokemon/')
	#p.join()
#	print 'finished loop with depth =', depth

def usage():
	print ''
	print '   $ python remoji.py -c <little image directory>'
	print ''
	print '   $ python remoji.py -s <starting image name> <little image directory> <output name> <scale (ratio)> <depth (pixels)>'
	print ''
	print '   $ python remoji.py -i <starting gif name> <little image directory> <frame directory> <mosaic directory> <autoScale (optional)>'
	print ''
	print '   $ python -a <movie directory> <instructions file> <output name>'
	print ''

#MAIN FUNCTION
def main(argv = None):
	if argv is None:
		argv = sys.argv
	try:
		singleBool = False
		initiateFramesBool = False
		animateBool = False
		changeColorBool = False
		preProcBool = False
		loadBool = False
		mapBool = False
		joinBool = False
		opts, args = getopt.getopt(sys.argv[1:], 'hcsiapmlj')
		for opt, arg in opts:
			if opt == '-h':
				usage()
			if opt == '-c':
				print 'Adjusting colors of database directory images...'
				changeColorBool = True
			if opt == '-s':
				singleBool = True
				print 'Making mosaic of single image...'
			if opt == '-i':
				initiateFramesBool = True
				print 'Turning frames into mosaics of various resolutions...'
			if opt == '-a':
				animateBool = True
				print 'Making mpeg animation from instructions file...'
			if opt == '-m':
				mapBool = True
				print 'Making complete colorMap and writing it to a text file...'
			if opt == '-p':
				preProcBool = True
				print 'Making directory of frames by preprocessing instructions file...'
			if opt == '-l':
				loadBool = True
				print 'Making directory of frames by preprocessing instructions file (colorMap file provided)...'
			if opt == '-j':
				joinBool = True
				print 'Concatenating movie directories...'

#ARGS FOR INITIATING ANIMATION FRAMES
		if changeColorBool is True:
			dbDir = args[0]
			changeLittleImgs(dbDir)
			
#ARGS FOR SINGLE IMAGE
		if singleBool is True:
			targetImgName = args[0]
			littleImgDir = args[1]
			outputName = args[2]
			scale = float(args[3])
			depth = int(args[4])
			colorMap = {}

			littleImgs = getLittleImgs(littleImgDir)

			makeMosaic(targetImgName, scale, depth, littleImgs, outputName, colorMap, littleImgDir)
			print outputName + ' saved'

		if initiateFramesBool is True:
			startTime = time.time()
			name = args[0]			#i.e. 'squares/'
			littleImgDir = args[1]		#i.e. 'emoji/'
			framesDB = args[2]		#i.e. 'frames/'
			dbDir = args[3]			#i.e. 'mos/'
			littleImgs = getLittleImgs(littleImgDir)
			movieMaker.wipeDir(framesDB)
			movieMaker.wipeDir(dbDir)
			if args[4] != 'autoScale':
				scale = float(args[4])
				convertGif(name, framesDB)
			else:
				scale = 'autoScale'
				convertGif(name, framesDB, auto = True)
			makeLoopsFromFrames(framesDB, scale, littleImgs, dbDir + name)
			print time.time() - startTime, 'seconds'
		
# WHEN THE -A OPTION IS SELECTED, OUTPUT FRAMES IN MOVDIR FOR FINAL ANIMATION
		if animateBool is True:
#DO NOT DELETE DIS STUFF EYYYY 
			movDir = args[0]		#i.e. 'mov/'
			instructionsFile = args[1]	#i.e. 'instruct.txt'
			outputName = args[2]		#i.e. 'animation'
			
			movieMaker.wipeDir(movDir)

			movieMaker.readFile(instructionsFile, movDir, outputName)
			movieMaker.framesToMpg(outputName, movDir)
#			movieMaker.wipeDir('mov/')
#			trans = movieMaker.boxTrans('mmos/', 'hmos/', 'trans', 'mov/', 17, 0, 1, 1, 4, 15)
#			trans = movieMaker.boxTrans('hmos/', 'limos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 5, 6)
#			trans = movieMaker.boxTrans('limos/', 'wmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 6, 7)
#			trans = movieMaker.boxTrans('wmos/', 'catmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 7, 8)
#			trans = movieMaker.boxTrans('catmos/', 'cmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 8, 9)
#			trans = movieMaker.boxTrans('cmos/', 'pmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 9, 1)
#			trans = movieMaker.boxTrans('pmos/', 'mmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 9, 1)
#			trans = movieMaker.boxTrans('mmos/', 'hmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 1, 4, 5)
#			trans = movieMaker.boxTrans('hmos/', 'limos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 5, 6)
#			trans = movieMaker.boxTrans('limos/', 'wmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 6, 7)
#			trans = movieMaker.boxTrans('wmos/', 'catmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 7, 8)
#			trans = movieMaker.boxTrans('catmos/', 'cmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 8, 9)
#			trans = movieMaker.boxTrans('cmos/', 'pmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 9, 1)
#			trans = movieMaker.boxTrans('pmos/', 'mmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 9, 1)
#			trans = movieMaker.boxTrans('mmos/', 'hmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 4, 5)
#			trans = movieMaker.boxTrans('hmos/', 'limos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 5, 6)
#			trans = movieMaker.boxTrans('limos/', 'wmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 6, 7)
#			trans = movieMaker.boxTrans('wmos/', 'catmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 7, 8)
#			trans = movieMaker.boxTrans('catmos/', 'cmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 8, 9)
#			trans = movieMaker.boxTrans('cmos/', 'pmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 9, 1)
#			trans= movieMaker.boxTrans('pmos/', 'mmos/', 'trans', 'mov/', 17, trans.loopFrame, trans.frame, 1, 9, 1)
#			movieMaker.framesToMpg('trans', 'mov/')

		if mapBool is True:
			startTime = time.time()
			lilImgDir = args[0]
			mapFile = args[1]
			a = ''
			while((a != 'y') and (a != 'n')):
				a = raw_input('Overwrite file at ' + mapFile + ' if it exists? [y/n]')	
			if a == 'y':
				print 'Directory size: ', str(len(os.listdir(lilImgDir))) , 'images'
				preProc.buildColorMap(lilImgDir, mapFile)
			endTime = time.time()
			print time.time() - startTime, 'seconds'

		if preProcBool is True:
			startTime = time.time()
			movDir = args[0]		#i.e. 'mov/'
			instructionsFile = args[1]	#i.e. 'instruct.txt'
			outputName = args[2]		#i.e. 'animation'
			if loadBool is True:
				mapFile = args[3]
				colorMap = preProc.loadMapFile(mapFile)
				preProc.readFile(instructionsFile, movDir, outputName, colorMap)
			else:
				preProc.readFile(instructionsFile, movDir, outputName)
			print time.time() - startTime, 'seconds'

		if joinBool is True:
			movDirs = args[:-1]
			opMovDir = args[-1]
			print movDirs, opMovDir
			movieMaker.joinMovDirs(movDirs, opMovDir)
			

	except getopt.error as err:
		print str(err)
		sys.exit(-1)

if __name__ == '__main__':
	sys.exit(main())


