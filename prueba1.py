# Libreries
from tkinter import *
import cv2
import numpy as np
from PIL import Image, ImageTk
import imutils
import mediapipe as mp
import math
import os
import face_recognition as fr
import mysql.connector
import base64
from tkinter import Tk, Entry, font

# Function to encode image in Base64
def encode_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    return b64_string

# Face Code
def Code_Face(images):
    listacod = []

    # Iteramos
    for img in images:
        # Correccion de color
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # Codificamos la imagen
        cod = fr.face_encodings(img)[0]
        # Almacenamos
        listacod.append(cod)

    return listacod

# Close Windows LogBiometric
def Close_Windows():
    global step, conteo
    # Reset Variables
    conteo = 0
    step = 0
    pantalla2.destroy()

# Close Windows SignBiometric
def Close_Windows2():
    global step, conteo
    # Reset Variables
    conteo = 0
    step = 0
    pantalla3.destroy()

# Profile
def Profile():
    global step, conteo, UserName, OutFolderPathUser
    # Reset Variables
    conteo = 0
    step = 0

    pantalla4 = Toplevel(pantalla)
    pantalla4.title("BIOMETRIC SIGN")
    pantalla4.geometry("1280x720")

    back = Label(pantalla4, image=imagenB, text="Back")
    back.place(x=0, y=0, relwidth=1, relheight=1)

    # Archivo
    UserFile = open(f"{OutFolderPathUser}/{UserName}.txt", 'r')
    InfoUser = UserFile.read().split(',')
    Name = InfoUser[0]
    User = InfoUser[1]
    Pass = InfoUser[2]
    UserFile.close()

    # Check
    for clase in clase:
        # Interfaz
        texto1 = Label(pantalla4, text=f"Bienvenido {Name}", fg="Black", bg="lightgray", font=("Arial", 12, "bold"))
        texto1.place(x=580, y=50)
        # Label
        # Video
        lblImgUser = Label(pantalla4)
        lblImgUser.place(x=450, y=80)

        # Imagen
        PosUserImg = clase.index(User)
        UserImg = images[PosUserImg]

        ImgUser = Image.fromarray(UserImg)
        #
        ImgUser = cv2.imread(f"{OutFolderPathFace}/{User}.png")
        ImgUser = cv2.cvtColor(ImgUser, cv2.COLOR_RGB2BGR)
        ImgUser = Image.fromarray(ImgUser)
        # Ajustar tamaño
        desired_size = (420, 420)  # Ajusta a las dimensiones
        ImgUser = ImgUser.resize(desired_size, Image.Resampling.LANCZOS) # Usa Image.Resampling.LANCZOS en lugar de Image.ANTIALIAS

        #
        IMG = ImageTk.PhotoImage(image=ImgUser)

        lblImgUser.configure(image=IMG)
        lblImgUser.image = IMG


# Register Biometric
def Log_Biometric():
    global pantalla, pantalla2, conteo, parpadeo, img_info, step

    # Leemos la videocaptura
    if cap is not None:
        ret, frame = cap.read()

        # Frame Save
        frameSave = frame.copy()

        # RGB
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Show
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Si es correcta
        if ret == True:

            # Inference
            res = FaceMesh.process(frameRGB)

            # List Results
            px = []
            py = []
            lista = []
            r = 5
            t = 3

            # Resultados
            if res.multi_face_landmarks:
                # Iteramos
                for rostros in res.multi_face_landmarks:

                    # Draw Face Mesh
                    mpDraw.draw_landmarks(frame, rostros, FacemeshObject.FACEMESH_CONTOURS, ConfigDraw, ConfigDraw)

                    # Extract KeyPoints
                    for id, puntos in enumerate(rostros.landmark):

                        # Info IMG
                        al, an, c = frame.shape
                        x, y = int(puntos.x * an), int(puntos.y * al)
                        px.append(x)
                        py.append(y)
                        lista.append([id, x, y])

                        # 468 KeyPoints
                        if len(lista) == 468:
                            # Ojo derecho
                            x1, y1 = lista[145][1:]
                            x2, y2 = lista[159][1:]
                            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                            longitud1 = math.hypot(x2 - x1, y2 - y1)
                            #print(longitud1)

                            # Ojo Izquierdo
                            x3, y3 = lista[374][1:]
                            x4, y4 = lista[386][1:]
                            cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2
                            longitud2 = math.hypot(x4 - x3, y4 - y3)
                            #print(longitud2)

                            # Parietal Derecho
                            x5, y5 = lista[139][1:]
                            # Parietal Izquierdo
                            x6, y6 = lista[368][1:]

                            # Ceja Derecha
                            x7, y7 = lista[70][1:]
                            # Ceja Izquierda
                            x8, y8 = lista[300][1:]

                            #cv2.circle(frame, (x5, y5), 2, (255, 0, 0), cv2.FILLED)
                            #cv2.circle(frame, (x6, y6), 2, (0, 0, 0), cv2.FILLED)
                            #cv2.circle(frame, (x7, y7), 2, (0, 255, 0), cv2.FILLED)
                            #cv2.circle(frame, (x8, y8), 2, (0, 255, 0), cv2.FILLED)

                            # Face Detect
                            faces = detector.process(frameRGB)

                            if faces.detections is not None:
                                for face in faces.detections:

                                    # bboxInfo - "id","bbox","score","center"
                                    score = face.score
                                    score = score[0]
                                    bbox = face.location_data.relative_bounding_box

                                    # Threshold
                                    if score > confThreshold:
                                        # Info IMG
                                        alimg, animg, c = frame.shape

                                        # Coordenates
                                        xi, yi, an, al = bbox.xmin, bbox.ymin, bbox.width, bbox.height
                                        xi, yi, an, al = int(xi * animg), int(yi * alimg), int(an * animg), int(al * alimg)

                                        # Width
                                        offsetan = (offsetx / 100) * an
                                        xi = int(xi - int(offsetan/2))
                                        an = int(an + offsetan)
                                        xf = xi + an

                                        # Height
                                        offsetal = (offsety / 100) * al
                                        yi = int(yi - offsetal)
                                        al = int(al + offsetal)
                                        yf = yi + al

                                        # Error < 0
                                        if xi < 0: xi = 0
                                        if yi < 0: yi = 0
                                        if an < 0: an = 0
                                        if al < 0: al = 0

                                    # Steps
                                    if step == 0:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step0
                                        alis0, anis0, c = img_step0.shape
                                        frame[50:50 + alis0, 50:50 + anis0] = img_step0

                                        # IMG Step1
                                        alis1, anis1, c = img_step1.shape
                                        frame[50:50 + alis1, 1030:1030 + anis1] = img_step1

                                        # IMG Step2
                                        alis2, anis2, c = img_step2.shape
                                        frame[270:270 + alis2, 1030:1030 + anis2] = img_step2

                                        # Condiciones
                                        if x7 > x5 and x8 < x6:

                                            # Cont Parpadeos
                                            if longitud1 <= 10 and longitud2 <= 10 and parpadeo == False:  # Parpadeo
                                                conteo = conteo + 1
                                                parpadeo = True
                                            if longitud1 > 10 and longitud2 > 10 and parpadeo == True:  # No Parpadeo
                                                parpadeo = False

                                            # Llenar Barra
                                            if conteo == 1:
                                                frame[500:600, 50:250] = img_step1

                                            if conteo == 2:
                                                frame[500:600, 250:450] = img_step1

                                            if conteo == 3:
                                                frame[500:600, 450:650] = img_step1

                                            if conteo == 4:
                                                frame[500:600, 650:850] = img_step1

                                            if conteo == 5:
                                                frame[500:600, 850:1050] = img_step1

                                            if conteo == 6:
                                                frame[500:600, 1050:1250] = img_step1
                                                step = 1

                                    # Step1
                                    if step == 1:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (0, 255, 255), 2)
                                        # IMG Step1
                                        alis1, anis1, c = img_step1.shape
                                        frame[50:50 + alis1, 50:50 + anis1] = img_step1

                                        # IMG Step0
                                        alis0, anis0, c = img_step0.shape
                                        frame[50:50 + alis0, 1030:1030 + anis0] = img_step0

                                        # IMG Step2
                                        alis2, anis2, c = img_step2.shape
                                        frame[270:270 + alis2, 1030:1030 + anis2] = img_step2

                                        # Condiciones
                                        if x7 > x5 and x8 < x6:
                                            # Cont Parpadeos
                                            if longitud1 <= 10 and longitud2 <= 10 and parpadeo == False:  # Parpadeo
                                                conteo = conteo + 1
                                                parpadeo = True
                                            if longitud1 > 10 and longitud2 > 10 and parpadeo == True:  # No Parpadeo
                                                parpadeo = False

                                            # Llenar Barra
                                            if conteo == 1:
                                                frame[500:600, 50:250] = img_step2

                                            if conteo == 2:
                                                frame[500:600, 250:450] = img_step2

                                            if conteo == 3:
                                                frame[500:600, 450:650] = img_step2

                                            if conteo == 4:
                                                frame[500:600, 650:850] = img_step2

                                            if conteo == 5:
                                                frame[500:600, 850:1050] = img_step2

                                            if conteo == 6:
                                                frame[500:600, 1050:1250] = img_step2
                                                step = 2

                                    # Step2
                                    if step == 2:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (0, 255, 0), 2)
                                        # IMG Step1
                                        alis1, anis1, c = img_step1.shape
                                        frame[50:50 + alis1, 50:50 + anis1] = img_step1

                                        # IMG Step2
                                        alis2, anis2, c = img_step2.shape
                                        frame[50:50 + alis2, 1030:1030 + anis2] = img_step2

                                        # IMG Step0
                                        alis0, anis0, c = img_step0.shape
                                        frame[270:270 + alis0, 1030:1030 + anis0] = img_step0

                                        # Face Detect
                                        faceLoc = faceR.locate_faces(frameRGB)

                                        # Extract Info Face
                                        for (top, right, bottom, left), face in faceLoc:

                                            # Rectangle
                                            cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 2)

                                            # Cut Face
                                            faceDetect = frameSave[top:bottom, left:right]

                                            # Dimensions
                                            faceDetect = imutils.resize(faceDetect, width=150)

                                            # Save Face
                                            cv2.imwrite(f"{OutFolderPathFace}/frame_{conteo}.png", faceDetect)

                                            # Face Inference
                                            facesTest = cv2.imread(f"{OutFolderPathFace}/frame_{conteo}.png")
                                            facesTest = cv2.cvtColor(facesTest, cv2.COLOR_BGR2RGB)
                                            faceLocations = fr.face_locations(facesTest)

                                            # One Face Detected
                                            if len(faceLocations) == 1:
                                                step = 3
                                                break

                                    # Step3
                                    if step == 3:
                                        # Step Images
                                        frame[50:50 + alis0, 50:50 + anis0] = img_step0
                                        frame[50:50 + alis1, 1030:1030 + anis1] = img_step1
                                        frame[270:270 + alis2, 1030:1030 + anis2] = img_step2

                                        # Encode Faces
                                        frameStep3 = frame.copy()
                                        step = 4

                                    # Step4
                                    if step == 4:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 0), 2)

                                        # Encode Faces
                                        faceStep4 = frameStep3[yi:yf, xi:xf]
                                        faceStep4 = imutils.resize(faceStep4, width=200)

                                        # Save Face
                                        cv2.imwrite(f"{OutFolderPathFace}/User_{conteo}.png", faceStep4)

                                        # Encode Face
                                        faceEnc = fr.face_encodings(faceStep4)[0]

                                        # Step Images
                                        frame[50:50 + alis0, 50:50 + anis0] = img_step0
                                        frame[50:50 + alis1, 1030:1030 + anis1] = img_step1
                                        frame[270:270 + alis2, 1030:1030 + anis2] = img_step2

                                        # Get Base64 String
                                        img_base64_str = encode_image_base64(f"{OutFolderPathFace}/User_{conteo}.png")
                                        print(f"Base64 Encoded Image: {img_base64_str}")

                                        # Save to Database (MySQL)
                                        mydb = mysql.connector.connect(
                                            host="localhost",
                                            user="your_username",
                                            password="your_password",
                                            database="your_database"
                                        )

                                        mycursor = mydb.cursor()
                                        sql = "INSERT INTO users (username, face_encoding) VALUES (%s, %s)"
                                        val = (username, img_base64_str)
                                        mycursor.execute(sql, val)
                                        mydb.commit()
                                        mycursor.close()
                                        mydb.close()

                                        step = 5

                                    # Show Frame
                                    img = Image.fromarray(frame)
                                    imgtk = ImageTk.PhotoImage(image=img)
                                    lblVideo.configure(image=imgtk)
                                    lblVideo.image = imgtk

        # Show Frame
        pantalla2.after(20, Log_Biometric)

# Window Login
def LoginBiometric():
    global cap, pantalla2, lblVideo, detector, faceR, FaceMesh, FacemeshObject, ConfigDraw, img_step0, img_step1, img_step2, imagenB, parpadeo, conteo, step, confThreshold, offsetx, offsety, img_info, OutFolderPathFace

    # Variables
    cap = cv2.VideoCapture(0)
    parpadeo = False
    conteo = 0
    step = 0
    confThreshold = 0.7
    offsetx = 20
    offsety = 20
    clases = []  # Define tu lista o variable adecuada

    # Windows
    pantalla2 = Toplevel(pantalla)
    pantalla2.title("BIOMETRIC LOGIN")
    pantalla2.geometry("1280x720")

    # Detector
    mpFace = mp.solutions.face_detection
    mpDraw = mp.solutions.drawing_utils
    faceR = mpFace.FaceDetection(model_selection=1, min_detection_confidence=confThreshold)

    # FaceMesh
    FaceMesh = mp.solutions.face_mesh
    FacemeshObject = FaceMesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=confThreshold)
    ConfigDraw = mpDraw.DrawingSpec(thickness=1, circle_radius=1)

    # Imagenes
    img_step0 = cv2.imread("images/step0.png")
    img_step1 = cv2.imread("images/step1.png")
    img_step2 = cv2.imread("images/step2.png")
    imagenB = PhotoImage(file="images/background.png")
    img_info = cv2.imread("images/Info.png")

    # Interface
    lblVideo = Label(pantalla2)
    lblVideo.place(x=0, y=0, relwidth=1, relheight=1)

    # Show Frames
    Log_Biometric()

# Window Sign
def SignBiometric():
    global cap, pantalla3, lblVideo2, detector, faceR, FaceMesh, FacemeshObject, ConfigDraw, img_step0, img_step1, img_step2, imagenB, parpadeo, conteo, step, confThreshold, offsetx, offsety, img_info, OutFolderPathFace

    # Variables
    cap = cv2.VideoCapture(0)
    parpadeo = False
    conteo = 0
    step = 0
    confThreshold = 0.7
    offsetx = 20
    offsety = 20

    # Windows
    pantalla3 = Toplevel(pantalla)
    pantalla3.title("BIOMETRIC SIGN")
    pantalla3.geometry("1280x720")

    # Detector
    mpFace = mp.solutions.face_detection
    mpDraw = mp.solutions.drawing_utils
    faceR = mpFace.FaceDetection(model_selection=1, min_detection_confidence=confThreshold)

    # FaceMesh
    FaceMesh = mp.solutions.face_mesh
    FacemeshObject = FaceMesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=confThreshold)
    ConfigDraw = mpDraw.DrawingSpec(thickness=1, circle_radius=1)

    # Imagenes
    img_step0 = cv2.imread("images/step0.png")
    img_step1 = cv2.imread("images/step1.png")
    img_step2 = cv2.imread("images/step2.png")
    imagenB = PhotoImage(file="images/background.png")
    img_info = cv2.imread("images/Info.png")

    # Interface
    lblVideo2 = Label(pantalla3)
    lblVideo2.place(x=0, y=0, relwidth=1, relheight=1)

    # Show Frames
    Log_Biometric()

# Login
Button(pantalla, text="BIOMETRIC LOGIN", command=LoginBiometric).pack()
# Sign
Button(pantalla, text="BIOMETRIC SIGN", command=SignBiometric).pack()

# Loop
pantalla.mainloop()
