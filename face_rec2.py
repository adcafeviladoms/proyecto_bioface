#Programa hecho y modificado por Adrian Camacho para proyecto final de curso ASIX2.

import os.path
import datetime
import pickle
import mysql.connector as db

import tkinter as tk
import cv2
from PIL import Image, ImageTk
import face_recognition

import util
from test import test


keys = {
        "host": "localhost",
        "user": "root",
        "password": "",
        "database": "agency"}


class App:
    def __init__ (self):
            self.con = db.connect(host=keys["host"], user=keys["user"], password=keys["password"], database=keys["database"])
            self.logged_in = False
            self.current_user = None



            self.main_window = tk.Tk()

#tamaño de la ventana de la app
            self.main_window.geometry("1200x520+360+100")



#boton login > nombre, color, funcion que hace

            self.user_name_entry = util.get_entry_text(self.main_window)
            self.user_name_entry.place(x=750, y=100)

            self.text_label_user_name_entry = util.get_text_label(self.main_window, 'Introduce tu usuario: ')
            self.text_label_user_name_entry.place(x=750, y=50)

            self.login_button_main_window = util.get_button(self.main_window, 'Conectar', '#0037E1', self.login)
            self.login_button_main_window.place(x=750, y=200)

            self.logout_button_main_window = util.get_button(self.main_window, 'Desconectar', 'red', self.logout)
            self.logout_button_main_window.place(x=750, y=300)

            self.register_new_user_button_main_window = util.get_button(self.main_window, 'Nuevo usuario', 'gray', self.register_new_user, fg='black')
            self.register_new_user_button_main_window.place(x=750, y=400)
#definimos la camara y el lugar donde irá
            self.webcam_label = util.get_img_label(self.main_window)
            self.webcam_label.place ( x=10, y=0, width=700, height=500)

            self.add_webcam(self.webcam_label)
#definimos el lugar de la database. Y creamos un if para que en el caso de que no este creada, se cree en la misma carpeta en la cual se encuentra el programa.
            self.db_dir = './db'
            if not os.path.exists(self.db_dir):
                os.mkdir(self.db_dir)

            self.log_path = './log.txt'

#funcion para la camara web
    def add_webcam(self, label):

#Como utilizaremos esta funcion varias veces, utilizamos if para crearla si no lo está

            if 'cap' not in self.__dict__:
                self.cap = cv2.VideoCapture(0)

                self._label = label
                self.process_webcam()
    def process_webcam(self):
            ret, frame= self.cap.read()
            self.most_recent_capture_arr = frame

#Con esta funcion convertimos la imagen en blanco y negro para que puedan procesar mejor la camara y los colores. BGR Format
            img_= cv2.cvtColor(self.most_recent_capture_arr, cv2.COLOR_BGR2RGB)

#introducimos Pillow y definimos segun el import
            self.most_recent_capture_pil = Image.fromarray(img_)

            imgtk = ImageTk.PhotoImage(image=self.most_recent_capture_pil)

            self._label.imgtk = imgtk
            self._label.configure(image=imgtk)

            self._label.after(20, self.process_webcam)


    def check_current_user(self):
#Definición para asegurarnos de uqe solo se haga una conexión al usuario y comprobarlo
            if self.logged_in:
                print('Ya estás conectado', 'Usuario actual: {}.'.format(self.current_user))
                return True
            else:
                print('Ningún usuario ha iniciado sesión', 'Vuelve a conectarte.')
                return False

    def login(self):
        # Definición para función login, añadimos el antispoofing
            label = test(
                    image=self.most_recent_capture_arr,
                    model_dir='C:/xampp/htdocs/ProgramaFinal/Silent-Face-Anti-Spoofing-master/resources/anti_spoof_models',
                    device_id=0
                )

            if label == 1:

                if not self.check_current_user():
                    user_name_input = self.user_name_entry.get('1.0', tk.END).strip()

                    user_name = util.recognize(self.most_recent_capture_arr, self.db_dir)

                    user_db = util.getUser(user_name)
                    print(user_db)

                    if user_name in ['unknown_person', 'no_persons_found'] or user_name != user_name_input:
                        print(user_name, user_name_input)
                        util.msg_box('Ups...', 'Usuario desconocido. Registrate o intentalo de nuevo.')
                    else:
                        util.msg_box('Bienvenido!', 'Bienvenido al sistema, {}.'.format(user_name))
                        self.current_user = user_name_input
                        self.is_connected = True  # actualizamos la variable de estado al conectarnos
                        with open(self.log_path, 'a') as f:
                            f.write('{},{},in\n'.format(user_name, datetime.datetime.now()))
                            f.close()
                            # Registro de entrada en user_history
                            user_id = user_db["id"]
                            login_time = datetime.datetime.now()
                            util.insert_user_history(self.con, user_id, login_time=login_time)

            else:
                util.msg_box('Algo huele mal aqui...', 'Eres falso!')

    def logout(self):

            label = test(
                image=self.most_recent_capture_arr,
                model_dir='C:/xampp/htdocs/ProgramaFinal/Silent-Face-Anti-Spoofing-master/resources/anti_spoof_models',
                device_id=0
            )
            if label == 1:

                if not self.is_connected:
                    util.msg_box('Ya estás desconectado', 'Vuelve a conectarte.')
                else:
                    self.check_current_user()
                    with open(self.log_path, 'a') as f:
                        user_name = util.recognize(self.most_recent_capture_arr, self.db_dir)
                        if user_name in ['unknown_person', 'no_persons_found']:
                            util.msg_box('Ups...', 'Usuario desconocido. Registrate o intentalo de nuevo.')
                        else:
                            util.msg_box('Hasta pronto!', 'Te has desconectado del sistema.')
                            self.is_connected = False  # actualizamos la variable de estado al desconectarnos
                            f.write('{},{},out\n'.format(user_name, datetime.datetime.now()))
                            f.close()
                            # Registro de salida en user_history
                            user_id = util.getUser(user_name)["id"]
                            logout_time = datetime.datetime.now()
                            util.insert_user_history(self.con, user_id, logout_time=logout_time)

            else:
                util.msg_box('Algo huele mal aqui...', 'Eres falso!')


#Funcion para el registro
    def register_new_user(self):
#funcion para crear nueva ventana para el registro de la foto nueva.
#Creamos botones con sus funciones y usos.
            self.register_new_user_window = tk.Toplevel(self.main_window)
            self.register_new_user_window.geometry("1200x520+370+120")

            self.accept_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Aceptar', 'green', self.accept_register_new_user)
            self.accept_button_register_new_user_window.place(x=750, y=300)

            self.try_again_button_register_new_user_window = util.get_button(self.register_new_user_window, 'Intentalo de nuevo', 'red', self.try_again_register_new_user)
            self.try_again_button_register_new_user_window.place(x=750, y=400)

            self.capture_label = util.get_img_label(self.register_new_user_window)
            self.capture_label.place(x=10, y=0, width=700, height=500)

            self.add_img_to_label(self.capture_label)
#Creamos espacio para pedir un nombre de login. Importante, siempre que creamos un objeto utilizando tinker tenemos que informar donde lo estamos creando self.register_new... en este caso
            self.entry_text_register_new_user=util.get_entry_text(self.register_new_user_window)
            self.entry_text_register_new_user.place(x=750, y=150)

            self.text_label_register_new_user = util.get_text_label (self.register_new_user_window, 'Por favor, introduce tu nombre: ')
            self.text_label_register_new_user.place(x=750, y=70)

    def try_again_register_new_user(self):
            self.register_new_user_window.destroy()

    def add_img_to_label(self, label):
            imgtk = ImageTk.PhotoImage(image= self.most_recent_capture_pil)
            label.imgtk = imgtk
            label.configure(image=imgtk)

    #variable para obtener información en la ventana
            self.register_new_user_capture = self.most_recent_capture_arr.copy()


        #definiendo la ventana principal
    def start(self):
            self.main_window.mainloop()

    def accept_register_new_user(self):
            try:
                    name = self.entry_text_register_new_user.get(1.0, "end-1c")
                    embeddings = face_recognition.face_encodings(self.register_new_user_capture)[0]

                    file = open(os.path.join(self.db_dir, '{}.pickle'.format(name)), 'wb')
                    pickle.dump(embeddings, file)

                    result = util.registerUser(name, embeddings)
                    result["affected"] += 1
                    result["id"] = result["id"]

                    print(result, name)


                    if result["affected"] > 0:
                        util.msg_box('Éxito!', 'El usuario se ha registrado!')
                    else:
                        util.msg_box('Error!', 'Ocurrió un error al registrar el usuario')

            except Exception as e:

                    util.msg_box('Error!', f'Ocurrió un error al registrar el usuario. Detalles del error: {e}')
                    print(e)
            self.register_new_user_window.destroy()

    #definiendo cuando llamamos la app
if __name__ == "__main__":
    app = App()
    app.start()