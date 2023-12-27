This program finds what combination of foods are nutritoinally complete. This problem is related to the Stigler Diet problem, but instead of trying to minimize cost, we're trying to find the solutions that use the fewest distinct food types. We sets a system of inequalities to model a person's dietary needs, then find a combination of foods that will satisfy the inequalities.

The program can either solve or optimize. That is, when solving, the solver is asked to return any solution that satisfies the system of inequalities run without command line parameters. This takes about 20-30 seconds to run.

```
python find_complete_foods.py
```

It can also optimize the solutions so that the quantites are as close as possible to the lower bound (minimum dietary requirements). This takes about 20-30 minutes to run:

```
python find_complete_foods.py optimal
```

I'm still trying to understand the solver. When only solvinig without optimizatioin, it returns 2 solutions, both of which are the same. When solvinig with optimization, it returns 14 solutions. I would expect it to return the same number of solutions each time, but with different quantitles.

