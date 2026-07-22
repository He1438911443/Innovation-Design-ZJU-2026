import maya.cmds as cmds
import random as rand

def createSatelite(starList, numOfMoons, distance, scaleFactor):
	incr = 360.0 / numOfMoons
	for star in starList:
		eachStarList=[]
		for i in range(1, numOfMoons+1):
			name = cmds.duplicate(star)
			eachStarList.append(name)
			cmds.xform(name, ro=[0, incr*i, 0], r=True, os=True)
			cmds.xform(name, s=[scaleFactor, scaleFactor, scaleFactor],  r=True)
			cmds.xform(name, t=[distance, 0, 0], r=True, os=True)
		for i in range(0, numOfMoons):
			cmds.parent(eachStarList[i], star)
	
def actionProc(winID, numOfMoons, distance, scaleFactor, *pArgs):
	print("Start action")
	cmds.deleteUI(winID)

	cmds.select(all=True)
	cmds.delete()	
	Sun = cmds.sphere(name='sun')
	createSatelite([Sun[0]], numOfMoons, distance, scaleFactor)
	
def cancelProc(winID, *pArgs):
	print("action is cancelled")
	cmds.deleteUI(winID)

def createUI():	
	winID = cmds.window(title="Satelite System", resizeToFitChildren=True ) #widthHeight=(318, 200),
	cmds.columnLayout( adjustableColumn=True )
	
	cmds.frameLayout(borderVisible=True, labelVisible=False)
	filename= "D:\\YangXiaosong\\Research\\Projects\\2025\\ChinaTrip\\July\\ZhejiangUniversity\\TAP\\2_solarsystem.jpg"
	if cmds.file(filename, query=True, exists=True):
		cmds.image(image=filename, width=318, height=114)
	else:
		print("picture doesn't exist or path is not right")
	cmds.setParent("..")
	
	cmds.frameLayout(borderVisible=True, label="Control Parameters")
	cmds.columnLayout( adjustableColumn=True )
	numMoonsControl = cmds.intSliderGrp(label='number of moons', minValue=4, maxValue=20, value=12, field=True)
	distControl = cmds.intSliderGrp(label='Distance from parent to child', minValue=5, maxValue=40, value=20, field=True)
	resizeControl = cmds.floatSliderGrp( columnWidth3=[300,200,100],label='size ratio of child to parent star', minValue=0.1, maxValue=1, value=0.2, step=0.01, field = True )
	cmds.setParent("..")
	cmds.setParent("..")
	cmds.separator()
	cmds.frameLayout(borderVisible=True, labelVisible=False)
	cmds.rowLayout(numberOfColumns=2, columnWidth2=[200, 200], columnAttach=[(1, 'both', 10), (2, 'both', 10)])
	cmds.button(label = "OK", command = lambda *args: actionProc(winID, cmds.intSliderGrp(numMoonsControl, query=True, value=True), cmds.intSliderGrp(distControl, query=True, value=True), cmds.floatSliderGrp(resizeControl, query=True, value=True)))
	cmds.button(label = "Cancel", command = lambda *args: cancelProc(winID))
	cmds.setParent("..")
	cmds.setParent("..")
	cmds.showWindow(winID)

if __name__ == "__main__":
	createUI()
