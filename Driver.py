from util import parse_args
from ngram_methods import daily_ngram_collector, changing_ngram, ngram_frequency_dist, ngram_histogram, \
    char_length_histogram, ngram_adjacency_matrix, ngram_alloy_matrix

from account_methods import get_locations, bot_or_not, entities_count_difference, description_change_frequency

def main():

    args = parse_args()
    # changing_ngram(args.input_file1, args.input_file2, args.output_file, args.n)
    # ngram_frequency_dist(args.input_file1, args.output_file, args.n)
    # daily_ngram_collector(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # get_locations(args.input_file1, args.input_file2, args.output_file)
    # ngram_histogram(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # char_length_histogram(args.input_file1, args.output_file)
    # ngram_adjacency_matrix(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # entities_count_difference(args.input_file1, args.input_file2, args.output_file)
    # description_change_frequency(args.input_file1, args.output_file)
    ngram_alloy_matrix(args.input_file1, args.input_file2, args.output_file, args.n)


if __name__ == "__main__":
    main()
