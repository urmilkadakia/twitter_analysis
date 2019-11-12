import re


def log_twitter_error(logger, tweep_error, message=""):
    """Log a TweepError exception."""
    if tweep_error.api_code:
        api_code = tweep_error.api_code
    else:
        api_code = int(re.findall(r'"code":[0-9]+', tweep_error.reason)[0].split(':')[1])
    if api_code == 32:
        logger.error("invalid Twitter API authentication tokens")
    elif api_code == 34:
        logger.error("requested object (user, Tweet, etc) not found")
    elif api_code == 64:
        logger.error("your Twitter developer account is suspended and is not permitted")
    elif api_code == 130:
        logger.error("Twitter is currently in over capacity")
    elif api_code == 131:
        logger.error("internal Twitter error occurred")
    elif api_code == 135:
        logger.error("could not authenticate your Twitter API tokens")
    elif api_code == 136:
        logger.error("you have been blocked to perform this action")
    elif api_code == 179:
        logger.error("you are not authorized to see this Tweet")
    else:
        if message:
            logger.error("error while using the Twitter REST API: %s. Message = %s", tweep_error, message)
        else:
            logger.error("error while using the Twitter REST API: %s", tweep_error)
