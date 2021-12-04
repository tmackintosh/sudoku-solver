import numpy as np

sudokus = np.load("data/hard_puzzle.npy")
solutions = np.load("data/hard_solution.npy")
print(solutions[10])