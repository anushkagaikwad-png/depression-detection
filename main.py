# import the necessary packages
from flask import Flask, render_template, redirect, url_for, request,session,Response
from werkzeug.utils import secure_filename
from supportFile import *
import os
import cv2
import pandas as pd
import utils
import nltk
import moviepy.editor as mp
import speech_recognition as sr 
import sqlite3
from datetime import datetime
from autocorrect import Speller
import json

interest=''
problem=''

video = ''
name = ''
spell = Speller(lang='en')
r = sr.Recognizer()

app = Flask(__name__)

app.secret_key = '1234'
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def landing():
	return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
		try:
			name = cursorObj.fetchone()[0]
			return redirect(url_for('home'))
		except:
			error = "Invalid Credentials Please try again..!!!"
			return render_template('login.html',error=error)
	return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			name = request.form['name']
			email = request.form['email']
			password = request.form['password']
			rpassword = request.form['rpassword']
			pet = request.form['pet']
			if(password != rpassword):
				error='Password dose not match..!!!'
				return render_template('register.html',error=error)
			try:
				con = sqlite3.connect('mydatabase.db')
				cursorObj = con.cursor()
				cursorObj.execute(f"SELECT Name from Users WHERE Email='{email}' AND password = '{password}';")
			
				if(cursorObj.fetchone()):
					error = "User already Registered...!!!"
					return render_template('register.html',error=error)
			except:
				pass
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")			
			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Users (Date text,Name text,Email text,password text,pet text)")
			cursorObj.execute("INSERT INTO Users VALUES(?,?,?,?,?)",(dt_string,name,email,password,pet))
			con.commit()

			return redirect(url_for('login'))

	return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
	error = None
	global name
	if request.method == 'POST':
		email = request.form['email']
		pet = request.form['pet']
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute(f"SELECT password from Users WHERE Email='{email}' AND pet = '{pet}';")
		
		try:
			password = cursorObj.fetchone()
			#print(password)
			error = "Your password : "+password[0]
		except:
			error = "Invalid information Please try again..!!!"
		return render_template('forgot-password.html',error=error)
	return render_template('forgot-password.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
	global name
	return render_template('home.html',name=name)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
	return render_template('dashboard.html',name=name)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
	if request.method=='POST':
		if request.form['uploadbutton'] == 'Upload':
			savepath = r'upload/'
			f = request.files['doc']
			f.save(os.path.join(savepath,(secure_filename('test.mp4'))))
			return render_template('upload.html',name=name,file=f.filename,mgs='File uploaded..!!')
		elif request.form['uploadbutton'] == 'Detect Depression':
			return redirect(url_for('video'))
	return render_template('upload.html',name=name)


@app.route('/video', methods=['GET', 'POST'])
def video():
	global name
	return render_template('video.html',name=name)

@app.route('/video_stream')
def video_stream():
	global name
	return Response(video_feed(name),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/textmining',methods=['GET', 'POST'])
def textmining():
	global video
	global name
	'''
	if request.method == 'POST':
		username = request.form["name"]
		video = request.form["video"]
		num = request.form["num"]
	'''

	clip = mp.VideoFileClip('upload/test.mp4') 
	clip.audio.write_audiofile('converted.wav')
	audio = sr.AudioFile("converted.wav")
	with audio as source:
		audio_file = r.record(source)
	symptoms = r.recognize_google(audio_file)

	username = name

	print(username)
	print(symptoms)

	# define punctuation
	punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''

	my_str = symptoms

	# To take input from the user
	# my_str = input("Enter a string: ")

	# remove punctuation from the string
	no_punct = ""
	for char in my_str:
		if char not in punctuations:
			no_punct = no_punct + char
	
	symptoms = no_punct

	
	utils.export("data/"+username+"-symptoms.txt", symptoms, "w")
			
	data = utils.getTrainData()

	def get_words_in_tweets(tweets):	
		all_words = []
		for (words, sentiment) in tweets:
			all_words.extend(words)
		return all_words

	def get_word_features(wordlist):		
	
		wordlist = nltk.FreqDist(wordlist)
		word_features = wordlist.keys()
		return word_features

	word_features = get_word_features(get_words_in_tweets(data))		
	


	def extract_features(document):		
		document_words = set(document)
		features = {}
		for word in word_features:
			#features[word.decode("utf8")] = (word in document_words)
			features[word] = (word in document_words)
		#print(features)
		return features

	allsetlength = len(data)
	print(allsetlength)		
	#training_set = nltk.classify.apply_features(extract_features, data[:allsetlength/10*8])		
	training_set = nltk.classify.apply_features(extract_features, data)
	#test_set = data[allsetlength/10*8:]		
	test_set = data[88:]		
	classifier = nltk.NaiveBayesClassifier.train(training_set)			
	
	def classify(symptoms):
		return(classifier.classify(extract_features(symptoms.split())))
		
			
		
	f = open("data/"+ username+"-symptoms.txt", "r")	
	f = [line for line in f if line.strip() != ""]	
	tot=0
	pos=0
	neg=0
	for symptom in f:
		tot = tot + 1
		result = classify(symptom)
		now = datetime.now()
		dt_string = now.strftime("%d/%m/%Y %H:%M:%S")	
		con = sqlite3.connect('mydatabase.db')
		cursorObj = con.cursor()
		cursorObj.execute("CREATE TABLE IF NOT EXISTS TextResult (Date text,Name text,Output text)")
		cursorObj.execute("INSERT INTO TextResult VALUES(?,?,?)",(dt_string,name,result))
		con.commit()
		if(result == "Depression Detected"):
			neg = neg + 1
		print(result)

	pos = tot - neg
	if(neg > pos):
		result = "Depression Detected"
		'''
		message = client.messages \
								.create(
										body = "https://www.youtube.com/watch?v=2UtwSI7lgkQ",
										from_='+14696544981',
										to="+91"+str(num)
									)
		'''
	else:
		result = "No Depression Detected"


	return render_template('textmining.html',result=result,symptoms =symptoms,name=name)			    
	#return render_template('textmining.html')

@app.route('/record', methods=['GET', 'POST'])
def record():
	global name
	conn = sqlite3.connect('mydatabase.db', isolation_level=None,
						detect_types=sqlite3.PARSE_COLNAMES)
	df = pd.read_sql_query(f"SELECT * from Result WHERE Name='{name}';", conn)
	
	return render_template('record.html',name=name,tables=[df.to_html(classes='table-responsive table table-bordered table-hover')], titles=df.columns.values)

@app.route('/text_record', methods=['GET', 'POST'])
def text_record():
	global name
	conn = sqlite3.connect('mydatabase.db', isolation_level=None,
						detect_types=sqlite3.PARSE_COLNAMES)
	df = pd.read_sql_query(f"SELECT * from TextResult WHERE Name='{name}';", conn)
	
	return render_template('textrecord.html',name=name,tables=[df.to_html(classes='table-responsive table table-bordered table-hover')], titles=df.columns.values)

@app.route('/bot', methods=['GET', 'POST'])
def bot():
	state = 0
	global name
	global num
	
	if request.method == 'POST':
		if request.form['sub']=='Submit':
			state = 1
			name1 = request.form['name']
			num = request.form['num']
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS botUsers (Date text,Name text,Contact text)")
			cursorObj.execute("INSERT INTO botUsers VALUES(?,?,?)",(dt_string,name1,num))
			con.commit()

		if request.form['sub']=='Rate':
			rating = request.form['rate']
			suggestion = request.form['suggestions']
			now = datetime.now()
			dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

			con = sqlite3.connect('mydatabase.db')
			cursorObj = con.cursor()
			cursorObj.execute("CREATE TABLE IF NOT EXISTS Feedback (Date text,Name text,Contact text,Ratings text,Feedback text)")
			cursorObj.execute("INSERT INTO Feedback VALUES(?,?,?,?,?)",(dt_string,name,num,rating,suggestion))
			con.commit()
			return redirect(url_for('home'))


	#print(state)
	return render_template('bot.html',state = json.dumps(state),name=name)


@app.route("/get")
def get_bot_response():
	global interest
	global problem
	user_response = spell(request.args.get('msg'))
	user_response=user_response.lower()
	botResponse = ''
	print(interest,problem)
	if ('bye' not in user_response):
		if any([x in user_response for x in ['thank you','thanks','thanx','ty']]):
			flag=False
			#print("CollegeBot: You are welcome..")
			botResponse = "You are welcome.."
		elif any([x in user_response for x in['financial','health','relationship']]):
			botResponse = 'Okay, what is your interest? 1. Video 2. Book 3. Quotes 4. Medicine'
			problem = user_response
		elif any([x in user_response for x in['video','book','quotes','medicine']]):
			interest = user_response
			if('financial' in problem):
				if('video' in interest):
					botResponse = 'video link: https://youtu.be/JWjb7WoL9WA'
				elif('book' in interest):
					botResponse = 'Book: Rich dad poor dad'
				elif('quotes' in interest):
					botResponse = 'Rich people believe ‘I create my life.’ Poor people believe ‘Life happens to me.'
				elif('medicine' in interest):
					botResponse = 'Suggested Medicine: Tab xyz'
				else:
					botResponse = 'plz let me know your problem first'
			elif('health' in problem):
				if('video' in interest):
					botResponse = 'video link: https://youtu.be/9-8UN0cPCmQ'
				elif('book' in interest):
					botResponse = 'You are what you eat'
				elif('quotes' in interest):
					botResponse = 'He who has health has hope and he who has hope has everything.'
				elif('medicine' in interest):
					botResponse = 'Suggested Medicine: Tab xyz'
				else:
					botResponse = 'plz let me know your problem first'	
			elif('relationship' in problem):
				if('video' in interest):
					botResponse = 'video link: https://youtu.be/0uLLuodEFhE'
				elif('book' in interest):
					botResponse = 'Book: Emotion and Relationship'
				elif('quotes' in interest):
					botResponse = 'Every man I meet wants to protect me'
				elif('medicine' in interest):
					botResponse = 'Suggested Medicine: Tab xyz'	
				else:
					botResponse = 'plz let me know your problem first'			
		else:
			if(greeting(user_response)!=None):
				#print("CollgeBot: "+greeting(user_response))
				botResponse = greeting(user_response)
			else:
				#print("CollgeBot: ",end="")
				#print(response(user_response))
				#botResponse = response(user_response)
				#sent_tokens.remove(user_response)
				botResponse = 'I am sorry! I dont understand you'
				
	else:
		flag=False
		#print("CollgeBot: Bye! take care..")
		botResponse = "Bye! take care.."

	#return str(english_bot.get_response(user_response))
	return botResponse

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
	global name
	conn = sqlite3.connect('mydatabase.db', isolation_level=None,
						detect_types=sqlite3.PARSE_COLNAMES)
	df = pd.read_sql_query(f"SELECT * from Feedback WHERE Name='{name}';", conn)
	
	return render_template('feedback.html',name=name,tables=[df.to_html(classes='table-responsive table table-bordered table-hover')], titles=df.columns.values)


# No caching at all for API endpoints.
@app.after_request
def add_header(response):
	# response.cache_control.no_store = True
	response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
	response.headers['Pragma'] = 'no-cache'
	response.headers['Expires'] = '-1'
	return response


if __name__ == '__main__' and run:
	app.run(host='0.0.0.0', debug=True, threaded=True)
