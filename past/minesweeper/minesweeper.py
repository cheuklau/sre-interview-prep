# Implement minesweeper
#
# User selects a grid size.
# Randomly assign mines to grid points.
# For each other grid point calculate how many
# neighboring grid points are mines and
# assign that total to it.
# User will select a grid point:
# If it is a mine, game is over.
# If it is not a mine, display the number
# of neighboring mines.
#

import random

# User input for grid size
size = 10

# Number of mines
num_mines = int(0.20 * size * size)

# Initialize grid
grid = [[0 for i in range(size)] for j in range(size)]

# Randomly assign mine positions
set_mines = 0
while set_mines < num_mines:
    x = random.choice(range(0, size))
    y = random.choice(range(0, size))
    if grid[x][y] == 0:
        grid[x][y] = "b"
        set_mines += 1

# Assign value to each grid point
for x in range(0, size):
    for y in range(0, size):
        if grid[x][y] != "b":
            tmp = 0
            # Check one above
            if y < size - 1:
                if grid[x][y + 1] == "b":
                    tmp += 1
            # Check one below
            if y > 0:
                if grid[x][y - 1] == "b":
                    tmp += 1
            # Check one to the left
            if x > 0:
                if grid[x - 1][y] == "b":
                    tmp += 1
            # Check one to the right
            if x < size - 1:
                if grid[x + 1][y] == "b":
                    tmp += 1
            grid[x][y] = tmp

# Initialize solution grid
solution = [["X" for i in range(size)] for j in range(size)]

# Start the game
game_over = False
while not game_over:

    # Re-display game board
    for row in solution:
        print row

    # Ask user for input
    x_user = int(raw_input("choose row: "))
    y_user = int(raw_input("choose column: "))
    mark_user = raw_input("bomb (y/n): ")

    if mark_user == "y":
        solution[x_user][y_user] = "?"
    else:
        if grid[x_user][y_user] == "b":
            game_over = True
        else:
            solution[x_user][y_user] = str(grid[x_user][y_user])

if game_over:
    print "You lost"
else:
    print "You won"

for row in grid:
    print row



