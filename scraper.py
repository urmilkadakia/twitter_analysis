from config import parse_args
import csv
import twitter_scraper
import time


def main():

    timestr = time.strftime("%m_%d_%Y")
    args = parse_args()
    inputfile = open(args.inputfile, 'r')
    if args.format == 'csv':
        outputfile = csv.writer(open(args.outputfile + 'output_' + timestr + '.txt', "w+"))
    else:
        outputfile = open(args.outputfile + 'output_' + timestr + '.txt', "w+")
    clean_userid_file = ''
    if args.clean_userid:
        clean_userid_file = csv.writer(open(args.outputfile + 'new_userid_list_' + timestr + '.txt', "w+"))
    twitter_scraper.genFile(inputfile, outputfile, args.format, args.clean_userid, clean_userid_file)


if __name__ == "__main__":
    main()
