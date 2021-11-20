import numpy as np
import time
import math

from numpy.core.fromnumeric import var

difficulties = ["very_easy", "easy", "medium", "hard"]

class Sudoku:
    def __init__(self, values, variables = [], domains = [], constraints = [], columns = "ABCDEFGHI", numbers = "123456789", peers = {}):
        self.values = values
        
        self.variables = variables
        self.domains = domains
        self.constraints = constraints

        self.columns = columns
        self.rows = numbers

        self.peers = peers

        self.unsolvable = False

        self.create_variables()
        self.create_domains()
        self.create_constraints()

    def is_solved(self):
        if self.unsolvable:
            return True

        for constraint in self.constraints:
            operand1 = str(self.domains[constraint[0]])
            operand2 = str(self.domains[constraint[1]])
            operator = constraint[2]

            if int(operand1) > 9 or int(operand2) > 9:
                return False

            if not eval(operand1 + operator + operand2):
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
                new_domains[variable] = int(self.rows)
            else:
                new_domains[variable] = current_value

        self.domains = new_domains

    def create_peers(self, variable):
        peers = []

        column = self.columns.find(variable[0:1])
        row = self.rows.find(variable[1:2])

        top_left = (math.floor(column / 3), math.floor(row / 3))

        for character in self.columns:
            if character == variable[0:1] and str(self.columns.find(character) + 1) == variable[1:2]:
                continue

            peers.append(character + str(row + 1))
            peers.append(variable[0:1] + str(self.columns.find(character) + 1))

        for i in range (0, 3):
            for j in range (0, 3):
                column_to_add = self.columns[i + (3 * top_left[0])]
                row_to_add = self.rows[j + (3 * top_left[1])]
                square_to_add = column_to_add + row_to_add

                if square_to_add not in peers and square_to_add != variable:
                    peers.append(square_to_add)

        self.peers[variable] = peers

    def create_constraints(self):
        constraints = []

        for variable in self.variables:
            self.create_peers(variable)

            for peer in self.peers[variable]:
                if variable != peer:
                    constraints.append([variable, peer, "!="])

        self.constraints = constraints

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

    def get_variable_column(self, variable):
        column = self.columns.find(variable[0:1])

        numbers = []
        for i in range (0, 9):
            numbers.append(self.values[column, i])

        return numbers

    def get_variable_row(self, variable):
        row = self.rows.find(variable[1:2])

        numbers = []
        for i in range (0, 9):
            numbers.append(self.values[i, row])

        return numbers

    def get_variable_unit(self, variable):
        row = self.rows.find(variable[1:2])
        column = self.columns.find(variable[0:1])

        unit_number = (math.floor(column / 3), math.floor(row / 3))
        numbers = []

        for i in range (0, 3):
            cell_column = unit_number[0] + i

            for j in range (0, 3):
                cell_row = unit_number[1] + i

                numbers.append(self.values[cell_column][cell_row])

        return numbers

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

# Least constraining value
def select_value(problem, starting_variable):
    possible_values = problem.domains[starting_variable]
    peers = problem.peers[starting_variable]

    constrained_variables_count = []
    least_constrained_values = []

    for value in str(possible_values):
        constrained_variables = 0

        for peer in peers:
            if str(problem.domains[peer]).find(str(value)):
                constrained_variables += 1

        constrained_variables_count.append(constrained_variables)
        constrained_variables_count.sort()
        index = constrained_variables_count.index(constrained_variables)
        least_constrained_values.insert(index, value)
        
    return least_constrained_values

# Most constrained variable heuristic
def select_unassigned_variable(problem):
    most_constrained_variable = None
    possible_values = np.inf

    for variable in problem.variables:
        domain = problem.domains[variable]

        if domain < 10:
            continue

        if domain < possible_values:
            possible_values = domain
            most_constrained_variable = variable

    return most_constrained_variable

# Assign values to variables under the heuristic and assess whether they've
# valid or not. If not, backtrack up and start again using a different value.
def backtrack(problem, depth = 0):
    if problem.is_solved():
        return problem

    starting_variable = select_unassigned_variable(problem)
    possible_values = select_value(problem, starting_variable)

    column = problem.columns.find(starting_variable[0:1])
    row = problem.rows.find(starting_variable[1:2])

    select_value(problem, starting_variable)

    for character in possible_values:
        value = int(character)
        
        new_values = problem.values.copy()
        new_values[column][row] = value

        new_sudoku = Sudoku(new_values)

        AC3(new_sudoku)

        # AC3 sets unsolvable to true on failure
        if not new_sudoku.unsolvable:
            result = backtrack(new_sudoku, depth + 1)

            if not new_sudoku.unsolvable:
                return result

        # Remove from domain
        location = possible_values.index(character)
        new_str = possible_values[:location] + possible_values[location + 1:]

        new_domain = ""
        for element in new_str:
            new_domain = new_domain + str(element)

        problem.domains[starting_variable] = new_domain

    problem.unsolvable = True
    return problem

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

        for sudoku in sudokus:
            start_time = time.process_time()

            problem = Sudoku(sudoku)

            AC3(problem)
            
            if not problem.is_solved():
                problem = backtrack(problem)

            problem = backtrack(problem)

            end_time = time.process_time()

            correct = np.array_equal(problem.get_sudoku(), solutions[count])
            test_time = end_time - start_time
            
            if not correct:
                print("Failed test", count)
                failed += 1
            else:
                print("Test passed", test_time)

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