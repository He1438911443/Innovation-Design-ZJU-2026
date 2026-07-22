'''  Gear System Generator
	This program contains three major functions:
	1. modeling of a single gear
	2. create a series of gears with random configuration (size, teeth number, etc) and disperse at different locations, either disconnected or connected
	3. Animation, choose one gear as the driving gear, set the rotation keyframes, all other gears will be driven using expression
	
	The first and second task is inspired by http://www.digitaltutors.com/forum/showthread.php?29583-Python-Gear-Generator
'''

import maya.cmds as cmds
import random as random
import math as math

def createGear(numTeeth, gearHeight, gearRadius, gearThickness, teethHeight):
	''' create one single gear

	numTeeth		: number of teeth for the gear
	gearHeight		: the height of the gear
	gearRadius		: the radius of the gear
	gearThickness	: the thickness of the pipe model
	teethHeight		: the height of each tooth
	'''	
	gear = cmds.polyPipe(sa=numTeeth * 2,h=gearHeight,r=gearRadius,t=gearThickness, name="gear")
	intStartFace = numTeeth *2 * 2
	intEndFace = numTeeth *2 * 3 - 1

	####Deselect all and use for loop to select faces
	cmds.select(clear=True)
	for i in range (intStartFace, intEndFace, 2):
		cmds.select(gear[0] + ".f[%d]" % i, add=True)

	#####Extrude the selected faces
	cmds.polyExtrudeFacet(ltz=teethHeight*.2,lsx=1)
	cmds.polyExtrudeFacet(ltz=teethHeight*.8,lsx=0.5)
	cmds.select(gear[0])
	cmds.addAttr(longName='gearRadius', shortName = 'gr', attributeType='float')
	cmds.addAttr(longName='teeth', shortName = 'tee', attributeType='short')
	cmds.setAttr(gear[0]+'.gr', gearRadius)
	cmds.setAttr(gear[0]+'.tee', numTeeth)
	cmds.delete(constructionHistory=True)
	
	# could consider use polyBevel or polySmooth to make gear model much smoother

def modelGearProc(numTeeth, gearHeight, gearRadius, gearThickness, teethHeight, *pArgs):
	''' start to model a gear '''
	createGear(numTeeth, gearHeight, gearRadius, gearThickness, teethHeight)
	
def cancelProc(*pArgs):
	''' close up the popup window'''
	print("action is cancelled")
	cmds.deleteUI("gearSystem")

def modelRandomGearsProc(numGears, *pArgs):
	''' create a series of gears
	numGears : the number of gears to be created
	'''
	for i in range(numGears):
		numTeeth = random.randint(10,20)
		gearHeight = random.uniform(0.1, 2)
		gearRadius = random.uniform(1, 5)
		gearThickness = random. uniform(0.1, gearRadius)
		teethHeight = random.uniform(gearRadius*.1, gearRadius*0.5)
		createGear(numTeeth, gearHeight, gearRadius, gearThickness, teethHeight)
		
def disperseGearsProc(*pArgs):
	''' put all gears at random position, collision is tested'''
	listOfGears = cmds.ls('gear*', transforms=True)
	posList = []
	count = 0
	for i in listOfGears:
		iteration = 0
		foundNewPos = False
		radius = cmds.getAttr(i+'.gr')
		while (not foundNewPos and iteration < 100):
			foundNewPos = True
			xPos = random.uniform(-40, 40)
			zPos = random.uniform(-40, 40)
			for j in range(count):
				if (math.sqrt((xPos-posList[j][0])*(xPos-posList[j][0])+(zPos-posList[j][1])*(zPos-posList[j][1]))<radius+posList[j][2]):
					foundNewPos = False
					break
			iteration+=1
		if iteration < 100:
			posList.append((xPos,zPos, radius))
			count+=1
			cmds.xform(i, t=[xPos, 0, zPos])
		else:
			print("can't disperse in the range [-10, 10], please extend this area")
			return

def setDrivenAnimationProc(*pArgs):
	''' choose two gears, and create keyframes for the driving gear, make two gears bite into each other. 
	In this funciton, an expression will be created to link the animation of the first gear
	to the second one'''
	listOfGears = cmds.ls('gear*', selection=True, transforms=True)
	numGears = len(listOfGears)
	if numGears != 2:
		print("Please select only two gear each time, the first gear is the driving gear")
		return
	numTeeth1 = cmds.getAttr(listOfGears[0]+".tee")
	numTeeth2 = cmds.getAttr(listOfGears[1]+".tee")
	command = listOfGears[1]+".rotateY=-"+listOfGears[0]+".rotateY*"+ str(numTeeth1)+"/"+str(numTeeth2)
	print(command)
	cmds.expression(name="drvingGearExp", alwaysEvaluate=True, s=command)
	
def gearSystemUI():	
	''' create the User interface for the modelling of gear, disperse, set driving gear, create animation '''
	
	# clear scene
	cmds.select(all = True)
	cmds.delete()

	windowID = 'gearSystem'
	if cmds.window(windowID, exists=True):
		cmds.deleteUI(windowID)

	winWidth = 400;
	winHeight = 400;
	cmds.window(windowID, wh=(winWidth,winHeight))

	# first section: model individual gear
	cmds.columnLayout( adjustableColumn=True )
	numTeethControl = cmds.intSliderGrp(label='number of teeth', minValue=4, maxValue=100, value=10, field=True)
	gearHeightControl = cmds.floatSliderGrp( label='height of gear', minValue=0.1, maxValue=5, value=1, step=0.1, field = True )
	gearRadiusControl = cmds.floatSliderGrp( label='radius of gear', minValue=0.1, maxValue=100, value=3, step=0.1, field = True )
	gearThicknessControl = cmds.floatSliderGrp( label='thickness of gear', minValue=0.1, maxValue=100, value=1, step=0.1, field = True )
	gearTeethHeightControl = cmds.floatSliderGrp( label='teeth height', minValue=0.1, maxValue=10, value=1, step=0.1, field = True )

	cmds.setParent('..')
	cmds.rowColumnLayout(numberOfColumns=2, columnWidth = [(1, winWidth/2.0), (2, winWidth/2.0)], columnAttach= [(1, "both", 10), (2, "both", 10)] )
	cmds.button(label = "Create a gear", command = lambda *args: modelGearProc(cmds.intSliderGrp(numTeethControl, query=True, value=True), cmds.floatSliderGrp(gearHeightControl, query=True, value=True), cmds.floatSliderGrp(gearRadiusControl, query=True, value=True), cmds.floatSliderGrp(gearThicknessControl, query=True, value=True), cmds.floatSliderGrp(gearTeethHeightControl, query=True, value=True)))
	cmds.button(label = "Finished", command = cancelProc)

	cmds.setParent('..')
	
	# second section: randomly create a series of gears, disperse without intersection
	cmds.columnLayout( adjustableColumn=True )
	cmds.separator(style="in", width=10, height = 20)
	numGearsControl = cmds.intSliderGrp(label='number of random gears', minValue=1, maxValue=50, value=10, field=True)
	cmds.button(label = "create series of gears", command = lambda *args: modelRandomGearsProc(cmds.intSliderGrp(numGearsControl, query=True, value=True)))
	cmds.button(label = "disperse all gears", command = disperseGearsProc)
	cmds.showWindow()
	
	# third section: create animation, set driven animation, use the animation of the first selected gear to drive the second gear, make sure you seleted two gears
	cmds.separator(style="in", width=10, height = 20)
	cmds.button(label = "set driven animation", command = setDrivenAnimationProc)
	cmds.separator(style="in", width=10, height = 20)
	cmds.button(label = "Finished", command = cancelProc)
	
# main program, start with the function buildTree()
if __name__ == "__main__":
	gearSystemUI()
