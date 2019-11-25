import os
import argparse

from tweepy_methods import twitter_scarper, get_twitter_user_id_from_screen_name
from analysis_methods import daily_ngram_collector, changing_ngram, ngram_frequency_dist, ngram_histogram, \
    char_length_histogram, ngram_adjacency_matrix, ngram_alloy_matrix, ngram_transmutation_matrix, \
    ngram_document_term_matrix, calculate_present_absent, get_locations, entities_count_difference, \
    description_change_frequency
from botometer_methods import bot_or_not
from reconstruction_methods import reconstruct_longitudinal_data


def is_valid_path(parser, arg):
    """
    Throws an error if the file does not exists at the given location
    :param parser: Object of argparse class
    :param arg: file path for which the function is going to check whether it exist or not
    :return: Return file path if file exist or throw an error of file not exist
    """
    if not os.path.exists(arg):
        parser.error("The file/folder %s does not exist!" % arg)
    else:
        return arg  # return file path


def main():

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Sub-parsers for twitter_scraper
    twitter_scraper_parser = subparsers.add_parser('twitter_scraper')
    twitter_scraper_parser.add_argument("-i", dest="input_file", required=True,
                                        help="Path to input file", type=lambda x: is_valid_path(parser, x))
    twitter_scraper_parser.add_argument("-o", dest="output_file", required=False,
                                        help="Path to output file")
    twitter_scraper_parser.add_argument("-format", dest="format", required=False, choices=["json", "csv"],
                                        help="Specify the format of the output file. Default format is json.",
                                        default="json", type=str)
    twitter_scraper_parser.add_argument("-size", dest="size_flag", required=False,
                                        help="Specify True if you do not want to store tweets with profile "
                                             "information. This will reduce file size. This only works with the "
                                             "json format. Default is False.", default=False, type=bool)
    twitter_scraper_parser.add_argument("-cleaned", dest="clean_userid_flag", required=False,
                                        help="Specify True if want to store a cleaned list of user ids. Default is "
                                             "False.", default=False, type=bool)
    twitter_scraper_parser.set_defaults(function=call_twitter_scraper)

    # Sub-parsers for reconstruct_longitudinal_data
    reconstruct_longitudinal_data_parser = subparsers.add_parser('reconstruct_longitudinal_data')
    reconstruct_longitudinal_data_parser.add_argument("-i", dest="input_file", required=True,
                                                      help="Path to input file", type=lambda x: is_valid_path(parser, x))
    reconstruct_longitudinal_data_parser.add_argument("-o", dest="output_file", required=False,
                                                      help="Path to output file")
    reconstruct_longitudinal_data_parser.add_argument("-num_users", dest="number_of_users", required=True,
                                                      help="To identify the input file as they are named based on the "
                                                           "number of users", type=int)
    reconstruct_longitudinal_data_parser.add_argument("-end", dest="end_date", required=True,
                                                      help="Date up to which the function will reconstruct data. "
                                                           "Default is today.", type=str)

    reconstruct_longitudinal_data_parser.set_defaults(function=call_reconstruct_longitudinal_data)

    # Sub-parsers for ngram_frequency_dist
    ngram_frequency_dist_parser = subparsers.add_parser('ngram_frequency_dist')
    ngram_frequency_dist_parser.add_argument("-i", dest="input_file", required=True,
                                             help="Path to input file", type=lambda x: is_valid_path(parser, x))
    ngram_frequency_dist_parser.add_argument("-o", dest="output_file", required=False,
                                             help="Path to output file")
    ngram_frequency_dist_parser.add_argument("-ngram", dest="ngram", required=False,
                                             help="Specify the ngram. Default value of the ngram is 1.",
                                             default=1, type=int)
    ngram_frequency_dist_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                             help="Filter all non alpha numeric words. Default value is False.",
                                             default=False, type=bool)
    ngram_frequency_dist_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                             help="Filter all stop words.  Default value is False.",
                                             default=False, type=bool)
    ngram_frequency_dist_parser.set_defaults(function=call_ngram_frequency_dist)

    # Sub-parsers for changing_ngram
    changing_ngram_parser = subparsers.add_parser('changing_ngram')
    changing_ngram_parser.add_argument("-i1", dest="input_file1", required=True,
                                       help="Path to input file 1", type=lambda x: is_valid_path(parser, x))
    changing_ngram_parser.add_argument("-i2", dest="input_file2", required=True,
                                       help="Path to input file 2", type=lambda x: is_valid_path(parser, x))
    changing_ngram_parser.add_argument("-o", dest="output_file", required=False,
                                       help="Path to output file")
    changing_ngram_parser.add_argument("-ngram", dest="ngram", required=False,
                                       help="Specify the ngram. Default value of ngram is 1.", default=1, type=int)
    changing_ngram_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                       help="Filter all non alpha numeric words.  Default value is False.",
                                       default=False, type=bool)
    changing_ngram_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                       help="Filter all stop words.  Default value is False.",
                                       default=False, type=bool)
    changing_ngram_parser.set_defaults(function=call_changing_ngram)

    # Sub-parsers for daily_ngram_collector
    daily_ngram_collector_parser = subparsers.add_parser('daily_ngram_collector')
    daily_ngram_collector_parser.add_argument("-i", dest="input_file_folder", required=True,
                                              help="Path to the folder in which input files are stored",
                                              type=lambda x: is_valid_path(parser, x))
    daily_ngram_collector_parser.add_argument("-o", dest="output_file", required=False,
                                              help="Path to output file")
    daily_ngram_collector_parser.add_argument("-num_users", dest="number_of_users", required=True,
                                              help="To identify the input file as they are named based on "
                                                   "number of users", type=int)
    daily_ngram_collector_parser.add_argument("-start", dest="start_date", required=True,
                                              help="Date from which function will start to calculate", type=str)
    daily_ngram_collector_parser.add_argument("-end", dest="end_date", required=True,
                                              help="Date up to which function will calculate", type=str)
    daily_ngram_collector_parser.add_argument("-ngram", dest="ngram", required=False,
                                              help="Specify the ngram. Default value of ngram is 1.",
                                              default=1, type=int)
    daily_ngram_collector_parser.add_argument("-cutoff", dest="cutoff_freq", required=False,
                                              help="The ngrams that has less frequency than the cutoff frequency "
                                                   "will not be included in the output file. Default value of "
                                                   "cutoff frequency is 5.", default=5, type=int)
    daily_ngram_collector_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                              help="Filter all non alpha numeric words. Default value is False.",
                                              default=False, type=bool)
    daily_ngram_collector_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                              help="Filter all stop words. Default value is False.",
                                              default=False, type=bool)
    daily_ngram_collector_parser.set_defaults(function=call_daily_ngram_collector)

    # Sub-parsers for char_length_histogram
    char_length_histogram_parser = subparsers.add_parser('char_length_histogram')
    char_length_histogram_parser.add_argument("-i", dest="input_file", required=True,
                                              help="Path to input file", type=lambda x: is_valid_path(parser, x))
    char_length_histogram_parser.add_argument("-o", dest="output_file", required=False,
                                              help="Path to output file")
    char_length_histogram_parser.set_defaults(function=call_char_length_histogram)

    # Sub-parsers for ngram_histogram
    ngram_histogram_parser = subparsers.add_parser('ngram_histogram')
    ngram_histogram_parser.add_argument("-i", dest="input_file", required=True,
                                        help="Path to input file", type=lambda x: is_valid_path(parser, x))
    ngram_histogram_parser.add_argument("-o", dest="output_file", required=False,
                                        help="Path to output file")
    ngram_histogram_parser.add_argument("-ngram", dest="ngram", required=False,
                                        help="Specify the ngram.  Default value of ngram is 1.",
                                        default=1, type=int)
    ngram_histogram_parser.add_argument("-cutoff", dest="cutoff_freq", required=False,
                                        help="The ngrams that has less frequency than the cutoff frequency "
                                             "will not be included in the output file.  Default value of "
                                             "cutoff frequency is 5.", default=5, type=int)
    ngram_histogram_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                        help="Filter all non alpha numeric words. Default value is False.",
                                        default=False, type=bool)
    ngram_histogram_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                        help="Filter all stop words. Default value is False.",
                                        default=False, type=bool)
    ngram_histogram_parser.set_defaults(function=call_ngram_histogram)

    # Sub-parsers for ngram_adjacency_matrix
    ngram_adjacency_matrix_parser = subparsers.add_parser('ngram_adjacency_matrix')
    ngram_adjacency_matrix_parser.add_argument("-i", dest="input_file", required=True,
                                               help="Path to the input files",
                                               type=lambda x: is_valid_path(parser, x))
    ngram_adjacency_matrix_parser.add_argument("-o", dest="output_file", required=False,
                                               help="Path to output file")
    ngram_adjacency_matrix_parser.add_argument("-ngram", dest="ngram", required=False,
                                               help="Specify the ngram. Default value of ngram is 1.",
                                               default=1, type=int)
    ngram_adjacency_matrix_parser.add_argument("-cutoff", dest="cutoff_freq", required=False,
                                               help="The ngrams that has less frequency than the cutoff frequency "
                                                    "will not be included in the output file. Default value of "
                                                    "cutoff frequency is 5.", default=5, type=int)
    ngram_adjacency_matrix_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                               help="Filter all non alpha numeric words. Default value is False.",
                                               default=False, type=bool)
    ngram_adjacency_matrix_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                               help="Filter all stop words. Default value is False.",
                                               default=False, type=bool)
    ngram_adjacency_matrix_parser.set_defaults(function=call_ngram_adjacency_matrix)

    # Sub-parsers for ngram_alloy_matrix
    ngram_alloy_matrix_parser = subparsers.add_parser('ngram_alloy_matrix')
    ngram_alloy_matrix_parser.add_argument("-i1", dest="input_file1", required=True,
                                           help="Path to input file 1", type=lambda x: is_valid_path(parser, x))
    ngram_alloy_matrix_parser.add_argument("-i2", dest="input_file2", required=True,
                                           help="Path to input file 2", type=lambda x: is_valid_path(parser, x))
    ngram_alloy_matrix_parser.add_argument("-o", dest="output_file", required=False,
                                           help="Path to output file")
    ngram_alloy_matrix_parser.add_argument("-ngram", dest="ngram", required=False,
                                           help="Specify the ngram.  Default value of ngram is 1.",
                                           default=1, type=int)
    ngram_alloy_matrix_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                           help="Filter all non alpha numeric words. Default value is False.",
                                           default=False, type=bool)
    ngram_alloy_matrix_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                           help="Filter all stop words. Default value is False.",
                                           default=False, type=bool)
    ngram_alloy_matrix_parser.set_defaults(function=call_ngram_alloy_matrix)

    # Sub-parsers for ngram_transmutation_matrix
    ngram_transmutation_matrix_parser = subparsers.add_parser('ngram_transmutation_matrix')
    ngram_transmutation_matrix_parser.add_argument("-i1", dest="input_file1", required=True,
                                                   help="Path to input file 1", type=lambda x: is_valid_path(parser, x))
    ngram_transmutation_matrix_parser.add_argument("-i2", dest="input_file2", required=True,
                                                   help="Path to input file 2", type=lambda x: is_valid_path(parser, x))
    ngram_transmutation_matrix_parser.add_argument("-o", dest="output_file", required=False,
                                                   help="Path to output file")
    ngram_transmutation_matrix_parser.add_argument("-ngram", dest="ngram", required=False,
                                                   help="Specify the ngram. Default value of ngram is 1.",
                                                   default=1, type=int)
    ngram_transmutation_matrix_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                                   help="Filter all non alpha numeric words. Default value is False.",
                                                   default=False, type=bool)
    ngram_transmutation_matrix_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                                   help="Filter all stop words. Default value is False.",
                                                   default=False, type=bool)
    ngram_transmutation_matrix_parser.set_defaults(function=call_ngram_transmutation_matrix)

    # Sub-parsers for ngram_document_term_matrix
    ngram_document_term_matrix_parser = subparsers.add_parser('ngram_document_term_matrix')
    ngram_document_term_matrix_parser.add_argument("-i1", dest="input_file1", required=True,
                                                   help="Path to input file 1", type=lambda x: is_valid_path(parser, x))
    ngram_document_term_matrix_parser.add_argument("-i2", dest="input_file2", required=True,
                                                   help="Path to word list file",
                                                   type=lambda x: is_valid_path(parser, x))
    ngram_document_term_matrix_parser.add_argument("-o", dest="output_file", required=False,
                                                   help="Path to output file")
    ngram_document_term_matrix_parser.add_argument("-ngram", dest="ngram", required=False,
                                                   help="Specify the ngram. Default value of ngram is 1.",
                                                   default=1, type=int)
    ngram_document_term_matrix_parser.add_argument("-alpha_numeric", dest="alpha_numeric", required=False,
                                                   help="Filter all non alpha numeric words.  Default value is False.",
                                                   default=False, type=bool)
    ngram_document_term_matrix_parser.add_argument("-stop_words", dest="stop_words", required=False,
                                                   help="Filter all stop words. Default value is False.",
                                                   default=False, type=bool)
    ngram_document_term_matrix_parser.set_defaults(function=call_ngram_document_term_matrix)

    # Sub-parsers for calculate_present_absent
    calculate_present_absent_parser = subparsers.add_parser('calculate_present_absent')
    calculate_present_absent_parser.add_argument("-i", dest="input_file_folder", required=True,
                                                 help="Path to the folder in which input files are stored",
                                                 type=lambda x: is_valid_path(parser, x))
    calculate_present_absent_parser.add_argument("-o", dest="output_file", required=False,
                                                 help="Path to output file")
    calculate_present_absent_parser.add_argument("-num_users", dest="number_of_users", required=True,
                                                 help="To identify the input file as they are named based on "
                                                      "number of users", type=int)
    calculate_present_absent_parser.add_argument("-start", dest="start_date", required=True,
                                                 help="Date from which function will start to calculate", type=str)
    calculate_present_absent_parser.add_argument("-end", dest="end_date", required=True,
                                                 help="Date up to which function will calculate", type=str)
    calculate_present_absent_parser.add_argument("-pattern", dest="pattern", required=True,
                                                 help="", type=str)
    calculate_present_absent_parser.set_defaults(function=call_calculate_present_absent)

    # Sub-parsers for get_twitter_user_id_from_screen_name
    get_twitter_user_id_from_screen_name_parser = subparsers.add_parser('get_twitter_user_id_from_screen_name')
    get_twitter_user_id_from_screen_name_parser.add_argument("-i", dest="input_file", required=True,
                                                             help="Path to input file",
                                                             type=lambda x: is_valid_path(parser, x))
    get_twitter_user_id_from_screen_name_parser.add_argument("-o", dest="output_file", required=False,
                                                             help="Path to output file")
    get_twitter_user_id_from_screen_name_parser.set_defaults(function=call_get_twitter_user_id_from_screen_name)

    # Sub-parsers for bot_or_not
    bot_or_not_parser = subparsers.add_parser('bot_or_not')
    bot_or_not_parser.add_argument("-i", dest="input_file", required=True,
                                   help="Path to input file", type=lambda x: is_valid_path(parser, x))
    bot_or_not_parser.add_argument("-o", dest="output_file", required=False,
                                   help="Path to output file")
    bot_or_not_parser.set_defaults(function=call_bot_or_not)

    # Sub-parsers for get_locations
    get_locations_parser = subparsers.add_parser('get_locations')
    get_locations_parser.add_argument("-i", dest="input_file", required=True,
                                      help="Path to input file", type=lambda x: is_valid_path(parser, x))
    get_locations_parser.add_argument("-o", dest="output_file", required=False,
                                      help="Path to output file")
    get_locations_parser.set_defaults(function=call_get_locations)

    # Sub-parsers for entities_count_difference
    entities_count_difference_parser = subparsers.add_parser('entities_count_difference')
    entities_count_difference_parser.add_argument("-i1", dest="input_file1", required=True,
                                                  help="Path to input file 1", type=lambda x: is_valid_path(parser, x))
    entities_count_difference_parser.add_argument("-i2", dest="input_file2", required=True,
                                                  help="Path to input file 2", type=lambda x: is_valid_path(parser, x))
    entities_count_difference_parser.add_argument("-o", dest="output_file", required=False,
                                                  help="Path to output file")
    entities_count_difference_parser.set_defaults(function=call_entities_count_difference)

    # Sub-parsers for description_change_frequency
    description_change_frequency_parser = subparsers.add_parser('description_change_frequency')
    description_change_frequency_parser.add_argument("-i", dest="input_file_folder", required=True,
                                                     help="Path to the folder in which input files are stored",
                                                     type=lambda x: is_valid_path(parser, x))
    description_change_frequency_parser.add_argument("-o", dest="output_file", required=False,
                                                     help="Path to output file")
    description_change_frequency_parser.add_argument("-num_users", dest="number_of_users", required=True,
                                                     help="To identify the input file as they are named based on "
                                                          "number of users", type=int)
    description_change_frequency_parser.add_argument("-start", dest="start_date", required=True,
                                                     help="Date from which function will start to calculate", type=str)
    description_change_frequency_parser.add_argument("-end", dest="end_date", required=True,
                                                     help="Date up to which function will calculate", type=str)
    description_change_frequency_parser.set_defaults(function=call_description_change_frequency)

    args = parser.parse_args()
    args.function(args)


def call_twitter_scraper(args):
    twitter_scarper(args.input_file, args.output_file, args.format, args.size_flag, args.clean_userid_flag)


def call_reconstruct_longitudinal_data(args):
    reconstruct_longitudinal_data(args.input_file, args.output_file, args.number_of_users)


def call_ngram_frequency_dist(args):
    ngram_frequency_dist(args.input_file, args.output_file, args.ngram, args.alpha_numeric, args.stop_words)


def call_changing_ngram(args):
    changing_ngram(args.input_file1, args.input_file2, args.output_file, args.ngram, args.alpha_numeric,
                   args.stop_words)


def call_daily_ngram_collector(args):
    daily_ngram_collector(args.input_file_folder, args.output_file, args.number_of_users, args.start_date,
                          args.end_date, args.ngram, args.cutoff_freq, args.alpha_numeric, args.stop_words)


def call_char_length_histogram(args):
    char_length_histogram(args.input_file, args.output_file)


def call_ngram_histogram(args):
    ngram_histogram(args.input_file, args.output_file, args.ngram, args.cutoff_freq, args.alpha_numeric,
                    args.stop_words)


def call_ngram_adjacency_matrix(args):
    ngram_adjacency_matrix(args.input_file, args.output_file, args.ngram, args.cutoff_freq, args.alpha_numeric,
                           args.stop_words)


def call_ngram_alloy_matrix(args):
    ngram_alloy_matrix(args.input_file1, args.input_file2, args.output_file, args.ngram, args.alpha_numeric,
                       args.stop_words)


def call_ngram_transmutation_matrix(args):
    ngram_transmutation_matrix(args.input_file1, args.input_file2, args.output_file, args.ngram, args.alpha_numeric,
                               args.stop_words)


def call_ngram_document_term_matrix(args):
    ngram_document_term_matrix(args.input_file1, args.input_file2, args.output_file, args.ngram, args.alpha_numeric,
                               args.stop_words)


def call_calculate_present_absent(args):
    calculate_present_absent(args.input_file_folder, args.output_file, args.number_of_users, args.start_date,
                             args.end_date, args.pattern)


def call_get_twitter_user_id_from_screen_name(args):
    get_twitter_user_id_from_screen_name(args.input_file, args.output_file)


def call_bot_or_not(args):
    bot_or_not(args.input_file, args.output_file)


def call_get_locations(args):
    get_locations(args.input_file, args.output_file)


def call_entities_count_difference(args):
    entities_count_difference(args.input_file1, args.input_file2, args.output_file)


def call_description_change_frequency(args):
    description_change_frequency(args.input_file_folder, args.output_file, args.number_of_users, args.start_date,
                                 args.end_date)


if __name__ == "__main__":
    main()
