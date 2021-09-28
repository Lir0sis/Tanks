import game

# class Test:
#     def __init__(self):
#         self.test1 = 'sampleText'ііііііііііі



if __name__ == '__main__':
    # obj1 = Test()
    # obj2 = obj1
    # obj2.test1 = 'Nope'
    # # print(obj1.test1, obj2.test1)
    # # print('sssss')
    
    gameInst = game.Game.getInstance()

    while True:
        
        gameInst.run()