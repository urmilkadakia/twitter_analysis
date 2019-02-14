from util import parse_args
from ngram_analysis import daily_ngram_collector, changing_ngram, ngram_frequency_dist, get_locations, \
    ngram_histogram, char_length_histogram


def main():

    args = parse_args()
    # changing_ngram(args.input_file1, args.input_file2, args.output_file, args.n)
    # ngram_frequency_dist(args.input_file1, args.output_file, args.n)
    # daily_ngram_collector(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # get_locations(args.input_file1, args.input_file2, args.output_file)
    ngram_histogram(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # char_length_histogram(args.input_file1, args.output_file)


if __name__ == "__main__":
    main()
