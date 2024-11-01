import csv
import json
import math
import os
import zipfile
import argparse

import requests

from constants import USDA_NUTRIENT_NAMES, NUMBER_SCALE, NUTRIENT_UNITS


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
    foods = json.loads(open(filtered_json_path).read())
    foods = sorted(
        foods, key=lambda x: (x["foodCategory"]["description"], x["description"])
    )

    with open(csv_path, "w") as csvfile:
        # creating a csv writer object
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(
            [
                "Food ID",
                "Food",
            ]
            + USDA_NUTRIENT_NAMES
        )
        csvwriter.writerow(["", "NUTRIENT_UNITS"] + NUTRIENT_UNITS)

        column_unit = [None] * len(USDA_NUTRIENT_NAMES)
        min_nonzero_value = [float("inf")] * len(USDA_NUTRIENT_NAMES)
        for food in foods:
            labels = [
                food["ndbNumber"],
                f'{food["foodCategory"]["description"]} > {food["description"]}',
            ]
            assert ">" not in food["foodCategory"]["description"]
            assert ">" not in food["description"]

            nutrient_values = [0] * len(USDA_NUTRIENT_NAMES)
            for nutrient in food["foodNutrients"]:
                if nutrient["nutrient"]["name"] in USDA_NUTRIENT_NAMES:
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

                    # Round everything to a specific number of decimal places,
                    # later we will scale our integer variables by this amount.
                    amount = round(amount, int(math.log10(NUMBER_SCALE)))

                    dest_col = USDA_NUTRIENT_NAMES.index(nutrient["nutrient"]["name"])

                    # Make sure all values are in the same unit.
                    if column_unit[dest_col] is None:
                        column_unit[dest_col] = nutrient_unit
                    else:
                        assert column_unit[dest_col] == nutrient_unit

                    if amount != 0:
                        min_nonzero_value[dest_col] = min(
                            amount, min_nonzero_value[dest_col]
                        )

                    nutrient_values[dest_col] = amount

            csvwriter.writerow(labels + nutrient_values)

    scale = 10 ** max([math.ceil(-math.log10(m)) for m in min_nonzero_value])

    # Ensure that the hardcoded values don't need to be updated.
    assert scale == NUMBER_SCALE
    assert column_unit == NUTRIENT_UNITS

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
    # Download to the directory of this file, i.e. ./data
    download_dir = os.path.join(os.path.dirname(__file__))

    zip_url = "https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_json_2018-04.zip"
    zip_path = os.path.join(download_dir, os.path.basename(zip_url))
    json_path = zip_path[: -len(".zip")] + ".json"
    filtered_json_path = os.path.join(download_dir, "food_data.json")
    csv_path = os.path.join(download_dir, "food_data.csv")
    selected_foods_path = os.path.join(download_dir, "selected_foods.txt")

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
        [zip_path, json_path, filtered_json_path],
        should_delete_intermediate_files,
    )


def download_data_if_needed(should_not_prompt, should_delete_intermediate_files):
    data_file_present = os.path.isfile("./data/food_data.csv")

    if not should_not_prompt and not data_file_present:
        confirmation = input("Data file not present. Download data file? [y/N]: ")
        if confirmation.lower() != "y":
            print("Exiting.")
            exit(1)

    if not data_file_present:
        create_filtered_csv(
            should_delete_intermediate_files=should_delete_intermediate_files
        )
        print()
        print("Starting solver...")


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
