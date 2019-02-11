from util import parse_args
from twitter_scraper import TwitterScraper


def main():

    args = parse_args()
    twitter_scraper_object = TwitterScraper(args.input_file1, args.output_file)
    twitter_scraper_object.generate_file(args.format, args.clean_userid)


if __name__ == "__main__":
    main()
