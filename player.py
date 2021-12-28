import pygame
import game
import utils

class Player:
    def __init__(self, child, lives):
        self.lives = lives
        self.child = child
        self.direction = [0.0, -1.0]
        self.prevPos = [None, None]
        self.changedPos = True

    def update(self):
        if not self.child:
            return
        keys = pygame.key.get_pressed()
        keypressed = False
        if keys[pygame.K_w]:
            self.direction = [0.0, -1.0]
            keypressed = True
        elif keys[pygame.K_a]:
            self.direction = [-1.0, 0.0]
            keypressed = True
        elif keys[pygame.K_s]:
            self.direction = [0.0, 1.0]
            keypressed = True
        elif keys[pygame.K_d]:
            self.direction = [1.0, 0.0]
            keypressed = True
        
        if keys[pygame.K_SPACE]:
            self.child.action()
        self.child.setDirection(self.direction, keypressed)

        x, y = utils.getCenteredMatrixCoord(self.child.x + utils.MAP_UNIT_SCALE/2), utils.getCenteredMatrixCoord(self.child.y + utils.MAP_UNIT_SCALE/2)
        if self.prevPos != [x, y]:
            self.changedPos = True
            self.prevPos = [x, y]
        else:
            self.changedPos = False


class MinMaxAssisted():
    def __init__(self, child, lives):
        self.oponents = None
        self.lives = lives
        self.child = child
        self.direction = (0.0, -1.0)
        if child:
            self.prevPos = (child.m_x, child.m_y)
        self.changedPos = True
        self.game = None

    def update(self):
        if not self.child:
            return

        if not self.game:
            self.game = game.Game.getInstance()

        self.oponents = self.game.enemies
        isMoving = False
        
        action, move = None, None
        if self.changedPos or any([o.changedPos for o in self.oponents]):
            action, move = utils.miniMax(3, self.game)

        if action:
            self.direction = action
            self.child.action()
            isMoving = False
        if move:
            self.direction = move
            isMoving = True

        self.child.setDirection(self.direction, isMoving)

        x, y = utils.getCenteredMatrixCoord(self.child.x + utils.MAP_UNIT_SCALE/2), utils.getCenteredMatrixCoord(self.child.y + utils.MAP_UNIT_SCALE/2)
        if self.prevPos != (x, y) and x != None and y != None:
            self.changedPos = True
            self.prevPos = (x, y)
        else:
            self.changedPos = False

        

