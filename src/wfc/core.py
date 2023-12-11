import heapq
import random
from math import log2


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

        for x in self.output_size[0]:
            self.grid.append([])
            for _ in self.output_size[1]:
                self.grid[x].append(CoreCell(self.frequency_hints))


class CoreCell:
    possible = {}  # dic of int:bool
    core_data = None

    is_collapsed = False

    sum_of_possible_tile_weights = None
    sum_of_possible_tile_weight_log_weights = None

    entropy_noise = random.uniform(0.00001, 0.009)

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

        raise (
            "sum_of_possible_weights was inconsistent with possible_tile_iter and frequency_hints"
        )

    def entropy(self) -> float:
        entropy = log2(self.sum_of_possible_tile_weights) - (
            self.sum_of_possible_weight_log_weights / self.sum_of_possible_tile_weights
        )
        return entropy + self.entropy_noise

    def __init__(self, input_core_data) -> None:
        self.core_data = input_core_data
        for tile in self.core_data.keys():
            self.possible[tile] = True


class EntropyCoord:
    entropy: float = None
    coord: tuple = None

    def __lt__(self, other):
        return self.entropy < other.entropy


class CoreState:
    core_data: CoreData = None
    entropy_heap = []

    def __init__(self, input_core_data) -> None:
        self.core_data = input_core_data

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

        raise ("entropy_heap is empty, but there are still uncollapsed cells")

    def collapse_cell_at(self, coord):
        cell: CoreCell = self.core_data.grid[coord[0]][coord[1]]
        tile_index_to_lock_in = cell.choose_tile_index(self.core_data.frequency_hints)
        cell.is_collapsed = True

        for tile_index in cell.possible.keys():
            if tile_index != tile_index_to_lock_in:
                cell.possible[tile_index] = False

    def propagate(self):
        pass

    def run(self):
        while self.remaining_uncollapsed_cells > 0:
            next_coord = self.choose_next_cell()
            self.collapse_cell_at(next_coord)
            self.propagate()
            self.remaining_uncollapsed_cells -= 1


def wfc_core(adjacency_rules, frequency_hints, output_size):
    core_data = CoreData(adjacency_rules, frequency_hints, output_size)
    core_state = CoreState(core_data)
