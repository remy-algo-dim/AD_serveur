import sys, os
from flask import Flask, render_template,request,json, url_for, flash, request, session, redirect, Blueprint
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import json
import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'premium'))
import main_robot_1

sys.dont_write_bytecode = True

try:
	# Connect to the database
	connection = pymysql.connect(host='linkedin.c0oaoq9odgfz.eu-west-3.rds.amazonaws.com',
								 user='root',
								 password='Leomessi9',
								 db='linkedin',
								 charset='utf8mb4',
								 cursorclass=pymysql.cursors.DictCursor)

except:
	# So we create the db
	print('Database not exists')
	conn = pymysql.connect(host='localhost',user='root',password='Leomessi9')
	conn.cursor().execute('create database linkedin')
	conn.cursor().execute('create table linkedin.user (id int NOT NULL AUTO_INCREMENT,email varchar(255) NOT NULL,\
									password varchar(255), name varchar(255), client varchar(255), security_code int, PRIMARY KEY (id));')
	connection = pymysql.connect(host='linkedin.c0oaoq9odgfz.eu-west-3.rds.amazonaws.com',
								 user='root',
								 password='Leomessi9',
								 db='linkedin',
								 charset='utf8mb4',
								 cursorclass=pymysql.cursors.DictCursor)



app = Flask(__name__)
app.secret_key = 'super secret key'




""" -------------------------------------------- 1ere Partie : Log in/ Log out -------------------------------------------- """

@app.route('/')
def index():
	return render_template('index_remy.html')



@app.route('/signup')
def signup():
	return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
	email = request.form.get('email')
	name = request.form.get('name')
	password = request.form.get('password')

	with connection.cursor() as cursor:
		# On check si le mail n'est pas ds la DB
		if cursor.execute("""SELECT email FROM linkedin.user WHERE email=%s""", (email)) == 1:
			flash('Email address already exists')
			return redirect(url_for('signup'))
		else:
			# On rajoute la personne ds la DB
			cursor.execute("""INSERT INTO linkedin.user (email, name, password) VALUES (%s, %s, %s)""", (email, name, generate_password_hash(password, method='sha256')))
			connection.commit()
			return redirect(url_for('login'))




@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False

	with connection.cursor() as cursor:
		# On verifie d'abord si le mail existe
		if cursor.execute("""SELECT email FROM linkedin.user WHERE email=%s""", email) == 0:    
			flash('Please check your login details and try again.')
			return redirect(url_for('login'))
		# On recupere ici le mdp de la db correspondant au mail entre par le user
		query_expected_pwd = cursor.execute("""SELECT password FROM linkedin.user WHERE email=%s""", email)
		password_hached = cursor.fetchall()[0]['password'] # Password hache
		expected_pwd = check_password_hash(password_hached, password) # True si le password entre correspond au password hache
		if expected_pwd is False:
			# Si le mdp entre est faux
			flash('Please check your login details and try again.')
			return redirect(url_for('login'))
		else:
			query = cursor.execute("""SELECT id FROM linkedin.user WHERE email=%s""", email)
			session['id'] = cursor.fetchall()[0]['id']
			session['email'] = email
			session['password'] = password
			return redirect(url_for('profile'))



""" A partir du moment on on s'est login, c'est a dire que le mdp qu'on a rentre correspond a celui de la DB, 
une SESSION existe, et c'est a nous de constuire session[column_name] avec column_name faisant parti des colonnes de la db,
afin d'enregistrer quelquepart les valeurs de la session (au moins pour une colonne, et les autres colonnes existeront automatiquement
je crois ...)
On peut aussi cree des colonnes intermediaires comme : session['new_val'] = X

Lorsqu'on fera session.pop, la session expirera et session[X] ne renverra rien """


@app.route('/profile')
def profile():
	""" Profile est divise en une methode GET et une POST afin de pouvoir acceder a son profil sans avoir besoin de runner
	l'algo ou de le runner par erreur. Dans la methode POST on fait en sorte que le user entre une nouvelle fois son mdp
	et appuie sur start pour lancer l'algo """
	try:
		# !!!!! Comme vu ds la fonction logout, si la session a expire, on ne rentrera meme pas ds le if car session['email'] n'existe
		# meme plus et donc on ne peux plus acceder a cette page
		if session['email']:
			return render_template('profile.html', name=session['email'])
	except:
		return redirect(url_for('login'))

@app.route('/profile', methods=['POST'])
def profile_post():
	password_non_hashed = request.form.get('password')
	try:
		with connection.cursor() as cursor:
			query_expected_pwd = cursor.execute("""SELECT password FROM linkedin.user WHERE email=%s""", session['email'])
			password_hached = cursor.fetchall()[0]['password']
			expected_pwd = check_password_hash(password_hached, password_non_hashed)
			if expected_pwd:
				session['password_non_hashed'] = password_non_hashed #on cree ce nouvel objet ds la session pr l'utiliser dans la route script
				return redirect(url_for('script'))
			else:
				return redirect(url_for('profile'))
	except:
		return redirect(url_for('login'))



@app.route('/logout')
def logout():
	# Lorsqu'on se logout, on pop l'email (par exemple), et donc notre session expire, il n'y a donc plus d'objet session
	session.pop('email', None)
	return redirect(url_for('login'))


""" -------------------------------------------- 2eme Partie : Algos -------------------------------------------- """




@app.route('/script')
def script():
	try:
		if session['email']:
			print('on va appliquer main robot 1')
			return main_robot_1.main(session['id'], session['email'], session['password_non_hashed'])
	except:
		return redirect(url_for('login'))


@app.route('/dash')
def dashboard():
	# le dashboard va chercher les datas dans le json
	try:
		if session['email']:
			with open(os.path.join(os.path.dirname(__file__), '../src/premium/Contacts/stats_'+str(session['id'])+'.json'),'r') as j:
				json_data = json.load(j)
				nb_contacted_total = json_data["Total messages envoyes"]
				nb_contacted_today = json_data["Total envoyes aujourd'hui"]
				nb_contacted_per_filter = json_data["Personnes a contacter pour ce filtre"]
				pending_invit = json_data["Pending invit"]
				print(nb_contacted_total, nb_contacted_today,nb_contacted_per_filter, pending_invit)
				return render_template('index.html', total_envoyes=nb_contacted_total, total_today=nb_contacted_today,
						nb_contacted_per_filter=nb_contacted_per_filter, pending_invit=pending_invit)
	except:
		return redirect(url_for('login'))


if __name__ == "__main__":
	app.run(port=5000, host='0.0.0.0')


	#login_manager = LoginManager()
	#login_manager.login_view = 'login'
	#login_manager.init_app(app)


	#@login_manager.user_loader
	#def load_user(id):
	#    try:
	#        return session['id']
	#    except:
	#        return None  


# ssh -i remy_key.pem  ubuntu@ec2-15-188-147-7.eu-west-3.compute.amazonaws.com
# sudo docker run -v /home/ubuntu/AD_serveur/:/src -p 80:5000 -t -d --restart always algo-dimension


