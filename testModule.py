
import copy
import random
from typing import Self
import pygame
import sys

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

#classes
class playerCharacter(pygame.sprite.Sprite):
    def __init__(self, startLocation: pygame.Vector2, *groups):
      super().__init__(*groups)
      #self.spriteSheet[] = 
      #PPos: center of the characters hit box
      self.movementMode = 0;
      self.PPos = startLocation
      self.hitbox = pygame.Rect((0,0),(50,100))
      
      self.velocity = pygame.Vector2(0,0)
      self.acceleration = pygame.Vector2(0,0)
      self.colorBlock = pygame.surface.Surface(size = (self.hitbox.width,self.hitbox.height),)
      self.colorBlock.fill("Green")

class worldObject(pygame.sprite.Sprite):
    def __init__(self, startLocation: pygame.Vector2, *groups):
      super().__init__(*groups)
      self.pos = startLocation
      self.hitbox = pygame.Rect((startLocation),(100,500))
      self.colorBlock = pygame.surface.Surface(size = (self.hitbox.height,self.hitbox.width),)
      self.colorBlock.fill("Red")
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
def packageWorldGroup(targetGroup):
    worldPrint = []
    for sprite in targetGroup.sprites():
        worldPrint.append((sprite.colorBlock, sprite.hitbox.topleft + worldOffset))
    return worldPrint



#movement stuff

#these functions decide how the character should move, the move world and camera function actually moves the character using the final output

#movement Abilties
def Jump(targetCharacter: playerCharacter):
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_SPACE]:
        targetCharacter.acceleration -= pygame.Vector2(0,100)


#movement Modes
#mode 0
def PhysFalling(targetCharacter: playerCharacter) -> pygame.Vector2:
    #check: should change movement Mode?

    #fall

    targetCharacter.acceleration += pygame.Vector2(0,9.8);

    #Add player input
    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_a]:
        targetCharacter.acceleration -= pygame.Vector2(10,0)
    if pressed[pygame.K_d]:
        targetCharacter.acceleration += pygame.Vector2(10,0)



def moveWorldOffset(acceleration, targetCharacter: playerCharacter, currentScene: Scene):
    #calculates character offset and global offset(camera location) as well as character position

    #Save old position
    oldPosition = pygame.Vector2(targetCharacter.PPos.x,targetCharacter.PPos.y)

    #Part 1: apply acceleration
    targetCharacter.velocity += pygame.Vector2(targetCharacter.acceleration.x,targetCharacter.acceleration.y)

    targetCharacter.PPos += targetCharacter.velocity


    # apply world boundry check
    #Check for collisions with the left and top of the world
    if targetCharacter.PPos.y <= targetCharacter.hitbox.height/2:
        targetCharacter.PPos.y = targetCharacter.hitbox.height/2
    if targetCharacter.PPos.x <= targetCharacter.hitbox.width/2:
        targetCharacter.PPos.x = targetCharacter.hitbox.width/2
    #Check for collisions with the right and bottom of the world
    if currentScene.worldExtents.x <= targetCharacter.PPos.x + targetCharacter.hitbox.width/2:
        targetCharacter.PPos.x = currentScene.worldExtents.x - targetCharacter.hitbox.width/2
    if currentScene.worldExtents.y <= targetCharacter.PPos.y + targetCharacter.hitbox.height/2:
        targetCharacter.PPos.y = currentScene.worldExtents.y - targetCharacter.hitbox.height/2


    #Part2: given the characters position, which has accounted for the owrld boundry and world objects that may have obstructed movement, move the camera to its proper position

    #calculate where the camera is supposed to be (global offset) and where the character is on the screen, character offset refers to the center of the character's distance from the top and left side of the CAMERA
    #"where the camera is" is the opposite of how all world objects should be offset

    #modify camaera position in case the player is towards the top or lefft edge of the world border

    
    cameraOffset = pygame.Vector2(targetCharacter.PPos.x,targetCharacter.PPos.y)
    characterOffset = pygame.Vector2(currentScene.cameraExtents.x/2, currentScene.cameraExtents.y/2)

    if targetCharacter.PPos.y <= currentScene.cameraExtents.y/2:
        characterOffset.y = targetCharacter.PPos.y
        cameraOffset.y = currentScene.cameraExtents.y/2
    if targetCharacter.PPos.x <= currentScene.cameraExtents.x/2:
        characterOffset.x = targetCharacter.PPos.x
        cameraOffset.x = currentScene.cameraExtents.x/2
    #modify camaera position in case the player is towards the bottom or right edge of the world border

    if (targetCharacter.PPos.y >= currentScene.worldExtents.y - (currentScene.cameraExtents.y/2)):
        characterOffset.y = currentScene.cameraExtents.y - (currentScene.worldExtents.y - targetCharacter.PPos.y)
        cameraOffset.y = (currentScene.worldExtents.y - (currentScene.cameraExtents.y / 2))
    if (targetCharacter.PPos.x >= currentScene.worldExtents.x - (currentScene.cameraExtents.x/2)):
        characterOffset.x = currentScene.cameraExtents.x - (currentScene.worldExtents.x - targetCharacter.PPos.x)
        cameraOffset.x = (currentScene.worldExtents.x - (currentScene.cameraExtents.x / 2))

    #update character Velocity
    targetCharacter.acceleration = pygame.Vector2(0,0)
    targetCharacter.velocity =  targetCharacter.PPos - oldPosition 


    #set equal to worldOffset and characterOffset and PPos of player character
    return -cameraOffset, characterOffset - (pygame.Vector2((targetCharacter.hitbox.x/2),(targetCharacter.hitbox.y/2))), targetCharacter.PPos





testImage = pygame.transform.smoothscale(pygame.image.load("images/288_1_honda_vfr_decals_Background.jpg"), (500,500))

score = scoreFont.render("score:", False, "Green")

characterSprite = playerCharacter(pygame.Vector2(1920/2,1080/2), characterElements)
firstObject = worldObject(pygame.Vector2(0,0), worldObjects)
secondObject = worldObject(pygame.Vector2(100,100), worldObjects)
testScene = Scene(pygame.Vector2(1920,1080), pygame.Vector2(500,500), pygame.Vector2(0,0), worldObject)

worldOffset = pygame.Vector2()
desiredMove = pygame.Vector2()
print(worldObjects)

#characterSprite.hitbox.topleft

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("test", worldOffset)
            pygame.quit()
            sys.exit()
    #region simple movement
    # desiredMove = pygame.Vector2(0,0)
    # pressed = pygame.key.get_pressed()
    # if pressed[pygame.K_w]:
    #    desiredMove.y -= 10
    # if pressed[pygame.K_s]:
    #    desiredMove.y += 10
    # if pressed[pygame.K_a]:
    #    desiredMove.x -= 10
    # if pressed[pygame.K_d]:
    #    desiredMove.x += 10
    # if (desiredMove != pygame.Vector2(0,0)):
    #     desiredMove = desiredMove.normalize() * 5
    #endregion

    PhysFalling(characterSprite)
    Jump(characterSprite)


    worldOffset, testScene.characterOffset, characterSprite.PPos = moveWorldOffset(characterSprite.acceleration, characterSprite, testScene)
    print(characterSprite.velocity, characterSprite.PPos, worldOffset,testScene.characterOffset)
    backgroundBlock = pygame.surface.Surface((screen.get_rect().width, screen.get_rect().height))

    backgroundBlock.fill("White")

    screen.blit(backgroundBlock, (0,0))
    
    #screen.blit(testImage, (0,0))
    screen.blit(testScene.cameraBlock, (0,0))
    screen.blits(packageWorldGroup(worldObjects))
    screen.blit(characterSprite.colorBlock, pygame.Vector2((testScene.characterOffset.x - (characterSprite.hitbox.width/2)), (testScene.characterOffset.y - (characterSprite.hitbox.height/2))))
    screen.blit(score, (random.randrange(0,50),0))
    
    pygame.display.update()
    clock.tick(60)