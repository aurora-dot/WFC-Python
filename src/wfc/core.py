from random import sample


class Wave:
    patterns = None
    freqs = None
    adjacencies = None

    grid = None
    entropies = None

    def __init__(self, dimensions, input_frequencies, input_adjacencies) -> None:
        w, h = dimensions

        self.patterns = input_frequencies.keys()
        self.freqs = input_frequencies.values()
        self.adjacencies = input_adjacencies

        pattern_length = len(input_frequencies)

        self.grid = [
            [True for pattern in range(pattern_length)] for cell in range(w * h)
        ]
        self.entropies = dict(
            enumerate(
                sample(
                    tuple(
                        pattern_length if i > 0 else pattern_length - 1
                        for i in range(w * h)
                    ),
                    w * h,
                )
            )
        )
        print(set(self.entropies.values()))

    def run(self):
        while self.entropies:
            pass

        return self.grid


def wfc_core(adjacency_rules, frequency_hints, output_size):
    wave = Wave(output_size, frequency_hints, adjacency_rules)
