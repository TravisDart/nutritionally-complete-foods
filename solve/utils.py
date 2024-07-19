import argparse


def get_arg_parser():
    parser = argparse.ArgumentParser(
        description="Find sets of foods that combine to satisfy one's daily nutritional requirements."
    )
    parser.add_argument(
        "-n",
        type=int,
        default=8,
        help="The number of foods in the solution set. The default is 8 foods.",
    )
    parser.add_argument(
        "--test-data",
        action="store_true",
        help="Use test data instead of real data.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Verbosity logging. Use -vv for very verbose.",
    )
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Find the single best solution and print it.",
    )
    return parser
