import random as rnd
import game
import map
import utils

class RandomEnemy:
    def __init__(self, child, lives):
        self.lives = lives
        self.child = child
        self.direction = [0, -1]
        self.actionReadiness = 0
        self.game = None
        self.m_posNext = [0, 0]
        self.timeUntilChoice = 0.0
        if child:
            self.prevPos = [child.m_x, child.m_y]
        self.changedPos = True
        self.game = None 



    def update(self):
        if not self.child:
            return

        if not self.game:
            self.game = game.Game.getInstance()

        self.frendlies = [f.child for f in self.game.enemies]

        weights = None
        if self.timeUntilChoice > 1.8:
            weights = (85, 15)
            self.timeUntilChoice = 0
        else:
            weights = (180, 5)
        self.timeUntilChoice += utils.deltaTime

        m_x, m_y = self.child.m_x, self.child.m_y
        neighbours = utils.getLegalNeighbours((m_x, m_y), self.game.map.mapMatrix, [self.child])
        pos = rnd.choice(neighbours)
        direction = (pos[0] - m_x, pos[1] - m_y)

        dxy = (self.direction[0] + m_x, self.direction[1] + m_y)

        x, y = utils.getCenteredMatrixCoord(self.child.x + utils.MAP_UNIT_SCALE/2), \
            utils.getCenteredMatrixCoord(self.child.y + utils.MAP_UNIT_SCALE/2)

        if (dxy) in neighbours or not (x or y):
            self.m_posNext = rnd.choices([dxy, pos], weights=weights, k=1)[0]
            self.direction = (self.m_posNext[0] - m_x, self.m_posNext[1] - m_y)
        else:
            self.direction = direction
            self.m_posNext = pos

        if not all(isinstance(i, map.Destroyable) for i in self.game.map.mapMatrix[self.m_posNext[1]][self.m_posNext[0]]):
            self.actionReadiness = 100
        else:
            self.actionReadiness += rnd.choice([1,10,20,50,250]) * utils.deltaTime

        if self.actionReadiness >= 100:
            if self.child.action(self.frendlies):
                self.actionReadiness = 0

        self.child.setDirection(self.direction, True)

        if self.prevPos != [m_x, m_y]:
            self.changedPos = True
            self.prevPos = [m_x, m_y]
        else:
            self.changedPos = False

class StarAEnemy:
    def __init__(self, child, lives) -> None:
        self.oponents = None
        self.lives = lives
        self.child = child
        self.direction = (0.0, -1.0)
        self.changedPos = True
        # self.m_posNext = [0, 0]
        self.path = None
        if child:
            self.prevPos = [child.m_x, child.m_y]
        self.currentMove = (0, 0)
        self.nextMove = (0, 0)
        self.game = None
        
    def update(self):
        if not self.child:
            return

        if not self.game:
            self.game = game.Game.getInstance()
            self.oponents = self.game.players
            self.frendlies = [f.child for f in self.game.enemies]

        isMoving = self.currentMove != None

        if self.changedPos or any([o.changedPos for o in self.oponents]):
            self.path = utils.starA(
                (self.child.m_x, self.child.m_y), 
                (self.oponents[0].child.m_x, self.oponents[0].child.m_y),
                self.game.map.mapMatrix, self.frendlies + [self.oponents[0].child])
            self.path = self.path[1:]
            if(len(self.path) >= 1):
                self.nextMove = (
                    self.path[0][0] - self.prevPos[0], 
                    self.path[0][1] - self.prevPos[1])
            
        if(not self.currentMove):
            if(self.nextMove):
                self.currentMove = self.nextMove

        self.direction = self.currentMove

        self.child.setDirection(self.direction, isMoving)
        self.child.action()
        #self.game.state.queueAction()
        x, y = utils.getCenteredMatrixCoord(self.child.x + utils.MAP_UNIT_SCALE/2, 0.45), \
            utils.getCenteredMatrixCoord(self.child.y + utils.MAP_UNIT_SCALE/2, 0.45)

        if self.prevPos != [x, y] and x != None and y != None:
            self.changedPos = True
            self.prevPos = [x, y]
            self.currentMove = None
        else:
            self.changedPos = False