import sys
import flask_api
from flask import request, g, jsonify, Response, make_response
from flask_api import FlaskAPI,status, exceptions
import sqlite3

app = FlaskAPI(__name__) 

def get_db():
	db = getattr(g,'_database', None)
	if db is None:
		db = g._database = sqlite3.connect('music.db')
	return db


# To get all plalists
@app.route("/playlists",methods=['GET'])
def get_all_playlists():
	try:
		sqlQry = "select playlist_id,playlist_title,user_name,created_date from playlists"		
		db =  get_db()
		rs = db.execute(sqlQry)
		
		res = rs.fetchall()
		rs.close()
		
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND
	
	return jsonify(list(res)), status.HTTP_200_OK


#To get particular playlist info
@app.route("/playlists/<playlist_id>",methods=['GET'])
def get_playlist(playlist_id):
	try:
		print("playlist_id",playlist_id)
		sqlQry = "select a.user_name,a.playlist_title,a.created_date,b.track_id from playlists a, playlist_tracks b where a.playlist_id = b.playlist_id and a.playlist_id = '%s'" %(playlist_id)
		print("sqlQry",sqlQry)
		db =  get_db()
		rs = db.execute(sqlQry)
		res = rs.fetchall()
		print(res)
		rs.close()
		if len(res)>0:
					print("res")
		else:
			return { 'message': "Track not found" }, status.HTTP_404_NOT_FOUND
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	return jsonify(list(res)), status.HTTP_200_OK


#To get all playlist by a user 
@app.route("/playlistsbyuser/<user_name>",methods=['GET'])
def get_user_playlists(user_name):
	try:
		sqlQry = "select A.playlist_id,A.playlist_title,A.description,A.created_date from playlists A, users B where a.user_name = b.user_name and a.user_name = '%s'" %user_name		
		db =  get_db()
		rs = db.execute(sqlQry)
		res = rs.fetchall()
		rs.close()
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	return jsonify(list(res)), status.HTTP_200_OK


#To create playlists of a user
@app.route("/playlists",methods=['POST'])
def create_playlists():
	mandatory_fields = ['playlist_title','user_name','track_id']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()

	playlist_title = request.data.get('playlist_title','')
	user_name      = request.data.get('user_name','')
	description    = request.data.get('description','')
	track_title    = (request.data.get('track_id',''))
	
	db = get_db()
	try:
		sqlQry1 = "insert into playlists(user_name,playlist_title,description) values ('%s','%s','%s')" %(user_name,playlist_title,description)
		db.execute(sqlQry1)
		
		
		sqlQry2 = "insert into playlist_tracks(playlist_id,track_id) values ((select max(playlist_id) from playlists ),track_id)" %(str(track_title))
		db.execute(sqlQry2)
		db.commit()
		response  = Response(status=201)
		response.headers['location'] = '/playlistsbyuser/'+user_name
		response.headers['status'] = '201 Created'

	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_409_CONFLICT

	return response, status.HTTP_201_CREATED
	

#to add tracks in playlist	
@app.route("/playlists/<playlist_id>",methods=['POST'])
def add_tracks(playlist_id):
	mandatory_fields = ['track_id']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()

	track_id = request.data.get('track_id','')
	print("track_id:",track_id)
	
	db = get_db()
	try:
		
			#track_id = res[0][0]
			sqlQry2 = "insert into playlist_tracks(playlist_id,track_id) values ('%s','%s')" %(playlist_id,str(track_id))
			print("sqlQry2:",sqlQry2)
			db.execute(sqlQry2)
			db.commit()
			print("1")
			response  = Response(status=201)
			response.headers['location'] = '/playlists/'+playlist_id
			response.headers['status'] = '201 Created'
			print("1")

	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_409_CONFLICT

	return response, status.HTTP_201_CREATED	


#To delete a playlist
@app.route("/playlists/<playlist_title>",methods=['DELETE'])
def delete_playlist(playlist_title):
	try:
		db = get_db()
		sqlQry = "delete from playlist_tracks where playlist_id = (select playlist_id from playlists where playlist_title ='%s')" %playlist_title
		rs = db.execute(sqlQry)
		
		sqlQry = "delete from playlists where playlist_title ='%s'" %playlist_title
		rs = db.execute(sqlQry)
		
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	db.commit()
	return "Playlist deleted successfully", status.HTTP_200_OK


if __name__ == "__main__":
	app.run(debug=True)
	
