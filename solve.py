# Sudoku Solver #

import numpy as np
import time
import math

difficulties = ["very_easy", "easy", "medium", "hard"]

"""
Sudoku class allows us to instantiate objects that can abstract the problem.
"""
class Sudoku:
    def __init__(self, values, variables = [], constraints = [], peers = {}, peer_groups = {}):
        """
        Instantiates a new Sudoku object that can abstract each state and be manipulated to keep track of state progress.

        @param values: 2D List of values, or 0 where there is no value
        @param variables: List of all variables (squares) in the state (sudoku). For example: "A1", "I9".
        @param constraints: List of all constraints in the state. For example: ["A1", "I9", "!="]
        @param peers: Dictionary of every variable's peers where the key is the variable and the value is the list of peers.
        @param peer_groups: Dictionary of every variable's peer groups, such as the list of variables in its row, column and unit.

        @returns Newly created Sudoku object
        """

        # Values are the initial inputs in the Sudoku.
        # Used to create constraints and restrict domains.
        self.values = values

        self.columns = "ABCDEFGHI"
        self.rows = "123456789"

        # Peers dictionaries allow us easy look up of a variable's peers without
        # having to iterate through the whole state.
        self.peers = peers
        self.peer_groups = peer_groups
        
        # Typical CSP formulation
        self.variables = variables or self.create_variables()
        self.constraints = constraints or self.create_constraints()
        self.domains = self.create_domains()

        self.unsolvable = False

    def is_solved(self):
        """
        Assesses the domains of the whole table and returns whether the state is a
        goal state.

        @returns Boolean of whether the state is a goal state.
        """
        if self.unsolvable:
            return True

        for constraint in self.constraints:
            operand1 = constraint[0]
            operand2 = constraint[1]
            operator = constraint[2]
        
            domain1 = str(self.domains[operand1])
            domain2 = str(self.domains[operand2])

            if not eval(domain1 + operator + domain2):
                return False

        return True

    def create_variables(self):
        """
        Generates a list of all variables in a Sudoku state, such as "A1", "I9"

        @returns List of newly created variables
        """
        variables = []

        for character in self.columns:
            for number in self.rows:
                cell_id = character + number
                
                if cell_id not in variables:
                    variables.append(cell_id)

        return variables

    def create_domains(self):
        """
        Generates a dictionary for the domain of each variable to be all 9 numbers 
        except values that already have a set value, where the domain is simply
        that value.

        Keys are strings
        Domains are integers to allow integer comparison when assessing states

        ["A1"] = 123456789
        ["I9"] = 7

        @returns List of newly created dictionary of each variable's domain.
        """
        new_domains = {}

        for variable in self.variables:
            column = self.columns.find(variable[0:1])
            row = self.rows.find(variable[1:2])

            current_value = self.values[column][row]

            # If there is no set value assigned to a variable, it has a value of 0
            if current_value == 0:
                new_domains[variable] = int(self.rows)
            else:
                new_domains[variable] = current_value

        return new_domains

    def create_peers(self, variable):
        """
        Generates the lists of peers and peer groups for the variable.

        Peers is simply a list of the peer variables.
        Peer groups are split into 3 lists representing peers in, respectively, the same:
            - row
            - column
            - unit

        @param variable: String of the variable name to generate peers for

        @returns None
        """
        peers = []
        peer_groups = [ [], [], [] ]

        variable_column = variable[0:1]
        variable_row = variable[1:2]

        column = self.columns.find(variable_column)
        row = self.rows.find(variable_row)

        # Top left of the unit allows us to easy generate the unit peers.
        top_left = (math.floor(column / 3), math.floor(row / 3))

        for peer_column in self.columns:
            peer_row = self.columns.find(peer_column) + 1

            # Don't generate the variable as its own peer
            if peer_column == variable_column and str(peer_row) == variable_row:
                continue

            peers.append(peer_column + str(row + 1))
            peers.append(variable_column + str(peer_row))

            if peer_column + str(row + 1) != variable:
                peer_groups[0].append(peer_column + str(row + 1))

            if (variable_column + str(peer_row)) != variable:
                peer_groups[1].append(variable_column + str(peer_row))

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
        """
        Generates a list of all constraints for the Sudoku CSP

        @returns List of generated constraints.
        """
        constraints = []

        for variable in self.variables:
            self.create_peers(variable)

            for peer in self.peers[variable]:
                if variable != peer and not [peer, variable, "!="] in constraints:
                    constraints.append([variable, peer, "!="])

        return constraints

    def get_sudoku(self):
        """
        Generates a typical array of values from the state's domains.
        Or generates a numpy array of -1 if the state is a non-solvable
        state.

        @returns Array of values in the state or numpy array of -1s if the state is unsolvable
        """
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
    """
    Determines whether a value should be removed from a variable's domain
    as one of the variable's peers has the value as an assignment.

    @param domain2: int of the domain we're checking against
    @param valueA: character of the value we're assessing is in the domain
    @param operator: a string representing the Python notation for a comparison, for example: "!=", "==", ">"

    @returns boolean of whether the element should be removed from the domain
    """
    for valueB in str(problem.domains[domain2]):
        if eval(str(valueA) + operator + str(valueB)):
            return False

    return True

def AC3(problem):
    """
    Arc-Consistency 3 Algorithm

    Given the current problem's state, iterate through the constraints
    and remove values from variable's domains when an inconsistency is
    detected.

    Follow this up by checking any peers that may have been affected by
    this removal for further inference.

    This provides complete arc consistency in the state by manipulating
    the problem parameter directly.

    @param problem: CSP object to manipulate for arc-consistency

    @returns boolean: whether any values in the domain were removed
    """

    # Keep track of whether any values have been changed so inference
    # knows to keep arc consistency after a potential peer consistency
    # check.
    changed = False
    agenda = []

    for constraint in problem.constraints:
        # Add both the constraint, and the reverse of the constraint to
        # the agenda.
        agenda.append(constraint)
        agenda.append([constraint[1], constraint[0], constraint[2]])

    while len(agenda) > 0:
        constraint = agenda.pop()
        
        domain1 = constraint[0]
        domain2 = constraint[1]
        operator = constraint[2]

        # Keep track of removals to remove them
        # after the initial iteration has completed as
        # the domains should be immutable while they're
        # being iterated through
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

            problem.domains[domain] = int(problem.domains[domain])

    return changed

def valid_peer_set(problem):
    """
    Determine whether we can render the state as unsolvable by seeing
    whether there are any variable domains which cannot be put into
    a peer group. 
    
    For example, if there is no place for a 7 in row A, we know the
    state is unsolvable.

    @returns boolean of whether all peer groups are consistent
    """
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

        # If a number hasn't been seen in any domain in the peer
        # group, we know it can't be assigned into this peer group
        if len(list) != 9:
            problem.unsolvable = True
            return False

    return True

# Peer consistency
def peer_consistency(problem):
    """
    If there is only 1 place that a value can go in a peer group,
    we know the value must go there.
    """
    # Keep track of whether any domains have been changed so
    # inference knows to keep peer consistency if any domains
    # were changed by a further arc consistency check.
    changed = False

    for variable in problem.variables:
        domain = problem.domains[variable]

        # A variable has 1 domain if it is already assigned
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

                    # We may be able to infer further values after
                    # this variable is assigned.
                    peer_consistency(problem)

                    changed = True
                    break

    return changed

def inference(problem):
    """
    Given the assignments of the states, we are able to reduce and remove
    values from each variables domain through arc consistency and peer
    consistency.

    @returns the mutated CSP object after inference
    """
    arcs_changed = AC3(problem)
    peers_changed = peer_consistency(problem)

    if problem.unsolvable:
        return problem

    if not valid_peer_set(problem):
        problem.unsolvable = True
        return problem

    if (peers_changed or arcs_changed):
        return inference(problem)
    else:
        return problem

def select_unassigned_variable(problem):
    """
    Select the most constrained variable in a state to give us
    the best chance of reducing the search tree to find a solution.

    @returns the variable name of the most constrained variable
    """
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

def backtrack(problem, depth = 0):
    """
    Assign a value to a variable given suitable heuristics and check
    whether the new state is a goal state. If not, backtrack up to
    the previous assignment and try a new value.

    @param problem: CSP to search for goal states

    @returns new or mutated CSP object in a goal state or unsolvable state
    """
    if problem.is_solved():
        return problem

    # Most constrained value heuristic
    starting_variable = select_unassigned_variable(problem)
    possible_values = str(problem.domains[starting_variable])

    column = problem.columns.find(starting_variable[0:1])
    row = problem.rows.find(starting_variable[1:2])

    for character in possible_values:
        value = int(character)
        
        new_values = problem.values.copy()
        new_values[column][row] = value

        # Create new sudoku object with new assignments so we can keep
        # the previous assignments in the stack in case this one fails
        new_sudoku = Sudoku(new_values, variables = problem.variables, constraints = problem.constraints, peers = problem.peers, peer_groups = problem.peer_groups)

        if depth != 0:
            inference(new_sudoku)

        if not new_sudoku.unsolvable:
            result = backtrack(new_sudoku, depth + 1)

            if not result.unsolvable:
                return result

        # Remove from domain
        location = possible_values.index(character)
        problem.domains[starting_variable] = possible_values[:location] + possible_values[location + 1:]

    # If we've tried every value with no success, we know there are no possibilites
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
            inference(problem)
            
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