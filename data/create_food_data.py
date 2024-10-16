import csv
import json
import os
import zipfile
import argparse

import requests


def download_zipfile(zip_url, zip_path):
    """Downloads a zipfile to the specified directory.

    Args:
      zip_url: The URL of the zipfile.
      zip_path: The location where the zipfile is extracted.
    """
    response = requests.get(zip_url)
    response.raise_for_status()

    with open(zip_path, "wb") as zip_file:
        zip_file.write(response.content)
    print(f"Downloaded zipfile: {zip_path}")


def extract_json(zip_path, json_path):
    """Extracts a single JSON file from a zipfile, and saves it.

    Args:
      zip_path: The path to the zipfile.
      json_path: The desired filename for the extracted JSON data.
    """
    # Extract the single JSON file
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        json_file = zip_ref.namelist()[0]  # Extract the first file
        with zip_ref.open(json_file) as zip_file:
            json_data = zip_file.read().decode("utf-8")

    # Save the JSON data to a file
    with open(json_path, "w") as output_file:
        output_file.write(json_data)
    print(f"Extracted and saved JSON: {json_path}")


def create_filtered_json(json_path, filtered_json_path, selected_foods_path):
    all_foods = json.loads(open(json_path).read())
    all_foods = all_foods["SRLegacyFoods"]  # Only one top-level key
    selected_foods = open(selected_foods_path).read().splitlines()
    selected_food_names = [tuple(x.split(" > ")) for x in selected_foods]

    output = []
    for food in all_foods:
        category = food["foodCategory"]["description"]
        food_name = food["description"]
        if (category, food_name) in selected_food_names:
            output += [food]

    open(filtered_json_path, "w").write(json.dumps(output))
    print(f"Created filtered JSON: {filtered_json_path}")


def create_csv(filtered_json_path, csv_path):
    required_nutrients = [
        "Calcium, Ca",
        "Carbohydrate, by difference",
        "Choline, total",
        "Copper, Cu",
        "Energy",
        "Total lipid (fat)",
        "Fiber, total dietary",
        "Fluoride, F",
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
        "Vitamin B-12",
        "Vitamin C, total ascorbic acid",
        "Vitamin D (D2 + D3)",
        "Vitamin E (alpha-tocopherol)",
        "Vitamin K (phylloquinone)",
        "Water",
        "Zinc, Zn",
    ]

    foods = json.loads(open(filtered_json_path).read())
    foods = sorted(
        foods, key=lambda x: (x["foodCategory"]["description"], x["description"])
    )

    with open(csv_path, "w") as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            [
                "ID",
                "Category",
                "Food",
                "Scientific_Name",
            ]
            + required_nutrients
        )

        column_unit = [None] * len(required_nutrients)
        for food in foods:
            labels = [
                food["ndbNumber"],
                food["foodCategory"]["description"],
                food["description"],
                food.get("scientificName", ""),
            ]
            nutrient_values = [0] * len(required_nutrients)
            for nutrient in food["foodNutrients"]:
                if nutrient["nutrient"]["name"] in required_nutrients:
                    amount = nutrient["amount"]
                    nutrient_unit = nutrient["nutrient"]["unitName"]

                    if nutrient_unit == "kJ":
                        # convert kJ to kcal
                        nutrient_unit = "kcal"
                        amount *= 0.239  # 1 kJ * (0.239 kcal / kJ) = 0.239 kcal
                    elif nutrient["nutrient"]["name"] == "Manganese, Mn":
                        # The daily requirements data has Manganese in µg, but the data has it in mg.
                        # So, convert mg to µg.
                        amount *= 1000
                        nutrient_unit = "µg"

                    amount /= 100  # The standard serving size is 100g. Normalize to 1g.
                    amount = round(amount, 3)  # Round everything to 3 decimal places.

                    dest_col = required_nutrients.index(nutrient["nutrient"]["name"])

                    # Make sure all values are in the same unit.
                    if column_unit[dest_col] is None:
                        column_unit[dest_col] = nutrient_unit
                    else:
                        assert column_unit[dest_col] == nutrient_unit

                    if amount == 0:
                        nutrient_values[dest_col] = amount
                    else:
                        nutrient_values[dest_col] = f"{amount} {nutrient_unit}"

            csvwriter.writerow(labels + nutrient_values)

    print(f"Created final CSV: {csv_path}")


def delete_intermediate_files(
    files_to_delete: list[str], should_delete_intermediate_files: bool = False
):
    """Delete the files in the list `files_to_delete`.

    Args:
      files_to_delete: A list of filenames to be deleted.
      should_delete_intermediate_files: If True, delete the files without prompting.
    """
    # Prompt the user for confirmation unless the command-line flag is passed.
    if not should_delete_intermediate_files:
        confirmation = input("Delete intermediate data files? [y/N]: ")
        should_delete_intermediate_files = confirmation.lower() == "y"

    if should_delete_intermediate_files:
        for file in files_to_delete:
            basename = os.path.basename(file)
            try:
                os.remove(file)  # Attempt to delete the file
                print(f"Deleted: {basename}")
            except FileNotFoundError:
                print(f"Not found: {basename}")
            except OSError as error:
                print(f"Error deleting: {basename} ({error})")


def create_filtered_csv(should_delete_intermediate_files: bool = False):
    download_dir = os.path.dirname(__file__)  # Download to the current directory
    zip_url = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip"
    zip_path = os.path.join(download_dir, os.path.basename(zip_url))
    json_path = zip_path[: -len(".zip")] + ".json"
    filtered_json_path = os.path.join(download_dir, "food_data.json")
    csv_path = os.path.join(download_dir, "food_data.csv")
    selected_foods_path = "selected_foods.txt"

    if not os.path.exists(filtered_json_path):
        if not os.path.exists(json_path):
            if not os.path.exists(zip_path):
                download_zipfile(zip_url, zip_path)
            extract_json(zip_path, json_path)
        create_filtered_json(json_path, filtered_json_path, selected_foods_path)
    create_csv(filtered_json_path, csv_path)

    print()
    print("Data file successfully created.")
    delete_intermediate_files(
        [zip_path, json_path, filtered_json_path], should_delete_intermediate_files
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create input data file for the solver."
    )
    parser.add_argument(
        "-d",
        action="store_true",
        help="Delete intermediate files without prompting.",
    )
    args = parser.parse_args()

    create_filtered_csv(should_delete_intermediate_files=args.d)
