#  L-System Generator
#
#  inspired by Janne Kaasalainen's work from http://blog.studioe18.com/69/visualizing-l-systems/
#  
import maya.cmds as cmds
import math as math


def addRule(ruleDict, replaceStr, newStr ):
	''' add a new rule to the ruleDict

	ruleDict		: the dictionary holding the rules
	replaceStr		: the old character to be replaced
	newStr			: the new string replacing the old one
	'''
	ruleDict[ replaceStr ] = newStr

def iterate(baseString, numIterations, ruleDict):
	''' following the rules, replace old characters with new ones

	baseString		: start string
	numIterations	: how many times the rules will be used
	ruleDict		: the dictionary holding the rules
	return			: return the final expanded string
	'''
	while numIterations > 0:
		replaced = ""
		for i in baseString:
			replaced = replaced + ruleDict.get(i,i)
		baseString = replaced
		numIterations-=1
	return baseString

def createBranch(startPoint, length, angle):
	''' create a cylinder for each branch

	startPoint	: startPoint, base point for the new cylinder
	length		: step size for growing
	angle		: the rotation angle for branching, used for calculating the axis of the cylinder
	return		: return the created object
	'''
	radians = angle * math.pi /180.0
	branch = cmds.polyCylinder(axis=[math.sin(radians), math.cos(radians), 0.0], r=length/5.0, height=length)
	cmds.move(startPoint[0] + 0.5*length*math.sin(radians), startPoint[1] + 0.5*length*math.cos(radians),startPoint[2]+0.0)
	return branch[0]

def calculateVector( length, rotation ):
	'''calculate the vector from the start point to the end point for each branch

	length		: step size for growing
	rotation	: the rotation angle for branching
	return		: return the vector from start point to end point
	'''
	radians = math.pi * rotation / 180
	return [length* math.sin(radians), length* math.cos(radians), 0.0]	

def createModel( actionString, length, turn):
    '''create the 3D model based on the actionString, following the characters in the string, 
    one by one, grow the branches, and finally group all branches together into one group

      actionString	: instructions on how to construct the model
      length		: step size for growing
      turn			: the rotation angle for branching
      return		: return the group of all the branches
    '''
    inputString = actionString
    index = 0		# Where at the input string we start from
    angle = 0		# Degrees, nor radians
    currentPoint = [0.0, 0.0, 0.0]	# Start from origin
    coordinateStack = []	# Stack where to store coordinates
    angleStack = []		# Stack to store angles
    branchList = []

    while ( index < len( inputString ) ):
        if inputString[index] == 'F':
            branch = createBranch(currentPoint, length, angle)
            branchList.append(branch)
            vector = calculateVector( length, angle )
            newPoint = [currentPoint[0] + vector[0], currentPoint[1] + vector[1], currentPoint[2] + vector[2]]
            currentPoint = newPoint	# update the position to go on growing from the new place
        elif inputString[index] == '-':
            angle = angle - turn
        elif inputString[index] == '+':
            angle = angle + turn
        elif inputString[index] == '[': # add new branches, save the old position into the stack
            coordinateStack.append( currentPoint )
            angleStack.append( angle )
        elif inputString[index] == ']': # finish the branches, get back to the root position
            currentPoint = coordinateStack.pop()
            angle = angleStack.pop()
        # Move to the next drawing directive
        index = index + 1
    groupName = cmds.group(branchList, n = "tree")
    return groupName
	
def setMaterial(objName, materialType='lambert', colour=(0, 1, 0)):
   '''Assigns a material to the object 'objectName'

      objectName   : is the name of a 3D object in the scene
      materialType : is string that specifies the type of the sufrace shader, 
                     this can be any of Maya's valid surface shaders such as:
                     lambert, blin, phong, etc.
      colour       : is a 3-tuple of (R,G,B) values within the range [0,1]
                     which specify the colour of the material
      On Exit      : 'objName' has been assigned a new material according to the 
                     input values of the procedure, and a tuple (of two strings) 
                     which contains the new shading group name, and the new shader
                     name is returned to the caller
	'''
   # create a new shading node
   setName = cmds.sets(name='_MaterialGroup_', renderable=True, empty=True)
   # create a new shading node
   shaderName = cmds.shadingNode(materialType, asShader=True)
   # change its colour
   cmds.setAttr(shaderName+'.color', colour[0], colour[1], colour[2], type='double3')
   # add to the list of surface shaders
   cmds.surfaceShaderList(shaderName, add=setName)
   # assign the material to the object
   cmds.sets(objName, edit=True, forceElement=setName)
	
def buildTree():
	''' add the rules, initialise the control parameters, such as 
	iteration numbers, branch rotation angle, step size of growing '''
	
	# clear up the scene
	cmds.select(all=True)
	cmds.delete()
	
	# add the rules to the rule dictionary
	ruleDictionary = {} # holding the rules (key, value) such as (F, F + f - FF + F + F F + Ff + FF -f + FF - F - FF - Ff- FFF), (f,ffffff)
	actionString = ""	# the final action string to build the tree
	addRule(ruleDictionary, "X", "F-[[X]+X]+F[+FX]-X" )
	addRule(ruleDictionary, "F", "FF" )

	# set growing parameters
	iterations = 5
	axiom = "X"
	stepLength = 0.1
	rotateAngle = 25
	
	# create the action string
	finalString=iterate(axiom, iterations, ruleDictionary)
	print(finalString)
	# create the 3D model
	modelGroup = createModel(finalString, stepLength, rotateAngle)
	
	# set the color to green
	setMaterial(modelGroup)

# main program, start with the function buildTree()
if __name__ == "__main__":
	buildTree()