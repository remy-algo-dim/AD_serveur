import sys, os
from flask import Flask, render_template,request,json, url_for, flash, request, session, redirect, Blueprint
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash
import json
import datetime
import logging
import time
import traceback


sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'premium'))
import main_robot_1, main_robot_2, test_send_msg

sys.dont_write_bytecode = True

# Logger
logging.basicConfig(stream=sys.stdout,
                    level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)



def db_connect():
	logger.info("Connexion to the database")
	# Connect to the database
	connection = pymysql.connect(host='linkedin.c0oaoq9odgfz.eu-west-3.rds.amazonaws.com',
								 user='root',
								 password='Leomessi9',
								 db='linkedin',
								 charset='utf8mb4',
								 cursorclass=pymysql.cursors.DictCursor)
	return connection

def db_create():
	# So we create the db
	logger.info('Database not exists')
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
	check_pswd = request.form.get('check your password')
	if password != check_pswd:
		flash('Check again your password')
		return redirect(url_for('signup'))
	else:
		connection = db_connect()
		with connection.cursor() as cursor:
			# On check si le mail n'est pas ds la DB
			if cursor.execute("""SELECT email FROM linkedin.user WHERE email=%s""", (email)) == 1:
				flash('Email address already exists')
				connection.close()
				return redirect(url_for('signup'))
			else:
				# On rajoute la personne ds la DB
				cursor.execute("""INSERT INTO linkedin.user (email, name, password) VALUES (%s, %s, %s)""", (email, name, generate_password_hash(password, method='sha256')))
				connection.commit()
				connection.close()
				return redirect(url_for('login'))




@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
	email = request.form.get('email')
	password = request.form.get('password')
	remember = True if request.form.get('remember') else False

	connection = db_connect()
	with connection.cursor() as cursor:
		# On verifie d'abord si le mail existe
		if cursor.execute("""SELECT email FROM linkedin.user WHERE email=%s""", email) == 0:    
			flash('Please check your login details and try again.')
			connection.close()
			return redirect(url_for('login'))

	connection.close()
	connection = db_connect()
	with connection.cursor() as cursor:
		# On recupere ici le mdp de la db correspondant au mail entre par le user
		query_expected_pwd = cursor.execute("""SELECT password FROM linkedin.user WHERE email=%s""", email)
		password_hached = cursor.fetchall()[0]['password'] # Password hache
		expected_pwd = check_password_hash(password_hached, password) # True si le password entre correspond au password hache
		if expected_pwd is False:
			# Si le mdp entre est faux
			flash('Please check your login details and try again.')
			connection.close()
			return redirect(url_for('login'))
		else:
			query = cursor.execute("""SELECT id, name, robot FROM linkedin.user WHERE email=%s""", email)
			query_output = cursor.fetchall()[0]
			session['id'] = query_output['id']
			session['name'] = query_output['name']
			session['robot'] = query_output['robot']
			session['email'] = email
			session['password'] = password
			connection.close()
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
			return render_template('profile.html', name=session['name'])
	except:
		return redirect(url_for('login'))

@app.route('/profile', methods=['POST'])
def profile_post():
	password_non_hashed = request.form.get('password')
	try:
		connection = db_connect()
		with connection.cursor() as cursor:
			query_expected_pwd = cursor.execute("""SELECT password FROM linkedin.user WHERE email=%s""", session['email'])
			password_hached = cursor.fetchall()[0]['password']
			expected_pwd = check_password_hash(password_hached, password_non_hashed)
			if expected_pwd:
				logger.info("PSWD linkedin valide")
				session['password_non_hashed'] = password_non_hashed #on cree ce nouvel objet ds la session pr l'utiliser dans la route script
				connection.close()
				return redirect(url_for('script'))
			else:
				logger.info("PSWD errone")
				connection.close()
				return redirect(url_for('profile'))
	except:
		traceback.print_exc()
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
			print(session['robot'])
			if session['robot'] == 1:
				logger.info("Lancement du robot 1")
				return main_robot_1.main(session['id'], session['email'], session['password_non_hashed'])
			elif session['robot'] == 2:
				logger.info("Lancement du robot 2")
				return main_robot_2.main(session['id'], session['email'], session['password_non_hashed'])
			else:
				logger.info('Erreur dans le choix du robot a lancer')
				return render_template('error.html')
	except:
		traceback.print_exc()
		logger.info("Algo non execute jusqu'a la fin")
		return render_template('error.html')


@app.route('/dash')
def dashboard():
	# le dashboard va chercher les datas dans le json
	try:
		if session['email']:
			with open(os.path.join(os.path.dirname(__file__), '../src/premium/Contacts/stats_'+str(session['id'])+'.json'),'r') as j:
				logger.debug("Acces au JSON")
				json_data = json.load(j)
				nb_contacted_total = json_data["Total messages envoyes"]
				nb_contacted_today = json_data["Total envoyes aujourd'hui"]
				nb_contacted_per_filter = json_data["Personnes a contacter pour ce filtre"]
				pending_invit = json_data["Pending invit"]
				try:
					total_connexions = json_data["Total connexions envoyees"]
					logging.info("Dashboard robot 2")
					return render_template('index.html', total_envoyes=nb_contacted_total, total_today=nb_contacted_today,
						nb_contacted_per_filter=nb_contacted_per_filter, pending_invit=pending_invit, total_connexions=total_connexions)
				except:
					logging.info("Dashboard robot 1")
					total_connexions = nb_contacted_total
					return render_template('index.html', total_envoyes=nb_contacted_total, total_today=nb_contacted_today,
						nb_contacted_per_filter=nb_contacted_per_filter, pending_invit=pending_invit, total_connexions=total_connexions)

	except:
		return redirect(url_for('login'))
{"Total connexions envoyees": 200, "Total messages envoyes": 84, "Total envoyes aujourd'hui": 0, "Personnes a contacter pour ce filtre": "...", "Pending invit": "..."}


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


# ssh -i remy_key.pem  ubuntu@ec2-35-180-36-3.eu-west-3.compute.amazonaws.com
# sudo docker run -v /home/ubuntu/AD_serveur/:/src -p 80:5000 -t -d --restart always algo-dimension
""" TODO : dashboard AD,
ajouter les stats du dash a mysql et pas que les fihiers temporaires
send flow message, mieux filtrer des le debut, je ne prends que les personnes que je nai pas contacte hier mais je dois mieux
filtrer en prenanr celles qui ont deja un 1 ds nbe message. Malheureusement je ne peux pas debuger car jai deja envoye le nbe max 
de connexion, et flemme de changer le cdode que pr ca

jai change le code en passant par linkedin standard mais peut etre que cest juste du au xpath du bouton envoie sur premium
qui change ebn fonction du profil
"""

