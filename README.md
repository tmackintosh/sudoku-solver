<i>Abstract</i>: Implementing a constraint satisfaction problem with backtracking is able to solve all sudoku examples very quickly.

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

It is always possible to reduce any individual constraint down to a set of individual binary constraints (such as `A1 != B1`), however given the size of each alldiff constraint this would be a lot of constraints.

Given our programmatic ability to iterate through a set and make each binary constraint individually, defining each would be unnecessary.

<b>3 Algorithm Selection</b>

- AC-3: O(cd^3) where c is number of binary constraints, d is domain
- K-consistency: O(n^2d), but very difficult to compute and high space complexity

The AC-3 algorithm is one that seems sufficient to solve sudokus to the untrained eye, with its systematic removal of options in a similar (albeit not exact) way to how a human would perhaps tackle it.

However it has a major pitfall, not only does it have a polynomial time complexity (O(cd<sup>3</sup>)<sup>[1]</sup>, it also isn't complete. For example, it could present multiple options for each cell despite all these "options" being consistent.

Backtracking is a methodology that caught my eye for some time

Another option for solving sudokus would be using various arc-consistency methods. Many pieces of online software and academic papers have been written<sup>[2]</sup> about using various arc-consistency methods to reduce computations in backtracking algorithms.

However, the complexity of these seems too far for me to replicate in a reasonable amount of time given that the objectives for this project is to become comfortable with implementing CSPs.

<b><i>References</b></i>

1. p214; Artificial Intelligence, a Modern Approach (Third Edition); Russel S, Norvig P