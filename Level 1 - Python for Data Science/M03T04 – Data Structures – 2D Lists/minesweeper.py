import random

mine = "#"
nomine = "-"

def create_grid(rows=5, cols=5):
    choice = [mine, nomine]
    grid = []
    for _ in range(rows):
        rowlist = [random.choice(choice) for _ in range(cols)]
        grid.append(rowlist)
    return grid

def get_offsets():
    offsets = []
    for r in [-1, 0, 1]:
        row = []
        for c in [-1, 0, 1]:
            if not (r == 0 and c == 0):  
                row.append([r, c])
        offsets.append(row)
    return offsets


def count_bombs(grid, row, col):
    offsets = get_offsets()
    count = 0
    for r_list in offsets:
        for dr, dc in r_list:
            nr = row + dr
            nc = col + dc
            if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
                if grid[nr][nc] == mine:
                    count += 1
    return count


def build_count_grid(grid):
    count_grid = []
    for r in range(len(grid)):
        row_list = []
        for c in range(len(grid[0])):
            if grid[r][c] == mine:
                row_list.append(mine)
            else:
                row_list.append(str(count_bombs(grid, r, c)))
        count_grid.append(row_list)
    return count_grid


def print_grid(grid):
    for row in grid:
        print(" ".join(row))


grid = create_grid()
print("Original Grid:")
print_grid(grid)

print("\nBomb Count Grid:")
count_grid = build_count_grid(grid)
print_grid(count_grid)
