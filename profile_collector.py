from config import parse_args
import twitter_scraper


def main():

    args = parse_args()
    twitter_scraper.genFile(args.inputfile, args.outputfile, args.format, args.clean_userid)


if __name__ == "__main__":
    main()
