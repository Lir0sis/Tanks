import pygame
import utils

class Player:
    def __init__(self, child):
        self.child = child
        self.direction = [0.0, -1.0]

    def update(self):
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

        

