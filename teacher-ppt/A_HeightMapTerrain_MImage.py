import maya.OpenMaya as om
import maya.cmds as cmds

imageFile = "D:\\YangXiaosong\\Research\\Projects\\2025\\ChinaTrip\\July\\ZhejiangUniversity\\TAP\\A_200px-Heightmap.png"
import os.path
if not os.path.isfile(imageFile):
	print("image doesn't exist")
	exit()

img = MayaImage(imageFile)
width = img.width
height = img.height

# the main code
cmds.select(all=True)
cmds.delete()

terrain = cmds.polyPlane( axis=[0,1,0], w=10, h=10, sx=width-1, sy=height-1, ch=False)

# change the vertex position of the plan according tot he terrainData
for i in range(height):
	for j in range(width):
		r,g,b,a=img.getPixel(i,j)
		cmds.move(0, r/255.0, 0, terrain[0]+".vtx["+str(i*width+j)+"]", r=True)
	cmds.refresh(f = True)
