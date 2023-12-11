import heapq
import random
from enum import Enum
from math import log2


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


NUM_DIRECTIONS = 4
ALL_DIRECTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]


class EntropyCoord:
    entropy: float = None
    coord: tuple = None

    def __init__(self, entropy, coord) -> None:
        self.entropy = entropy
        self.coord = coord

    def __lt__(self, other):
        return self.entropy < other.entropy


class RemovalUpdate:
    tile_index: int = None
    coord: tuple = None

    def __init__(self, tile_index, coord) -> None:
        self.tile_index = tile_index
        self.coord = coord


class TileEnablerCount:
    by_direction = 4

    def __init__(self, by_direction) -> None:
        self.by_direction = by_direction


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


class CoreState:
    core_data: CoreData = None
    entropy_heap = []
    tile_removals = []
    tile_enabler_counts = {}

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
                self.tile_removals.append(RemovalUpdate(tile_index, coord))

    def propagate(self):
        while len(self.tile_removals) > 0:
            removal_update = self.tile_removals.pop()
            for direction in ALL_DIRECTIONS:
                # neighbour_coord = removal_update.coord.neighbour(direction)
                # neighbour_cell = self.grid.get_mut(neighbour_coord)
                pass

        #         while let Some(removal_update) = self.tile_removals.pop() {
        #             // at some point in the recent past, removal_update.tile_index was
        #             // removed as a candidate for the tile in the cell at
        #             // removal_update.coord

        #             for &direction in ALL_DIRECTIONS.iter() {
        #                 // propagate the effect to the neighbour in each direction
        #                 let neighbour_coord = removal_update.coord.neighbour(direction);
        #                 let neighbour_cell = self.grid.get_mut(neighbour_coord);

        #                 // iterate over all the tiles which may appear in the cell one
        #                 // space in `direction` from a cell containing
        #                 // `removal_update.tile_index`
        #                 for compatible_tile in self.adjacency_rules.compatible_tiles(
        #                     removal_update.tile_index,
        #                     direction,
        #                 ) {

        #                     // relative to `neighbour_cell`, the cell at
        #                     // `removal_update.coord` is in the opposite direction to
        #                     // `direction`
        #                     let opposite_direction = opposite(direction);

        #                     // look up the count of enablers for this tile
        #                     let enabler_counts = &mut neighbour_cell
        #                         .tile_enabler_counts[compatible_tile];

        #                     // check if we're about to decrement this to 0
        #                     if enabler_counts.by_direction[direction] == 1 {

        #                         // if there is a zero count in another direction,
        #                         // the potential tile has already been removed,
        #                         // and we want to avoid removing it again
        #                         if !enabler_counts.contains_any_zero_count() {
        #                             // remove the possibility
        #                             neighbour_cell.remove_tile(
        #                                 compatible_tile,
        #                                 &self.frequency_hints,
        #                             );
        #                             // check for contradiction
        #                             if neighbour_cell.has_no_possible_tiles() {
        #                                 // CONTRADICTION!!!
        #                             }
        #                             // this probably changed the cell's entropy
        #                             self.entropy_heap.push(EntropyCoord {
        #                                 entropy: neighbour_cell.entropy(),
        #                                 coord: neighbour_coord,
        #                             });
        #                             // add the update to the stack
        #                             self.tile_removals.push(RemovalUpdate {
        #                                 tile_index: compatible_tile,
        #                                 coord: neoighbour_coord,
        #                             });
        #                         }
        #                     }

        #                     enabler_counts.by_direction[direction] -= 1;
        #                 }
        #             }
        #         }
        #     }
        # }

    def run(self):
        while self.remaining_uncollapsed_cells > 0:
            next_coord = self.choose_next_cell()
            self.collapse_cell_at(next_coord)
            self.propagate()
            self.remaining_uncollapsed_cells -= 1


def initial_tile_enabler_counts(num_tiles: int, adjacency_rules: dict) -> tuple:
    ret = []

    for tile_a in range(num_tiles):
        counts = TileEnablerCount([0, 0, 0, 0])

        for direction in ALL_DIRECTIONS:
            for tile_b in adjacency_rules[tile_a][direction]:
                counts.by_direction[direction] += 1

            ret.append(counts)
    return ret


def wfc_core(adjacency_rules, frequency_hints, output_size):
    core_data = CoreData(adjacency_rules, frequency_hints, output_size)
    core_state = CoreState(core_data)
