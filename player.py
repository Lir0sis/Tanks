import pygame
import utils

class Player:
    def __init__(self, child):
        self.child = child
        self.direction = [0.0, -1.0]
        self.prevPos = [0, 0]
        self.changedPos = False

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

        x, y = self.child.m_x, self.child.m_y
        if self.prevPos != [x, y]:
            self.changedPos = True
            self.prevPos = [x, y]
        else:
            self.changedPos = False

        

