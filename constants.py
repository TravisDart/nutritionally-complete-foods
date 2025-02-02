# CP-SAT only does integers, and no nutrient or requirement is less than .001, so scale to make .001 * NUMBER_SCALE = 1.
# This value affects both the number of decimal places to which the source data is rounded
# and the scale of the integer variables in the CP-SAT model.
NUMBER_SCALE = 1_000

# The solver uses 3 decimal places, but the source data uses 5 decimal places of precision.
# Using more precision helps the SQL calculations a bit.
# Note that NUMBER_SCALE and DATA_DECIMAL_PLACES are describing the same thing in different ways.
DATA_DECIMAL_PLACES = 5

FOOD_OFFSET = 2  # The first few columns of the food data are labels.

DB_URL = "postgresql://postgres:pg_password@localhost:5432/food"

USDA_NUTRIENT_NAMES = [
    "Calcium, Ca",
    "Carbohydrate, by difference",
    "Choline, total",
    "Copper, Cu",
    "Energy",
    "Total lipid (fat)",
    "Fiber, total dietary",
    "Folate, total",
    "Iron, Fe",
    "Magnesium, Mg",
    "Manganese, Mn",
    "Niacin",
    "Phosphorus, P",
    "Potassium, K",
    "Protein",
    "Riboflavin",
    "Selenium, Se",
    "Sodium, Na",
    "Thiamin",
    "Vitamin A, RAE",
    "Vitamin B-6",
    "Vitamin C, total ascorbic acid",
    "Vitamin D (D2 + D3)",
    "Vitamin E (alpha-tocopherol)",
    "Vitamin K (phylloquinone)",
    "Zinc, Zn",
]

# This is actually unused at the moment, but might come in handy sometime.
# quantity * UNIT_CONVERSION[unit] = quantity_in_grams
UNIT_CONVERSION = {
    "g": 1.0,
    "µg": 1.0 / 1_000_000,
    "mg": 1.0 / 1_000,
    "kcal": 1.0,
}

NUTRIENT_UNITS = [
    "mg",  # calcium
    "g",  # carbohydrate
    "mg",  # choline
    "mg",  # copper
    "kcal",  # energy
    "g",  # fat
    "g",  # total_fiber
    "µg",  # folate
    "mg",  # iron
    "mg",  # magnesium
    "µg",  # manganese
    "mg",  # niacin
    "mg",  # phosphorus
    "mg",  # potassium
    "g",  # protein
    "mg",  # riboflavin
    "µg",  # selenium
    "mg",  # sodium
    "mg",  # thiamin
    "µg",  # vitamin_a
    "mg",  # vitamin_b6
    "mg",  # vitamin_c
    "µg",  # vitamin_d
    "mg",  # vitamin_e
    "µg",  # vitamin_k
    "mg",  # zinc
]

NUTRIENT_NAMES = [  # Columns of the CSV that are in SQL.
    "calcium",
    "carbohydrate",
    "choline",
    "copper",
    "energy",
    "fat",
    "total_fiber",
    "folate",
    "iron",
    "magnesium",
    "manganese",
    "niacin",
    "phosphorus",
    "potassium",
    "protein",
    "riboflavin",
    "selenium",
    "sodium",
    "thiamin",
    "vitamin_a",
    "vitamin_b6",
    "vitamin_c",
    "vitamin_d",
    "vitamin_e",
    "vitamin_k",
    "zinc",
]

# fmt: off
TOP_FOODS = [
    35205, 11525, 11270, 9009, 4058, 11946, 11987, 11458, 16001, 11637, 11939, 20076, 2041, 2028, 35074,
    16062, 16076, 42200, 16055, 12169, 11625, 4047, 11977, 11297, 20003, 11230, 4583, 43146, 16067,
    2003, 4534, 11291, 11097, 12171, 16111, 11591, 11276, 11819, 11976, 20072, 4044, 16396, 4511, 4060,
    11161, 2012, 16085, 12029, 4531, 12163, 35093, 11003, 16390, 11086, 4582, 4506, 11087, 11683, 11432,
    4541, 11292, 11982, 2022, 11269, 2015, 2044, 11277, 9139, 2023, 11152, 11165, 4584, 16019, 4588,
    12078, 2066, 4536, 14353, 2009, 35207, 11112, 11660, 11268, 11162, 20077, 11941, 12023, 16078,
    12198, 11588, 16389, 9148, 20138, 35196, 35232, 12698, 11026, 20078, 11334, 12024, 11993, 11952,
    11419, 11113, 11245, 4581, 2007, 4516, 11529, 2013, 11953, 11506, 2033, 11936, 4517, 9002, 11271,
    11158, 4502, 11208, 9244, 11569, 11214, 4053, 11027, 4529, 16080, 35194, 9221, 11239, 16133, 12174,
    11098, 11467, 11937, 9041, 4042, 12170, 11667, 16392, 11234, 20027, 4501, 11931, 11974, 4528, 9129,
    2024, 11240, 9116, 11293, 2046, 2017, 9001, 11967, 12006, 42231, 11203, 12012, 11938, 2016, 11023,
    11300, 12040, 20015, 9147, 20068, 16112, 4055, 4514, 9289, 2021, 20071, 43143, 11530, 11333, 11979,
    4518, 2029, 4513, 16135, 2047, 11998, 16394, 4038, 12036, 12193, 4515, 2038, 4037, 11988, 16060,
    9183, 9165, 2010, 43365, 11141, 11096, 4530, 12037, 16108, 2011, 2020, 4572, 11983, 12005, 11207,
    2042, 11301, 2006, 11955, 11052, 2027, 12039, 16091, 12220, 11099, 11284, 2014, 2039, 16056, 11663,
    2043, 16116, 48052, 4573, 11505, 12038, 11527, 16410, 11670, 11147, 11204, 31019, 4669, 2036, 14368,
    11233, 11110, 35203, 2037, 11090, 16132, 4510, 11962, 11978, 12160, 4532, 2008, 11957, 11615, 20060,
    11242, 2031, 11148, 16115
]

KNOWN_SOLUTIONS = {
    4: [
        [
            (9221, 5653),  # Fruits and Fruit Juices > Tangerine juice, raw
            (12038, 202),  # Nut and Seed Products > Seeds, sunflower seed kernels, oil roasted, without salt
            (11939, 115),  # Vegetables and Vegetable Products > Mushrooms, portabella, exposed to ultraviolet light, grilled
            (2009, 76),  # Spices and Herbs > Spices, chili powder
        ], [
            (9221, 5237),  # Fruits and Fruit Juices > Tangerine juice, raw
            (12038, 210),  # Nut and Seed Products > Seeds, sunflower seed kernels, oil roasted, without salt
            (11993, 130),  # Vegetables and Vegetable Products > Mushrooms, maitake, raw
            (2009, 65),  # Spices and Herbs > Spices, chili powder
        ], [
            (9221, 5609),  # Fruits and Fruit Juices > Tangerine juice, raw
            (12038, 197),  # Nut and Seed Products > Seeds, sunflower seed kernels, oil roasted, without salt
            (2009, 107),  # Spices and Herbs > Spices, chili powder
            (11936, 102),  # Vegetables and Vegetable Products > Mushrooms, brown, italian, or crimini, exposed to ultraviolet light, raw
        ], [
            (9221, 5726),  # Fruits and Fruit Juices > Tangerine juice, raw
            (12038, 196),  # Nut and Seed Products > Seeds, sunflower seed kernels, oil roasted, without salt
            (11938, 180),  # Vegetables and Vegetable Products > Mushroom, white, exposed to ultraviolet light, raw
            (2009, 84),  # Spices and Herbs > Spices, chili powder
        ],
    ],
    18: [
        [
            (9009, 276),  # Fruits and Fruit Juices > Apples, dehydrated (low moisture), sulfured, uncooked
            (11268, 107),  # Vegetables and Vegetable Products > Mushrooms, shiitake, dried
            (11284, 88),  # Vegetables and Vegetable Products > Onions, dehydrated flakes
            (4531, 60),  # Fats and Oils > Oil, soybean lecithin
            (48052, 49),  # Cereal Grains and Pasta > Vital wheat gluten
            (2007, 37),  # Spices and Herbs > Spices, celery seed
            (11936, 34),  # Vegetables and Vegetable Products > Mushrooms, brown, italian, or crimini, exposed to ultraviolet light, raw
            (42231, 31),  # Fats and Oils > Oil, flaxseed, cold pressed
            (11615, 28),  # Vegetables and Vegetable Products > Chives, freeze-dried
            (42200, 14),  # Legumes and Legume Products > Papad
            (4038, 7),  # Fats and Oils > Oil, wheat germ
            (2047, 2),  # Spices and Herbs > Salt, table
            (9289, 2),  # Fruits and Fruit Juices > Prunes, dehydrated (low-moisture), uncooked
            (2017, 1),  # Spices and Herbs > Spices, dill weed, dried
            (4532, 1),  # Fats and Oils > Oil, hazelnut
            (11667, 1),  # Vegetables and Vegetable Products > Seaweed, spirulina, dried
            (12169, 1),  # Nut and Seed Products > Seeds, sesame butter, paste
            (16390, 1),  # Legumes and Legume Products > Peanuts, all types, dry-roasted, without salt
        ],
    ],
}
# fmt: on

if __name__ == "__main__":
    for number_of_foods in KNOWN_SOLUTIONS:
        for known_solution in KNOWN_SOLUTIONS[number_of_foods]:
            assert known_solution == sorted(known_solution, key=lambda x: x[0])
