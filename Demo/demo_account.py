from util import parse_args

from account_methods import get_locations


def main():

    args = parse_args()
    get_locations(args.input_file1, args.input_file2, args.output_file)


if __name__ == "__main__":
    main()