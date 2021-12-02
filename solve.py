import numpy as np
import time
import math

from numpy.core.fromnumeric import var

difficulties = ["hard"]

class Sudoku:
    def __init__(self, values, variables = [], domains = [], constraints = [], columns = "ABCDEFGHI", numbers = "123456789", peers = {}, peer_groups = {}):
        self.values = values
        
        self.variables = variables
        self.domains = domains
        self.constraints = constraints

        self.columns = columns
        self.rows = numbers

        self.peers = peers
        self.peer_groups = peer_groups

        self.unsolvable = False

        if self.variables == []:
            self.create_variables()

        if self.domains == []:
            self.create_domains()

        if self.constraints == []:
            self.create_constraints()

    def is_solved(self):
        if self.unsolvable:
            return True

        for constraint in self.constraints:
            domain0 = str(self.domains[constraint[0]])
            domain1 = str(self.domains[constraint[1]])
            if not eval(domain0 + constraint[2] + domain1):
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
        peer_groups = [ [], [], [] ]

        column = self.columns.find(variable[0:1])
        row = self.rows.find(variable[1:2])

        top_left = (math.floor(column / 3), math.floor(row / 3))

        for character in self.columns:
            if character == variable[0:1] and str(self.columns.find(character) + 1) == variable[1:2]:
                continue

            peers.append(character + str(row + 1))
            peers.append(variable[0:1] + str(self.columns.find(character) + 1))

            if character + str(row + 1) != variable:
                peer_groups[0].append(character + str(row + 1))

            if (variable[0:1] + str(self.columns.find(character) + 1)) != variable:
                peer_groups[1].append(variable[0:1] + str(self.columns.find(character) + 1))

        for i in range (0, 3):
            for j in range (0, 3):
                column_to_add = self.columns[i + (3 * top_left[0])]
                row_to_add = self.rows[j + (3 * top_left[1])]
                square_to_add = column_to_add + row_to_add

                if square_to_add not in peers and square_to_add != variable:
                    peers.append(square_to_add)

                if square_to_add != variable:
                    peer_groups[2].append(square_to_add)

        self.peers[variable] = peers
        self.peer_groups[variable] = peer_groups

    def create_constraints(self):
        constraints = []

        for variable in self.variables:
            self.create_peers(variable)

            for peer in self.peers[variable]:
                if variable != peer and not [peer, variable, "!="] in constraints:
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

def element_should_be_removed(problem, domain2, valueA, operator):
    for valueB in str(problem.domains[domain2]):
        if eval(str(valueA) + operator + str(valueB)):
            return False

    return True

def AC3(problem):
    changed = False
    agenda = []

    for constraint in problem.constraints:
        agenda.append(constraint)
        agenda.append([constraint[1], constraint[0], constraint[2]])

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
            changed = True

            if problem.domains[domain] == "":
                problem.unsolvable = True
                return False

            problem.domains[domain] = int(str(problem.domains[domain]))

    return changed

def valid_peer_set(problem):
    peer_groups = problem.peer_groups
    
    for variable in peer_groups:
        list = str(problem.domains[variable])
        group = peer_groups[variable]
        
        for compare in group:
            for new_variable in compare:
                domain = problem.domains[new_variable]
                for character in str(domain):
                    if character not in list:
                        list = list + character

        if len(list) != 9:
            problem.unsolvable = True
            return False

    return True

# Peer consistency
def peer_consistency(problem):
    changed = False

    for variable in problem.variables:
        domain = problem.domains[variable]

        if len(str(domain)) == 1:
            continue

        for value in str(domain):
            for group in problem.peer_groups[variable]:
                unique = True

                for peer in group:
                    if value in str(problem.domains[peer]):
                        unique = False
                        break

                if unique:
                    problem.domains[variable] = int(value)
                    peer_consistency(problem)
                    changed = True
                    break

    return changed

def inference(problem):
    peers_changed = peer_consistency(problem)
    arcs_changed = AC3(problem)

    if problem.unsolvable:
        return problem

    if not valid_peer_set(problem):
        problem.unsolvable = True
        return problem

    if (peers_changed or arcs_changed):
        return inference(problem)
    else:
        return problem

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
    possible_values = str(problem.domains[starting_variable])

    column = problem.columns.find(starting_variable[0:1])
    row = problem.rows.find(starting_variable[1:2])

    for character in possible_values:
        value = int(character)
        
        new_values = problem.values.copy()
        new_values[column][row] = value

        new_sudoku = Sudoku(new_values, variables = problem.variables, constraints = problem.constraints, peers = problem.peers, peer_groups = problem.peer_groups)

        if depth != 0:
            new_sudoku = inference(new_sudoku)

        if not new_sudoku.unsolvable:
            result = backtrack(new_sudoku, depth + 1)

            if not result.unsolvable:
                return result

        # Remove from domain
        location = possible_values.index(character)
        problem.domains[starting_variable] = possible_values[:location] + possible_values[location + 1:]

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
            problem = inference(problem)
            
            if not problem.is_solved():
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
        print(total_time / 15, "average solution.")
        print("-")

    print("Shortest time in total:", global_shortest_time)
    print("Longest time in total:", global_longest_time)

main()