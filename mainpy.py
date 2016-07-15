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
app.secret_key = 'super secret key i just made up'
index = 0


UPLOAD_FOLDER = os.getcwd() + '/uploads'


app = Flask(__name__)
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



#this is for if you want to create a password
def create_random_string(length):
    charcters= string.ascii_letters + string.digits
    rndString=""
    for i in range(length):
        rndString += charcters[random.randint(0, len(charcters) - 1)]
    return rndString


@app.route('/',methods=["GET","POST"])
def homepage():
    app.secret_key = 'super secret key i just made up'

    if request.method == 'POST':#if there was a file uploaded

        inputfile = request.files['file']
        if len(inputfile.filename) > 0:
            flask.render_template("main.html")
        global filetype #i want to check the filetype in another function
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
        else: # if it is not an image file
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

    return  render_template(
                    "image-listen.html",
                    file_name=filename,
                    imagetext=texttosay
                    )

if __name__ == "__main__":
##  this makes sure it only runs if called from main
    app.run(debug=True)
