# Image-to-Audio-Website

####This is my Image to Mp3 application, It is built using Flask and a few other libraries,

To run you have to install Flask, enchant (PyEnchant to install on pip2 and pip3),teseract,Festivival and a TTS Voice, and finnaly make sure you have acess to the Random, Os, and String libraries.

Once you Install all of the 
To install festival and a TTS voice run these commands:
```
sudo apt-get install festival festlex-cmu festlex-poslex festlex-oald libestools1.2 unzip
sudo apt-get install festvox-don festvox-rablpc16k festvox-kallpc16k festvox-kdlpc16k
```

More info [Here](http://ubuntuforums.org/showthread.php?t=751169) : (The CMU Arctic and Nitech HTS seem to be deprecated)

To install Tesseract run:
```
sudo apt-get install tesseract-ocr
```
To execute the web app run main.py, then go to http://+[your web ip address]+":"+[Port 5,000] 
For example i went to:
```
http://127.0.0.1:5000
```
This worked for me.


To use the website just upload an image, continue to the next page where the program will use OCR to extract text. Then you should edit the text to remove misspelled words (or tell the program to do it for you), click continue, refresh the page after it has loaded, then listen and enjoy!
