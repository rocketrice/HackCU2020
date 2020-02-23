import cv2
import time
import pigpio
import tweepy
import face_recognition
import os


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
try:
    for index, image_name in enumerate(os.listdir(path)):
        #filenam
        #print(image_path)
        person_image = face_recognition.load_image_file(path + image_name)
        known_faces.append( face_recognition.face_encodings(person_image)[0])
        filename = os.path.splitext(image_name)[0] # removes .jpg from name to store in dictionary
        names[index] = filename
        last_index += 1
except IndexError:
    print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
    quit()

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

# loop runs if capturing has been initialized. 
while 1:

    # reads frames from a camera 
    ret, img = cap.read()

    # convert to gray scale of each frames 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detects faces of different sizes in the input image 
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
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
    elif k == 8:
        # back space pressed

        # Take Picture
        cv2.imwrite('upload.png', img)

        # Check if face is in DB
        unknown_image = face_recognition.load_image_file("upload.png")
        unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
        # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
        results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

        if not True in results:
            input_good = False
            while input_good == False:
                handle = input("What is your twitter handle: ")
                if not " " in handle:
                    input_good = True
            image_name = handle + ".png"
            os.system("cp upload.png ./Photos/" + image_name)
            person_image = face_recognition.load_image_file(path + image_name)
            known_faces.append(face_recognition.face_encodings(person_image)[0])
            filename = os.path.splitext(image_name)[0]  # removes .jpg from name to store in dictionary
            names[last_index] = filename
            last_index += 1
        else:
            i = results.index(True)
            handle = names[i]

        # Upload image
        media = api.media_upload("upload.png")

        # Post tweet with image
        tweet = "Gander made just befriended @" + handle
        post_result = api.update_status(status=tweet, media_ids=[media.media_id])

# Close the window 
cap.release()

# De-allocate any associated memory usage 
cv2.destroyAllWindows()