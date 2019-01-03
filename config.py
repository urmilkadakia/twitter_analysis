import argparse
import os

# Throws an error if the file does not exists at the given location
def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg  # return file path


def parse_args():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="inputfile", required=True,
                        help="Input file path", type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-o", dest="outputfile", required=True,
                        help="Output file path")
    parser.add_argument("-f", dest="format", required=False, choices=["json", "csv"],
                        help="Specify the format of the output file.", default="json", type=str)
    parser.add_argument("-u", dest="clean_userid", required=False,
                        help="Specify 1 if want to store a cleaned list of user ids", default=0, type=int)
    args = parser.parse_args()

    return args

def parse_args2():

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", dest="inputfile", required=True,
                        help="Input file path", type=lambda x: is_valid_file(parser, x))
    parser.add_argument("-o", dest="outputfile", required=True,
                        help="Output file path")
    parser.add_argument("-ngram", dest="n", required=False,
                        help="Specify the ngram", default=1, type=int)
    args = parser.parse_args()

    return args
