import game

if __name__ == '__main__':
    gameInst = game.Game.getInstance()

    while True:
        gameInst.run()