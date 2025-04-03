from pickle import TRUE
import random
import pygame
import sys

pygame.init()
clock = pygame.time.Clock()
clock.tick(60)

#screen settings
screen = pygame.display.set_mode((1600,1200))
pygame.display.set_caption("simple 2D game")

#Text
scoreFont = pygame.font.Font(None,50)

#deault sprites
class playerCharacter(pygame.sprite.Sprite):
    def __init__(self, *groups):
      super().__init__(*groups)
      #self.spriteSheet[] = 
      self.hitbox = pygame.Rect((0,0),(100,500))
      self.colorBlock = pygame.surface.Surface(size = (self.hitbox.height,self.hitbox.width),)
      self.colorBlock.fill("Red")

score = scoreFont.render("score:", False, "Green")

characterSprite = playerCharacter()

while TRUE:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(characterSprite.colorBlock, (0,0))
    screen.blit(score, (random.randrange(0,50),0))
    pygame.display.update()
  