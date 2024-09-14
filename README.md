# Nutritionally Complete Foods v0.2

* [Overview](#Overview)
* [Current State of Development](#Current-State-of-Development)
* [Environment Setup](#Environment-Setup)
* [Source Data](#Source-Data)
* [The Solver](#The-Solver)
* [Example Solutions](#Example-Solutions)
* [Visualization](#Visualization)



## Overview

This program finds combination of foods that are nutritionally complete while minimizing the number of different foods and only considering foods that you might grow yourself. - If you wanted to grow a garden to completely sustain yourself, what are your options?



## Current State of Development

Currently, this program uses an optimizing solver, which means it finds the combinations of foods that most closely meet the minimum dietary requirements. But, the goal is to find all solutions that satisfy the allowable range of nutritional requirements, not just the solutions closest to the minimum requirements. So, I'm realizing that an optimizing solver is not the best tool for this problem.

I originally chose this solver because the [Stigler Diet](https://en.wikipedia.org/wiki/Stigler_diet) problem is similar to our problem and can be solved efficiently with an optimizing solver. But, instead of trying to minimize cost, our goal is to find the fewest distinct food types, and that is a pretty fundamental difference.

Given a mathematical function shaped like a mountain, an optimizing solver will try to find its peak. When presented with a plateau shape, the solver just skates around looking for a peak. Ideally, I would like to tell the solver to stop optimizing once it has found any solution and to not consider that combination again.

In the `solve_all.py` file (see below), I have tried to use the optimizing solver to find all solutions: Once one solution of is found, the algorithm removes the foods that compose the solution from the list and solves again. When no more solutions are found, then the process is repeated using every combination of the foods found in the solutions. - Unfortunately, this basically reduces to a slow brute-force search.



## Environment Setup

Project requirements are stored in `requirements.txt`. Setting up an environment is a little outside of the scope of this readme, but if you are unfamiliar with how to do so, I've included my preferred method in the expandable section below.

<details>
  <summary>Environment setup</summary>

```
# Your OS will need the prerequisites, and that's not particularly straightforward.
# This is what you'll need to install on Ubuntu:
sudo apt install curl git-core gcc make zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev libssl-dev liblzma-dev

# Install pyenv.
curl https://pyenv.run | bash

# Integrate into your shell. (Restart your shell after this.)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init -)"' >> ~/.bashrc

# Create a virtual environment with Python 3.12.2
pyenv virtualenv 3.12.2 nutritionally-complete-foods

# Activate that virtual environment
pyenv activate nutritionally-complete-foods

# Install the requirements to that environment
pip install -r requirements.txt

# ...

# Deactivate the environment when you're done
source deactive
```

</details>




## Source Data

This project uses a subset of the [USDA's SR Legacy dataset](https://fdc.nal.usda.gov/) as input. Before running the solver, download and parse this dataset by running:

```
cd data
python create_food_data.py
```

This will result in a file called `food_data.csv` which is one of the two input files for the solver. There are currently 1,241 foods in this list.

The other input file is the CSV of daily recommended values, which comes from the [USDA's Dietary Reference Intake (DRI) Calculator](https://www.nal.usda.gov/human-nutrition-and-food-safety/dri-calculator). You can either use the example file in this repo ( `data/Daily Recommended Values.csv`), or you can modify the values based on your personalized requirements. Ideally, I would like this program to directly integrate the calculation of dietary requirements, but the spreadsheet gives us a good enough initial goal.



## The Solver

After you have generated the source data file, run the solver like so:

```
cd solve
python solve.py
```

This will output a list of foods that combine to satisfy the given dietary constrains. 

As the goal is to find the fewest number of foods required, the solver is currently hardcoded to find 7 foods. (There are no solutions with 6 foods or fewer.) The number of foods in the solution can be set with the `-n` flag:

```
python solve.py -n 9
```



## Example Solutions

The program takes about 3hrs to run and all solutions can be found in `solve/constants.py`.

Currently, all solutions contain Kiwifruit (ID #520) and either dry or rehydrated seaweed (ID 31019 and 31020, respectively). This leads me to suspect we're missing a lot of solutions.

Example solution:

1. Olives, pickled, canned or bottled, green (877g) - ID #9195
2. Kiwifruit, ZESPRI SunGold, raw (1,019g) - ID #9520
3. Mushrooms, portabella, exposed to ultraviolet light, raw (303g) - ID #11998
4. Beverages, tea, black, brewed, prepared with tap water (805g) - ID #14355
5. Seaweed, Canadian Cultivated EMI-TSUNOMATA, dry (49g) - ID #31019
6. Plums, wild (Northern Plains Indians) (1,108g) - ID #35206
7. Beans, baked, canned, no salt added (956g) - ID #43449



## Visualization

The `visualize/` folder contains a Jupyter notebook that displays a chart of the actual nutrient value vs the acceptable range. This was first created to verify that the solver was returning correct solutions, so currently the example solution contains processed foods that I eventually removed from consideration (e.g. potato pancakes). Once the solver is perfected, we need to create a tighter integration between the solver and the visualizer.

This is run in the standard way by running `jupyter notebook`, then opening `visualize/Visualize Nutrients.ipynb` in the Jupyter web application. Below is a screenshot:

![Screenshot of the Jupyter Notebook](screenshot.png)

