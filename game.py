import pygame
import sys
import math
from map import *
from utils import *
from player import *

class Screen:
    def __init__(self, width = 640, height = 480):
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode((width, height))

    def getSize(self):
        return (self._width, self._height)

    def getScreen(self):
        return self._screen

    def update(self):
        pygame.display.update()

    def drawSprite(self, obj):
        self._screen.blit(obj.image, obj.rect)

    def fill(self, color):
        self._screen.fill(color)

'''class SampleObject():
    def __init__(self):
        self.image = pygame.image.load('./ball.png')
        rect = self.image.get_rect()
        self.image = pygame.transform.smoothscale(self.image, (math.floor(rect.w * 0.4), math.floor(rect.h * 0.4)))
        self.rect = self.image.get_rect()
        self.speed = 24

    def action(self):
        print("FIRE")
        
    def update(self):
        self.rect.centerx += self.direction[0] * self.speed / FPS
        self.rect.centery += self.direction[1] * self.speed / FPS
        print(self.rect.center)
'''

class Game:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.screen = Screen()
        self.player = Player(Tank('./OriginalTank.png'))
        self.player.child.resize(0.1)

    def run(self):
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        self.clock.tick(utils.FPS)

        for i in updateable:
            i.update()
        for i in drawable:
            self.screen.drawSprite(i)

        utils.time += 1 / utils.FPS

        self.player.update()
        self.player.child.update()
        self.screen.drawSprite(self.player.child)


        self.screen.update()

game = Game()

while 1:
    # point = pygame.mouse.get_pos()
    game.screen.fill(utils.WHITE)

    # pygame.draw.circle(game.screen.getScreen(), utils.ORANGE, game.screen.getSize(), 20) 
    game.run()
    # pygame.draw.circle(sc, utils.RED, point, 2)