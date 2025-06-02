from spotify import get_recently_played_using_time
from time import datetime_to_iso_test
from dotenv import load_dotenv
from spotify import create_playlist, add_songs
import pprint


load_dotenv()

# Take time now, convert to strava format(iso 8601), then convert to unix timestamp. Pass that in.
if __name__ == "__main__":
    # Convert time
    after = datetime_to_iso_test()
    # Get songs using time
    song_names, song_ids = get_recently_played_using_time(after)
    pprint.pprint(song_ids)

    # Create playlist test:
    playlist_id = create_playlist(
        user_id="kamandgetit",
        token="",
        playlist_name="Greetings from VsCode",
        playlist_description="Definitely a test!",
        public=True,
    )
    print(playlist_id)

    # Add songs to playlist
    print(
        add_songs(
            recently_played_songs_id_array=list(song_ids), playlist_id=playlist_id
        )
    )
