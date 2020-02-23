import cv2
import time
import pigpio
import tweepy
import face_recognition
import os
from tkinter import Tk, Label, Button, Entry, StringVar
from functools import partial


handle_input = ""

# Constants
SERVO_SPEED = 10

# load data sets
face_cascade = cv2.CascadeClassifier('/home/pi/Desktop/env/lib/python3.7/site-packages/cv2/data/haarcascade_frontalface_default.xml')

# capture frames from a camera 
cap = cv2.VideoCapture(1)

# connect to the
pi = pigpio.pi()

# set to middle
position = 1500
pi.set_servo_pulsewidth(18, position) # middle

def need_move_servo(face_x, face_width, img):
    face_center = face_x + (face_width/2)
    img_center = img.shape[1] / 2
    THRESHOLD = face_width/4

    if img_center - face_center > THRESHOLD:
        return -1
    elif face_center - img_center > THRESHOLD:
        return 1
    else:
        return 0

def add_and_post(tk, text):
    handle_input = text.get()
    tk.destroy


# Twitter API
twitter_auth_keys = {
    "consumer_key": "quRVTzQpkAH8HnpoSkZbIdTxv",
    "consumer_secret": "Efew2bIFEer0UrYGMVa2TSfAwpMmFoXks7phyfnFyYxnyfRXc2",
    "access_token": "1231384108003024897-OLXRdh0vXMoaGPsaO68lcAX8GiyXeT",
    "access_token_secret": "iVzR5u9zcdV0g1fCIGcnEaukFOfKroPAeH6VrKw7yx0mH"
}

auth = tweepy.OAuthHandler(
    twitter_auth_keys['consumer_key'],
    twitter_auth_keys['consumer_secret']
)
auth.set_access_token(
    twitter_auth_keys['access_token'],
    twitter_auth_keys['access_token_secret']
)
api = tweepy.API(auth)

# Face Compare
path = "./Photos/"
known_faces=[]
names = {}
last_index = 0

# GUI
top = Tk()
top.geometry("400x250")
handle_label = Label(top, text = "Handle").place(x = 30,y = 50)
stringinput = StringVar()
sbmitbtn = Button(top, text = "Submit",activebackground = "pink", activeforeground = "blue").place(x = 30, y = 170)
e1 = Entry(top, textvariable=stringinput).place(x = 80, y = 50)
add_and_post = partial(top, stringinput)

try:
    for index, image_name in enumerate(os.listdir(path)):
        #filename
        #print(image_path)
        person_image = face_recognition.load_image_file(path + image_name)
        known_faces.append( face_recognition.face_encodings(person_image)[0])
        filename = os.path.splitext(image_name)[0] # removes .jpg from name to store in dictionary
        names[index] = filename
        last_index += 1
except IndexError:
    print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
    quit()

# loop runs if capturing has been initialized. 
while 1:

    # reads frames from a camera 
    ret, img = cap.read()

    # convert to gray scale of each frames 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detects faces of different sizes in the input image 
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    face_cords = [0,0,0,0]

    for (x, y, w, h) in faces:
        # Save cords
        face_cords[0] = x
        face_cords[1] = y
        face_cords[2] = w
        face_cords[3] = h
        # To draw a rectangle in a face  
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 2)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        #print("face_center: " + str(x + (w/ 2)) + " img_center: " + str(img.shape[1]/2) + " Servo command: " + str(need_move_servo(x, w, img)))

        # move servo
        move = need_move_servo(x, w, img)
        if move == 1 and position > 1010:
            position -= SERVO_SPEED
            pi.set_servo_pulsewidth(18, position)
        elif move == -1 and position < 2010:
            position += SERVO_SPEED
            pi.set_servo_pulsewidth(18, position)

        break


    height = img.shape[0]
    width = img.shape[1]
    # draw target line
    #cv2.line(img, (int(width / 2), 0), (int(width / 2), height), (255, 0, 0), 2)

    #display image
    cv2.imshow('img', img)

    # Wait for Esc key to stop 
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        # escape pressed
        break
    elif k == 8 and len(faces) > 0:
        # back space pressed

        # Take Pictures
        cv2.imwrite('upload.png', img)
        cv2.imwrite('crop.png', img.crop(face_cords[0], face_cords[1], face_cords[2], face_cords[3]))

        # Check if face is in DB
        unknown_image = face_recognition.load_image_file("crop.png")
        unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
        # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
        results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

        if not True in results:
            input_good = False
            while input_good == False:
                top.mainloop()
                handle = handle_input
                if " " not in handle and "@" not in handle and "#" not in handle and handle != "":
                    input_good = True
            image_name = handle + ".png"
            os.system("cp crop.png ./Photos/" + image_name)
            person_image = face_recognition.load_image_file(path + image_name)
            known_faces.append(face_recognition.face_encodings(person_image)[0])
            filename = os.path.splitext(image_name)[0]  # removes .jpg from name to store in dictionary
            names[last_index] = filename
            last_index += 1
            tweet = "Gander just befriended @" + handle
        else:
            i = results.index(True)
            handle = names[i]
            tweet = "Gander just saw his friend @" + handle

        # Upload image
        media = api.media_upload("upload.png")

        # Post tweet with image
        post_result = api.update_status(status=tweet, media_ids=[media.media_id])

# Close the window 
cap.release()

# De-allocate any associated memory usage 
cv2.destroyAllWindows()