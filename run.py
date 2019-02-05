import sys
import spotipy
import spotipy.util as util
import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
from operator import itemgetter, attrgetter
from random import randint


scope = 'user-library-read'
username = 'fake'
client_id='PUT YOUR CLIENT ID HERE'
client_secret='PUT YOUR CLIENT SECRET HERE'
redirect_uri='http://localhost'  #This needs to be in your spotify app setup as well


def GetArtistOldestAlbum(sp,artistid, artistname):
    #Get Oldest Album with Tracks:
    oldest_album_id = ''
    oldest_album_name = ''
    oldest_album_date = datetime.datetime.strptime('2080', "%Y")
    
    albums = []
    results = sp.artist_albums(artistid, album_type='album', country=None, limit=50, offset=0)
    albums.extend(results['items'])
    while results['next']:
        results = sp.next(results)
        albums.extend(results['items'])
        
    for album in albums:
        tracks = []
        results = sp.album_tracks(album['id'], limit=50, offset=0)
        tracks.extend(results['items'])
        while results['next']:
            results = sp.next(results)
            tracks.extend(results['items'])
        if len(tracks) > 2:
            albumdate = None
            if album['release_date_precision'] == 'year': 
                albumdate = datetime.datetime.strptime(album['release_date'], "%Y")
            elif album['release_date_precision'] =='month': 
                albumdate = datetime.datetime.strptime(album['release_date'], "%Y-%M")
            else:
                #print(album['release_date'],album['release_date'][0:7])
                albumdate = datetime.datetime.strptime(album['release_date'][0:7], "%Y-%M")
                
            if (oldest_album_date > albumdate):
                #print('oldest', album['name'],album['release_date'],album['release_date_precision'],len(tracks))
                oldest_album_date = albumdate
                oldest_album_id = album['id']
                oldest_album_name= album['name'] + ' - ' + album['id']
            #else:
            #    print('not oldest', album['name'],album['release_date'],album['release_date_precision'],len(tracks))
        else:
            print('too small', album['name'],album['release_date'],album['release_date_precision'],len(tracks))
    #print (artistname, artistid, oldest_album_name,oldest_album_date,oldest_album_id)

    return (oldest_album_name,oldest_album_date)

def GetRelatedArtistWithNextOldestAlbum(sp, artistid, oldest_album_date, alreadyusedartistids):
    debug = False
    if debug:
        print('Related artists for', artistid)
    related = sp.artist_related_artists(artistid)
    
    date_years_before = oldest_album_date - relativedelta(years=2)

    sorted_info = []
    for artist in related['artists']:
        if artist['id'] in alreadyusedartistids:
            if debug:
                print('     already used:',artist['name'])
            fake = ''
        else:
            rel_artist_album_name,rel_artist_album_date = GetArtistOldestAlbum(sp, artist['id'], artist['name'])
            days_from_years = abs((date_years_before - rel_artist_album_date).days)
            
            rel_artist_id = artist['id']
            rel_artist_info = artist['name'] + ' - ' + rel_artist_album_name
            sorted_info.append([days_from_years,rel_artist_album_date,rel_artist_id,rel_artist_info])
    
    sorted_info = sorted(sorted_info, key=itemgetter(0))
    if debug:
        for si in sorted_info:
            print(si[2], si[1],si[3], si[0])
            
    for si in sorted_info:
        alreadyusedartistids.append(si[2])
        return si[2], si[1],si[3], alreadyusedartistids    
   
    
artistlist = ['Bob Marley', 'Darshan Raval','Maroon Five', 'Queen', 'August Burns Red', 'Daft Punk', 'Dolly Parton']
for art in artistlist:
    try:
        token = util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=redirect_uri)
        print(token)

        if token:
            sp = spotipy.Spotify(auth=token)
            search_string = art
            
            iterations = 0
            alreadyusedartistids = []
            
            oldestsofar = datetime.datetime.strptime('2080', "%Y")
            
            results = sp.search(q='artist:' + search_string, type='artist')
            items = results['artists']['items']
            if len(items) > 0:
                artist = items[0]
                print(artist['name'], artist['id'])
                artid = artist['id']
                oldest_album_name,oldest_album_date = GetArtistOldestAlbum(sp,artist['id'],artist['name'])
                #oldest_album_name,oldest_album_date = 'Ten Redux', datetime.datetime.strptime('1991-01-27', "%Y-%M-%d")
                
                print(artist['name'], artist['id'], oldest_album_name,oldest_album_date)
                
                relatedartistid = artid
                relatedartist_date = oldest_album_date
                relatedartistid, relatedartist_date, relatedartistinfo, alreadyusedartistids = GetRelatedArtistWithNextOldestAlbum(sp, relatedartistid,relatedartist_date,alreadyusedartistids)
                print('***',relatedartistid, relatedartist_date, relatedartistinfo)
                
                if True:
                    while iterations < 100:
                        iterations = iterations + 1
                        relatedartistid, relatedartist_date, relatedartistinfo, alreadyusedartistids = GetRelatedArtistWithNextOldestAlbum(sp, relatedartistid,relatedartist_date,alreadyusedartistids)
                        if oldestsofar >= relatedartist_date:
                            oldestsofar = relatedartist_date
                            print('***', relatedartistid, relatedartist_date, relatedartistinfo)
                        else:
                            
                            print('*n*', relatedartistid, relatedartist_date, relatedartistinfo)
                        
                
                
                
            else:
                print('Could not find artist')
        else:
            print( "Can't get token for", username)
    except:
        print('Error')
