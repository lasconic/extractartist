from pyechonest import artist
from pyechonest.util import EchoNestIOError
import requests
import string
import time
import codecs

apikey = 'musichackday'
endpoint = 'http://api.musescore.com/services/rest/score'
format = 'json'

def find_substring(needle, haystack):
	if haystack is None or needle is None:
		return False
	index = haystack.lower().find(needle.lower())
	if index == -1:
	    return False
	if index != 0 and haystack[index-1] not in string.whitespace:
	    return False
	L = index + len(needle)
	if L < len(haystack) and haystack[L] not in string.whitespace:
	    return False
	return True

def findSongs(songComposer, score):
	songs = songComposer.get_songs()
	if len(songs) == 0:
		print "No song for artist " + score['permalink']
	index = 0
	for song in songs:
		songTitle = song.title
		if songTitle.lower() in score['title'].lower():
			print "MATCH:" + songComposer.name + " - " + song.title + " - " + score['permalink']
			return True
		if songTitle.lower() in score['metadata']['title'].lower():
			print "MATCH:" + songComposer.name + " - " + song.title + " - " + score['permalink']
			return True
		index += 1
	if(index !=0 and index == len(songs)):
		print "No matching song for artist " + score['permalink']
	return False

def findSongsMBZ(songComposer, score):
	if (len(songComposer.name) < 2):
		return False
	mbzId = songComposer.get_foreign_id()
	if(mbzId is None):
		return False
	idx = mbzId.rfind(':') + 1
	mbzId = mbzId[idx:]
	r = requests.get('http://ws.audioscrobbler.com/2.0/?method=artist.gettoptracks&mbid=' + mbzId+ '&api_key=d93cef551db47d8e5527f3bd2ac5d30f&format=json')
	songs = r.json()
	#if (songs['error'] != '0'):
	#	return False
	index = 0
	for song in songs['toptracks']['track']:
		songTitle = song['name']
		if (songTitle.lower() == songComposer.name.lower()):
			continue
		if (len(songTitle) < 2):
			continue
		if find_substring(songTitle, score['title']) and songTitle:
			print "MATCH:" + songComposer.name + " - " + songTitle + " - " + score['permalink']
			file.write('"' +songComposer.name + '";"' + songComposer.id  + '";"' + songTitle + '";"' + song['mbid'] + '";"'  + score['permalink'] + '"\n')
			return True
		if find_substring(songTitle, score['metadata']['title']):
			print "MATCH:" + songComposer.name + " - " + songTitle + " - " + score['permalink']
			file.write('"' +songComposer.name + '";"' + songComposer.id  + '";"' + songTitle + '";"' + song['mbid'] + '";"'  + score['permalink'] + '"\n')
			return True
		index += 1
	#if(index !=0 and index == len(songs)):
	#	print "No matching song for artist " + score['permalink']
	return False


def findSongsInArray(composers, score):
	for songComposer in composers:
		if findSongsMBZ(songComposer, score):
			return True
	return False


file = codecs.open("output.csv", "a", "utf-8-sig")

for page in xrange(23,50):
	url = endpoint  + '.' +format + '&oauth_consumer_key=' + apikey + '&page=' + str(page)
	r = requests.get(url)

	scores = r.json()

	print str(page) + " - " + str(len(scores))
	for score in scores:
		try:
			scoreid = score['id']

			#get a score
			url = endpoint + "/" + str(scoreid) + '.' +format + '&oauth_consumer_key=' + apikey
			r = requests.get(url)
			score = r.json()

			scoreComposer = score['metadata']['composer']

			description = False
			# try to get the score composer in the composer string
			
			results = artist.extract(scoreComposer)
			
			# if not found try in the description
			if (len(results) == 0):	
				results = artist.extract(score['description'])
				description = True

			
			if (len(results) > 0):
			    found = findSongsInArray(results, score)
			    if( not found and not description):
			    	try:
			    		results = artist.extract(score['description'])
			    		found = findSongsInArray(results, score)
			    	except EchoNestIOError:
						print "pyechonest.util.EchoNestIOError"
						continue
			#else: 
				#print "Artist not found " + score['permalink']
		except EchoNestIOError:
			print "pyechonest.util.EchoNestIOError"
			continue
		except ValueError:
			print "ValueError"
			continue
		except TypeError:
			print 'TypeError'
			continue
		except KeyError:
			print 'KeyError'
			continue
		time.sleep(10)
file.close()
