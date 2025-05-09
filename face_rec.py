import os
from datetime import time
import time
import cv2
import numpy as np

face_cascade = cv2.CascadeClassifier('resource_dir/face_xml/haarcascade_frontalface_default.xml')

# camera = cv2.VideoCapture(0)


def TestFace(face_message):
    person_name_img = {}
    counter = 0
    for filename in os.listdir("face_databases"):
        if filename.endswith(".jpg"):
            with open("./face_databases/" + filename, 'rb') as f:
                person_name_img.update({filename: cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)})
    camera = cv2.VideoCapture(0)
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rec = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
        if counter % 100 == 0:
            print('请靠近屏幕')
        else:
            for (x, y, w, h) in faces_rec:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                for key, value in person_name_img.items():
                    person_gray = cv2.cvtColor(value, cv2.COLOR_BGR2GRAY)
                    match_face = cv2.matchTemplate(gray_img[y:y + h, x:x + w], person_gray, cv2.TM_CCOEFF_NORMED)
                    if match_face.max() > 0.5:
                        if key == face_message:
                            print(f"匹配到{key}的信息!")
                            cv2.destroyAllWindows()
                            camera.release()
                            return True
        cv2.imshow("camera", frame)
        cv2.waitKey(5)
        counter += 1
        if counter > 400:
            cv2.destroyAllWindows()
            camera.release()
            return False


def TestAllFace():
    person_name_img = {}
    counter = 0
    face_name = ""
    for filename in os.listdir("face_databases"):
        if filename.endswith(".jpg"):
            with open("./face_databases/" + filename, 'rb') as f:
                person_name_img.update({filename: cv2.imdecode(np.frombuffer(f.read(), np.uint8), cv2.IMREAD_COLOR)})
    camera = cv2.VideoCapture(0)
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rec = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
        if counter % 100 == 0:
            print('请靠近屏幕')
        else:
            for (x, y, w, h) in faces_rec:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                for key, value in person_name_img.items():
                    person_gray = cv2.cvtColor(value, cv2.COLOR_BGR2GRAY)
                    match_face = cv2.matchTemplate(gray_img[y:y + h, x:x + w], person_gray, cv2.TM_CCOEFF_NORMED)
                    if match_face.max() > 0.5:
                        print(f"匹配到{key}的信息!")
                        cv2.destroyAllWindows()
                        camera.release()
                        return key
        cv2.imshow("camera", frame)
        cv2.waitKey(5)
        counter += 1
        if counter > 400:
            cv2.destroyAllWindows()
            camera.release()
            return ""


def GetFace():
    camera = cv2.VideoCapture(0)
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        cv2.imshow('face_window', frame)
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rec = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
        if len(faces_rec) == 1:
            path_filename = "./face_databases/" + str(time.time()) + '.jpg'
            cv2.imwrite(path_filename, frame)
            print(path_filename)
            break
        cv2.waitKey(5)


def ShowFace():
    camera = cv2.VideoCapture(0)
    timer = 0
    while timer < 500:
        ret, frame = camera.read()
        if not ret:
            break
        cv2.imshow('face_window', frame)
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces_rec = face_cascade.detectMultiScale(gray_img, scaleFactor=1.1, minNeighbors=5)
        if len(faces_rec) == 1:
            camera.release()
            cv2.destroyAllWindows()
            return frame
        cv2.waitKey(5)
        timer += 1
    cv2.destroyAllWindows()
    camera.release()
    return None


if __name__ == '__main__':
    # GetFace()
    # march7th_1373737
    TestFace("march7th_1373737.jpg")
    # ShowFace()
