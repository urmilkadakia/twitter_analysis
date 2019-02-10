from config import parse_args
import twitter_scraper


def main():

    args = parse_args()
    twitter_scraper_object = twitter_scraper.Twitter_Scraper(args.inputfile, args.outputfile)
    twitter_scraper_object.genFile(args.format, args.clean_userid)


if __name__ == "__main__":
    main()
