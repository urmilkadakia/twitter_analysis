from util import parse_args
from twitter_scraper import Twitter_Scraper


def main():

    args = parse_args()
    twitter_scraper_object = Twitter_Scraper(args.inputfile, args.outputfile)
    twitter_scraper_object.generate_file(args.format, args.clean_userid)


if __name__ == "__main__":
    main()
