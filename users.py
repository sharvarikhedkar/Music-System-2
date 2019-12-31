import sys
import flask_api
from flask import request, g, jsonify, Response
from flask_api import FlaskAPI, status, exceptions
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3



app = FlaskAPI(__name__) 

def get_db():
	db = getattr(g,'_database', None)
	if db is None:
		db = g._database = sqlite3.connect('music.db')
	return db

@app.route("/users/auth",methods=['POST'])
def auth_users():
	mandatory_fields = ["user_name","password"]

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()	

	user_name 	= request.data.get('user_name','')
	password 	= request.data.get('password','')
	
	sqlQry = "select hashed_password from users where user_name = '%s'" %user_name
	db =  get_db()
	rs = db.execute(sqlQry)
	res = rs.fetchall()
	
	encPass = res[0][0]
	
	rs.close()
	if check_password_hash(encPass, password):
		return "success", status.HTTP_200_OK
	else:
		return "Unauthorized Access", status.http_401_unauthorized


@app.route("/users",methods=['GET'])
def get_users():
	sqlQry = "select user_name,display_name,email_id,home_url,created_date from users "
	db =  get_db()
	rs = db.execute(sqlQry)
	res = rs.fetchall()
	rs.close()
	return jsonify(list(res)), status.HTTP_200_OK

@app.route("/users/<user_name>",methods=['GET'])
def get_user(user_name):
	
	try:	
		sqlQry = "select user_name,display_name,email_id,home_url,created_date from users where user_name ='%s'" %user_name
		db =  get_db()
		rs = db.execute(sqlQry)
		res = rs.fetchall()
		rs.close()
	
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_404_NOTFOUND
	
	else:
		return jsonify(list(res)), status.HTTP_200_OK


@app.route("/users",methods=['POST'])
def create_users():
	mandatory_fields = ['user_name','password','display_name','email_id']

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()
	
	try:
		user_name 	= request.data.get('user_name','')
		password 	= request.data.get('password','')
		hashed_password = generate_password_hash(password)
		display_name 	= request.data.get('display_name','')
		email_id 	= request.data.get('email_id','')
		home_url 	= request.data.get('home_url','')
		
		sqlQry = "insert into users(user_name,hashed_password,display_name,email_id,home_url) values ('%s','%s','%s','%s','%s')" %(user_name,hashed_password,display_name,email_id,home_url)
		db = get_db()
		db.execute(sqlQry)
		db.commit()
		response  = Response(status=201)
		response.headers['location'] = '/users/'+user_name
		response.headers['status'] = '201 Created'

	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_409_CONFLICT

	return response, status.HTTP_201_CREATED


@app.route("/users/<user_name>",methods=['DELETE'])
def delete_users(user_name):
	try:	
		sqlQry = "delete from users where user_name = '%s'" %user_name
		db = get_db()
		var = db.execute(sqlQry)
		db.commit()
		#print("var", var)
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_409_CONFLICT 

	return "User deleted successfully", status.HTTP_200_OK


@app.route("/users",methods=['PUT'])
def update_password():
	
	mandatory_fields = ["user_name","password","new_password"]

	if not all([field in request.data for field in mandatory_fields]):
        	raise exceptions.ParseError()	

	user_name 	= request.data.get('user_name','')
	password 	= request.data.get('password','')
	new_password 	= request.data.get('new_password','')

	new_hashed_password = generate_password_hash(new_password)
	
	try:
		sqlQr = "update users set hashed_password = '%s' where user_name = '%s'" %(new_hashed_password,user_name)
		db1 =  get_db()
		db1.execute(sqlQr)
		db1.commit()
			
	except Exception as e:
        	return { 'error': str(e) }, status.HTTP_409_CONFLICT
	
	return request.data, status.HTTP_200_OK


if __name__ == "__main__":
	app.run(debug=True)
	
