import numpy as np
import time

difficulties = ["hard"]

class Sudoku:
    def __init__(self, values, variables = [], domains = [], constraints = [], columns = "ABCDEFGHI", numbers = "123456789"):
        self.values = values
        
        self.variables = variables
        self.domains = domains
        self.constraints = constraints

        self.columns = columns
        self.rows = numbers

        self.unsolvable = False

        self.create_variables()
        self.create_constraints()
        self.create_domains()

    def is_solved(self):
        if self.unsolvable:
            return True

        for domain in self.domains:
            if self.domains[domain] > 9 or self.domains[domain] == 0:
                return False

        return True

    def create_variables(self):
        for character in self.columns:
            for number in self.rows:
                cell_id = character + number
                
                if cell_id not in self.variables:
                    self.variables.append(cell_id)

    def create_domains(self):
        new_domains = {}

        for variable in self.variables:
            column = self.columns.find(variable[0:1])
            row = self.rows.find(variable[1:2])

            current_value = self.values[column][row]

            if current_value == 0:
                new_domains[variable] = self.rows
            else:
                new_domains[variable] = current_value

        self.domains = new_domains

    def create_constraints(self):
        self.alldiff("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9")
        self.alldiff("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9")
        self.alldiff("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9")
        self.alldiff("D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9")
        self.alldiff("E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9")
        self.alldiff("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9")
        self.alldiff("G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8", "G9")
        self.alldiff("H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9")
        self.alldiff("I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9")

        self.alldiff("A1", "B1", "C1", "D1", "E1", "F1", "G1", "H1", "I1")
        self.alldiff("A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "I2")
        self.alldiff("A3", "B3", "C3", "D3", "E3", "F3", "G3", "H3", "I3")
        self.alldiff("A4", "B4", "C4", "D4", "E4", "F4", "G4", "H4", "I4")
        self.alldiff("A5", "B5", "C5", "D5", "E5", "F5", "G5", "H5", "I5")
        self.alldiff("A6", "B6", "C6", "D6", "E6", "F6", "G6", "H6", "I6")
        self.alldiff("A7", "B7", "C7", "D7", "E7", "F7", "G7", "H7", "I7")
        self.alldiff("A8", "B8", "C8", "D8", "E8", "F8", "G8", "H8", "I8")
        self.alldiff("A9", "B9", "C9", "D9", "E9", "F9", "G9", "H9", "I9")
        
        self.alldiff("A1", "B1", "C1", "A2", "B2", "C2", "A3", "B3", "C3")
        self.alldiff("A4", "B4", "C4", "A5", "B5", "C5", "A6", "B6", "C6")
        self.alldiff("A7", "B7", "C7", "A8", "B8", "C8", "A9", "B9", "C9")
        self.alldiff("D1", "E1", "F1", "D2", "E2", "F2", "D3", "E3", "F3")
        self.alldiff("D4", "E4", "F4", "D5", "E5", "F5", "D6", "E6", "F6")
        self.alldiff("D7", "E7", "F7", "D8", "E8", "F8", "D9", "E9", "F9")
        self.alldiff("G1", "H1", "I1", "G2", "H2", "I2", "G3", "H3", "I3")
        self.alldiff("G4", "H4", "I4", "G5", "H5", "I5", "G6", "H6", "I6")
        self.alldiff("G7", "H7", "I7", "G8", "H8", "I8", "G9", "H9", "I9")
        
    def alldiff(self, *args):
        for arg1 in args:
            for arg2 in args:
                if arg1 != arg2 and [arg1, arg2, "!="] not in self.constraints:
                    self.constraints.append([arg1, arg2, "!="])

    def get_sudoku(self):
        sudoku = []

        if self.unsolvable:
            return np.full((9, 9), -1)

        for row in self.columns:
            new_row = []

            for column in self.rows:
                new_row.append(self.domains[row + column])

            sudoku.append(new_row)

        return sudoku

class Node:
    def __init__(self, problem, parent = None):
        self.parent = parent
        self.problem = problem
        self.children = []

    def insert_child(self, problem):
        self.children.append(problem)

def element_should_be_removed(problem, domain2, valueA, operator):
    for valueB in str(problem.domains[domain2]):
        if eval(str(valueA) + operator + str(valueB)):
            return False

    return True

def AC3(problem):
    agenda = []

    for constraint in problem.constraints:
        agenda.append(constraint)

    count = 0

    while len(agenda) > 0:
        count += 1
        constraint = agenda.pop()
        
        domain1 = constraint[0]
        domain2 = constraint[1]
        operator = constraint[2]

        removals = []

        for value in str(problem.domains[domain1]):
            if element_should_be_removed(problem, domain2, value, operator):
                removals.append([value, domain1])

                for original_constraint in problem.constraints:
                    if original_constraint[1] == domain1 and original_constraint not in agenda:
                        agenda.append(original_constraint)

        for removal in removals:
            value = removal[0]
            domain = removal[1]

            location = str(problem.domains[domain]).find(value)
            problem.domains[domain] = str(problem.domains[domain])[:location] + str(problem.domains[domain])[location + 1:]

            if problem.domains[domain] == "":
                problem.unsolvable = True
                return

            problem.domains[domain] = int(str(problem.domains[domain]))

def backtrack(node):
    print("Backtrack")
    if node.problem.is_solved():
        return node.problem

    domains = []

    for domain in node.problem.domains:
        if len(str(node.problem.domains[domain])) > 1:
            domains.append((node.problem.domains[domain], domain))
            
    for domain in domains:
        shortest_domain = domain[0]
        shortest_domain_cell = domain[1]
        
        column = node.problem.columns.find(str(shortest_domain_cell)[0:1])
        number = node.problem.rows.find(str(shortest_domain_cell)[1:2])

        new_values = node.problem.values.copy()

        for character in str(shortest_domain):
            new_values[column][number] = int(character)
            new_problem = Sudoku(new_values)

            AC3(new_problem)

            if node.problem.is_solved():
                print("Solved")
                return node.problem
            if node.problem.unsolvable:
                print("Unsolvable")
                return False

            node.insert_child(Node(new_problem))

        for child in node.children:
            result = backtrack(child)

            if result is not None and result != False and not result.unsolvable:
                return result

    return Sudoku(np.full((9, 9), -1))

def main():
    global_longest_time = 0
    global_shortest_time = np.inf

    for difficulty in difficulties:
        print("Testing", difficulty)
        sudokus = np.load("data/" + difficulty + "_puzzle.npy")
        solutions = np.load("data/" + difficulty + "_solution.npy")

        count = 0
        sudoku_to_solve = 2
        failed = 0
        total_time = 0
        longest_time = 0
        shortest_time = np.inf

        # for sudoku in sudokus:
        start_time = time.process_time()

        # problem = Sudoku(sudoku)
        problem = Sudoku(sudokus[sudoku_to_solve])

        AC3(problem)
        problem = backtrack(Node(problem))

        end_time = time.process_time()

        correct = np.array_equal(problem.get_sudoku(), solutions[sudoku_to_solve])
        # correct = np.array_equal(problem.get_sudoku(), solutions[count])
        if not correct:
            print("Test failed.")
            failed += 1

        test_time = end_time - start_time
        if test_time > longest_time:
            longest_time = test_time
        if test_time < shortest_time:
            shortest_time = test_time

        total_time += test_time

        count += 1

        # No indent
        if longest_time > global_longest_time:
            global_longest_time = longest_time
        if shortest_time < global_shortest_time:
            global_shortest_time = shortest_time

        print("Testing complete")
        print(failed, "tests failed.")
        print(longest_time, "was the longest solution.")
        print(shortest_time, "was the shortest solution.")
        print(total_time, "was taken in total.")
        print("-")

    print("Shortest time in total:", global_shortest_time)
    print("Longest time in total:", global_longest_time)

main()