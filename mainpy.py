# -*- coding: utf-8 -*-
#this is in python2
import flask
import random
import string
import os
from flask import Flask, request, redirect, url_for,flash,render_template
from werkzeug.utils import secure_filename
import subprocess
import enchant



#this is entire website
app = flask.Flask(__name__)
#explicitly state what the static folder is callled
app.static_folder = 'static'
app.secret_key = 'super secret key'
index = 0
#------------------------------------------    
#DATABASE ADDITION  BEGIN
#------------------------------------------
from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_DB'] = 'img2mp3'



def create_user(username,password):
     conn = mysql.connect
     cur = conn.cursor()
     #check username
     username_available=True
     cur.execute('''SELECT username FROM users;''')
     
     for tuple_ in  cur.fetchall():
        # note that since it is a tuple it will check if the whole item is in the array
        # so you wont have: is "D" in "Dimitri" but: is "D" in ("Dimitri")
        if username in tuple_:
             username_available = False

     if username_available:
         cur.execute('''INSERT INTO users VALUES('{0}', '{1}', 'No');'''.format(username,password))
         conn.commit()
         conn.close()
         return "Success"
     else:
         return "Username not available."
    
#has_owner must be Yes or No
def create_file_entry(id_,filename,has_owner,imageview_url,imagelisten_url,username=None,): 

    if username is None:
        conn = mysql.connect
        cur = conn.cursor()
        #instert into database
        cur.execute('''INSERT INTO files VALUES(NULL, '%s','%s','%s','%s','%s');
        ''' %(id_,
        	filename.replace("'","\\'"),
        	has_owner,
        	imageview_url.replace("'","\\'"),
        	imagelisten_url.replace("'","\\'"))
        	)
        # I could sanitze the quote marks after creating the string but this seems simpler
        conn.commit()   
        conn.close()
    else:
        conn = mysql.connect
        cur = conn.cursor()
        cur.execute('''INSERT INTO files VALUES('%s', '%s','%s','%s','%s','%s');
        ''' %(username.replace("'","\\'"),
        	id_,
        	filename.replace("'","\\'"),
        	has_owner,
        	imageview_url.replace("'","\\'"),
        	imagelisten_url.replace("'","\\'"))
        )
                
        cur.execute('''UPDATE users SET has_files="Yes" WHERE username="%s"
        ''' %(username)
        )
      
   
        conn.commit()   
        conn.close()
        
def does_login_exist(username,password):
     conn = mysql.connect
     cur = conn.cursor()
     cur.execute('''
      SELECT username,password 
      FROM users  
      WHERE username='%s' AND password='%s';
     ''' %(username,password)  
     )
     return cur.fetchall() != ()
def hasfiles(username,password):
     conn = mysql.connect
     cur = conn.cursor()
     cur.execute('''
      SELECT has_files 
      FROM users  
      WHERE username='%s' AND password='%s';
     ''' %(username,password)  
     )
     return cur.fetchall()[0][0]
def getstoredimages(username,password):
     
  
     conn = mysql.connect
     cur = conn.cursor()
     #this will get all information connected with the user
     cur.execute('''
      SELECT imageview_url,imagelisten_url,filename 
      FROM files  INNER JOIN users  
      ON users.username=files.username 
      WHERE users.username="%s" AND password="%s";
     ''' %(username,password)  
     )
 
     #this makes an array of dictionaries so jinja can access them all individually, right now one only needs filename
     # but I am considering adding a way to directly access the imageview and imagelisten urls
     url_dictionary_array=[{}]
     for database_entry in cur.fetchall():
        tempdict={"imageview":database_entry[0],"imagelisten":database_entry[1],"filename":database_entry[2]}
        url_dictionary_array.append(tempdict)
  
     return url_dictionary_array
                    
 

def set_username_and_password_cookies_and_return_response(username,password,response_to_return):
    response = app.make_response(response_to_return)
    response.set_cookie('username',username)
    response.set_cookie('password',password)
    return response
    
    
@app.route('/log-in_sign-up',methods=["GET","POST"])
def log_in():    
    if request.method == 'POST':
        #in this case max returns the argument that is not None 
        if max(request.form.get("Login"),request.form.get("Sign-Up"))==request.form.get("Login"):
            #TODO -check if user has files already saved or not
            if does_login_exist(request.form.get("Username"),request.form.get("Password")):
                if hasfiles(request.form.get("Username"),request.form.get("Password")) =="Yes":
                    return set_username_and_password_cookies_and_return_response(
                        request.form.get("Username"),
                        request.form.get("Password"),
                        #Return Successful log in message
                        flask.render_template(#show all the information the user has storred
                                "show-all.html",
                                 url_dictionary_array=getstoredimages(request.form.get("Username"),request.form.get("Password"))
                                )
                        )
                else:
                    return redirect("/")
            else:
                return flask.render_template(
                    "login-signup.html",
                    message="Log in not found",
                    )
        else:
            if create_user(request.form.get("Username"),request.form.get("Password"))=="Success":
                return  set_username_and_password_cookies_and_return_response(
                request.form.get("Username"),
                request.form.get("Password"),
                #Return Successful log in message
                #this dosn't need an new html file
                """
                <!doctype html>
                <html align="center" >
                <h2>Sign Up Successful!<h2>
                <button onclick="window.location.href='http://img2mp3.com/'">Return Home</button>
                </html>
                """
                )
            else:
                return flask.render_template(
                    "login-signup.html",
                    message="Username not available",
                    )
           
            
    return  flask.render_template("login-signup.html")
@app.route("/show-all")
def showall():
    if request.cookies.get("username") != None:
        return flask.render_template(#show all the information the user has storred
                                    "show-all.html",
                                     url_dictionary_array=getstoredimages(request.cookies.get("username"),request.cookies.get("password"))
                                    )
    else:
        return "<h2>Please log in to view this page</h2>"
@app.route("/show-file/<filename>")#Don't Worry it checks the cookies to see if the requestor is signed in or not
def showfile(filename):
    url_dictionary_array=getstoredimages(request.cookies.get("username"),request.cookies.get("password"))
 
    for dictionary in [ x for x in url_dictionary_array if len(x)>0 ]: 
        if dictionary["filename"]==filename:
            return flask.render_template(
                            "main.html",
                            file_name=filename
                            )
      
    return "<h2>File was not found under your current log in with this filename</h2>"
#------------------------------------------    
#DATABASE ADDITION  END
#------------------------------------------   
UPLOAD_FOLDER = '/var/www/FlaskApps/Image-to-Audio-Website-master/uploads'


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
filetype = ""


def check_file(inputfile):
#in the manpage tesseract says it can read "(anything readable by Leptonica)"
#in http://tpgit.github.io/UnOfficialLeptDocs/leptonica/README.html#image-i-o
#the UnOfficial Leptonica documentation it said it can read the following files:
    files = ['jpeg', 'jpg', 'png', 'tiff', 'bmp', 'pnm', 'gif', 'webp']

    fileinfo = "NULL"
    if len(inputfile.filename) == 0:
        return fileinfo
    if "." not in inputfile.filename or inputfile.filename.split(".")[-1] in files:
        inputfile.save(
            os.path.join(app.config['UPLOAD_FOLDER'], inputfile.filename)
        )
        fileinfo = subprocess.check_output([
            "file",
            "-bi",
            UPLOAD_FOLDER + "/" + inputfile.filename
            ])

#the above function will check the file itself to see if it is compatable
#when it has no ending for linux users,
#and it will check if it is an executable
#for if a hacker is trying to comprise the website
# after it is checked to be safe it is saved to the server
    return fileinfo



#this function acts as a password generator
def create_random_string(length):
    charcters= string.ascii_letters + string.digits
    rndString=""
    for i in range(length):
        rndString += charcters[random.randint(0, len(charcters) - 1)]
    return rndString


@app.route('/',methods=["GET","POST"])
def homepage():
    app.secret_key = 'super secret key'
    if request.method == 'POST':#if there was a file uploaded
       	inputfile = request.files['file']
      	
        if len(inputfile.filename) > 0:
            flask.render_template("main.html")

	#this will deferentiate files of the same name and add security
	inputfile.filename=create_random_string(10)+"-"+inputfile.filename.replace(" ","")
	#this also makes filenames unlikely to be guesed adding privacy to the files 

	#i want to check the filetype in another function so i made this global
        global filetype
       
        filetype = check_file(inputfile)
	
        if "image" in filetype:
            return flask.render_template(
                    "main.html",
                    file_name=inputfile.filename
                    )

        elif filetype == "NULL":
            return flask.render_template(
                    "main.html",
                    errormessage="error in file name please change file",
                    )
        else:  #if it is not an image file
            return flask.render_template(
                "main.html",
                errormessage="wrong file type, please change file"
                )

    return flask.render_template("main.html")


@app.route('/uploads/<filename>')
def uploads(filename):
    return flask.send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.route('/listen/<foldername>/<audiofile>')
def getaudio(foldername, audiofile):
    audiodirectory = app.config['UPLOAD_FOLDER'] + "/" + foldername
    return flask.send_from_directory(audiodirectory,
         audiofile)


@app.route('/image-view/<file_name>', methods=['GET', 'POST'])
def image_view(file_name):
    textfile = os.path.join(
            app.config['UPLOAD_FOLDER'],
            #remove the ending if there is one because tesseract appends '.txt'
            file_name if "." not in file_name
            else file_name.replace(file_name.split(".")[-1], "")
            )
    #convert to txt
    subprocess.call([
                "tesseract",
                os.path.join(app.config['UPLOAD_FOLDER'], file_name),
                textfile
                ])
    f = open(textfile + ".txt")
    text = f.read()
    f.close()
    return render_template(
                    #this is where user can edit the text to mitigate errors
                    "image-view.html",
                    filetype="image",
                    file_name=file_name,
                    # this avoids the UnicodeDecodeError:
                    imagetext=text.decode('utf-8')
                    )

@app.route('/listen/<filename>',methods=["GET","POST"])
def image_listen(filename):
    directory = UPLOAD_FOLDER + '/' + filename + ".folder"
    if not os.path.exists(directory):
        os.mkdir(directory)


    Dictionary = enchant.Dict("en")
    #for some reason flask just can't understand Unicode in python2
    asciistring = ""
    for word in request.args.get('imageText').split(" "):
        for letter in word:
            if ord(letter) <= 128 and letter != '"':
                asciistring += letter
        asciistring += " "
    words = asciistring.split(" ")
    texttosay = ""
    doublecheckedwords = []
    if request.args.get('action') == "destroy":
        for word in words:
            try:
                #remove punctuation
                word = ''.join(char for char in word if char not in string.punctuation)
                #check  the word to see if they can be said
                if Dictionary.check(word.strip()):

                    #finnaly if no errors are thrown and it is a word
                    doublecheckedwords.append(word)
            except:
                pass
        texttosay = " ".join(map(str, doublecheckedwords))

    else:
        texttosay = asciistring
     #create  the sound files;
    subprocess.Popen(
            #this will crate word.wav file
           "echo \"{0}\"|text2wave -o \"{1}/MAIN.wav\"".format(texttosay,directory),
            stdin=subprocess.PIPE,
            shell=True)
    #convert the wave to mp3

    subprocess.call(
        [
            "lame",
             "-V2",
             directory + "/MAIN.wav",
             directory + "/MAIN.mp3"
        ])
    
#it is not reccomended to use "shell=True" when handling user input but
#this should be safe because any injected text will be a string


    #just before creating the page,update the database.

    id_=filename.split("-")[0]#remove the randomly created string
    #TODO change to be based on request
    imageview_url="http://img2mp3.com/image-view/"+filename+"?"
    imagelisten_url=request.url
    id_in_database=False;
    #Check if the id is not already in the database
    conn = mysql.connect
    cur = conn.cursor()
    #check username
    username_available=True
    cur.execute('''SELECT id FROM files;''')

    for tuple_ in  cur.fetchall():
    # note that since it is a tuple it will check if the whole item is in the array
    # so you wont have: is "D" in "Dimitri" but: is "D" in ("Dimitri")
        if id_ in tuple_:
             id_in_database = True

    conn.commit()   
    conn.close()
    
   
    if id_in_database == False:
     #the Yes, No strings are if the file has an owner or not
        if request.cookies.get('username') != None:
            create_file_entry(id_,filename,"Yes",imageview_url,imagelisten_url,username=request.cookies.get('username')) 
        else:
            
            create_file_entry(id_,filename,"No",imageview_url,imagelisten_url) 
        
    #now return  
    
    return  render_template(
                    "image-listen.html",
                    file_name=filename,
                    imagetext=texttosay
                    )

if __name__ == "__main__":
##  this makes sure it only runs if called from main
    app.run(debug=True)
