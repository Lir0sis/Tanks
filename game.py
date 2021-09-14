import pygame
import sys
import map
import utils
import player
import time

timelist = []

class Screen:
    def __init__(self, width = 640, height = 480):
        self._width = width
        self._height = height
        self._screen = pygame.display.set_mode((width, height))

    def setOffset(self, size):
        width, height = size
        utils.OFFSET_X = round((self._width - width)/2)
        utils.OFFSET_Y = round((self._height - height)/2)
        # print('Offset:',utils.OFFSET_X, utils.OFFSET_Y)

    def getSize(self):
        return (self._width, self._height)

    def getScreen(self):
        return self._screen

    def getScale(self, size):
        width, height = size
        # # print(size)
        # # print(self._width, self._height)
        # # print('Scale:',self._width/(width + 10), self._height/(height + 10))
        return min(self._width/(width + 10), self._height/(height + 10))

    def drawSprite(self, obj):
        self._screen.blit(obj.image, obj.rect)

    def drawLines(self, vertices):
        start_pos = vertices[0]
        scale = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
        offset = utils.MAP_UNIT_SCALE / 2
        for end_pos in vertices:
            x1, y1 = end_pos
            x2, y2 = start_pos
            pygame.draw.line(self._screen, utils.RED, 
                (x1 * scale + utils.OFFSET_X + offset, y1 * scale + utils.OFFSET_Y + offset), 
                (x2 * scale + utils.OFFSET_X + offset, y2 * scale + utils.OFFSET_Y + offset), width=1)
            start_pos = end_pos

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
        # print("FIRE")
        
    def update(self):
        self.rect.centerx += self.direction[0] * self.speed / FPS
        self.rect.centery += self.direction[1] * self.speed / FPS
        # print(self.rect.center)
'''

class Game:
    __instance = None
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.screen = Screen()
        self.map = map.Map()

        boardWidth, boardHeight = self.map._getBoardSize()
        utils.WINDOW_SCALE = self.screen.getScale((boardWidth, boardHeight))
        self.screen.setOffset((boardWidth * utils.WINDOW_SCALE, boardHeight * utils.WINDOW_SCALE))

        self.map.init()

        self.player = player.Player(map.Tank('./OriginalTank.png'))
        playerTank = self.player.child
        x, y = playerTank.m_x, playerTank.m_y
        self.map.mapMatrix[x][y].append(playerTank)
        map.gameLayer.append(playerTank.rect)
        map.impassableLayer.append(playerTank.rect)
    
    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = Game()
        return cls.__instance

    def run(self):
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        self.clock.tick(utils.FPS)
        
        self.screen.fill((0, 170, 221))

        for i in map.updateable:
            i.update()
        for i in map.drawable:
            self.screen.drawSprite(i)

        utils.time += 1 / utils.FPS

        self.player.update()
        self.player.child.update()
        self.screen.drawSprite(self.player.child)

        # sscale = utils.WINDOW_SCALE
        # pygame.draw.circle(self.screen.getScreen(), (255, 0, 0), (round(self.player.child.x * scale) + utils.OFFSET_X + scale * utils.MAP_UNIT_SCALE/2,
        #  round(self.player.child.y * scale) + utils.OFFSET_Y + scale * utils.MAP_UNIT_SCALE/2), 5 * scale, 3)

        start = time.time()
        path = self.map.bfs(self.player.child.getMatrixPos(), (4,3))
        end = time.time()
        if len(timelist) >= 30:
            avg = sum(timelist) / len(timelist)
            timelist.pop(0)
            timelist[0] = avg
            print(avg)
        timelist.append(end-start)
        
        self.screen.drawLines(path)
        self.screen.update()