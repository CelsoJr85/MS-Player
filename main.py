""" MS PLAYER 2024 - v1.0.0 """
''' Importações '''
import tkinter as tk
from tkinter import *
from tkinter.ttk import Progressbar
import vlc
import os
from tkinter import Frame, Button, Entry, Label, filedialog, messagebox
from PIL import Image, ImageTk
from pytube import YouTube
import requests
from io import BytesIO

''' Variáveis Globais '''
media_paths = []
current_media_index = 0
media_player = None
video_list = None

''' Interface '''


def mediaCenter():
    global media_paths, current_media_index, media_player, video_list

    fundo = tk.Tk()
    fundo.geometry("300x300+1060+450")
    fundo["bg"] = "#6E2F7C"
    app = Frame(fundo, bg="#36244B")
    app.place(relx=0.003, rely=0.003, relwidth=0.995, relheight=0.995)
    fundo.overrideredirect(True)

    ''' Aplicativo Principal '''

    def fecharAplicativo():
        stop_media()
        fundo.destroy()

    def stop_media():
        global media_player
        if media_player:
            media_player.stop()
            media_player.release()
            media_player = None

    def play_media_in_label(master, media_path, media_label):
        global media_player
        stop_media()

        instance = vlc.Instance("--no-xlib")
        media_player = instance.media_player_new()
        media = instance.media_new(media_path)
        media.get_mrl()
        media_player.set_media(media)
        media_player.set_hwnd(media_label.winfo_id())
        media_player.play()

    def select_media(selected_indices, listbox):
        global current_media_index, media_paths
        if selected_indices:
            current_media_index = selected_indices[0]
            update_listbox(listbox)

    def play_or_resume():
        global current_media_index, media_paths
        if media_paths:
            media_path = media_paths[current_media_index]
            play_media_in_label(app, media_path, media_label)

    def update_listbox(listbox):
        global media_paths
        listbox.selection_clear(0, tk.END)
        listbox.selection_set(current_media_index)
        listbox.see(current_media_index)
        listbox.activate(current_media_index)

    def next_media():
        global current_media_index
        if media_paths and len(media_paths) > 1:
            current_media_index = (current_media_index + 1) % len(media_paths)
            play_or_resume()

    def prev_media():
        global current_media_index
        if media_paths and len(media_paths) > 1:
            current_media_index = (current_media_index - 1) % len(media_paths)
            play_or_resume()

    ''' LISTA DE VIDEOS '''
    def listaMedia():
        top = tk.Tk()
        top.geometry("300x200+1060+250")
        top["bg"] = "#0A4234"
        top.overrideredirect(True)

        def fechar():
            top.destroy()

        def seleciona(event):
            global current_media_index
            stop_media()
            selected_indices = video_list.curselection()
            if selected_indices:
                current_media_index = selected_indices[0]
                select_media(selected_indices, video_list)
                play_or_resume()

        video_list = Listbox(top, bg="#1C4C51", fg="#FF4600", font="Helvetica 10",
                             borderwidth=0, border=None, selectbackground="#30333C")
        video_list.place(relx=0.001, rely=0.001, relwidth=0.99, relheight=0.9)

        media_files = [file for file in os.listdir("videos") if file.endswith((".mp4", ".mp3"))]
        for index, media_file in enumerate(media_files):
            media_paths.append(os.path.join("videos", media_file))
            video_list.insert(tk.END, media_file)

        video_list.bind("<Double-Button-1>", seleciona)
        select_button = Button(top, text="Selecionar", bg="#0A4234", fg="#fff", borderwidth=0, border=None,
                               command=lambda: select_media(video_list.curselection(), video_list))
        select_button.place(relx=0.1, rely=0.9, relwidth=0.2, relheight=0.1)
        sair = Button(top, text="Fechar", bg="#0A4234", fg="#fff", borderwidth=0, border=None,
                               command=fechar)
        sair.place(relx=0.77, rely=0.9, relwidth=0.2, relheight=0.1)

        update_listbox(video_list)

        top.mainloop()

    ''' DOWNLOAD DE VIDEOS '''
    def download_videos():
        fundo.destroy()
        down = tk.Tk()
        down.geometry("300x300+1060+420")
        down["bg"] = "#1C4C51"
        down.overrideredirect(True)

        global img
        img = None  # Inicializa a referência global da imagem

        def close():
            down.destroy()
            mediaCenter()

        def pesquisar():
            global img  # Usa a referência global da imagem
            url = entrada.get()
            yt = YouTube(url)
            titulo = yt.title
            foto = yt.thumbnail_url
            nova_img = Image.open(BytesIO(requests.get(foto).content))
            nova_img = nova_img.resize((280, 280), Image.LANCZOS)

            # Converte a imagem PIL para PhotoImage e atualiza na Label
            img = ImageTk.PhotoImage(nova_img)
            label_img.config(image=img)
            nome_musica['text'] = "Titulo: " + titulo

        def donwload_mp4():
            download_Folder = "videos"
            url = entrada.get()

            try:
                yt = YouTube(url)
                yt.register_on_progress_callback(progresso)

                # Filtra as streams disponíveis para arquivos mp4
                mp4_streams = yt.streams.filter(file_extension="mp4")

                # Escolhe a stream de maior resolução (itag 22 é frequentemente usado para 720p)
                video_stream = mp4_streams.get_highest_resolution()

                # Faz o download do vídeo na pasta especificada
                video_stream.download(download_Folder)
            except Exception as e:
                messagebox.showinfo("Sucesso", "Vídeo baixado no diretório 'videos'.")

        def browse():
            donwload_Directory = filedialog.askdirectory(initialdir="Escolha o Diretório")
            donwload_Path.set(donwload_Directory)

        anterior = 0

        def progresso(stream, chunk, falta):
            global anterior
            tamanho = stream.filesize
            baixado = tamanho - falta
            emprogresso = int(baixado / tamanho * 100)
            if emprogresso > anterior:
                anterior = emprogresso
                bp['value'] = emprogresso
                down.update_idletasks()
            if emprogresso == 100:
                anterior = 0

        frame = Frame(down, bg="#1C4C51")
        frame.pack(fill=tk.BOTH, expand=tk.YES)
        sair = Button(down, bg="#1C4C51", fg="#fff", text="Fechar", borderwidth=0,
                      border=None, command=close, activebackground="#292C35")
        sair.place(relx=0.8, rely=0.93, relwidth=0.15, relheight=0.05)
        download_MP4 = Button(down, bg="#1C4C51", fg="#fff", text="MP4", borderwidth=0,
                      border=None, command=donwload_mp4, activebackground="#292C35")
        download_MP4.place(relx=0.2, rely=0.93, relwidth=0.15, relheight=0.05)

        btnbsc = Button(down, text="     ⬇️", fg="#fff", bg="#226F75", borderwidth=0, border=None,
                        font="Helvetica 10", activebackground="#292C35", command=pesquisar)
        btnbsc.place(relx=0.89, rely=0.02, relwidth=0.1, relheight=0.1)
        entrada = Entry(down, bg="#fff", borderwidth=0.002, fg="#000", font="Arial 12")
        entrada.place(relx=0.01, rely=0.02, relwidth=0.87, relheight=0.1)
        """ CORPO """
        # tela
        label_img = Label(down, bg="#1D2A34", text="", width=30, anchor=tk.CENTER)
        label_img.place(relx=0.005, rely=0.25, relwidth=0.985, relheight=0.6)
        # Titulo
        nome_musica = Label(down, text="música", bg="#1C4C51", fg="#FF4600", width=37,
                            font="Helvetica 10", anchor=tk.CENTER)
        nome_musica.place(relx=0.01, rely=0.14, relwidth=0.98, relheight=0.05)

        down.mainloop()


    ''' Restante do código '''
    # Barra de Progresso
    bp = Progressbar(app, orient=tk.HORIZONTAL, length=400, mode='determinate')
    bp.place(relx=0.001, rely=0.7, relwidth=0.99, relheight=0.01)

    # Labels
    media_label = Label(app, bg="#1D2A34")
    media_label.place(relx=0.001, rely=0.08, relwidth=0.99, relheight=0.7)

    # Botões
    btn_lista = Button(app, text="Lista", fg="#fff", bg="#0A4234",
                       borderwidth=0, border=None, command=listaMedia)
    btn_lista.place(relx=0.1, rely=0.001, relwidth=0.15, relheight=0.08)

    btn_download = Button(app, text="Download", fg="#fff", bg="#1C4C51",
                       borderwidth=0, border=None, command=download_videos)
    btn_download.place(relx=0.3, rely=0.001, relwidth=0.2, relheight=0.08)

    btn_play_selected = Button(app, text="Play/Resume", command=play_or_resume)
    btn_play_selected.place(relx=0.1, rely=0.8, relwidth=0.15, relheight=0.08)

    btn_stop = Button(app, text="Stop", command=stop_media)
    btn_stop.place(relx=0.3, rely=0.8, relwidth=0.15, relheight=0.08)

    btn_next = Button(app, text="Next", command=next_media)
    btn_next.place(relx=0.45, rely=0.8, relwidth=0.15, relheight=0.08)

    btn_prev = Button(app, text="Prev", command=prev_media)
    btn_prev.place(relx=0.75, rely=0.8, relwidth=0.15, relheight=0.08)

    btnfechar = Button(app, text=" Fechar ", bg="#36244B", fg="#fff", borderwidth=0, border=None, command=fecharAplicativo)
    btnfechar.place(relx=0.8, rely=0.003)

    fundo.mainloop()


mediaCenter()
