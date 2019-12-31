#!/usr/bin/python

import requests, json, xspf
import sys
import flask_api
from flask import request, g, jsonify, Response, make_response
from flask_api import FlaskAPI, status, exceptions



app = FlaskAPI(__name__)

# To get  playlists xspf xml by id
@app.route("/playlist/<playlist_id>",methods=['GET'])
def get_all_playlistbyid(playlist_id):
	try:
		url = 'http://localhost:8000/playlists/'+playlist_id
		headers = {'content-type': 'application/xspf+xml'}
		print("play id:",playlist_id);
		playlist_res = requests.get(url,headers=headers)
		print("playlist playlist_res:",playlist_res)
		json_object = playlist_res.json()
		print("playlist json:",json_object)
		if len(json_object) > 0:
			xmlObj = xspf.Xspf()
			xmlObj.title = json_object[0][1]
			xmlObj.creator = json_object[0][0]
			for list1 in json_object:
				track_id = list1[3]
				print("track_id:",track_id)
				track_url = 'http://localhost:8000/tracksbyid/'+str(track_id)
				track_headers = {'content-type': 'application/xspf+xml'}
				track_res = requests.get(track_url,headers=track_headers)
				track_jsonObj = track_res.json()
				print("track_jsonObj:",track_jsonObj)
				if len(track_jsonObj) > 0:
					for trackList in track_jsonObj:
						trackTitle = trackList["track_title"]
						trackCreator = trackList["track_artist"]
						track_node = xspf.Track(title=trackTitle, creator=trackCreator,album=trackList["album_title"])
						track_node.trackNum = str(trackList["track_id"])
						track_node.location = trackList["media_url"]
						track_node.duration = str(trackList["track_length"])
						xmlObj.add_track(track_node)
						
						
						
				else:
					return { 'message': "Track not found" }, status.HTTP_404_NOT_FOUND
					
				
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	return xmlObj.toXml(), status.HTTP_200_OK






if __name__ == "__main__":
	app.run(debug=True)
