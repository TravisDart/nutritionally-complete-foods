NUMBER_SCALE = 1_000  # CP-SAT only does integers, so scale to use 3 decimal places.
FOOD_OFFSET = 4  # The first 4 columns of the food data are labels.
MAX_NUMBER = 5_000_000

KNOWN_SOLUTIONS = {
    4: [
        # No, this actually isn't a correct solution.
        [
            (9024, 2759),
            (11672, 1006),
            (14091, 1199),
            (14355, 804),
        ],
        [
            (9068, 3382),
            (11672, 913),
            (14091, 1227),
            (14355, 804),
        ],
    ],
}
