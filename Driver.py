from util import parse_args
from ngram_methods import daily_ngram_collector, changing_ngram, ngram_frequency_dist, ngram_histogram, \
    char_length_histogram, ngram_adjacency_matrix, ngram_alloy_matrix, ngram_transmutation_matrix, \
    ngram_document_term_matrix, cal_present_absent

from account_methods import get_locations, bot_or_not, entities_count_difference, description_change_frequency, \
    get_twitter_user_id_from_screen_name


def main():

    args = parse_args()
    # bot_or_not(args.input_file1, args.output_file)
    # changing_ngram(args.input_file1, args.input_file2, args.output_file, args.n)
    # ngram_frequency_dist(args.input_file1, args.output_file, args.n)
    # daily_ngram_collector(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # get_locations(args.input_file1, args.output_file)
    # ngram_histogram(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # char_length_histogram(args.input_file1, args.output_file)
    # ngram_adjacency_matrix(args.input_file1, args.output_file, args.n, args.cutoff_freq)
    # entities_count_difference(args.input_file1, args.input_file2, args.output_file)
    # description_change_frequency(args.input_file1, args.output_file)
    # ngram_alloy_matrix(args.input_file1, args.input_file2, args.output_file, args.n)
    # ngram_transmutation_matrix(args.input_file1, args.input_file2, args.output_file, args.n)
    # ngram_document_term_matrix(args.input_file1, args.input_file2, args.output_file, args.n)
    # get_twitter_user_id_from_screen_name(args.input_file1, args.output_file)
    # cal_present_absent("/home/urmilkadakia/Desktop/Masters/Social_behavioral/twitter_analysis/OUTPUT/temp/", 100,
    # "2019_04_24", "2019_04_25", "")
    cal_present_absent(args.input_file1, args.output_file, '2019_04_20', '2019_04_25', 'of')


if __name__ == "__main__":
    main()
