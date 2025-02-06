from get_songs import get_recently_played_using_time
from helpers import datetime_to_iso_test
from dotenv import load_dotenv
from dateutil import parser

import datetime
import pprint
import  math
import os


load_dotenv()

# Take time now, convert to strava format(iso 8601), then convert to unix timestamp. Pass that in.
if __name__ == "__main__":

    after = datetime_to_iso_test()
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    name = map(lambda x: x['track']['name'], get_recently_played_using_time(AUTH_TOKEN, after)['items'])
    pprint.pprint(list(name))