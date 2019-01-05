import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pylast
import time
import os
import logging


#LASTFM credentials
API_KEY = '6cadeed51479fbece77f4f6f9d0f8f92'
API_SECRET = '9e90f57f812a83d68265e4e001ec61e1'
username = 'popsxjlive'
password_hash = pylast.md5('cc2018,')
network = pylast.LastFMNetwork(API_KEY, api_secret = API_SECRET, username = username, password_hash = password_hash)

# SPOTIFY credentials
SPOTIFY_KEY = "22355c3b7ef8428b9835f6d19ca44f2b"
SPOTIFY_SECRET = "a1a20a518e6844e0a56ee5c6b1f0c9e9"

# DEBUG
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

def get_slots(intent_request):
    return intent_request['currentIntent']['slots']


def picture_with_url(song_name, img_url, preview_url):
    img_url = "\"" + img_url + "\""
    preview_url = "\"" + preview_url + "\""
    return "<br>{0:s}</br><br><a href={1:s} target = \"view_window\"><img src={2:s}/></a></br>".format(song_name,
                                                                                                       preview_url,
                                                                                                       img_url)

def get_auido_html(preview_url):
    preview_url = "\"" + preview_url + "\""
    return "<br><audio src={0:1} controls=\"controls\"></audio></br>".format(preview_url)



def get_content(recommendations_list):
    if recommendations_list is not None:
        html_code = ''
        for item in recommendations_list:
            name, img_url, pre_url = item.split(",")
            audio_code = get_auido_html(pre_url)
            html_code = html_code + picture_with_url(name, img_url, pre_url)+audio_code

        return html_code
    else:
        return None


def validate_info(song_name, musician_name):
    return (song_name != None and musician_name != None)


def get_items_list(original_query_result):
    return original_query_result['tracks']['items']

# get similar songs from lastfm


def get_similar_songs(song_name, artist):
    seed_song = network.get_track(artist, song_name)
    try:
        similar_songs_list = []
        recommendations = seed_song.get_similar()
        if len(recommendations) > 0:
            if len(recommendations) >=3:
                recommendations = recommendations[0:3]
            else:
                recommendations = recommendations[0:len(recommendations)]
            for i in range(0, len(recommendations)):
                similar_songs_list.append(str(recommendations[i][0]))
            return similar_songs_list
        else:
            return None
    except Exception as e:
        print("No tracks found. Please check your input!")
        return None


def get_name_img_preview_url(similar_results_list):
    recommendation_list = []
    if similar_results_list is not None:
        client_credentials_manager = SpotifyClientCredentials(SPOTIFY_KEY, SPOTIFY_SECRET)
        sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)
        for similar_song in similar_results_list:

            results = sp.search(q=similar_song, type = 'track', limit = 1)
            results_list = get_items_list(results)
            # determine whether it is null value
            if len(results_list) == 0:
                print("OOPS. There is no such song in spotify. Sorry!")
            else:
                img_url = results_list[0]['album']['images'][1]['url']
                preview_url = results_list[0]['preview_url']

                if similar_song is None:
                    similar_song = "Song name is None"
                if img_url is  None:
                    img_url = "https://cdn.browshot.com/static/images/not-found.png"
                if preview_url is None:
                    preview_url = "https://www.theuselesswebindex.com/error/"
                name_img_pre = similar_song + "," + img_url + "," + preview_url
                recommendation_list.append(name_img_pre)
        return recommendation_list
    else:
        return None


def thank_you_response(intent_request):
    return {"dialogAction": {
    "type": "Close",
    "fulfillmentState": "Fulfilled",
    "message": {
      "contentType": "PlainText",
      "content": "You are welcome."
    }
    }}


def song_suggestion_response(intent_request):
    song_name = get_slots(intent_request)['SongName']
    musician_name = get_slots(intent_request)['MusicianName']
    logger.debug(song_name + musician_name)

    if validate_info(song_name, musician_name):
        similar_songs_list = get_similar_songs(song_name, musician_name)
        recommendations_list = get_name_img_preview_url(similar_songs_list)
        print(recommendations_list)
        html_code = get_content(recommendations_list)

        if html_code is not None:
            return {"dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "You’re all set. Enjoy my recommendations! Click the picture to play music.{0:s}".format(
                        html_code)
                }
            }}
        else:
            return {"dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Whoops! I can not find that. Please check your input!"
                }
            }}


def play_music_response(intent_request):
    song_name = get_slots(intent_request)['SongName']
    musician_name = get_slots(intent_request)['MusicianName']
    logger.debug(song_name + musician_name)
    song_list = []
    if validate_info(song_name, musician_name):
        if musician_name == "#":
            search_keyword = song_name
        else:
            search_keyword = song_name + " - " + musician_name
        song_list.append(search_keyword)
        song_info_list = get_name_img_preview_url(song_list)
        html_code = get_content(song_info_list)

        if html_code is not None:
            return {"dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Enjoy your music.{0:s}".format(
                        html_code)
                }
            }}
        else:
            return {"dialogAction": {
                "type": "Close",
                "fulfillmentState": "Fulfilled",
                "message": {
                    "contentType": "PlainText",
                    "content": "Whoops! I can not find that. Please check your input!"
                }
            }}

def conversation_response(intent_request):
    name = 'Pharrell Williams - Happy'
    img_url = 'https://i.scdn.co/image/473a3dd985633cb0f5f9cf43b738edf8271fbd09'
    pre_url = 'https://p.scdn.co/mp3-preview/609cf640a652b3ca4d22b1d604f0885b7a591af9?cid=22355c3b7ef8428b9835f6d19ca44f2b'
    html_code = ''
    html_code = html_code + picture_with_url(name, img_url, pre_url) + get_auido_html(pre_url)
    return {"dialogAction": {
        "type": "Close",
        "fulfillmentState": "Fulfilled",
        "message": {
            "contentType": "PlainText",
            "content": "All what I want to say is in the music.{0:s}".format(
                html_code)
        }
    }}

def greeting_response(intent_request):
    return {"dialogAction": {
    "type": "Close",
    "fulfillmentState": "Fulfilled",
    "message": {
      "contentType": "PlainText",
      "content": "Hi, I am Music bot Tara. Now I am able to do following things. <br>1.<I>play music</I></br><br>2.<I>recommend music</I></br><br>3.<I>have conversation</I></br><br>Start Service by inputing command</br>"
    }
    }}

def dispatch(intent_request):
    intent_name = intent_request['currentIntent']['name']
    if intent_name == 'GreetingIntent':
        return greeting_response(intent_request)
    elif intent_name == 'SongRecommendationIntent':
        return song_suggestion_response(intent_request)
    elif intent_name == 'PlayMusic':
        return play_music_response(intent_request)
    elif intent_name == 'ConversationIntent':
        return conversation_response(intent_request)
    elif intent_name == 'ThankYouIntent':
        return thank_you_response(intent_request)
    raise Exception("Intent with name" + intent_name + 'not supported')

def lambda_handler(event, context):
    #set default time zone
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    return dispatch(event)