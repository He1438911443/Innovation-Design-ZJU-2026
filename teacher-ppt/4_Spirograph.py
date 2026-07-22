# Using particle to implement the balls shooting out in the sky and drop, bounce on the ground
 
import maya.cmds as cmds
import math as math

def calSpirographTrajectory(M, N, f):
	posArray = []
	numPointCircle = 360
	angleIncre = math.pi * 2.0 / numPointCircle
	for i in range(numPointCircle):
		x = (1-1.0*N/M)*math.cos(N*i*angleIncre)+1.0*f*N/M*math.cos((M-N)*i*angleIncre)
		y = (1-1.0*N/M)*math.sin(N*i*angleIncre)-1.0*f*N/M*math.sin((M-N)*i*angleIncre)
		posArray.append((x,0, y))
	return posArray

def drawSpirograph(posArray):
	cmds.curve(p=posArray, d=1)

# main program
if __name__ == "__main__":
	M = 24
	N = 13
	f = 0.5 # f in (0,1]
	posArray = calSpirographTrajectory(M, N, f)
	print(posArray)
	drawSpirograph(posArray)