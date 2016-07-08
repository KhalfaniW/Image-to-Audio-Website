# Image-to-Audio-Website

####This is my Image to Mp3 application, It is built using Flask and a few other libraries,

To run you have to install Flask, enchant (python2 only),Festivival and a TTS Voice, and finnaly make sure you have acess to the Random, Os, and String Libraries.

Once you Install all of the 
To install festival and a TTS voice run these commands:
```
sudo apt-get install festival festlex-cmu festlex-poslex festlex-oald libestools1.2 unzip
sudo apt-get install festvox-don festvox-rablpc16k festvox-kallpc16k festvox-kdlpc16k
```
More info [Here](http://ubuntuforums.org/showthread.php?t=751169) (The CMU Arctic and Nitech HTS seem to be deprecated)

To execute the web app run main.py, then go to http://+[your web ip address example 127.0.0.1]+":"+[Port 5,000] 
For example i went to:
```
http://127.0.0.1:5000
```
This worked for me.

THen it should be working for you;

To use the website just upload an image, conintiue to the next page where the program will use OCR to extract text, edit the text to remove non-words (or tell the program to do it for you), click continue, refresh the page after it has loaded, then Listen and enjoy!
