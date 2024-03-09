from constants import FOOD_OFFSET


def validate_data(nutrients, foods, food_header):
    # Make sure the labels match.
    for i, nutrient in enumerate(nutrients):
        if nutrient[0] != food_header[i + FOOD_OFFSET]:
            print(nutrient[0], "and", food_header[i + FOOD_OFFSET], "don't match")

    # Make sure the units are the same
    for i, nutrient in enumerate(nutrients):
        # Make sure the Nutritional Requirement row is consistent with itself.
        values = set()
        if nutrient[1][1] is not None:
            values.add(nutrient[1][1])
        if nutrient[2][1] is not None:
            values.add(nutrient[2][1])
        if nutrient[3] is not None:
            values.add(nutrient[3])
        if len(values) != 1:
            print("Problem!", nutrient)

        # Make sure the Nutritional Requirement unit is the same as all of the food units.
        for j, food in enumerate(foods):
            if food[i + FOOD_OFFSET][0] != 0:
                if nutrient[3] != food[i + FOOD_OFFSET][1]:
                    print(
                        "Another Problem!",
                        nutrient[3],
                        food[i + FOOD_OFFSET][1],
                        nutrient,
                        food[i + FOOD_OFFSET],
                        food[:FOOD_OFFSET],
                    )

    print("Data validated!")
