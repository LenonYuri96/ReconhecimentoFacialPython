import sys
import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2
import numpy as np
from PIL import Image, ImageTk
from utils.create_table import create_table
from utils.data_insert import cadastro, fetch_users
from utils.my_connection import mysql_get_mydb
import threading
import webbrowser

# Variáveis globais
saveface = False
savefaceC = 0
trained = False
recognizer = None
cap = None
face_cascade = None
current_id = None
current_name = None
capture_thread = None
window_closed = False
training_after_close = False


def creatDir(name, path=""):
    full_path = os.path.join(os.getcwd(), path, name.lower())
    if not os.path.exists(full_path):
        os.makedirs(full_path)


def saveFace(user_id, name, sobrenome):
    global saveface
    global current_id
    global current_name

    saveface = True
    creatDir("usuario")
    name_folder = f"{name}_{sobrenome}"
    creatDir(name_folder, "usuario")
    current_id = user_id
    current_name = name_folder
    print(f"Diretório criado para o ID {user_id}: usuario/{name_folder}")


def saveImg(img, user_id):
    user_dir = f"usuario/{current_name}"
    if not os.path.exists(user_dir):
        print(f"Erro: O diretório {user_dir} não existe.")
        return
    qtd = os.listdir(user_dir)
    img_path = f"{user_dir}/{str(len(qtd))}.jpg"
    cv2.imwrite(img_path, img)
    print(f"Imagem salva em {img_path}")


def trainData():
    global recognizer
    global trained

    trained = False
    persons = fetch_users()

    if persons is None or len(persons) == 0:
        print("Nenhum usuário encontrado para treinamento.")
        return

    ids = []
    faces = []

    for user_id, nome, sobrenome in persons:
        user_folder = os.path.join("usuario", f"{nome}_{sobrenome}")
        user_faces = os.listdir(user_folder)

        if len(user_faces) < 2:
            print(f"Usuário {user_id} não tem fotos suficientes para treinamento.")
            continue

        for f in user_faces:
            img = cv2.imread(os.path.join(user_folder, f), 0)
            faces.append(img)
            ids.append(user_id)

    if len(faces) < 2:
        print("Não há fotos suficientes para treinamento.")
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(ids))
    trained = True
    print("Treinamento concluído.")


def start_recognition():
    global trained
    global saveface
    global cap
    global face_cascade
    global recognizer
    global savefaceC
    global current_id
    global current_name
    global capture_thread
    global window_closed

    if cap is not None and cap.isOpened():
        print("Já há uma captura em andamento.")
        return

    cap = cv2.VideoCapture(0)
    face_cascade = cv2.CascadeClassifier(
        os.path.join(os.getcwd(), "haarcascade_frontalface_default.xml")
    )
    if recognizer is None:
        recognizer = cv2.face.LBPHFaceRecognizer_create()

    def close_capture():
        global cap
        global training_after_close

        if cap:
            cap.release()
        cv2.destroyAllWindows()
        training_after_close = True
        window_closed = True
        camera_window.destroy()
        print("Janela de captura fechada.")

    def update_frame():
        global saveface
        global savefaceC
        global recognizer
        global trained
        global current_id
        global current_name

        if window_closed:
            return

        ret, frame = cap.read()
        if not ret:
            return

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 6)

        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            roi_gray = gray[y : y + h, x : x + w]
            resize = cv2.resize(roi_gray, (200, 200))  # Reduzido o tamanho
            if trained:
                idf, conf = recognizer.predict(resize)
                user_data = fetch_users(user_id=idf)
                if user_data:
                    user_id, nome, sobrenome = user_data[0]
                    nameP = f"{nome} {sobrenome}"
                    cv2.putText(
                        frame,
                        f"ID: {idf}",
                        (x + 5, y + 190),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (255, 255, 255),
                        1,
                        cv2.LINE_AA,
                    )
                    cv2.putText(
                        frame,
                        nameP,
                        (x + 5, y + 175),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0) if conf < 40 else (0, 0, 255),
                        1,
                        cv2.LINE_AA,
                    )

                    if conf < 40:
                        cv2.putText(
                            frame,
                            "Catraca Liberada",
                            (10, 95),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 255, 0),
                            1,
                            cv2.LINE_AA,
                        )
                    else:
                        cv2.putText(
                            frame,
                            "Catraca Bloqueada",
                            (10, 115),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.8,
                            (0, 0, 255),
                            1,
                            cv2.LINE_AA,
                        )

                    cv2.putText(
                        frame,
                        "Treinado",
                        (10, 65),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        1,
                        cv2.LINE_AA,
                    )

                else:
                    cv2.putText(
                        frame,
                        "Desconhecido",
                        (x + 5, y + 25),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 0, 255),
                        1,
                        cv2.LINE_AA,
                    )
            else:
                cv2.putText(
                    frame,
                    "Nao Treinado",
                    (10, 65),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 255),
                    1,
                    cv2.LINE_AA,
                )
            if saveface:
                cv2.putText(
                    frame,
                    str(savefaceC),
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 255),
                    1,
                    cv2.LINE_AA,
                )

                saveImg(resize, current_id)
                savefaceC += 1
                if savefaceC >= 20:
                    savefaceC = 0
                    saveface = False
                    print("20 fotos salvas. Fechando a janela da câmera.")
                    close_capture()
                    return

        # Converta a imagem do OpenCV para o formato Tkinter
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
        camera_window.imgtk = imgtk  # Manter uma referência à imagem

        camera_window.after(10, update_frame)

    def create_camera_window():
        global camera_window
        global canvas

        camera_window = tk.Toplevel(root)
        camera_window.title("Janela da Câmera")
        camera_window.geometry("640x480")  # Dimensões ajustadas
        camera_window.protocol("WM_DELETE_WINDOW", lambda: close_capture())
        camera_window.configure(bg="white")

        # Canvas para exibir o vídeo
        canvas = tk.Canvas(
            camera_window, width=640, height=480, bg="white"
        )  # Dimensões ajustadas
        canvas.pack(fill=tk.BOTH, expand=True)

        tk.Button(
            camera_window,
            text="Fechar",
            command=close_capture,
            font=("Arial", 10),
            bg="#ff4c4c",
            fg="white",
            borderwidth=0,
            relief="flat",
        ).pack(pady=5)
        return camera_window

    window_closed = False
    capture_thread = threading.Thread(target=update_frame)
    capture_thread.start()

    camera_window = create_camera_window()


def open_save_face():
    global saveface
    saveface = True


def open_train_data():
    trainData()


def show_warning_and_start(user_id):
    user_data = fetch_users(user_id=user_id)
    if not user_data:
        print(f"Dados do usuário {user_id} não encontrados.")
        return

    # Corrigido: acesso por índice
    user = user_data[0]
    nome = user[1]
    sobrenome = user[2]

    response = messagebox.askokcancel(
        "Aviso",
        "Por favor, remova óculos, bonés ou qualquer outro acessório que possa dificultar o reconhecimento.\n\nClique em OK para começar a capturar as imagens.",
    )
    if response:
        saveFace(user_id, nome, sobrenome)
        start_recognition()


def handle_cadastro():
    nome = nome_entry.get()
    sobrenome = sobrenome_entry.get()
    email = email_entry.get()

    if nome and sobrenome and email:
        user_id = cadastro(nome, sobrenome, email)
        show_warning_and_start(user_id)
    else:
        messagebox.showwarning("Cadastro", "Todos os campos devem ser preenchidos.")


def open_credits():
    credits_window = tk.Toplevel(root)
    credits_window.title("Créditos")

    credits_window.geometry("800x600")  # Dimensões ajustadas
    credits_window.configure(bg="white")

    header_frame = tk.Frame(
        credits_window, bg="lightblue", height=50, borderwidth=1, relief="solid"
    )
    header_frame.pack(fill=tk.X, side=tk.TOP)

    tk.Label(header_frame, text="Créditos", font=("Arial", 18), bg="lightblue").pack(
        pady=5
    )

    tk.Label(credits_window, text="Alunos:", font=("Arial", 16), bg="white").pack(
        pady=5
    )
    alunos_frame = tk.Frame(credits_window, bg="white")
    alunos_frame.pack(pady=5)

    alunos = [
        ("Adilson", "https://github.com/JuninnZZ"),
        ("Bianca", "https://github.com/Bima0l"),
        ("Davi", "https://github.com/DaviAfons"),
        ("Gabriel", "https://github.com/NAEzinn"),
        ("Sofia", "https://github.com/SofiaTressePires"),
    ]

    for nome, url in alunos:
        tk.Button(
            alunos_frame,
            text=nome,
            command=lambda url=url: open_url(url),
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            borderwidth=1,
            relief="flat",
            padx=8,
            pady=4,
        ).pack(pady=2)

    tk.Label(credits_window, text="Instrutores:", font=("Arial", 16), bg="white").pack(
        pady=5
    )
    instrutores_frame = tk.Frame(credits_window, bg="white")
    instrutores_frame.pack(pady=5)

    instrutores = [
        ("Lenon Yuri", "https://github.com/LYuri26"),
        ("Franco M. A. Caixeta", "https://github.com/RoCkHeLuCk"),
    ]

    for nome, url in instrutores:
        tk.Button(
            instrutores_frame,
            text=nome,
            command=lambda url=url: open_url(url),
            font=("Arial", 12),
            bg="#4CAF50",
            fg="white",
            borderwidth=1,
            relief="flat",
            padx=8,
            pady=4,
        ).pack(pady=2)

    tk.Button(
        credits_window,
        text="Fechar",
        command=credits_window.destroy,
        font=("Arial", 12),
        bg="#ff4c4c",
        fg="white",
        borderwidth=0,
        relief="flat",
        padx=8,
        pady=4,
    ).pack(pady=10)


def open_url(url):
    webbrowser.open_new_tab(url)


def init_program():
    global trained
    global saveface
    global savefaceC
    global current_id
    global current_name

    cnx = mysql_get_mydb()
    if cnx:
        create_table(cnx)
        print("Banco de dados e tabela criados com sucesso.")
    else:
        print("Não foi possível conectar ao banco de dados.")
        exit()

    trainData()
    print("Treinamento inicial concluído.")


# Inicializa o programa
init_program()

# Configura a interface gráfica
root = tk.Tk()
root.title("Reconhecimento Facial Senai Uberaba")
root.geometry("1024x768")  # Dimensões ajustadas
root.configure(bg="white")


def on_closing():
    global cap
    global capture_thread
    global window_closed

    if cap:
        cap.release()
    if capture_thread and capture_thread.is_alive():
        window_closed = True
        capture_thread.join()
    cv2.destroyAllWindows()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_closing)


def create_button(parent, text, command, **kwargs):
    button = tk.Button(parent, text=text, command=command, **kwargs)
    button.pack(pady=5, fill=tk.X, padx=10)
    return button


# Cabeçalho
header_frame = tk.Frame(root, bg="lightblue", height=100, borderwidth=1, relief="solid")
header_frame.pack(fill=tk.X, side=tk.TOP)

# Caminho relativo para a imagem do logo
logo_path = os.path.join(os.getcwd(), "images", "logo.png")
header_img = Image.open(logo_path)
# Reduzido o tamanho da imagem
header_img = header_img.resize((200, 200), Image.LANCZOS)
header_imgtk = ImageTk.PhotoImage(header_img)
header_label = tk.Label(header_frame, image=header_imgtk, bg="lightblue")
header_label.pack(pady=5)

# Formulário de cadastro
form_frame = tk.Frame(root, bg="white", borderwidth=1, relief="solid", padx=10, pady=10)
form_frame.pack(pady=10, padx=10, fill=tk.X)

tk.Label(form_frame, text="Nome:", font=("Arial", 10), bg="white").grid(
    row=0, column=0, padx=5, pady=2, sticky=tk.W
)
tk.Label(form_frame, text="Sobrenome:", font=("Arial", 10), bg="white").grid(
    row=1, column=0, padx=5, pady=2, sticky=tk.W
)
tk.Label(form_frame, text="E-mail:", font=("Arial", 10), bg="white").grid(
    row=2, column=0, padx=5, pady=2, sticky=tk.W
)

nome_entry = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
nome_entry.grid(row=0, column=1, padx=5, pady=2, sticky=tk.W)
sobrenome_entry = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
sobrenome_entry.grid(row=1, column=1, padx=5, pady=2, sticky=tk.W)
email_entry = tk.Entry(form_frame, font=("Arial", 10), bd=1, relief="solid")
email_entry.grid(row=2, column=1, padx=5, pady=2, sticky=tk.W)

tk.Button(
    form_frame,
    text="Cadastrar",
    command=handle_cadastro,
    font=("Arial", 10),
    bg="#4CAF50",
    fg="white",
    borderwidth=0,
    relief="flat",
).grid(row=3, columnspan=2, pady=5)

# Botões na janela principal
button_frame = tk.Frame(
    root, bg="white", borderwidth=1, relief="solid", padx=10, pady=10
)
button_frame.pack(pady=10, fill=tk.X, padx=10)

# Estilo dos botões
button_style = {
    "font": ("Arial", 10),
    "bg": "#4CAF50",
    "fg": "white",
    "width": 30,
    "borderwidth": 0,
    "relief": "flat",
}

# Criando os botões com o estilo aprimorado
create_button(button_frame, "Reconhecer", start_recognition, **button_style)
create_button(button_frame, "Treinar Dados", open_train_data, **button_style)
create_button(button_frame, "Créditos", open_credits, **button_style)
create_button(button_frame, "Fechar", root.quit, **button_style)

# Rodapé
footer_frame = tk.Frame(root, bg="lightgray", height=50)
footer_frame.pack(fill=tk.X, side=tk.BOTTOM)

footer_label = tk.Label(
    footer_frame,
    text="Aplicação desenvolvida pela Turma de Informática Para Internet Trilhas de Futuro 2024\nInstrutor: Lenon Yuri",
    bg="lightgray",
    font=("Arial", 8),
    justify=tk.CENTER,
)
footer_label.pack(pady=5)

root.mainloop()
