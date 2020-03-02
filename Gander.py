import numpy as np
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

# need_move_servo calculates whether the camera needs to be adjusted based off of the vision data
def need_move_servo(face_x, face_width, img):
    # get the centers
    face_center = face_x + (face_width/2)
    img_center = img.shape[1] / 2
    THRESHOLD = face_width/4

    # check the locations relative to the threshold
    if img_center - face_center > THRESHOLD:
        return -1
    elif face_center - img_center > THRESHOLD:
        return 1
    else:
        return 0

# add_and_post is called when a new friend is submitted
def add_and_post(tk, text):
    # close the window
    tk.destroy()


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
known_face_encodings=[]
known_face_names = {}
process_this_frame = True
last_index = 0

# GUI
top = Tk()
top.geometry("400x250")
top.title('New friend :)')
handle_label = Label(top, text = "Handle").place(x = 30,y = 50)
stringinput = StringVar()
add_and_post = partial(add_and_post, top, stringinput)
sbmitbtn = Button(top, text = "Submit", command = add_and_post, activebackground = "pink", activeforeground = "blue").place(x = 30, y = 170)
e1 = Entry(top, textvariable=stringinput).place(x = 80, y = 50)

# init the facecompare
try:
    for index, image_name in enumerate(os.listdir(path)):
        #filename
        #print(image_path)
        person_image = face_recognition.load_image_file(path + image_name)
        known_face_encodings.append(face_recognition.face_encodings(person_image)[0])
        filename = os.path.splitext(image_name)[0] # removes .jpg from name to store in dictionary
        known_face_names[index] = filename
        last_index += 1
except IndexError:
    print("I wasn't able to locate any faces in at least one of the images. Check the image files. Aborting...")
    quit()

while True:
    # Grab a single frame of video
    ret, frame = cap.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', frame)

    # Display the resulting image
    if len(face_locations) >= 1:

        (t,r,b,l) = face_locations[0]
        x = l
        w = r - l
        # move servo
        move = need_move_servo(x, w, img)
        if move == 1 and position > 1010:
            position -= SERVO_SPEED
            pi.set_servo_pulsewidth(18, position)
        elif move == -1 and position < 2010:
            position += SERVO_SPEED
            pi.set_servo_pulsewidth(18, position)

        break



    # Wait for Esc key to stop 
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        # escape pressed
        break
    elif k == 8 and len(faces) > 0:
        # back space pressed

        # Take Pictures
        cv2.imwrite('upload.png', img)
        x = face_cords[0]
        y = face_cords[1]
        w = face_cords[2]
        h = face_cords[3]
        cv2.imwrite('crop.png', img[y:y+h, x:x+w])

        try:
            # Check if face is in DB
            unknown_image = face_recognition.load_image_file("crop.png")
            unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
            # results is an array of True/False telling if the unknown face matched anyone in the known_faces array
            results = face_recognition.compare_faces(known_face_encodings, unknown_face_encoding)

            # if we have a new friend
            if not True in results:
                input_good = False
                while input_good == False:
                    # get the new friend's handle
                    top.mainloop()
                    handle = stringinput.get()
                    print(handle)
                    # check and make sure it is a good handle
                    if " " not in handle and "@" not in handle and "#" not in handle and handle != "":
                        input_good = True
                # Make the name of the image to be the friend's handle
                image_name = handle + ".png"
                # copy over into the photo DB
                os.system("cp crop.png ./Photos/" + image_name)
                # Add the face to the facecompare
                person_image = face_recognition.load_image_file(path + image_name)
                known_face_encodings.append(face_recognition.face_encodings(person_image)[0])
                filename = os.path.splitext(image_name)[0]  # removes .jpg from name to store in dictionary
                known_face_names[last_index] = filename
                last_index += 1
                # generate the caption
                tweet = "Gander just befriended @" + handle + " at #HackCU"
            else:
                # get the first name that matches the face
                i = results.index(True)
                handle = known_face_names[i]
                # generate the caption
                tweet = "Gander just saw his friend @" + handle + " at #HackCU"

            # Upload image
            media = api.media_upload("upload.png")

            # Post tweet with image
            post_result = api.update_status(status=tweet, media_ids=[media.media_id])
            print("POSTED")
        except Exception:
            print(Exception)

# Close the window 
cap.release()

# De-allocate any associated memory usage 
cv2.destroyAllWindows()