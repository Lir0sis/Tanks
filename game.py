import pygame
import sys
import math
from map import *
import utils
from player import *

class Screen:
    def __init__(self, width = 640, height = 480):
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode((width, height))

    def setOffset(self, size):
        width, height = size
        utils.OFFSET_X = math.floor((self._width - width)/2)
        utils.OFFSET_Y = math.floor((self._height - height)/2)
        print('Offset:',utils.OFFSET_X, utils.OFFSET_Y)

    def getSize(self):
        return (self._width, self._height)

    def getScreen(self):
        return self._screen

    def getScale(self, size):
        width, height = size
        # print(size)
        # print(self._width, self._height)
        # print('Scale:',self._width/(width + 10), self._height/(height + 10))
        return min(self._width/(width + 10), self._height/(height + 10))

    def drawSprite(self, obj):
        self._screen.blit(obj.image, obj.rect)

    def fill(self, color):
        self._screen.fill(color)

    def update(self):
        pygame.display.update()

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
        self.map = Map()

        boardWidth, boardHeight = self.map._getBoardSize()
        utils.WINDOW_SCALE = self.screen.getScale((boardWidth, boardHeight))
        self.screen.setOffset((boardWidth * utils.WINDOW_SCALE, boardHeight * utils.WINDOW_SCALE))

        self.map.init()

        self.player = Player(Tank('./OriginalTank.png'))
        gameLayer.append(self.player.child.rect)
        impassableLayer.append(self.player.child.rect)
        

    def run(self):
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        self.clock.tick(utils.FPS)
        
        self.screen.fill(utils.BLACK)

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
    game.run()