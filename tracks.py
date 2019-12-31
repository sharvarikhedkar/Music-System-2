
import sys
import flask_api
from flask import request, g, jsonify, Response
from flask_api import FlaskAPI,status, exceptions
import sqlite3
import uuid



global dbname

app = FlaskAPI(__name__) 

sqlite3.register_converter('GUID', lambda b: uuid.UUID(bytes_le=b))
sqlite3.register_adapter(uuid.UUID, lambda u:(u.bytes_le))

def get_db(dbname):
	db = getattr(g,'_database', None)
	if db is None:
		print("1a",dbname)
		db = g._database = sqlite3.connect(dbname)
		print("1b")

		db.row_factory = make_dicts
	return db


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

#To get all tracks info
@app.route("/tracks",methods=['GET'])
def get_all_tracks():
	try:
		sqlQry = "select track_title,album_title,track_artist,track_length,media_url,album_url,created_date from tracks"
		db =  get_db("track_shard1.db")
		rs = db.execute(sqlQry)
		res = rs.fetchall()
		rs.close()
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	return jsonify(list(res)), status.HTTP_200_OK



#To get particular track info
@app.route("/tracks/<title>",methods=['GET'])
def get_track(title):
	try:
		sqlQry = "select track_title,album_title,track_artist,track_length,media_url,album_url,created_date from tracks where track_title = '%s'" %title
		db =  get_db()
		rs = db.execute(sqlQry)
		res = rs.fetchall()
		rs.close()
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	return jsonify(list(res)), status.HTTP_200_OK

#To get particular track info by trackid
@app.route("/tracksbyid/<track_id>",methods=['GET'])
def get_playlist(track_id):
	try:
		print("in track by idstr:",track_id)
		#u = uuid.UUID(str(track_id))

		#print("in trackbyid uuid:",u)
		#print("in track by idstr:",track_id)
		sqlQry = "select track_id,track_title,album_title,track_artist,track_length,media_url,album_url,created_date from tracks where track_id = '%s'" %track_id
		
		print("in track by sqlQry:",sqlQry)
		
		dbname = get_uuid(track_id)
		print("track guid is",dbname)		
		db =  get_db(dbname)

		rs = db.execute(sqlQry)
		res = rs.fetchall()
		print("res",res)
		rs.close()
		
		if len(res)>0:
					print("res")
		else:
			return { 'message': "Track not found" }, status.HTTP_404_NOT_FOUND
				
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	return jsonify(list(res)), status.HTTP_200_OK

def get_uuid(u):
	print("in func uuid:",u)
	#track_id = uuid.uuid4()
	a = uuid.UUID(u).int 
	
	print(a)
	b = a % 3
	print("shard key",b)

	if b==0:
		return "track_shard1.db"

	elif b==1:
		return "track_shard2.db"

	elif b==2:
		return "track_shard3.db"

	




#To insert new track
@app.route("/tracks",methods=['POST'])
def create_tracks():
	mandatory_fields = ['track_title','album_title','track_artist','track_length','media_url']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()	
	
	try:
		track_title 	= request.data.get('track_title','')
		album_title 	= request.data.get('album_title','')
		artist 		= request.data.get('track_artist','')
		track_length 	= request.data.get('track_length','')
		media_url 	= request.data.get('media_url','')
		album_url 	= request.data.get('album_url','')	
		
		u=uuid.uuid4()
		#print("string uuid:",str(u))
		#uInt=uuid.UUID(str(u)).int 
		dbname = get_uuid(str(u))
		#print("2")
		data = (str(u), track_title, album_title, artist, track_length, media_url, album_url)

		sqlQry = "insert into tracks(track_id,track_title,album_title,track_artist,track_length,media_url,album_url) values (?,?,?,?,?,?,?)" 
		#print("3")
		db = get_db(dbname)
		#print("3a")
		c = db.cursor()
		c.execute(sqlQry,data)
		#print("3b")
		db.commit()
		response  = Response(status=201)
		response.headers['location'] = '/tracksbyid/'+str(u)
		response.headers['status'] = '201 Created'
		#print("4")
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_409_CONFLICT
		
	return response, status.HTTP_201_CREATED



#To update a particular track info
@app.route("/tracks",methods=["PUT"])
def update_tracks():
	update_param =()
	mandatory_fields = ['track_id']

	if not all([field in request.data for field in mandatory_fields]):
		raise exceptions.ParseError()
	track_id 	= request.data.get('track_id')
	ntrack_title 	= request.data.get('new_track_title')
	nalbum_title 	= request.data.get('new_album_title','')
	nartist 	= request.data.get('new_track_artist','')
	ntrack_length 	= request.data.get('new_track_length','')
	nmedia_url 	= request.data.get('new_media_url','')
	nalbum_url 	= request.data.get('new_album_url','')	
	print("track_id::::",track_id)

	sqlQry = "UPDATE tracks SET "
	
	if ntrack_title:
		sqlQry +=' track_title =?'
		update_param = update_param + (ntrack_title,)

	if nalbum_title:
		sqlQry +=', album_title =?'
		update_param = update_param + (nalbum_title,)
		
	if nartist:
		sqlQry +=', track_artist =?'
		update_param = update_param + (nartist,)

	if ntrack_length:
		sqlQry +=', track_length =?'
		update_param = update_param + (ntrack_length,)
		
	if nmedia_url:
		sqlQry += ', media_url =?'
		update_param = update_param + (nmedia_url,)
		
	if nalbum_url:
		sqlQry += ', album_url =?'
		update_param = update_param + (nalbum_url,)


	sqlQry += ' WHERE track_id =?'
	update_param = update_param + (track_id,)

	sqlQry += ';'
	print("sqlQry::::",sqlQry)
	dbname = get_uuid(str(track_id))
	print("dbanem::::",dbname)

	db  = get_db(dbname)
	cur = db.cursor()
	cur.execute(sqlQry, update_param)
	db.commit()
	cur.close()
	
	return "Record Updated",status.HTTP_200_OK


#To delete a particular track
@app.route("/tracks/<track_id>",methods=['DELETE'])
def delete_tracks(track_id):
	try:
		dbname = get_uuid(str(track_id))
		db  = get_db(dbname)
		sqlQry = "delete from tracks where track_id = '%s'" %track_id
		rs = db.execute(sqlQry)
		db.commit()
	
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND

	return "Track deleted successfully", status.HTTP_200_OK


if __name__ == "__main__":
	app.run(debug=True)
	
