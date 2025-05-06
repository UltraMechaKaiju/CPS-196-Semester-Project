import random
import numpy as np
import pygame
import sys

from pygame.draw import polygon
import pygame.key

pygame.init()
clock = pygame.time.Clock()


#screen settings
screen = pygame.display.set_mode((1920,1080))
pygame.display.set_caption("simple 2D game")

#Text
scoreFont = pygame.font.Font(None,50)

#world Objects

#Groups
characterElements = pygame.sprite.Group()
worldObjects = pygame.sprite.Group()
collisionPolyObjects = pygame.sprite.Group()
collisionRectObjects = pygame.sprite.Group()

#classes
class playerCharacter(pygame.sprite.Sprite):
    def __init__(self, startLocation: pygame.Vector2, *groups):
      super().__init__(*groups)
      #self.spriteSheet[] = 
      #PPos: center of the characters hit box
      self.movementMode = 0;
      self.PPos = startLocation
      self.hitbox = pygame.Rect((startLocation),(50,100))
      self.verticies = [self.hitbox.topleft, self.hitbox.topright, self.hitbox.bottomright, self.hitbox.bottomleft]
      self.SATAxes = self.createSATAxes(self.verticies)

      self.velocity = pygame.Vector2(0,0)
      self.acceleration = pygame.Vector2(0,0)
      self.colorBlock = pygame.surface.Surface(size = (self.hitbox.width,self.hitbox.height),)
      self.colorBlock.fill("Green")
    def createSATAxes(self, verticies):
      Axes = []
      i=0
      for verts in verticies:
          Axes.append((verticies[i-1], verticies[i]))
          i += 1
      return Axes
    
    def getVerticies(self):
        return [self.hitbox.topleft, self.hitbox.topright, self.hitbox.bottomright, self.hitbox.bottomleft]
    def getGroundHitbox(self):
        return pygame.Rect(self.hitbox.bottomleft, (self.hitbox.width, 10))
    def checkGround(self, checkGroup: pygame.sprite.Group):
        for rect in collisionRectObjects.sprites():
            if self.getGroundHitbox().colliderect(rect.hitbox):
                print("groundfound")
                self.movementMode = 1
                return True
            else:
                print("nofound")
                return False


class worlRectObject(pygame.sprite.Sprite):
    def __init__(self, startLocation: pygame.Vector2, platformSize: pygame.Vector2, color: str,*groups):
      super().__init__(*groups)
      self.pos = startLocation
      self.hitbox = pygame.Rect((startLocation),(platformSize))
      self.colorBlock = pygame.surface.Surface(size = (self.hitbox.width,self.hitbox.height))
      self.colorBlock.fill(color)
      def getRect(self):
          return self.hitbox

class CollisionPolygon(pygame.sprite.Sprite):
    def __init__(self, color: str, vertexList, *groups):
        super().__init__(*groups)
        self.verticies = vertexList

class Scene():
    def __init__(self, wExtents: pygame.Vector2 = pygame.Vector2((1000,1000)),cExtents: pygame.Vector2 = pygame.Vector2((500,500)), chOffset: pygame.Vector2 = pygame.Vector2(0,0), worldObjectList = pygame.sprite.Group()) -> None:
        self.worldExtents = wExtents
        self.cameraExtents = cExtents
        self.globalOffset = pygame.Vector2(0,0)
        self.characterOffset = chOffset
        self.startingObjects = worldObjectList

        #testing variables
        self.cameraBlock = pygame.surface.Surface(size = (self.cameraExtents.x, self.cameraExtents.y))
        self.cameraBlock.fill("orange")

#Functions
def packageWorldGroup(targetGroup, worldOffset):
    worldPrint = []
    for sprite in targetGroup.sprites():
        worldPrint.append((sprite.colorBlock, sprite.hitbox.topleft + worldOffset))
    return worldPrint



#movement stuff

#these functions decide how the character should move, the move world and camera function actually moves the character using the final output

#movement Abilties
def Jump(targetCharacter: playerCharacter):
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_SPACE] and targetCharacter.movementMode == 1:
        targetCharacter.velocity[1] = -45
        targetCharacter.movementMode = 0


#movement Modes
#mode 0
def PhysFalling(targetCharacter: playerCharacter) -> pygame.Vector2:
    #check: should change movement Mode?

    #fall

    targetCharacter.acceleration += pygame.Vector2(0,9.8/4);

    #Add player input
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_a]:
        targetCharacter.acceleration -= pygame.Vector2(1,0)
    if pressed[pygame.K_d]:
        targetCharacter.acceleration += pygame.Vector2(1,0)



def moveWorldOffset(acceleration, targetCharacter: playerCharacter, currentScene: Scene):
    #calculates character offset and global offset(camera location) as well as character position

    #Save old position
    oldPosition = pygame.Vector2(targetCharacter.hitbox.topleft[0], targetCharacter.hitbox.topleft[1])

    #Part 1: apply acceleration
    targetCharacter.velocity += pygame.Vector2(targetCharacter.acceleration.x,targetCharacter.acceleration.y)

    targetCharacter.hitbox.topleft = ((targetCharacter.hitbox.topleft[0] + targetCharacter.velocity.x),(targetCharacter.hitbox.topleft[1] + targetCharacter.velocity.y))


    # apply world boundry check
    #Check for collisions with the left and top of the world
    if targetCharacter.hitbox.top < 0:
        targetCharacter.hitbox.top = 0
        #print("overtop")
    if targetCharacter.hitbox.left < 0:
        targetCharacter.hitbox.left = 0
        #print("overleft")
    #Check for collisions with the right and bottom of the world
    if currentScene.worldExtents.x < targetCharacter.hitbox.right:
        targetCharacter.hitbox.right = currentScene.worldExtents.x
        #print("overright")
    if currentScene.worldExtents.y < targetCharacter.hitbox.bottom:
        targetCharacter.hitbox.bottom = currentScene.worldExtents.y
        #print("overbottom")

    #update character Velocity
    targetCharacter.acceleration = pygame.Vector2(0,0)
    targetCharacter.velocity =  targetCharacter.hitbox.topleft  - oldPosition

    #part2: detect object collisions

    #simple collision for rectangles

    yDelta = 0
    xDelta = 0

    targetCharacter.movementMode = 0

    for rect in collisionRectObjects.sprites():
        if targetCharacter.hitbox.colliderect(rect.hitbox):
            #positive Result
            xDeltaRightward = rect.hitbox.right - targetCharacter.hitbox.left
            #Negative Result
            xDeltaLeftWard = rect.hitbox.left - targetCharacter.hitbox.right

            #positive result
            yDeltaDownWard = rect.hitbox.bottom - targetCharacter.hitbox.top
            #negative result
            yDeltaUpWard = rect.hitbox.top - targetCharacter.hitbox.bottom

            #decide which direction should be moved in the x and y axis
            if targetCharacter.velocity[0] >= 0:
                xDelta = xDeltaLeftWard
            else:
                xDelta = xDeltaRightward

            if targetCharacter.velocity[1] >= 0:
                yDelta = yDeltaUpWard
            else:
                yDelta = yDeltaDownWard


            #decide wether to move in the X or y direction
            if np.abs(yDelta) < np.abs(xDelta):
                if yDelta < 0:
                    targetCharacter.hitbox.bottom = rect.hitbox.top
                    targetCharacter.movementMode = 1
                else:
                    targetCharacter.hitbox.top = rect.hitbox.bottom
            else:
                if xDelta < 0:
                    targetCharacter.hitbox.right = rect.hitbox.left
                else:
                    targetCharacter.hitbox.left = rect.hitbox.right
    targetCharacter.acceleration = pygame.Vector2(0,0)
    targetCharacter.velocity =  targetCharacter.hitbox.topleft  - oldPosition






    #TODO:
    #Use SAT to look for overlapping polygons

    i = 0

    for axis in targetCharacter.SATAxes:
        #axis verticies
        x1 = axis[0][0]
        y1 = axis[0][1]
        x2 = axis[1][0]
        y2 = axis[1][1]

        CurrentAxis = pygame.Vector2(x1,y1) - pygame.Vector2(x2,y2)

        pygame.draw.line(screen, "Orange", (pygame.Vector2(x1,y1)), (pygame.Vector2(x1,y1)) - CurrentAxis )

        #For each Axis, project each vert from the character onto it

        for vert in targetCharacter.getVerticies():
            #Get each coordinate of the current vertex
            xc = vert[0]
            yc = vert[1]

            #project it onto the current Axis
            numerator = np.abs(((y2 - y1) * xc) - ((x2 - x1) * yc) + (x2*y1) - (y2*x1))
            denominator = np.sqrt((np.square(y2-y1)) + (np.square(x2 - x1)))

            projectionDistance = numerator/denominator

            #print(i, xc, yc, "verticies")
            #print (projectionDistance)

            #add the projection distance times the normalized projection vector to the projected vertex's start location
            projectedVertexLocation = pygame.Vector2((0,0), vert) - (((pygame.Vector2((x1,y1),(x2,y2))).rotate(90)).normalize()) * projectionDistance
            
            #print(projectedVertexLocation, "NewLoc")

            if pressed[pygame.K_LEFTBRACKET]:
                #pygame.draw.line(screen, "red", (vert), (vert) - projectedVertexLocation)
                #pygame.draw.line(screen, "Blue", (100,100), pygame.Vector2(100,100) + targetCharacter.velocity)
                #pygame.draw.line(screen, "White", (0,10), (1000,10))
                #pygame.draw.line(screen, "Black", , 1)
                ...

        #For each Axis, project all collision objects to it
        for poly in collisionPolyObjects:
            for vert in poly.verticies:
                #vert to project
                x0 = vert[0]
                y0 = vert[1]
        i += 1

                



    #Find radius of the polygon
    #Use forward Hull method to find how to fix any detected collisions 
        


    #slide along the collided surface if possible using the remaining force
    #continue sliding along collided polygons until energy runs out or movement is no longer possible



    #Part3: given the characters position, which has accounted for the world boundry and world objects that may have obstructed movement, move the camera to its proper position

    #calculate where the camera is supposed to be (global offset) and where the character is on the screen, character offset refers to the center of the character's distance from the top and left side of the CAMERA
    #"where the camera is" is the opposite of how all world objects should be offset

    #modify camaera position in case the player is towards the top or lefft edge of the world border
    
    cameraOffset = pygame.Vector2(targetCharacter.hitbox.left,targetCharacter.hitbox.top)
    characterOffset = pygame.Vector2(currentScene.cameraExtents.x/2, currentScene.cameraExtents.y/2)

    if targetCharacter.hitbox.top <= currentScene.cameraExtents.y/2:
        characterOffset.y = targetCharacter.hitbox.top
        cameraOffset.y = currentScene.cameraExtents.y/2
    if targetCharacter.hitbox.left <= currentScene.cameraExtents.x/2:
        characterOffset.x = targetCharacter.hitbox.left
        cameraOffset.x = currentScene.cameraExtents.x/2

    #modify camaera position in case the player is towards the bottom or right edge of the world border

    if (targetCharacter.hitbox.bottom >= currentScene.worldExtents.y - (currentScene.cameraExtents.y/2)):
        characterOffset.y = currentScene.cameraExtents.y - (currentScene.worldExtents.y - targetCharacter.hitbox.top)
        cameraOffset.y = (currentScene.worldExtents.y - (currentScene.cameraExtents.y / 2))
    if (targetCharacter.hitbox.right >= currentScene.worldExtents.x - (currentScene.cameraExtents.x/2)):
        characterOffset.x = currentScene.cameraExtents.x - (currentScene.worldExtents.x - targetCharacter.hitbox.left)
        cameraOffset.x = (currentScene.worldExtents.x - (currentScene.cameraExtents.x / 2))


    #set equal to worldOffset and characterOffset and PPos of player character
    return -(cameraOffset - (currentScene.cameraExtents.xy/2)), characterOffset, targetCharacter.PPos





testImage = pygame.transform.smoothscale(pygame.image.load("images/288_1_honda_vfr_decals_Background.jpg"), (500,500))

score = scoreFont.render("score:", False, "Green")

characterSprite = playerCharacter(pygame.Vector2(5,5), characterElements)

#firstObject = worlRectObject(pygame.Vector2(500,0), pygame.Vector2(1920/2,1080/2), "Red", collisionRectObjects)
secondObject = worlRectObject(pygame.Vector2(1920/2 + 500,1080/2), pygame.Vector2(1920/2,1080/2), "Blue", collisionRectObjects)
thirdObject = worlRectObject(pygame.Vector2(1920/2 + 500,0), pygame.Vector2(1920/2,1080/2), "Black", collisionRectObjects)
fourthObject = worlRectObject(pygame.Vector2(500,1080/2), pygame.Vector2(1920/2,1080/2), "Purple", collisionRectObjects)
sixthObject = worlRectObject(pygame.Vector2(0,150), pygame.Vector2(300,100), "Purple", collisionRectObjects)
seventhObject = worlRectObject(pygame.Vector2(200,500), pygame.Vector2(300,100), "Purple", collisionRectObjects)

testPolygon = CollisionPolygon("red", [(0,0), (100,0),(100,-100), (0,-100)], collisionPolyObjects)

testScene = Scene(pygame.Vector2(1920*4,1080*4), pygame.Vector2(1920,1080), pygame.Vector2(0,0), worlRectObject)

worldOffset = pygame.Vector2()
desiredMove = pygame.Vector2()
print(worldObjects)
for x in characterSprite.SATAxes:
    print(x)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    #region simple movement
    # desiredMove = pygame.Vector2(0,0)
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_q]:
        characterSprite.hitbox.center = (characterSprite.hitbox.center[0] - 10, characterSprite.hitbox.center[1] - 10)
    if pressed[pygame.K_e]:
        characterSprite.hitbox.center = (-100,-100)
    if pressed[pygame.K_r]:
        characterSprite.hitbox.center = (250,250)
    if pressed[pygame.K_LEFTBRACKET]:
        print(worldOffset)
    if pressed[pygame.K_RIGHTBRACKET]:
        #screen.blit(backgroundBlock, (0,0))
        ...

    # if (desiredMove != pygame.Vector2(0,0)):
    #     desiredMove = desiredMove.normalize() * 5
    #endregion
    

    PhysFalling(characterSprite)
    if characterSprite.movementMode == 1:
        Jump(characterSprite)


    worldOffset, testScene.characterOffset, characterSprite.PPos = moveWorldOffset(characterSprite.acceleration, characterSprite, testScene)
    #print(characterSprite.acceleration, characterSprite.velocity, "C:",characterSprite.hitbox.topleft, testScene.characterOffset, worldOffset)
    backgroundBlock = pygame.surface.Surface((screen.get_rect().width, screen.get_rect().height))

    backgroundBlock.fill("White")

    screen.blit(backgroundBlock, (0,0))
    
    #screen.blit(testImage, (0,0))
    #screen.blit(testScene.cameraBlock, (0,0))
    screen.blits(packageWorldGroup(collisionRectObjects, worldOffset))
    #pygame.draw.line(screen, "Black", (0,0), (1000,1000))
    screen.blit(characterSprite.colorBlock, pygame.Vector2((testScene.characterOffset.x), (testScene.characterOffset.y)))
    pygame.draw.rect(screen, "Red", characterSprite.hitbox, 5)
    pygame.draw.rect(screen, "Red", characterSprite.getGroundHitbox(), 5)
    screen.blit(score, (random.randrange(0,50),0))
    
    pygame.display.update()
    clock.tick(60)