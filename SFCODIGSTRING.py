# Librerias
from tkinter import *
import cv2
import numpy as np
from PIL import Image, ImageTk
import imutils
import mediapipe as mp
import math
import os
import face_recognition as fr
from tkinter import Tk, Entry, font
import base64
import sqlite3
from flask import Flask, request, jsonify

# Inicializa Flask
app = Flask(__name__)

# Conectar a la base de datos SQLite
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Crear tabla de usuarios
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, name TEXT, username TEXT, password TEXT, face_encoding TEXT)''')
conn.commit()

# Función para codificar imágenes en base64
def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')
    return image_base64

# Función para decodificar imágenes de base64
def decode_image_from_base64(image_base64):
    image_data = base64.b64decode(image_base64)
    np_array = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
    return image

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
    c.execute("SELECT name, username, password FROM users WHERE username=?", (UserName,))
    InfoUser = c.fetchone()
    Name, User, Pass = InfoUser

    # Check
    if User in clases:
        # Interfaz
        texto1 = Label(pantalla4, text=f"Bienvenido {Name}", fg="Black", bg="lightgray", font=("Arial", 12, "bold"))
        texto1.place(x=580, y=50)
        # Label
        # Video
        lblImgUser = Label(pantalla4)
        lblImgUser.place(x=450, y=80)

        # Imagen
        PosUserImg = clases.index(User)
        UserImg = images[PosUserImg]

        ImgUser = Image.fromarray(UserImg)
        #
        ImgUser = cv2.imread(f"{OutFolderPathFace}/{User}.png")
        ImgUser = cv2.cvtColor(ImgUser, cv2.COLOR_RGB2BGR)
        ImgUser = Image.fromarray(ImgUser)
        # Ajustar tamaño
        desired_size = (420, 420)  # Ajusta a las dimensiones
        ImgUser = ImgUser.resize(desired_size, Image.Resampling.LANCZOS)  # Usa Image.Resampling.LANCZOS en lugar de Image.ANTIALIAS

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
                            # print(longitud1)

                            # Ojo Izquierdo
                            x3, y3 = lista[374][1:]
                            x4, y4 = lista[386][1:]
                            cx2, cy2 = (x3 + x4) // 2, (y3 + y4) // 2
                            longitud2 = math.hypot(x4 - x3, y4 - y3)
                            # print(longitud2)

                            # Parietal Derecho
                            x5, y5 = lista[139][1:]
                            # Parietal Izquierdo
                            x6, y6 = lista[368][1:]

                            # Ceja Derecha
                            x7, y7 = lista[70][1:]
                            # Ceja Izquierda
                            x8, y8 = lista[300][1:]

                            # cv2.circle(frame, (x5, y5), 2, (255, 0, 0), cv2.FILLED)
                            # cv2.circle(frame, (x6, y6), 2, (0, 0, 0), cv2.FILLED)
                            # cv2.circle(frame, (x7, y7), 2, (0, 255, 0), cv2.FILLED)
                            # cv2.circle(frame, (x8, y8), 2, (0, 255, 0), cv2.FILLED)

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
                                        xi, yi, an, al = int(xi * animg), int(yi * alimg), int(
                                            an * animg), int(al * alimg)

                                        # Width
                                        offsetan = (offsetx / 100) * an
                                        xi = int(xi - int(offsetan / 2))
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
                                        alis0, anis0, cs0 = frame.shape
                                        imgStep0 = np.zeros((alis0, anis0, cs0), np.uint8)
                                        imgStep0 = frame[yi:yf, xi:xf]
                                        step = 1

                                    elif step == 1:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step1
                                        alis1, anis1, cs1 = frame.shape
                                        imgStep1 = np.zeros((alis1, anis1, cs1), np.uint8)
                                        imgStep1 = frame[yi:yf, xi:xf]
                                        step = 2

                                    elif step == 2:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step2
                                        alis2, anis2, cs2 = frame.shape
                                        imgStep2 = np.zeros((alis2, anis2, cs2), np.uint8)
                                        imgStep2 = frame[yi:yf, xi:xf]
                                        step = 3

                                    elif step == 3:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step3
                                        alis3, anis3, cs3 = frame.shape
                                        imgStep3 = np.zeros((alis3, anis3, cs3), np.uint8)
                                        imgStep3 = frame[yi:yf, xi:xf]
                                        step = 4

                                    elif step == 4:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step4
                                        alis4, anis4, cs4 = frame.shape
                                        imgStep4 = np.zeros((alis4, anis4, cs4), np.uint8)
                                        imgStep4 = frame[yi:yf, xi:xf]
                                        step = 5

                                    elif step == 5:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step5
                                        alis5, anis5, cs5 = frame.shape
                                        imgStep5 = np.zeros((alis5, anis5, cs5), np.uint8)
                                        imgStep5 = frame[yi:yf, xi:xf]
                                        step = 6

                                    elif step == 6:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step6
                                        alis6, anis6, cs6 = frame.shape
                                        imgStep6 = np.zeros((alis6, anis6, cs6), np.uint8)
                                        imgStep6 = frame[yi:yf, xi:xf]
                                        step = 7

                                    elif step == 7:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step7
                                        alis7, anis7, cs7 = frame.shape
                                        imgStep7 = np.zeros((alis7, anis7, cs7), np.uint8)
                                        imgStep7 = frame[yi:yf, xi:xf]
                                        step = 8

                                    elif step == 8:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step8
                                        alis8, anis8, cs8 = frame.shape
                                        imgStep8 = np.zeros((alis8, anis8, cs8), np.uint8)
                                        imgStep8 = frame[yi:yf, xi:xf]
                                        step = 9

                                    elif step == 9:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step9
                                        alis9, anis9, cs9 = frame.shape
                                        imgStep9 = np.zeros((alis9, anis9, cs9), np.uint8)
                                        imgStep9 = frame[yi:yf, xi:xf]
                                        step = 10

                                    elif step == 10:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step10
                                        alis10, anis10, cs10 = frame.shape
                                        imgStep10 = np.zeros((alis10, anis10, cs10), np.uint8)
                                        imgStep10 = frame[yi:yf, xi:xf]
                                        step = 11

                                    elif step == 11:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step11
                                        alis11, anis11, cs11 = frame.shape
                                        imgStep11 = np.zeros((alis11, anis11, cs11), np.uint8)
                                        imgStep11 = frame[yi:yf, xi:xf]
                                        step = 12

                                    elif step == 12:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step12
                                        alis12, anis12, cs12 = frame.shape
                                        imgStep12 = np.zeros((alis12, anis12, cs12), np.uint8)
                                        imgStep12 = frame[yi:yf, xi:xf]
                                        step = 13

                                    elif step == 13:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step13
                                        alis13, anis13, cs13 = frame.shape
                                        imgStep13 = np.zeros((alis13, anis13, cs13), np.uint8)
                                        imgStep13 = frame[yi:yf, xi:xf]
                                        step = 14

                                    elif step == 14:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step14
                                        alis14, anis14, cs14 = frame.shape
                                        imgStep14 = np.zeros((alis14, anis14, cs14), np.uint8)
                                        imgStep14 = frame[yi:yf, xi:xf]
                                        step = 15

                                    elif step == 15:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step15
                                        alis15, anis15, cs15 = frame.shape
                                        imgStep15 = np.zeros((alis15, anis15, cs15), np.uint8)
                                        imgStep15 = frame[yi:yf, xi:xf]
                                        step = 16

                                    elif step == 16:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step16
                                        alis16, anis16, cs16 = frame.shape
                                        imgStep16 = np.zeros((alis16, anis16, cs16), np.uint8)
                                        imgStep16 = frame[yi:yf, xi:xf]
                                        step = 17

                                    elif step == 17:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step17
                                        alis17, anis17, cs17 = frame.shape
                                        imgStep17 = np.zeros((alis17, anis17, cs17), np.uint8)
                                        imgStep17 = frame[yi:yf, xi:xf]
                                        step = 18

                                    elif step == 18:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step18
                                        alis18, anis18, cs18 = frame.shape
                                        imgStep18 = np.zeros((alis18, anis18, cs18), np.uint8)
                                        imgStep18 = frame[yi:yf, xi:xf]
                                        step = 19

                                    elif step == 19:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step19
                                        alis19, anis19, cs19 = frame.shape
                                        imgStep19 = np.zeros((alis19, anis19, cs19), np.uint8)
                                        imgStep19 = frame[yi:yf, xi:xf]
                                        step = 20

                                    elif step == 20:
                                        # Draw
                                        cv2.rectangle(frame, (xi, yi, an, al), (255, 0, 255), 2)
                                        # IMG Step20
                                        alis20, anis20, cs20 = frame.shape
                                        imgStep20 = np.zeros((alis20, anis20, cs20), np.uint8)
                                        imgStep20 = frame[yi:yf, xi:xf]
                                        step = 21








def Log():
    global RegName, RegUser, RegPass, InputNameReg, InputUserReg, InputPassReg, cap, lblVideo, pantalla2
    # Name, User, PassWord
    RegName, RegUser, RegPass = InputNameReg.get(), InputUserReg.get(), InputPassReg.get()

    # Conexión a la base de datos
    mydb = mysql.connector.connect(
        host="localhost",
        user="tu_usuario",
        password="tu_contraseña",
        database="nombre_de_tu_base_de_datos"
    )

    # Crear un cursor para ejecutar consultas SQL
    cursor = mydb.cursor()

    # Name, User, PassWord
    RegName, RegUser, RegPass = InputNameReg.get(), InputUserReg.get(), InputPassReg.get()

    if len(RegName) == 0 or len(RegUser) == 0 or len(RegPass) == 0:
        # Info incompleted
        print(" FORMULARIO INCOMPLETO ")

    else:
        # Info Completed
        # Check users
        UserList = os.listdir(PathUserCheck)
        # Name Users
        UserName = []
        for lis in UserList:
            # Extract User
            User = lis
            User = User.split('.')
            # Save
            UserName.append(User[0])

        # Check Names
        if RegUser in UserName:
            # Registred
            print("USUARIO REGISTRADO ANTERIORMENTE")

        else:
            # No Registred
            # Info
            info.append(RegName)
            info.append(RegUser)
            info.append(RegPass)

            # Guardar información en la base de datos
            try:
                # Consulta SQL para insertar datos en la tabla de usuarios
                sql = "INSERT INTO usuarios (nombre, usuario, contraseña) VALUES (%s, %s, %s)"
                val = (RegName, RegUser, RegPass)

                # Ejecutar la consulta SQL
                cursor.execute(sql, val)

                # Confirmar la transacción
                mydb.commit()

                # Limpiar campos de entrada
                InputNameReg.delete(0, END)
                InputUserReg.delete(0, END)
                InputPassReg.delete(0, END)

                # Mensaje de éxito
                print("Datos registrados correctamente")

            except Exception as e:
                # Mensaje de error
                print("Error al registrar usuario:", e)
                # Revertir la transacción en caso de error
                mydb.rollback()

            # Cerrar cursor y conexión a la base de datos
        cursor.close()
        mydb.close()

            # Save Info
            f = open(f"{OutFolderPathUser}/{RegUser}.txt", 'w')
            f.writelines(RegName + ',')
            f.writelines(RegUser + ',')
            f.writelines(RegPass + ',')
            f.close()

            # Clean
            InputNameReg.delete(0, END)
            InputUserReg.delete(0, END)
            InputPassReg.delete(0, END)

            # Ventana principal
            pantalla2 = Toplevel(pantalla)
            pantalla2.title("BIOMETRIC REGISTER")
            pantalla2.geometry("1280x720")

            back = Label(pantalla2, image=imagenB, text="Back")
            back.place(x=0, y=0, relwidth=1, relheight=1)

            # Video
            lblVideo = Label(pantalla2)
            lblVideo.place(x=0, y=0)
            #lblVideo.place(x=320, y=115)

            # Elegimos la camara
            cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
            cap.set(3, 1280)
            cap.set(4, 720)
            Log_Biometric()