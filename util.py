import os
import pickle
import mysql.connector as db
import face_recognition
from PIL import Image
import numpy as np
import mysql.connector
import tkinter as tk
from tkinter import messagebox
import os
import pickle
import face_recognition
import datetime

keys = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "agency"
}

# Conectarse a la base de datos
try:
    con = db.connect(host=keys["host"], user=keys["user"], password=keys["password"], database=keys["database"])
    print("Conexión exitosa")
except db.Error as e:
    print(f"Error de conexión: {e}")

#definimos como qeuremos los botones
def get_button(window, text, color, command, fg='white'):
    button = tk.Button(
        window,
        text=text,
        activebackground="black",
        activeforeground="white",
        fg=fg,
        bg=color,
        command=command,
        height=2,
        width=20,
        font=('Helvetica bold', 20)
    )

    return button


def get_img_label(window):
    label = tk.Label(window)
    label.grid(row=0, column=0)
    return label


def get_text_label(window, text):
    label = tk.Label(window, text=text)
    label.config(font=("sans-serif", 21), justify="left")
    return label


def get_entry_text(window):
    inputtxt = tk.Text(window,
                       height=1,
                       width=15, font=("Arial", 28))
    return inputtxt


def msg_box(title, description):
    messagebox.showinfo(title, description)



def recognize(img, db_path):
    # it is assumed there will be at most 1 match in the db

    embeddings_unknown = face_recognition.face_encodings(img)
    if len(embeddings_unknown) == 0:
        return 'no_persons_found'
    else:
        embeddings_unknown = embeddings_unknown[0]

    db_dir = sorted(os.listdir(db_path))

    match = False
    j = 0
    while not match and j < len(db_dir):
        path_ = os.path.join(db_path, db_dir[j])

        file = open(path_, 'rb')
        embeddings = pickle.load(file)

        match = face_recognition.compare_faces([embeddings], embeddings_unknown)[0]
        j += 1

    if match:
        return db_dir[j - 1][:-7]
    else:
        return 'unknown_person'



def convertToBinaryData(embeddings):
    try:
        binaryData = embeddings.tobytes()
        return binaryData
    except:
        return 0
    

    
def write_file(image_data, path):
    with open(path, 'wb') as file:
        file.write(image_data)

    img = Image.open(path)
    img.show()

def registerUser(name, embeddings):
    id = 0
    inserted = 0
    
    try:
        con = db.connect(host=keys["host"], user=keys["user"], password=keys["password"], database=keys["database"])
        cursor = con.cursor()
        pic = convertToBinaryData(embeddings)
        sql = "INSERT INTO user (name) VALUES (%s);"

        cursor.execute(sql, (name,))
        con.commit()
        inserted = cursor.rowcount
        id = cursor.lastrowid

    except db.Error as e:
            print("Error:", e)
        
    return {"id": id, "affected":inserted}


def getUser(name):
    id = 0
    rows = 0

    try:
        con = db.connect(host=keys["host"], user=keys["user"], password=keys["password"], database=keys["database"])
        cursor = con.cursor(prepared=True)
        sql = "SELECT * FROM user WHERE name = %s"

        cursor.execute(sql, (name,))
        records = cursor.fetchall()

        for row in records: 
            id = row[0]
        rows = len(records)
        
    except db.Error as e:
        print("Failed retrieving user:", e)
    finally:
        if con.is_connected():
            cursor.close()
            con.close()

    return {"id": id, "affected": rows}

def insert_user_history(con, user_name, login_time=None, logout_time=None):
    try:
        cursor = con.cursor()
        if login_time:
            sql = "INSERT INTO user_history (idUser, loginTime) VALUES (%s, %s);"
            cursor.execute(sql, (user_name, login_time))
        elif logout_time:
            sql = "UPDATE user_history SET logoutTime = %s WHERE idUser = %s AND logoutTime IS NULL;"
            cursor.execute(sql, (logout_time, user_name))
        con.commit()
        cursor.close()
        print(sql, login_time, logout_time)
    except db.Error as e:
        print("Failed to insert user history:", e)