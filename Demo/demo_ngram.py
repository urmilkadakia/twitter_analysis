from util import parse_args
from ngram_methods import ngram_histogram


def main():

    args = parse_args()
    ngram_histogram(args.input_file1, args.output_file, args.n, args.cutoff_freq)


if __name__ == "__main__":
    main()