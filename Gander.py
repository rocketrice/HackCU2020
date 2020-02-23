import cv2
import time
import pigpio

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
        print("face_center: " + str(x + (w/ 2)) + " img_center: " + str(img.shape[1]/2) + " Servo command: " + str(need_move_servo(x, w, img)))

        # move servo
        move = need_move_servo(x, w, img)
        if move == 1 and position > 1010:
            position -= 20
            pi.set_servo_pulsewidth(18, position)
        elif move == -1 and position < 2010:
            position += 20
            pi.set_servo_pulsewidth(18, position)

        break


    height = img.shape[0]
    width = img.shape[1]
    # draw target line
    cv2.line(img, (int(width / 2), 0), (int(width / 2), height), (255, 0, 0), 2)

    #display image
    cv2.imshow('img', img)

    # Wait for Esc key to stop 
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

# Close the window 
cap.release()

# De-allocate any associated memory usage 
cv2.destroyAllWindows()