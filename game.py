import random
import pygame
import sys
import map
import utils
import player
import time
import enemy
import enum

timelist = []

class State(enum.Enum):
    INPROCESS = 0
    WON = 1
    LOST = 2


class Screen:
    def __init__(self, width = 680, height = 680):
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

    def drawLinesByOne(self, vertices):
        if not vertices:
            return
        start_pos = vertices[0]
        scale = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
        offset = 0.5
        for end_pos in vertices:
            x, y = end_pos
            x2, y2 = start_pos
            pygame.draw.line(self._screen, utils.RED, 
                ((x + offset) * scale + utils.OFFSET_X, (y + offset) * scale + utils.OFFSET_Y), 
                ((x2 + offset) * scale + utils.OFFSET_X, (y2 + offset) * scale + utils.OFFSET_Y), width=1)
            start_pos = end_pos

            self.update()

    def drawLines(self, vertices):
        if not vertices:
            return
        start_pos = vertices[0]
        scale = utils.WINDOW_SCALE * utils.MAP_UNIT_SCALE
        offset = 0.5
        for end_pos in vertices:
            x, y = end_pos
            x2, y2 = start_pos
            pygame.draw.line(self._screen, utils.RED, 
                ((x + offset) * scale + utils.OFFSET_X, (y + offset) * scale + utils.OFFSET_Y), 
                ((x2 + offset) * scale + utils.OFFSET_X, (y2 + offset) * scale + utils.OFFSET_Y), width=1)
            start_pos = end_pos

    def drawPoints(self, vertices):
        if not vertices:
            return
        scale = utils.MAP_UNIT_SCALE * utils.WINDOW_SCALE
        radius = 0.5
        
        for pos in vertices:
            x, y = pos
            pygame.draw.circle(self._screen,utils.RED, 
            (x * scale + utils.OFFSET_X, y * scale + utils.OFFSET_Y), 
            radius * scale)

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
        self.state = State.INPROCESS
        self.clock = pygame.time.Clock()
        self.screen = Screen()
        self.map = map.Map(False, 'q-learn.lay')
        # self.path = []
        self.enemies = [enemy.StarAEnemy(None, 10000 + 1)]

        boardWidth, boardHeight = self.map._getBoardSize()
        utils.WINDOW_SCALE = self.screen.getScale((boardWidth, boardHeight))
        self.screen.setOffset((boardWidth * utils.WINDOW_SCALE, boardHeight * utils.WINDOW_SCALE))
        
        self.map.init()
        self.lastState = None
        self.points = None # utils.getNpoints(self.map.mapMatrix, 4)
        self.players = [player.QLearn(None, 1000 + 1)]#[player.MinMaxAssisted(None, 999 + 1)]
    
    @classmethod
    def getInstance(cls):
        if not cls.__instance:
            cls.__instance = Game()
        return cls.__instance

    def spawnPlayer(self, player, spawnPoins):
        lives = player.lives - 1
        if lives <= 0:
            return False
        
        spawn = random.choice(spawnPoins)
        x, y = spawn.m_x, spawn.m_y
        
        playerTank = map.Tank('tank.png', x * utils.MAP_UNIT_SCALE, 
            y * utils.MAP_UNIT_SCALE)
        player.__init__(playerTank, lives)
        self.map.mapMatrix[y][x].append(playerTank)
        return True

    def getPlayerIndex(self, player):
        return (self.players + self.enemies).index(player)

    def removeChild(self, player):
        if (player.child != None):
            player.child.rect = None

    def run(self):
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        self.clock.tick(utils.FPS)
        
        self.screen.fill(utils.BLACK)
        
        print(issubclass(type(map.Destroyable((0,0), 'coin')), map.Tile))

        if(self.state == State.WON or self.state == State.LOST) and not self.players[0].stopTraining():
            self.players[0].final(self.lastState[0])
            self.enemies[0].lives = 2
            self.players[0].lives = 2

        players_to_remove = []
        for player in self.players:
            if not player.child:
                if not self.spawnPlayer(player, map.playerSpawnPoints):
                   players_to_remove.append(player)
                   #self.lastState = self.map.getSimple()
        [self.removeChild(p) for p in players_to_remove]
        
        enemies_to_remove = []
        for player in self.enemies:
            if not player.child:
                if not self.spawnPlayer(player, map.enemySpawnPoints):
                    enemies_to_remove.append(player)
        [self.removeChild(p) for p in enemies_to_remove]

        if len(self.enemies) == 0:
            self.state = State.WON
            return
        elif len(self.players) == 0:
            self.state = State.LOST
            return

        for i in map.updatable:
            i.update()
        for i in map.drawable:
            self.screen.drawSprite(i)

        currTime = time.time()
        utils.deltaTime = currTime - utils.time
        utils.time = currTime

        for player in self.players + self.enemies:
            player.update()
            if player.child:
                if player.child.rect == None:
                    player.child = None
                    continue
                player.child.update()
                self.screen.drawSprite(player.child)
    
        if self.points and self.player.changedPos:
            to_visit = self.points.copy()
            nearest = self.player.child
            self.path = []

            start = time.time()
            while len(to_visit) > 0:
                item = nearest
                nearest = to_visit[0]
                x, y = item.m_x, item.m_y
                for p in to_visit:
                    dist1 = abs(p.m_x - x)**2 + abs(p.m_y - y)**2
                    dist2 = abs(nearest.m_x - x)**2 + abs(nearest.m_y - y)**2
                    
                    if dist1 < dist2:
                        nearest = p

                to_visit.remove(nearest)
               
                self.path += utils.starA((x, y), (nearest.m_x, nearest.m_y), self.map.mapMatrix, [self.player.child])
            end = time.time()
            # print(end - start)

        # start = time.time()
        # path = utils.dfs(self.player.child.getMatrixPos(), (4, 3), self.map.mapMatrix)
        # end = time.time()
        # if len(timelist) >= 30:
        #    avg = sum(timelist) / len(timelist)
        #    timelist.pop(0)
        #    timelist[0] = avg
        #    print(avg)
        #    self.screen.drawLines(path)
        # timelist.append(end-start)
        
        # self.screen.drawLines(self.path)

        self.screen.update()