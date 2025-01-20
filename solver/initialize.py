from data.download_data import create_filtered_csv
from solver.load_data import load_data
from solver.utils import get_arg_parser


def initialize(
    skip_download=False, verbose=True, only_these_ids=None, exclude_ids=None
):
    args = get_arg_parser().parse_args()

    if not skip_download:
        create_filtered_csv(
            args.download or args.only_download, args.delete_intermediate_files
        )

    if args.only_download:
        exit(0)

    foods, max_foods, min_requirements, max_requirements = load_data(
        only_these_ids=only_these_ids, exclude_ids=exclude_ids
    )

    if verbose:
        print()
        print("Starting solver...")

    return foods, max_foods, min_requirements, max_requirements, args.verbose, args.n
