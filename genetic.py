import random, ai
import numpy as np
#initializing vectors
NUM_PARAMS = 4

#Creates a p vector
# class Individual:
#   def __init__(self, height, cleared, holes, bump):
#     self.h = height
#     self.c = cleared
#     self.ho = holes
#     self.b = bump

def genIndividual ():
  height = random.randint(-50,50)
  complete = random.randint(-50,50)
  holes = random.randint(-50,50)
  bump = random.randint(-50,50)
  return np.array([height,complete,holes,bump])

def makePopulation (size):
  population = np.empty([NUM_PARAMS,size])
  for i in range(0,size):
    population[i] = genIndividual()
  print population

#fitness function is equal to total # of lines cleared
def fitness(ind, board):
  num_cleared = ai.calculateCompleteLines(board)


if __name__ == '__main__':
    makePopulation(4)
