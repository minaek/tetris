import game, random

ACTIONS = ["UP", "DOWN", "RIGHT", "LEFT", "SPACE", "Q"]

def calculateAggregateHeight(board):
    totalHeight = 0
    for x in range(BOARDWIDTH):
        column = board[x]   #starting from left
        temp = 0
        for y in range(len(column)):
            if(column[y] != '.'):
                temp = len(column) - y
                break
        totalHeight += temp
    return totalHeight

def calculateCompleteLines(board):
    totalCompleteLines = 0
    for y in range(game.BOARDHEIGHT):
        if(isCompleteLine(board,y)):
            totalCompleteLines += 1
    return totalCompleteLines

def calculateHoles(board):
    totalHoles = 0
    for x in range(game.BOARDWIDTH):
        column = board[x]   #starting from left
        temp = 0
        firstblock = False
        for y in range(len(column)):
            if(column[y] != '.'):
                firstblock = True
            if(firstblock and column[y] == '.'):
                temp+=1
        totalHoles += temp
    return totalHoles

def calculateBumpiness(board):
    heightList = []
    for x in range(game.BOARDWIDTH):
        column = board[x]   #starting from left
        temp = 0
        for y in range(len(column)):
            if(column[y] != '.'):
                temp = len(column) - y
                break
        heightList.append(temp)
    bumpiness = 0
    for z in range(len(heightList)-1):
        temp = abs(heightList[z] - heightList[z+1])
        bumpiness += temp
    return bumpiness


def generateBoardPositions():
    pass

def aiRand():
    randidx = random.randint(0, len(ACTIONS)-1)
    return ACTIONS[randidx]

if __name__ == '__main__':
    aiRand()


