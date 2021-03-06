import face_recognition
import os
import ntpath

# Load the jpg files into numpy arrays
#biden_image = face_recognition.load_image_file("Sai.jpg")
#obama_image = face_recognition.load_image_file("Jason.jpg")
#unknown_image = face_recognition.load_image_file("Sai2.jpg")

# Get the face encodings for each face in each image file
# Since there could be more than one face in each image, it returns a list of encodings.
# But since I know each image only has one face, I only care about the first encoding in each image, so I grab index 0.
path = "./Photos/"
known_faces=[]
names = {}
last_index = 0
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

unknown_image = face_recognition.load_image_file("Sai2.jpg")
unknown_face_encoding = face_recognition.face_encodings(unknown_image)[0]
# results is an array of True/False telling if the unknown face matched anyone in the known_faces array
results = face_recognition.compare_faces(known_faces, unknown_face_encoding)

print("Is the unknown face a picture of {}? {}".format(names[0], results[0]))
print("Is the unknown face a picture of {}? {}".format(names[1], results[1]))
print("Is the unknown face a new person that we've never seen before? {}".format(not True in results))
