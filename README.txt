Andrew Hannebrink 

Remoji is a Python-based command line photo-mosaic gif re-animator and image synthesizer with several features and options for image modification and performance optimization. Remoji utilizes PIL's Image module, the ImageDraw module, the multiprocessing module, ImageMagick, and ffmpeg for procedural image/frame modification, pixel-by-pixel RGB-value analysis, RGB-value averaging, color compression, RGB-value least-squares analysis, image segment replacement, 1D and 2D gradient creation, image synthesis parallelization, and HD mp4 video compression. This read-me will cover the current command line options, how they work, and measures that were taken to make them run faster. This project is a work in progress so this read-me may not be entirely up-to-date all the time, but hopefully this should help people to start to understand how this code works. Also, the code itself is generally pretty well commented, and I would encourage anyone interested in the programming side of this project to check out my actual Python source files in this repository 

Call Remoji from the command line as such: 

$ python remoji.py [-scmpl] 

Keep in mind that remoji.py must be in the same directory as the other python files in this package in order to work. This includes movieMaker.py, preProc.py, and spectrum.py. 

OPTIONS 

	-s	SYNTAX: <starting image name> <little image directory> <output name> <scale (ratio)> <depth (pixels)> 

		This option takes a starting image, a directory name followed by "/", a name to output the image to, a scale, and a depth (tile resolution in pixels) to create a single photo-mosaic image from the image library specified by <little image directory>. For instance, the command: 

" $ python remoji.py -s emoji/1f42a.png emoji/ camel.png 10 40" 

Would make a photo-mosaic of the image at the path "emoji/1f42a.png" using the images in the directory "emoji/", and save it as "camel.png" in the current directory. Also, the final image will be ten times the size, and comprised of miniature images that are forty pixels wide. This is accomplished by first calculating the average RGB-value of every image in the "emoji/" directory. The program saves this this information in a list of ImageInfo objects called littleImgs, a light-weight class I defined for holding an image's name, dimensions, and average RGB-value. When an ImageInfo object is initialized, it calls getAvgRGB() on the image that was used to initialize it. GetAvgRGB() calculates the average RGB-value of the entire image, and therefore must access every pixel of the image that it's called on. So, while storing an ImageInfo object is inexpensive, initializing one can be CPU-heavy for a large image. Then, the program cuts the image "emoji/1f42a.png" into tiles that are 40x40 pixels large, calculating the average RGB-value of each tile. Then, it calculates which image in littleImg's average RGB-value vector has the shortest distance to the average RGB-value of each tile, and creates a new image, placing images from littleImgs onto it with the correct locations and scales. Most of the heavy lifting is done by the makeMosaic() method, which calls a wide range of methods. 


	-c	SYNTAX: <little image directory> 
	 
	This option takes the little image directory, and re-saves all the images after converting their transparent pixels to solid white. This prevents PIL from occasionally converting transparent pixels to black, which can interfere with output image quality in some circumstances. So, running "$ python remoji.py -c emoji/" will over-write "emoji/" with images containing no transparent pixels, but white pixels in their place. 

	 
	-p	SYNTAX: <output movie directory> <instructions file> <output frames name> 
		OR: -p -l <output movie directory> <instructions file> <output frames name> <pickled color map file> 
	 
	This option allows you to turn segments and series of GIFs into photo-mosaic animations with custom commands to alter image resolutions, color schemes, little image directories, and speed gradually or suddenly throughout the animation. These commands are handled by the contents of the instructions file, a user-created text file that contains detailed animation instructions. The format of an instruction file "ins/pp.txt" is as follows: 



Sequence sq1 (mos) 
       square animalmini2/ 
               10      1       19      4 
       square animalmini2/ 
               20      1       4 
       square sketch/ 
               10      1       4       19 
endSeq 

Sequence neg1 (spec) emoji/ 
        (255, 255, 255) (150, 200, 255) (150, 150 255) 8 
                neg 
                        10      1       25      0 
                        20      1       0 
                        10      1       0       25 
        (255, 150, 150) (255, 255, 255) (150, 150, 255) 8 
endSeq 

Sequence neg2 (spec) emoji/ 
        (255, 150, 150) (255, 255, 255) (150, 150, 255) 8 
                neg 
                        10      1       0 
                        10      1       0       0 
                        20      1       0       250 
        (255, 200, 200) (255, 255, 255) (255, 150, 255) 8 
endSeq 

makeAnim 
	sq1 
	neg1 
	neg1 
	neg2 
	sq1 
	neg1 
	neg1 
	neg2 
endAnim 

In the above file, three Sequence classes are established by the names of sq1, neg1, and neg2. The first Sequence, sq1, will run in mosaic mode, as specified by the "(mos)" option. As seen in the next two lines, the syntax works like this: the first ten frames of sq1 will come from "square.gif", be comprised of images from the directory "animalmini2/", go at a speed of 1 frame/image, start with a resolution of 19 pixels, and gradually transition to a resolution of 4 pixels throughout the length of those ten frames. In the next two lines we see that the next 20 frames will also come from the next 20 frames of square.gif, looping to the beginning of square.gif if we run out of frames. This will also be at a speed of 1 frame/image. Notice that the ending resolution is not specified. So, it will have a starting and ending resolution of four pixels. Finally, the last ten frames will be the next ten frames of square.gif made up of images from the directory, "sketch/", with starting and ending resolutions of four and nineteen pixels respectively. 

So, sq1 was produced with "mosaic" mode, as indicated by the "(mos)" option. However, neg1 is initialized with "spectrum" mode, as indicated by the (spec) option. In this mode, a directory of miniature tile images is specified on the same line immediately after the (spec) option. In this case it is "emoji/". Then, with the absence of the little image directory being specified next to the gif name (neg) each time, the syntax works entirely the same, with the exception of the color wrapper lines. From one color wrapper line to the next, the gradient of colors allowed for each frame gradually changes. So starting at the first frame of neg1, only images closely matching the color gradient linearly ranging from each of the three RGB-values specified are allowed, with 8 steps in between each color. In this case, it is a gradient first taking 8 steps from (255, 255, 255) to (150, 200, 255), and then 8 more steps from (150, 200, 255) to (150, 150 255). Then, over the next 40 frames, the gradient of colors allowed will gradually change to the gradient specified by the line: (255, 150, 150) (255, 255, 255) (150, 150, 255) 8. This method of gradual color change uses a gradient of gradients if you will. A function in spectrum.py called make2dSpec creates this data structure. Notice that all Sequences must end with an endSeq marker. Also, like python, the lines are tab-dependent, so it is important that you format your files like the above example (USING TABS! NOT SPACES!). 

When re-animating the gifs, it cuts the gif in two, mirroring it on itself vertically at a resolution of 720 x 1280. These are large, high definition images, and there are a lot of them for most animations. Also, pixel by pixel average color calculation eats up CPU and is time consuming. So, I've added a number of features for expediting this photo-mosaic synthesis process for animations. First, as the per-processor reads the instruction file, it creates a map of unique frames. A frame's identity in this case is defined by the tuple (gifName, littleImgDir, frameNumber, resolution), where frameNumber refers to the which number frame from the supplied gif is being used, and the resolution refers to the pixel width of the miniature tile images. When a frame's identity is calculated and then not found in frameMap, it is added to frameMap, mapping to the image path string in the "unique/" directory. Also, it is saved in the "unique/" directory to that path. However, if the frame is found in frameMap, instead of recalculating the frame, the frame is taken directly from the image path specified by frameMap[frameIdentity tuple]. This saves the program from wasting time re-calculating identical frames. 
 
Similarly, specMap maps gradients defined by the tuple (pivot colors, levels per pivot color, little image directory). These identities map to the directories containing the images allowed by these gradients, preventing the calculation of duplicate Spectrum classes. 

Also very similarly, gifMap maps gif names to GifInfo classes, preventing unnecessary executions of the method remoji.convertGif() method, which calls the movieMaker.getTotFrames() method, which makes a system call to ImageMagick every time a new gif is detected. If an already-used gif is detected, the program does not have to make that time-consuming system call. 

The last map I use is colorMap. When readFile() begins, it is either passed an empty colorMap or one provided by the user with the -l (load map) option. colorMap is a dict formatted as such: { ( (r, g, b), littleImgDir)  : image-path }, where (r, g, b) is where (r, g, b) is a tuple containing an RGB-value, littleImgDir is a directory of an image, and image-path is the file path to the image who's average color most closely matches the color specified by (r, g, b) in littleImgDir. To prevent this map from getting to large, I compress every average color found to a 64-bit color. This makes the average end size of colorMap 64 times smaller. Note that this does not change the total number of possible colors in the final image, as only colors from the original image are compressed, but not the colors in the little image directory. 

	-l (only used with -p)	SYNTAX: -p -l <output movie directory> <instructions file> <output frames name> <pickled color-map file> 

To pass a pickled dict of a pre-calculated colorMap, use the -l (load map) option. When the -l option is on, the -p option takes an extra argument. This argument is the file path to which the pickled file will be saved. To save map construction time, you can make a map in advanced with the -m (map) option, as discussed below. 

	-m	SYNTAX: <little image directory> <output file name> 
	 
This option creates a Python dict structured like the colorMap variable discussed above, and saves it in a pickled file to be used with the -l (load map) option. The map it creates contains { ( ( (r, g, b), <little image directory>) : image path } for every possible 64-bit RGB-value.
