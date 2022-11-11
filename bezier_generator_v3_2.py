# -*- coding: utf-8 -*-
"""
Created on Sat Aug 28 18:27:52 2021

@author: simon
"""

# This version is done :)
# The only remaining improvements would be to clean up
# the code, and maybe add som quality-of-life features, listed below:


# ------ improvements ------
# if you tweak the handle belonging to the final point, and then add a new
# point, the position of the tweaked handle will be modified to fit the new
# point.
#


# Other...


#%%

import pygame
import numpy as np


#%%

# Pygame shit

WIDTH, HEIGHT = 900, 700
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Renderer")


FPS = 30


#%%

# Other setup

RESOLUTION = 500
linsp = np.linspace(0, 1, RESOLUTION, endpoint=True)


points = np.array([[0],
                   [0]])

# np.append(points, np.array([[1],[2]]), axis=1)

WHITE = (255,255,255)
BLUE = (105,75,255)
RED = (255,75,75)


keyIsBeingPressed = False
windowUpdateReady = False
movingPoint = False
pointToMove = 0
oppositeHandleDistance = 0 # when tweaking a handle, this value is the distance between the corresponding point and the opposite handle
oppositeHandleDistanceFound = False # Check to see if the above value has been found (should only be calculated once per moving action)
LINETHICKNESS = 5 # preferably an uneven number
POINTTHICKNESS = 11 # -||-


#%%

# lerp to the t'th percentile between two values with t ranging [0..1]

def lerpt(v1, v2, tval):
    out = v1 + (v2-v1)*tval
    return out



#%%

# Find the length/magnitude of a 2d vector

def vector2Length(vector):
    length = np.sqrt(vector[0]**2 + vector[1]**2)
    return length



#%%

# Update window

def updateWindow():
    WINDOW.fill(WHITE)
    
    drawCurve()
    
    drawPoints() # Draw curve- and handlepoints
    
    pygame.display.update()


#%%

# Wait for pressed button to be released to avoid one press resulting in multiple inputs

def waitForButtonRelease():
    global keyIsBeingPressed
    keyIsBeingPressed = True



#%% Add point


def addPoint():
    global points
    mousePos = pygame.mouse.get_pos()
    
    # Check if the point already exist (to prevent duplicate points)
    isInPoints = False
    for i in range(np.size(points,1)):
        if np.all(mousePos == points[:,i]):
            isInPoints = True
    
    
    if isInPoints == False:
    
        newCol = np.array([[mousePos[0]],[mousePos[1]]])
        
        # If there is only 1 point in the list (being (0,0) ), the list is
        # effectively empty, and the newly recorded point is added, and
        # no curve is drawn (because there is effectively only 1 point)
        if np.size(points,1) == 1:
            points = np.append(points, newCol, 1)
        
        # If there are 2 points (1 effective), a second point should be added
        # along with two handles, in the following order
        # [p0, p1] -> [p0, p1, h1, h2, p2]
        elif np.size(points,1) == 2:
            # Handles are added at 20% distance from their respective point
            h1 = np.array([lerpt(points[0,1], newCol[0], 0.2),
                           lerpt(points[1,1], newCol[1], 0.2)]).astype(int)
            
            h2 = np.array([lerpt(points[0,1], newCol[0], 0.8),
                           lerpt(points[1,1], newCol[1], 0.8)]).astype(int)
            
            points = np.append(points, h1, 1)
            points = np.append(points, h2, 1)
            points = np.append(points, newCol, 1)
        
        # If there are more than 2 effective points, that means we have at
        # least 2 point and 2 handles, and every newly recorded point from
        # here will result in the addition of a new curve point and 2 handles
        # parallel to the line joining the 2 points, and with length equal
        # to 20% of the distance to each respective point
        elif np.size(points,1) > 2:
            
            handleDirection = newCol[:,0] - points[:,-4]
            handleDirectionNormalized = handleDirection / vector2Length(handleDirection)
            
            # Handle(s) between last point and the newly recorded
            distance = vector2Length(points[:,-1] - newCol[:,0])
            
            h1 = points[:,-1] + handleDirectionNormalized * distance * 0.2
            h1 = h1.astype(int)
            h1 = np.reshape(h1, (2,1))
            
            
            h2 = np.array([lerpt(points[0,-1], newCol[0], 0.8),
                           lerpt(points[1,-1], newCol[1], 0.8)]).astype(int)
            
            
            # Handle between last point and the one before that (this is a
            # handle that gets edited, not a new one being generated)
            
            distance = vector2Length(points[:,-1] - points[:,-4])
            
            
            h01 = points[:,-1] + handleDirectionNormalized * distance * 0.2 * (-1)
            h01 = h01.astype(int)
            h01 = np.reshape(h01, (2,1))
            
            
            points[:,-2] = h01[:,0]
            points = np.append(points, h1, 1)
            points = np.append(points, h2, 1)
            points = np.append(points, newCol, 1)
    
    waitForButtonRelease()



#%% Remove point

def removePoint():
    global points
    
    waitForButtonRelease()
    
    mousePos = pygame.mouse.get_pos()
    smallestDist = np.inf
    smallestDistIndex = 0
    
    if np.size(points,1) == 2:
        points = np.delete(points,1,1)
    
    elif np.size(points,1) > 2:
    
        curveIndexList = findCurvePoints()
        
        for i in curveIndexList:
            dist = vector2Length(points[:,i] - mousePos)
            if dist < smallestDist:
                smallestDist = dist
                smallestDistIndex = i
        
        if smallestDistIndex == curveIndexList[0]:
            points = np.delete(points,1,1)
            points = np.delete(points,1,1)
            points = np.delete(points,1,1) # repeated 3 times since 1 point and 2 handles should be removed, and every time 1 is removed, the next takes over its index
        elif smallestDistIndex == curveIndexList[-1]:
            points = np.delete(points,-1,1)
            points = np.delete(points,-1,1)
            points = np.delete(points,-1,1)
        else:
            points = np.delete(points,smallestDistIndex-1,1)
            points = np.delete(points,smallestDistIndex-1,1)
            points = np.delete(points,smallestDistIndex-1,1)
            


#%% Move point

def findPointToMove():
    global movingPoint, pointToMove
    movingPoint = True
    
    waitForButtonRelease()
    
    mousePos = pygame.mouse.get_pos()
    smallestDist = np.inf
    smallestDistIndex = 0
    for i in range(1, np.size(points,1)):
        dist = vector2Length(points[:,i] - mousePos)
        if dist < smallestDist:
            smallestDist = dist
            smallestDistIndex = i
    
    pointToMove = smallestDistIndex



def movePoint():
    
    global points
    
    mousePos = pygame.mouse.get_pos()
    newPosition = np.array([[mousePos[0]],[mousePos[1]]])
    
    curveIndexList = findCurvePoints()
    handleIndexList = findHandlePoints()
    
    if pointToMove in curveIndexList:
        oldPosition = points[:,pointToMove]
        difference = newPosition[:,0] - oldPosition
        
        # Set bew position for the point being moved
        points[:,pointToMove] = newPosition[:,0]
        
        if pointToMove == curveIndexList[-1]:
            points[:,-2] += difference
        
        elif pointToMove == curveIndexList[0]:
            points[:,2] += difference
        
        else:
            points[:,pointToMove-1] += difference
            points[:,pointToMove+1] += difference
        
    
    
    elif pointToMove in handleIndexList:
        # Set new position for the handle being moved
        points[:,pointToMove] = newPosition[:,0]
        
        # Check what "side" of the point the handle is on (in context of the
        # "points" list)
        if pointToMove + 1 == curveIndexList[-1] or pointToMove - 1 == curveIndexList[0]:
            oppositePointExists = False
        
        elif pointToMove + 1 in curveIndexList:
            correspondingPoint = pointToMove + 1
            oppositeHandle = pointToMove + 2
            oppositePointExists = True
        elif pointToMove - 1 in curveIndexList:
            correspondingPoint = pointToMove - 1
            oppositeHandle = pointToMove - 2
            oppositePointExists = True
        
        
        if oppositePointExists == True:
            # Direction from handle to it's corresponding point
            direction = points[:,correspondingPoint] - points[:,pointToMove]
            directionNormalized = direction / vector2Length(direction)
            
            # Distance between opposite handle and correstponding point
            global oppositeHandleDistance, oppositeHandleDistanceFound
            if oppositeHandleDistanceFound == False:
                oppositeHandleDistance = vector2Length(points[:,correspondingPoint] - points[:,oppositeHandle])
                oppositeHandleDistanceFound = True
            
            oppositeHandleNewPosition = points[:,correspondingPoint] + directionNormalized * oppositeHandleDistance
            points[:,oppositeHandle] = oppositeHandleNewPosition


        

def stopMovingPoint():
    global movingPoint, oppositeHandleDistanceFound
    movingPoint = False
    oppositeHandleDistanceFound = False
    # Lol this is the dumbest fnciton ever, but i couldnt have it in the
    # main loop



#%% Draw curvepoints and handlepoints


# Check if there are points to draw, and draw them if there are

def drawPoints():
    if np.size(points,1) == 2:
        indexList = findCurvePoints()
        drawCurvePoints(indexList)
    
    elif np.size(points,1) > 2:
        curveIndexList = findCurvePoints()
        drawCurvePoints(curveIndexList)
        
        handleIndexList = findHandlePoints()
        drawHandlePoints(handleIndexList)
        drawHandleLines(curveIndexList)
        
        
        
        

def findCurvePoints():
    indexList = []
    result = 1
    while result < np.size(points,1):
        indexList.append(result)
        result += 3
    return indexList


def drawCurvePoints(indexList):
    for index in indexList:
        for i in range(11):
            for j in range(11):
                pygame.Surface.set_at(WINDOW, (points[0,index]+i-5, points[1,index]+j-5), BLUE)


def findHandlePoints():
    indexList = []
    result = 2
    step = 1
    while result < np.size(points,1) - 1:
        indexList.append(result)
        result += step
        if step == 1:
            step = 2
        else:
            step = 1
    return indexList


def drawHandlePoints(indexList):
    for index in indexList:
        for i in range(POINTTHICKNESS):
            for j in range(POINTTHICKNESS):
                pygame.Surface.set_at(WINDOW, (points[0,index] + i - POINTTHICKNESS//2, points[1,index] + j-POINTTHICKNESS//2), RED)




def drawHandleLines(indexList):
    for index in indexList:
        
        if index == indexList[0]:
            xs = points[0,index] + (points[0,index+1] - points[0,index]) * linsp
            ys = points[1,index] + (points[1,index+1] - points[1,index]) * linsp
        elif index == indexList[-1]:
            xs = points[0,index] + (points[0,index-1] - points[0,index]) * linsp
            ys = points[1,index] + (points[1,index-1] - points[1,index]) * linsp
        else:
            xs = points[0,index-1] + (points[0,index+1] - points[0,index-1]) * linsp
            ys = points[1,index-1] + (points[1,index+1] - points[1,index-1]) * linsp
        
        xs = xs.astype(int)
        ys = ys.astype(int)
        
        for i in range(RESOLUTION):
            pygame.Surface.set_at(WINDOW, (xs[i], ys[i]), RED)






#%% Draw bezier curve

def drawCurve():
    if np.size(points,1) > 2:
        curveIndexList = findCurvePoints()
        
        for i in range(len(curveIndexList) - 1):
            
            p1,p2,p3,p4 = points[:,curveIndexList[i] + 0], points[:,curveIndexList[i] + 1], points[:,curveIndexList[i] + 2], points[:,curveIndexList[i] + 3]
            
            xs = (-p1[0] + 3*p2[0] - 3*p3[0] + p4[0])*linsp**3 + (3*p1[0] - 6*p2[0] + 3*p3[0])*linsp**2 + (-3*p1[0] + 3*p2[0])*linsp + p1[0]
            ys = (-p1[1] + 3*p2[1] - 3*p3[1] + p4[1])*linsp**3 + (3*p1[1] - 6*p2[1] + 3*p3[1])*linsp**2 + (-3*p1[1] + 3*p2[1])*linsp + p1[1]
            xs = xs.astype(int)
            ys = ys.astype(int)
            
            for j in range(RESOLUTION):
                for p in range(LINETHICKNESS):
                    for k in range(LINETHICKNESS):
                        pygame.Surface.set_at(WINDOW, (xs[j] + p - LINETHICKNESS//2, ys[j] + k - LINETHICKNESS//2), (50,50,50))



#%%

# Main loop


def main():
    run = True
    clock = pygame.time.Clock()
    
    global keyIsBeingPressed, windowUpdateReady

    
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        
        keys_pressed = pygame.key.get_pressed()
        
        if sum(keys_pressed) == 0:
            keyIsBeingPressed = False
        
        
        
        
        if keyIsBeingPressed == False and movingPoint == False:
            # Code for adding point
            if keys_pressed[pygame.K_a]:
                addPoint()
                updateWindow()
            
            # code for registering that a point should be moved
            elif keys_pressed[pygame.K_m]:
                findPointToMove()
            
            elif keys_pressed[pygame.K_r]:
                removePoint()
                updateWindow()
            
            elif keys_pressed[pygame.K_p]:
                print(points)
                waitForButtonRelease()
        
        
        if keyIsBeingPressed == False and movingPoint == True: # Unsure if "keyIsBeingPressed == False" should be removed
            # code for moving a point after it has been registered that it should move
            movePoint()
            if keys_pressed[pygame.K_n]:
                stopMovingPoint()
            updateWindow()
        
            

    pygame.quit()
    

if __name__ == "__main__":
    main()