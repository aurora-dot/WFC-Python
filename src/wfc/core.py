import heapq
import random
from collections import deque
from copy import deepcopy
from math import log2

from wfc.shared import Direction


class ContradictionException(BaseException):
    pass


NUM_DIRECTIONS = 4
ALL_DIRECTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
OPPOSITE = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}


def initial_tile_enabler_counts(adjacency_rules: dict) -> tuple:
    ret = {}

    for tile_a in adjacency_rules:
        counts = [0, 0, 0, 0]

        for direction in ALL_DIRECTIONS:
            if direction in adjacency_rules[tile_a]:
                for tile_b in adjacency_rules[tile_a][direction]:
                    counts[direction.value] += 1

            ret[tile_a] = counts

    return ret


class CoreData:
    adjacency_rules = None
    frequency_hints = None
    output_size = None
    grid = []  # 2D grid, corresponds to the output grid
    remaining_uncollapsed_cells = None

    def __init__(
        self, input_adjacency_rules, input_frequency_hints, input_output_size
    ) -> None:
        self.adjacency_rules = input_adjacency_rules
        self.frequency_hints = input_frequency_hints
        self.output_size = input_output_size

        self.remaining_uncollapsed_cells = self.output_size[0] * self.output_size[1]

        for x in range(self.output_size[0]):
            self.grid.append([])
            for _ in range(self.output_size[1]):
                self.grid[x].append(CoreCell(self))


class Coord:
    coord: tuple = None
    core_data: CoreData = None

    def __init__(self, coord, core_data) -> None:
        self.coord = coord
        self.core_data = core_data

    def neighbour(self, direction):
        match direction:
            case Direction.UP:
                if self.coord[0] == 0:
                    return None
                else:
                    return (self.coord[0] - 1, self.coord[1])
            case Direction.DOWN:
                if self.coord[0] == len(self.core_data.grid):
                    return None
                else:
                    return (self.coord[0] + 1, self.coord[1])
            case Direction.LEFT:
                if self.coord[1] == 0:
                    return None
                else:
                    return (self.coord[0], self.coord[1] - 1)
            case Direction.RIGHT:
                if self.coord[1] == len(self.core_data.grid[0]):
                    return None
                else:
                    return (self.coord[0], self.coord[1] + 1)


class EntropyCoord(Coord):
    entropy: float = None

    def __init__(self, entropy, coord, core_data) -> None:
        super().__init__(coord, core_data)
        self.entropy = entropy

    def __lt__(self, other):
        return self.entropy < other.entropy


class RemovalUpdate(Coord):
    tile_index: int = None
    coord: tuple = None

    def __init__(self, tile_index, coord, core_data) -> None:
        super().__init__(coord, core_data)
        self.tile_index = tile_index


class CoreCell:
    possible = {}  # dic of int:bool
    core_data = None

    is_collapsed = False

    sum_of_possible_tile_weights = None
    sum_of_possible_tile_weight_log_weights = None

    entropy_noise = random.uniform(0.0000001, 0)

    tile_enabler_counts = {}

    def total_possible_tile_frequency(self, freq_hint: dict):
        total = 0
        for tile_index, is_possible in self.possible.items():
            if is_possible:
                total += freq_hint[tile_index]

    def remove_tile(self, tile_index, freq_hint):
        self.possible[tile_index] = False
        freq = freq_hint[tile_index]

        self.sum_of_possible_tile_weights -= freq
        self.sum_of_possible_tile_weight_log_weights -= freq * log2(freq)

    def choose_tile_index(self, frequency_hints):
        remaining = random.randint(0, self.sum_of_possible_tile_weights)

        for possible_tile_index in self.possible.keys():
            weight = frequency_hints[possible_tile_index]

            if remaining >= weight:
                remaining -= weight
            else:
                return possible_tile_index

        raise Exception(
            "sum_of_possible_weights was inconsistent with possible_tile_iter and frequency_hints"
        )

    def entropy(self) -> float:
        entropy = log2(self.sum_of_possible_tile_weights) - (
            self.sum_of_possible_tile_weight_log_weights
            / self.sum_of_possible_tile_weights
        )
        return entropy + self.entropy_noise

    def __init__(self, input_core_data) -> None:
        self.core_data: CoreData = input_core_data
        for tile in self.core_data.frequency_hints.keys():
            self.possible[tile] = True

        self.sum_of_possible_tile_weights = sum(
            [i for i in self.core_data.frequency_hints.values()]
        )
        self.sum_of_possible_tile_weight_log_weights = sum(
            [i * log2(i) for i in self.core_data.frequency_hints.values()]
        )

        self.tile_enabler_counts = initial_tile_enabler_counts(
            self.core_data.adjacency_rules
        )


class CoreState:
    core_data: CoreData = None
    entropy_heap = []
    tile_removals: deque = deque()

    def __init__(self, input_core_data) -> None:
        self.core_data = input_core_data

    def set_initial_entropy_heap(self):
        for x in range(len(self.core_data.grid)):
            for y in range(len(self.core_data.grid[x])):
                heapq.heappush(
                    self.entropy_heap,
                    EntropyCoord(
                        self.core_data.grid[x][y].entropy(),
                        (x, y),
                        self.core_data,
                    ),
                )

    def relative_frequency(self, tile_index) -> int:
        return self.frequency_hints[tile_index]

    def choose_next_cell(self) -> tuple:
        while len(self.entropy_heap) != 0:
            entropy_coord = heapq.heappop(self.entropy_heap)
            cell: CoreCell = self.core_data.grid[entropy_coord.coord[0]][
                entropy_coord.coord[1]
            ]
            if not cell.is_collapsed:
                return entropy_coord.coord

        raise Exception("entropy_heap is empty, but there are still uncollapsed cells")

    def collapse_cell_at(self, coord):
        cell: CoreCell = self.core_data.grid[coord[0]][coord[1]]
        tile_index_to_lock_in = cell.choose_tile_index(self.core_data.frequency_hints)
        cell.is_collapsed = True

        for tile_index in cell.possible.keys():
            if tile_index != tile_index_to_lock_in:
                cell.possible[tile_index] = False
                self.tile_removals.append(
                    RemovalUpdate(tile_index, coord, self.core_data)
                )

    def propagate(self):
        while len(self.tile_removals) > 0:
            removal_update = self.tile_removals.pop()
            for direction in ALL_DIRECTIONS:
                neighbour_coord: RemovalUpdate = removal_update.neighbour(direction)
                if neighbour_coord:
                    neighbour_cell: CoreCell = self.core_data.grid[neighbour_coord[0]][
                        neighbour_coord[1]
                    ]

                    for compatible_tile in self.core_data.adjacency_rules[
                        removal_update.tile_index
                    ][direction]:
                        opposite_direction = OPPOSITE[direction]
                        print(neighbour_cell.tile_enabler_counts)
                        enabler_counts = neighbour_cell.tile_enabler_counts[
                            compatible_tile
                        ]
                        if enabler_counts[direction.value] == 1:
                            if 0 not in enabler_counts:
                                neighbour_cell.remove_tile(
                                    compatible_tile, self.core_data.frequency_hints
                                )
                                if len(neighbour_cell.possible) == 0:
                                    raise ContradictionException()

                                heapq.heappush(
                                    self.entropy_heap,
                                    EntropyCoord(
                                        neighbour_cell.entropy(),
                                        neighbour_coord,
                                        self.core_data,
                                    ),
                                )
                                self.tile_removals.append(
                                    RemovalUpdate(
                                        compatible_tile, neighbour_coord, self.core_data
                                    )
                                )

                        neighbour_cell.tile_enabler_counts[compatible_tile][
                            direction.value
                        ] -= 1

    def run(self):
        while self.core_data.remaining_uncollapsed_cells > 0:
            next_coord = self.choose_next_cell()
            self.collapse_cell_at(next_coord)
            self.propagate()
            self.core_data.remaining_uncollapsed_cells -= 1


def wfc_core(adjacency_rules, frequency_hints, output_size):
    core_data = CoreData(adjacency_rules, frequency_hints, output_size)
    core_state = CoreState(core_data)
    core_state.set_initial_entropy_heap()

    core_state.run()

    output_grid = deepcopy(core_data.grid)
    for x in range(len(core_state.grid)):
        for y in range(len(core_state.grid[x])):
            possible_tile_indexes = [
                index
                for index, possible in core_state.grid[x][y].possible.items()
                if possible
            ]
            if len(possible_tile_indexes) != 1:
                raise Exception()

            tile_index = possible_tile_indexes[0]
            output_grid[x][y] = tile_index

    return output_grid
