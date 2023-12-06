from operator import mul


class CoreCell:
    possible = []  # List of bool


class CoreState:
    grid = []  # 2D grid, corresponds to the output grid
    remaining_uncollapsed_cells = None
    adjacency_rules = None
    frequency_hints = None

    def __init__(
        self, input_adjacency_rules, input_frequency_hints, output_size
    ) -> None:
        self.adjacency_rules = input_adjacency_rules
        self.frequency_hints = input_frequency_hints
        self.remaining_uncollapsed_cells = mul(output_size[0], output_size[1])

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
    pass
