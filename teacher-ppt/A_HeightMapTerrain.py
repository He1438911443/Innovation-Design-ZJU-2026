import sys
sys.path.append("/usr/lib64/python2.7/site-packages/")
import maya.cmds as cmds

imageFile = "/home/xyang/MayaScripts/2017-2018/Image/200px-Heightmap.png"
import os.path
if not os.path.isfile(imageFile):
	print("image doesn't exist")
	exit()

from PIL import Image
img = Image.open(imageFile)
pixels = img.load()

# the main code
cmds.select(all=True)
cmds.delete()

width = img.size[0]
height = img.size[1] 

terrain = cmds.polyPlane( axis=[0,1,0], w=10, h=10, sx=width-1, sy=height-1, ch=False)

# change the vertex position of the plan according tot he terrainData
for i in range(height):
	for j in range(width):
		cmds.move(0, pixels[j,i][0]/255.0, 0, terrain[0]+".vtx["+str(i*width+j)+"]", r=True)
	cmds.refresh(f = True)
