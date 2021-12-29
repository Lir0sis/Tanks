import random
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


class QLearn():
    def __init__(self, child, lives, alpha=0.2, gamma=0.8, epsilon=0.9, numTraining = 500):
        self.opponents = None
        self.lives = lives
        self.child = child
        self.direction = (0.0, -1.0)
        if child:
            self.prevPos = (child.m_x, child.m_y)
        self.changedPos = True
        self.stored_action = None
        self.currentMove = (0, 0)
        self.nextMove = (0, 0)
        self.game = None

        # QLearn parameters
        self.episodes = 0
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

        self.current_episode = 0
        self.episodes
        self.numTraining = numTraining

        self.q_table = utils.Counter()
        self.score = 0
        self.history = []

    def get_q(self, state, action): ##DONE
        return self.q_table[(state, action)]

    def get_max_q(self, state): ##DONE
        qs = [self.get_q(state, action) for action in state.getActions(self.game.getPlayerIndex(self))]
        if qs:
            return max(qs)
        else:
            0

    def get_action(self, state): ##DONE
        actions = state.getActions(self.game.getPlayerIndex(self))
        reward = state.getScore() - self.score

        if self.history:
            last_state, last_action = self.history[-1]
            q = self.get_q(last_state, last_action)
            max_q = self.get_max_q(state)
            self.q_table[(last_state, last_action)] = \
                  q + self.alpha * (reward + self.gamma * max_q)

        if random.random() < self.epsilon:
            action = random.choice(actions)
        else:
            action = self.pick_action(state)
            
        self.score = state.getScore()
        self.history.append((state, action))

        self.stored_action = action
        return self.stored_action

    def pick_action(self, state): ##DONE
        actions = state.getActions(self.game.getPlayerIndex(self))

        return max([(action, self.get_q(state, action)) for action in actions], key=lambda x: x[1])[0]

    def update(self):
        ##if (self.episodes > )
        if not self.child:
            return

        if not self.game:
            self.game = game.Game.getInstance()
            self.oponents = self.game.enemies

        if self.changedPos or any([o.changedPos for o in self.oponents]):
            action = self.get_action(self.game.map.getSimple())
            self.nextMove = action[1]

        isMoving = self.currentMove != None

        if(not self.currentMove):
            if(self.nextMove):
                self.currentMove = self.stored_action[1]
                if(self.stored_action[0]):
                    self.direction = self.stored_action[1]
                    self.child.action()


        self.direction = self.currentMove

        self.direction = self.currentMove

        self.child.setDirection(self.direction, isMoving)
        self.child.action()

        x, y = utils.getCenteredMatrixCoord(self.child.x + utils.MAP_UNIT_SCALE/2), utils.getCenteredMatrixCoord(self.child.y + utils.MAP_UNIT_SCALE/2)
        if self.prevPos != [x, y]:
            self.changedPos = True
            self.prevPos = [x, y]
            self.currentMove = None
        else:
            self.changedPos = False

    def stopTraining(self):
        return self.episodes == self.numTraining

    def final(self, state):
        print(self.episodes, self.score)

        reward = state.getScore() - self.score
        last_state, last_action = self.history[-1]
        q = self.get_q(last_state, last_action)

        self.q_table[(last_state, last_action)] = \
                  q + self.alpha * (reward + self.gamma * 0)

        self.score = 0
        self.lastState = []
        self.lastAction = []

        epsilon = 1 - self.episodes * 1.0 / self.numTraining

        self.epsilon = epsilon * 0.1

        self.episodes = self.episodes + 1

        if self.episodes % 10 == 0:
            print(f"Completed {self.episodes()}")

        if self.stopTraining():
            pass

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
