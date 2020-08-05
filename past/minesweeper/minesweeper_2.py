# Implement minesweeper
#
# Same as initial version but rectangle and
# more object oriented

import random

class Grid:

    def __init__(self, n_rows, n_cols, n_mines):

        self.n_rows = n_rows
        self.n_cols = n_cols
        self.n_mines = n_mines
        self.grid = self.create_grid(n_rows, n_cols, n_mines)


    def create_grid(self, n_rows, n_cols, n_mines):

        # Initialize grid to zeros
        grid = [[0 for col in range(n_cols)] for row in range(n_rows)]

        # Randomly assign mines
        self.assign_mines(grid, n_rows, n_cols, n_mines)

        # Assign values to each grid based on placed bombs
        self.assign_values(grid, n_rows, n_cols)

        return grid


    def assign_mines(self, grid, n_rows, n_cols, n_mines):

        set_mines = 0
        while set_mines < n_mines:
            row = random.choice(range(0, n_rows))
            col = random.choice(range(0, n_cols))
            # Mark selected location as a bomb
            if grid[row][col] == 0:
                grid[row][col] = "b"
                set_mines += 1


    def assign_values(self, grid, n_rows, n_cols):

        for row in range(0, n_rows):
            for col in range(0, n_cols):
                if grid[row][col] != "b":
                    n_bombs = 0
                    # Check one to the right
                    if col < n_cols - 1:
                        if grid[row][col + 1] == "b":
                            n_bombs += 1
                    # Check one to the left
                    if col > 0:
                        if grid[row][col - 1] == "b":
                            n_bombs += 1
                    # Check one below
                    if row > 0:
                        if grid[row - 1][col] == "b":
                            n_bombs += 1
                    # Check one above
                    if row < n_rows - 1:
                        if grid[row + 1][col] == "b":
                            n_bombs += 1
                    grid[row][col] = n_bombs


if __name__ == "__main__":

    # Grid setup
    n_rows, n_cols, n_mines = 2, 3, 3

    # Create the grid
    grid = Grid(n_rows, n_cols, n_mines).grid

    # Initialize solution grid
    solution = [["X" for i in range(n_cols)] for j in range(n_rows)]

    # Start the game
    n_found, n_total = 0, n_rows * n_cols - n_mines
    while True:

        # Re-display game board
        for row in solution:
            print row

        # Ask for user input
        row_inp = int(raw_input("choose row: "))
        col_inp = int(raw_input("choose column: "))
        mark = raw_input("mark as portential bomb? (y/n): ")

        # Check input against grid
        if mark == "y":
            solution[row_inp][col_inp] = "?"
        else:
            if grid[row_inp][col_inp] == "b":
                game_status = "You Lost"
                break
            else:
                solution[row_inp][col_inp] = str(grid[row_inp][col_inp])
                n_found += 1
                if n_found == n_total:
                    game_status = "You Won"
                    break

    # Print solution
    for row in grid:
        print row

    print game_status


