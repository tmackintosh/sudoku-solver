<i>Abstract</i>: We need to create an agent that solves sudokus. To approach this, it is generally thought to write algorithms which solves sudokus through typical human-like inference. If there are still ambiguous values from these assignments, we can harness an agents power to efficiently perform searches given the right heuristics.

In this document, I outline my approach and reasoning to writing a Python program that is able to solve all sudokus.

<b>1 Introduction</b>

All sudoku problems can be generalised into a specific constraint satisfaction problem with the following properties:

- X is the set of variables that represent all cells on a 9x9 sudoku board.
- D is the set of domains, { 1, 2, 3 ... 7, 8, 9 }, that represent that values that can be in each cell.
- C is the set of constraints that determine legal placements of the domain in each cell:
    - There shall be no cells in the same column that have the same domain;
    - There shall be no cells in the same row that have the same domain;
    - There shall be no cells in the same unit that have the same domain.

A "unit" is a 3x3 box of cells, which can be placed themselves in a 3x3 grid of units, to create the 9x9 sudoku of cells.

As we've declared the sudoku problem into a constraint satisfaction problem, we open our opportunities to use all the general CSP solving algorithms and methodologies on sudoku.

It is theorised that an optimally efficient CSP implementation for a sudoku can solve any sudoku, valid or otherwise, in 0.1 seconds<sup>[1]</sup>.

<b>2 Formulating the Problem</b>

```
X = {
    A1, A2, A3, A4, A5, A6, A7, A8, A9,
    B1, B2, B3, B4, B5, B6, B7, B8, B9,
    C1, C2, C3, C4, C5, C6, C7, C8, C9,
    D1, D2, D3, D4, D5, D6, D7, D8, D9,
    E1, E2, E3, E4, E5, E6, E7, E8, E9,
    F1, F2, F3, F4, F5, F6, F7, F8, F9,
    G1, G2, G3, G4, G5, G6, G7, G8, G9,
    H1, H2, H3, H4, H5, H6, H7, H8, H9,
    I1, I2, I3, I4, I5, I6, I7, I8, I9
}

D = { 1, 2, 3, 4, 5, 6, 7, 8, 9 }

C = {   
        [ For each row ]
        alldiff(A1, A2, A3, A4, A5, A6, A7, A8, A9),
        alldiff(B1, B2, B3, B4, B5, B6, B7, B8, B9),
        alldiff(C1, C2, C3, C4, C5, C6, C7, C8, C9),
        alldiff(D1, D2, D3, D4, D5, D6, D7, D8, D9),
        alldiff(E1, E2, E3, E4, E5, E6, E7, E8, E9),
        alldiff(F1, F2, F3, F4, F5, F6, F7, F8, F9),
        alldiff(G1, G2, G3, G4, G5, G6, G7, G8, G9),
        alldiff(H1, H2, H3, H4, H5, H6, H7, H8, H9),
        alldiff(I1, I2, I3, I4, I5, I6, I7, I8, I9),

        [ For each column ]
        alldiff(A1, B1, C1, D1, E1, F1, G1, H1, I1),
        alldiff(A2, B2, C2, D2, E2, F2, G2, H2, I2),
        alldiff(A3, B3, C3, D3, E3, F3, G3, H3, I3),
        alldiff(A4, B4, C4, D4, E4, F4, G4, H4, I4),
        alldiff(A5, B5, C5, D5, E5, F5, G5, H5, I5),
        alldiff(A6, B6, C6, D6, E6, F6, G6, H6, I6),
        alldiff(A7, B7, C7, D7, E7, F7, G7, H7, I7),
        alldiff(A8, B8, C8, D8, E8, F8, G8, H8, I8),
        alldiff(A9, B9, C9, D9, E9, F9, G9, H9, I9),

        [ For each unit ]
        alldiff(A1, B1, C1, A2, B2, C2, A3, B3, C3),
        alldiff(D1, E1, F1, D2, E2, F2, D3, E3, F3),
        alldiff(G1, H1, I1, G2, H2, I2, G3, H3, I3),
        alldiff(A4, B4, C4, A5, B5, C5, A6, B6, C6),
        alldiff(D4, E4, F4, D5, E5, F5, D6, E6, F6),
        alldiff(G4, H4, I4, G5, H5, I5, G6, H6, I6),
        alldiff(A7, B7, C7, A8, B8, C8, A9, B9, C9),
        alldiff(D7, E7, F7, D8, E8, F8, D9, E9, F9),
        alldiff(G7, H7, I7, G8, H8, I8, G9, H9, I9),
}
```

It is always possible to reduce any individual constraint down to a set of individual binary constraints (such as `A1 != B1`), however this would result in 1680 constraints. This is too much to individually list, however can be easily calculated by a potential agent.

<b> 3 Representing the Problem</b>

Since I am programming in Python, there is efficient and easy ways to encapsulate and compartmentalize key aspects of any CSP problem by creating a problem object.

Creating an object allows us not only to mutate the state (such as eliminating a value from a variable's domain) but also allows us to keep track of different states easily by instantiating a slightly mutated object. Using these different objects in the same scope can make algorithms such as backtracking far easier as we're simply reverting back to a pre-existing object (a pre-existing state) without having to keep track of where we have been.

<b>4 Basic Inference</b>

It is well known that a great deal of inference can be done on any sudoku, that is eliminating potential values. According to Peter Norvig, there are 2 general inference methods that are the most powerful for a sudoku solving agent<sup>[2]</sup>.

1. If there is a value in the domain of a variable, for which one of the variable's peers has that value as an assignment, that value should be eliminated from the variable's domain.
1. If there is a value in the domain of a variable, for which none of the variable's peers has that value in their domain, that variable must have that value as an assignment.

With this information, we are greatly able to prune any potential search trees.

<b>5 Arc Consistency</b>

We know that a large part of our inference is ensuring that if there is an assignment, no peer to the variable can have the assigned value in its domain.

We can think of this in terms of the larger CSP solution, that any two variables that are peers have an arc.

And that an arc is consistent if the assignments to both variables are not equal.

```
A1 is not equal to A2 as it is in the same row
A1 is not equal to B1 as it is in the same column
A1 is not equal to B2 as it is in the same unit
```

We have already defined above that these inferences are part of our model's constraints. Therefore, in order to automatically infer that the domains of peer groups can be reduced, we simply need to uphold <b>arc consistency</b>.

There are multiple proven algorithms which can take any CSP and manipulate the domains to achieve arc consistency. In sudoku, all our arcs are very simple: this must not equal this. It makes sense then to use the most simple, yet effective, arc consistency algorithm: the AC-3 algorithm.

The AC-3 algorithm on sudokus is actually so powerful, that it will solve nearly puzzles that are not labelled "hard" in under 0.1 seconds.

It follows that all the puzzles that are not solved in under 0.1 seconds, are not solved at all. This is because there is always a finite amount of inference we can make on any sudoku puzzle - sometimes we cannot infer enough about a variable to definitely make an assignment (that our domains aren't restricted to only a single value).

<b>6 Searching</b>

When we cannot infer enough about a variable to determine which value to assign, we need to search through all potential values in order to see whether any are goal states.

If we assign a variable to a value such that our inference determines that the state is unsolvable, we know definitely that the value cannot be part of the variable's domain. Once this has been determined, we <i>backtrack</i> up to the variable again and assign something else.

This is known as <b>backtracking</b> and is actually provides our program with completeness, meaning it will <i>always</i> find a solution to the sudoku.

Unfortunately, although the program now has completeness, the search tree for our backtracking algorithm is very large even with the inference being used a pre-processing step. The average amount of time taken to solve the 15 hard sudoku puzzles is ~300 seconds (with a worst case of 468 seconds).

To deal with this, we need to add heuristics that will help us both cut the search tree, and also better inform us on intelligent ways to traverse the search tree.

<b>7 Maintaining Arc Consistency</b>

To reduce the search tree, after each new Sudoku object is instantiated, we should run our arc consistency algorithm as a pre-processing step. In the context of backtracking, this means that when backtracking assigns a value to a variable, we traverse through the variable's peers to reduce their domains. Therefore, we don't assign those eliminated values in a further backtracking attempt.

As we're running our arc-consistency whenever a value is assigned, we are <i>maintaining arc consistency</i>. It follows that, of the 15 hard sudokus solved by backtracking, we reduce the average time down to just 30 seconds per puzzle (albeit worst-case still being over 200 seconds).

<b>8 Most Constrained Variable Heuristic</b>

It's great reducing the search tree, but a major factor in reducing average case complexity is the intelligence in which the search tree is traversed. As shown in the Eight Queen's Problem of Russel and Norvig's book<sup>[1]</sup>, it is far more likely to run into a solution to the problem when you first assess (in backtracking) the variable that has the least values in its domain.

Take the square A1 has a domain of [3, 4] and the square I9 has a domain [1, 2, 6, 9]. As the A1 square has a smaller domain, there is a 1/2 chance that we guess the correct branch of the tree. Contrast this to the I9 square, where we only have a 1/4 chance.

Therefore, by ordering the variables by how constrained their domains are, we are more accurately going to guess the branch that has a solution in it. This is known as the Most Constrained Variable heuristic.

Upon implementing this, we can see solution times tumble to an average of just 9 seconds for the 15 hard sudokus with a worst-case of 17 seconds.

<b>9 Advanced Inference</b>

Further to arc consistency, a common way that humans would solve a sudoku is by looking at a peer group and determining that a variable must have an assignment of a value if that variable is the only place that a value can be.

For example, if the peer group column A was:

[ 3, 5, 1, 2, 9, 8, 7, _, 4 ]

we can easily determine that the final space is a 6 as there is nowhere else it could possibly be.

This inference isn't detected by arc consistency, as the variable doesn't have an assignment, no arcs or domains are inconsistent.

We can sum this inference up by the term:

- if there exists a value in a domain, for which no other peer has that value in their domains, the value must be assigned.

This seemingly small piece of inference further reduces the average-case for the 15 hard sudokus puzzles to an average of 5 seconds. However, the worst-case still remains at 17 seconds.

<b>10 Valid Peer Sets</b>

Inspecting the current times for all 15 hard sudokus, we can see that the puzzles that take the longest to solve are the puzzles that have no solutions.

This is because our backtracking algorithm is traversing the whole search tree and decides that a puzzle cannot have a solution when the search tree has been exhausted. There is a way to determine this way before a search tree has been exhausted.

We're able to cut entire branches off of search trees by assessing each peer group individually and seeing whether all values can be assigned. For example, take the following domains for a peer group:

[ 12, 245, 46, 9, 7, 15, 58, 1258, 24 ]

On first flace, it may look like no more inference can be made from this peer group. However, notice that in no domain does the value 3 exist. In other words, the value of 3 can never be assigned to any variable in that peer group. Hence, we know that this state is unsolvable.

This allows us to determine very early and cut entire branches from our search tree.

This simple addition makes our times drastically tumble to an average case of just 2 seconds and a worst case of just 5.9 seconds for the 15 hard sudokus.

<b> 11 Least Constraining Value</b>

The final heuristic to be discussed is the Least Constraining Value heuristic. This heuristic directs the backtracking algorithm to choose elements from a variable's domain in the order which constrains the least of the variable's peers.

In theory, this should reduce average case times as it is tackling the largest branches in order (and hence, tackling the branches with a higher chance of finding a solution).

However, in practice in the sudoku program, it actually slowed down our search. The average case rose to 9 seconds and the worst-case soared up to 21 seconds.

For this reason, I decided <b>not</b> to implement the LCV heuristic.

<b>12 Limitations</b>

The main limitation of this solution is the way that sudoku problem is represented in object form.

Yes, this means that we can compartmentalise key aspects of the problem and easily keep track of backtracking states - however they are very cumbersome to instantiate and to mutate leading to extra unnecessary time.

Perhaps it would be worth heading in a different representation direction by having the domains purely be a 2-dimensional array where each variable is referenced only by their index to that array.

Keep track of the search tree would be as easy as keeping track of which variable was assigned at each node, so we can reverse the assignment when backtracking up.

It seems also that the main bottleneck in the algorithm is the backtracking search for solutions in the hard example problems.

<b>13 Final Results</b>
```
All 60 example sudokus
======================
Time Taken: 29.140625
Best-Case: 0.015625
Average-Case: 0.48567708
Worst-Case: 8.21875
```

```
15 Very Easy example sudokus
============================
Time Taken: 0.921875
Best-Case: 0.046875
Average-Case: 0.061458333
Worst-Case: 0.078125
```

```
15 Easy example sudokus
=======================
Time Taken: 0.796875
Best-Case: 0.015625
Average-Case: 0.053125
Worst-Case: 0.078125
```

```
15 Medium example sudokus
=========================
Time Taken: 1.328125
Best-Case: 0.046875
Average-Case: 0.088541666
Worst-Case: 0.109375
```

```
15 Hard example sudokus
=======================
Time Taken: 26.0625
Best-Case: 0.15625
Average-Case: 1.7375
Worst-Case: 8.21875
```

<b>14 Conclusion</b>

We have implemented a Constraint Satisfaction Problem for the sudoku puzzle that can heavily outperform humans by exploiting inference and searching through potential assignments.

Although not as optimal as I would have liked, it is still an interesting way to show that puzzles can be abstracted and inferred using deduction.

<b><i>References</b></i>

1. Russell, S.J. & Norvig, P., 2016. Artificial intelligence : a modern approach Third edition / contributing writers, Ernest Davis [and seven others].; Global.,
1. Norvig, P. "Solving Every Sudoku Puzzle", Peter Norvig, https://norvig.com/sudoku.html. Accessed 04 Dec 2021