from util import parse_args
from ngram_analysis import daily_ngram_collector, changing_ngram, ngram_frequency_dist, get_locations, ngram_histogram, \
    char_length_histogram


def main():

    args = parse_args()
    # changing_ngram(args.inputfile, args.inputfile, args.outputfile, args.n)
    # ngram_frequency_dist(args.inputfile, args.outputfile, args.n)

    daily_ngram_collector(args.inputfile1, args.outputfile, args.n, args.cutoff_freq)
    # get_locations(args.inputfile, args.outputfile)
    # ngram_histogram(args.inputfile, args.outputfile, 10, 1)
    # char_length_histogram(args.inputfile, args.outputfile)


if __name__ == "__main__":
    main()
