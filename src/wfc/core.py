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

    sum_of_possible_tile_weights = None
    sum_of_possible_tile_weight_log_weights = None

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

    def entropy(self) -> float:
        return log2(self.sum_of_possible_tile_weights) - (
            self.sum_of_possible_weight_log_weights / self.sum_of_possible_tile_weights
        )

    def __init__(self, input_core_data) -> None:
        self.core_data = input_core_data
        for tile in self.core_data.keys():
            self.possible[tile] = True


class CoreState:
    core_data = None

    def __init__(self, input_core_data) -> None:
        self.core_data = input_core_data

    def relative_frequency(self, tile_index) -> int:
        return self.frequency_hints[tile_index]

    def choose_next_cell(self) -> tuple:
        pass

    def collapse_cell_at(self, coord):
        pass

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
