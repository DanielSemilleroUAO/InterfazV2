# -*- coding: utf-8 -*-
"""
Created on Tue Jul 24 17:21:21 2018

@author: Daniel Delgado Rodrìguez
         Juan Fernando Guerrero F.  
"""
###############################################################################
###############################################################################
        #########           ###########                ###########            
        #        #      @        #                          # 
        #        #               #                          #
        #        #      #        #         #########        #
        #########       #        #        #         #       #
        #        #      #        #        #         #       #
        #        #      #        #        #         #       #
        #        #      #        #        #         #       #
        #########       #   ###########    #########        #
###############################################################################
###############################################################################
        
#-------------------------IMPORTAR LÌBRERIAS-----------------------------------
from multiprocessing import Process
from multiprocessing import Queue
from imutils.video import VideoStream
import tkinter
from PIL import Image, ImageTk
import cv2
from datetime import datetime,timedelta
from tkinter import ttk
from tkinter import font
from tkinter import Canvas
import numpy as np
import time
import os
#------------------------IMPORTAR SUB-MODULOS----------------------------------
from COMUNICACION import comunicacion
comunicacion_contenedor = comunicacion()
from PIR import SensorPIR
sensor = SensorPIR()
#-------------------------FUNCIÒN DE CLASIFICACIÒN-----------------------------
def classify_frame(net, inputQueue, outputQueue):
    while True:
        if not inputQueue.empty():
            frame = inputQueue.get()
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), size=(300, 300), swapRB=True, crop=False)
            net.setInput(blob)
            detections = net.forward()
            outputQueue.put(detections)
#-----------------ETIQUETAS DE LOS RESIDUOS A CLASIFICAR-----------------------
CLASSES = ["background", "bolsas_te", "botella_plastica", "botella_vidrio", "carton_alimento",
    "carton_caja", "metal_latas", "papel", "residuo_banano", "residuo_huevo", "residuo_manzana", "residuo_naranaja"]
TIPO = ["background", "organico", "plastico", "vidrio", "papel/carton",
    "papel/carton", "metal", "papel/carton", "organico", "organico", "organico", "organico"]
COLORS = [[0,0,0],[0,255,0],[42,46,75],[63,136,143],[144,144,144],[144,144,144],[34,113,179],[244,169,0],[0,255,0],[0,255,0],[0,255,0],[0,255,0]]
IMAGES = ["background", "IMAGENES/ORGANICO.png", "IMAGENES/PLASTICO.png", "IMAGENES/VIDRIO.png", "IMAGENES/PAPEL.png",
    "IMAGENES/PAPEL.png", "IMAGENES/METAL.png", "IMAGENES/PAPEL.png", "IMAGENES/ORGANICO.png", "IMAGENES/ORGANICO.png", "IMAGENES/ORGANICO.png", "IMAGENES/ORGANICO.png"]
VOZ = ["background", "Organico.mp3", "Plastico.mp3", "Vidrio.mp3", "PapelCarton.mp3",
    "PapelCarton.mp3", "Metal.mp3", "PapelCarton.mp3", "Organico.mp3", "Organico.mp3", "Organico.mp3", "Organico.mp3"]
TOPICS = ["background", "contenedor/organico", "contenedor/plastico", "contenedor/vidrio", "contenedor/papelcarton",
    "contenedor/papelcarton", "contenedor/metal", "contenedor/papelcarton", "contenedor/organico", "contenedor/organico", "contenedor/organico", "contenedor/organico"]
PORCENTAJES = [0,0,0,0,0,0,0,0,0,0,0,0,0]
tipos = ["organico", "plastico", "vidrio", "papel/carton","metal"]
#------------------IMPORTAR MODELO DE RED NEURONAL-----------------------------
ruta = "/home/linaro/CodTinkerV1/"
net = cv2.dnn.readNetFromTensorflow(ruta+"MODELO_DL/frozen_inference_graphV10.pb",ruta+"MODELO_DL/graph.pbtxt")
inputQueue = Queue(maxsize=1)
outputQueue = Queue(maxsize=1)
#-----------------HILO DE PROCESAMIENTO DEL MODELO-----------------------------
p = Process(target=classify_frame, args=(net, inputQueue,outputQueue,))
p.daemon = True
p.start()
#ruta = "/home/linaro/CodTinkerV1/"
#----------------------DESARROLLO INTERFAZ_GRAFICA-----------------------------
class Interfaz_grafica_usuario(tkinter.Tk):
    def __init__(self,parent):
        tkinter.Tk.__init__(self,parent)
#------------------------INICIALIZACIÒN DE VARIABLES---------------------------
        self.parent = parent
        self.ID_CONTENDOR = "bote0001"
        #-------------------VARIABLES DEL TIEMPO DE ENVIO----------------------
        self.tiempo_envio_datos = 5
        #------------------VARIABLES DE LOS CONTENDORES------------------------
        self.cantidad_contenedor_1 = 0
        self.cantidad_contenedor_2 = 0
        self.cantidad_contenedor_3 = 0
        self.cantidad_contenedor_4 = 0
        self.cantidad_contenedor_5 = 0
        self.cantidad_contenedor_6 = 0
        self.contendor_lleno = "-"        
        #----------------------TIEMPO DE ESPERA--------------------------------
        self.tiempo_espera = 30
#----------------------VARIABLES DE LA INTERFAZ GRAFICA------------------------
        #--------------ALMACENAR DATOS CANTIDAD RESIDUOS-----------------------
        self.contador = 0
        self.datos = []
        self.min_a = 0
        self.min_d = 0
        self.detectado = False
        self.intentos = 5
        self.valores = []
        self.indices = []
        self.tipo = []
        self.cajas = []
        self.seg_ant = 0
        self.seg_ant_c = 0
        self.seg_ant_i = 0
        self.seg_ant_r = 0
        self.contador_tomas = 0
        self.tiempo_toma = 3
        self.bandera_c = False
        self.bandera_i = False
        self.bandera_s = False
        self.contenedor_lleno = False
        self.menu = False
        self.porcentaje_r1 = 0
        self.porcentaje_r2 = 0
        self.porcentaje_r3 = 0
        self.porcentaje_r4 = 0
        self.porcentaje_r5 = 0
        self.porcentaje_r6 = 0
        self.contrasena = ""
        #--------------DATOS DE INFORMACIÒN DE LA INTERFAZ---------------------
        self.estado_contenedor = tkinter.StringVar()
        self.estado_contenedor.set(u"ESTADO DEL CONTENDOR E INFORMACIÓN DE FALLOS")
        self.residuo_1 = tkinter.StringVar()
        self.residuo_1.set(u"000 %")
        self.residuo_2 = tkinter.StringVar()
        self.residuo_2.set(u"000 %")
        self.residuo_3 = tkinter.StringVar()
        self.residuo_3.set(u"000 %")
        self.residuo_4 = tkinter.StringVar()
        self.residuo_4.set(u"000 %")
        self.residuo_5 = tkinter.StringVar()
        self.residuo_5.set(u"000 %")
        self.residuo_6 = tkinter.StringVar()
        self.residuo_6.set(u"000 %")
        
        hora_actual = datetime.now()
        hora_actual = hora_actual.strftime(""+str(hora_actual.year)+"/%m/%d-%H:%M:%S")
        self.hora = tkinter.StringVar()
        self.hora.set("HORA Y FECHA: "+hora_actual)
        
        self.estado_internet = tkinter.StringVar()
        self.verificar_conexion_internet()
        
#-----------------------INICIO DE PROCESO DE LOS SUB-MODULOS-------------------
        self.detections = None
        #----------------------CÀMARA USB----------------------------------------------
        try:
            self.vs = VideoStream(src=4).start()
            #---------------------CAMARA DE LA RASPBERRY PI--------------------------------
            #vs = VideoStream(usePiCamera=True).start()
        except:
            self.estado_contenedor.set(u"MALA CONEXIÓN O DAÑO DE LA CÁMARA")
#-----------------------ALMACENAMIENTO APAGADO---------------------------------
        self.initialize()
###############################################################################
###############################################################################
#---------------------------INTERFAZ PRINCIAPL---------------------------------
    def initialize(self):
        #---------------------LETRAS INTERFAZ PRINCIPAL------------------------
        letra_tiempo = font.Font(family='Helvetica', size=25, weight=font.BOLD)
        letra_otros = font.Font(family='Helvetica', size=8, weight=font.BOLD)
        #---------------------FONDO INTERFAZ-----------------------------------
        self.grid()
        self.fondo = tkinter.Frame(self, width=798, height=453, bg = "gray")
        self.fondo.grid(column=0, row = 0, padx=1, pady= 1)
        
        barra_principal = tkinter.Frame(self.fondo, width=793, height=2, bg = "gray")
        barra_principal.grid(column=0, row = 0, padx=1, pady= 0)
        #---------------------BARRA ESTADO CONTENEDOR--------------------------
        barra_estado = tkinter.Frame(barra_principal, width=490, height=2, bg = "gray")
        barra_estado.grid(column=0, row = 0, padx=1, pady= 0)
        subbarra_estado = tkinter.Frame(barra_estado, width=490, height=2, bg = "gray")
        subbarra_estado.grid(column=0, row = 0, padx=0, pady= 0)
        #---------------------ESTADO ACTUAL CONTENDOR--------------------------
        self.vista_estado = tkinter.Label(subbarra_estado,textvariable=self.estado_contenedor,anchor="center",fg="white",bg="blue", width=80,height = 1,font=letra_otros)
        self.vista_estado.grid(column=0,row=0,padx=0, pady=0,sticky='EW')
        #------------------------ID DEL CONTENDOR (UNICO)----------------------
        barra_informacion = tkinter.Frame(subbarra_estado, width=490, height=2, bg = "gray")
        barra_informacion.grid(column=0, row = 1, padx=0, pady= 0)
        
        id_contendor = tkinter.StringVar()
        id_contendor.set("ID: "+self.ID_CONTENDOR)
        identificador_contenedor = tkinter.Label(barra_informacion,textvariable=id_contendor,anchor="center",fg="white",bg="blue", width=25,height = 1,font=letra_otros)
        identificador_contenedor.grid(column=0,row=1,padx=0, pady=0,sticky='EW')
        #------------------------CONEXIÒN A INTERNET---------------------------
        identificador_contenedor = tkinter.Label(barra_informacion,textvariable=self.estado_internet,anchor="center",fg="white",bg="blue", width=30,height = 1,font=letra_otros)
        identificador_contenedor.grid(column=1,row=1,padx=0, pady=0,sticky='EW')
        #------------------------HORA ACTUAL DEL SISTEMA-----------------------
        identificador_contenedor = tkinter.Label(barra_informacion,textvariable=self.hora,anchor="center",fg="white",bg="blue", width=39,height = 1,font=letra_otros,justify="center")
        identificador_contenedor.grid(column=2,row=1,padx=0, pady=0,sticky='EW')
        #------------------------CONFIGURACION SUPER USUARIO-------------------
        barra_configuracion = tkinter.Frame(barra_principal, width=32, height=32, bg = "gray")
        barra_configuracion.grid(column=1, row = 0, padx=0, pady= 0)
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/CONFIGURACION.png")
        self.boton_configuracion = tkinter.Button(barra_configuracion, width=30, height=50, image=icono_configuracion, bg='white', command=self.menu_configuracion)
        self.boton_configuracion.grid(column=0,row=0,padx=0, pady=0)
        self.boton_configuracion.image = icono_configuracion
        #---------------BARRA DE INDICADORES E INFORMACIÒN CONTENDORES---------
        barra_indicador = tkinter.Frame(barra_estado, width=793, height=10, bg = "light gray")
        barra_indicador.grid(column=0, row = 1, padx=0, pady= 0)
        separador = tkinter.Frame(barra_indicador, width=2, height=20, bg = "light gray")
        separador.grid(column=18, row = 0, padx=0, pady= 0)
        #------------------FIGURAS INDICADOR (CÌRCULOS)------------------------
        self.indicador_contendor_1 = Canvas(barra_indicador,width=20, height=20, bg='light gray')
        self.indicador_contendor_1.grid(column=0, row = 0, padx=1, pady= 0)
        self.indicador_contendor_1.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        self.indicador_contendor_2 = Canvas(barra_indicador,width=20, height=20, bg='light gray')
        self.indicador_contendor_2.grid(column=3, row = 0, padx=1, pady= 0)
        self.indicador_contendor_2.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        self.indicador_contendor_3 = Canvas(barra_indicador,width=20, height=20, bg='light gray')
        self.indicador_contendor_3.grid(column=6, row = 0, padx=1, pady= 0)
        self.indicador_contendor_3.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        self.indicador_contendor_4 = Canvas(barra_indicador,width=20, height=20, bg='light gray')
        self.indicador_contendor_4.grid(column=9, row = 0, padx=1, pady= 0)
        self.indicador_contendor_4.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        self.indicador_contendor_5 = Canvas(barra_indicador,width=20, height=20, bg='light gray')
        self.indicador_contendor_5.grid(column=12, row = 0, padx=1, pady= 0)
        self.indicador_contendor_5.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        self.indicador_contendor_6 = Canvas(barra_indicador,width=20, height=20, bg='light gray')
        self.indicador_contendor_6.grid(column=15, row = 0, padx=1, pady= 0)
        self.indicador_contendor_6.create_oval(1, 1, 19, 19, width=1, fill='green')
        #-----------------------TITULOS RESIDUOS-------------------------------
        residuo_contenedor_1 = tkinter.StringVar()
        residuo_contenedor_1.set("PAPEL:")
        nombre_contenedor_1 = tkinter.Label(barra_indicador,textvariable=residuo_contenedor_1,anchor="w",fg="white",bg="blue", width=5,height = 1,font=letra_otros)
        nombre_contenedor_1.grid(column=1,row=0,padx=0, pady=0,sticky='EW')
        
        residuo_contenedor_2 = tkinter.StringVar()
        residuo_contenedor_2.set("METAL:")
        nombre_contenedor_2 = tkinter.Label(barra_indicador,textvariable=residuo_contenedor_2,anchor="w",fg="white",bg="blue", width=7,height = 1,font=letra_otros)
        nombre_contenedor_2.grid(column=4,row=0,padx=0, pady=0,sticky='EW')
        
        residuo_contenedor_3 = tkinter.StringVar()
        residuo_contenedor_3.set("ORGANICO:")
        nombre_contenedor_3 = tkinter.Label(barra_indicador,textvariable=residuo_contenedor_3,anchor="w",fg="white",bg="blue", width=9,height = 1,font=letra_otros)
        nombre_contenedor_3.grid(column=7,row=0,padx=0, pady=0,sticky='EW')
        
        residuo_contenedor_4 = tkinter.StringVar()
        residuo_contenedor_4.set("PLÀSTICO:")
        nombre_contenedor_4 = tkinter.Label(barra_indicador,textvariable=residuo_contenedor_4,anchor="w",fg="white",bg="blue", width=8,height = 1,font=letra_otros)
        nombre_contenedor_4.grid(column=10,row=0,padx=0, pady=0,sticky='EW')
        
        residuo_contenedor_5 = tkinter.StringVar()
        residuo_contenedor_5.set("VIDRIO:")
        nombre_contenedor_5 = tkinter.Label(barra_indicador,textvariable=residuo_contenedor_5,anchor="w",fg="white",bg="blue", width=6,height = 1,font=letra_otros)
        nombre_contenedor_5.grid(column=13,row=0,padx=0, pady=0,sticky='EW')
        
        residuo_contenedor_6 = tkinter.StringVar()
        residuo_contenedor_6.set("OTROS:")
        nombre_contenedor_6 = tkinter.Label(barra_indicador,textvariable=residuo_contenedor_6,anchor="w",fg="white",bg="blue", width=6,height = 1,font=letra_otros)
        nombre_contenedor_6.grid(column=16,row=0,padx=0, pady=0,sticky='EW')
        #---------------------PORCENTAJES DE LOS RESIDUOS----------------------
        self.valor_contenedor_1 = tkinter.Label(barra_indicador,textvariable=self.residuo_1,anchor="w",fg="white",bg="blue", width=5,height = 1,font=letra_otros)
        self.valor_contenedor_1.grid(column=2,row=0,padx=0, pady=0,sticky='EW')
        
        self.valor_contenedor_2 = tkinter.Label(barra_indicador,textvariable=self.residuo_2,anchor="w",fg="white",bg="blue", width=5,height = 1,font=letra_otros)
        self.valor_contenedor_2.grid(column=5,row=0,padx=0, pady=0,sticky='EW')
        
        self.valor_contenedor_3 = tkinter.Label(barra_indicador,textvariable=self.residuo_3,anchor="w",fg="white",bg="blue", width=5,height = 1,font=letra_otros)
        self.valor_contenedor_3.grid(column=8,row=0,padx=0, pady=0,sticky='EW')
        
        self.valor_contenedor_4 = tkinter.Label(barra_indicador,textvariable=self.residuo_4,anchor="w",fg="white",bg="blue", width=5,height = 1,font=letra_otros)
        self.valor_contenedor_4.grid(column=11,row=0,padx=0, pady=0,sticky='EW')
        
        self.valor_contenedor_5 = tkinter.Label(barra_indicador,textvariable=self.residuo_5,anchor="w",fg="white",bg="blue", width=5,height = 1,font=letra_otros)
        self.valor_contenedor_5.grid(column=14,row=0,padx=0, pady=0,sticky='EW')
        
        self.valor_contenedor_6 = tkinter.Label(barra_indicador,textvariable=self.residuo_6,anchor="w",fg="white",bg="blue", width=5,height = 1,font=letra_otros)
        self.valor_contenedor_6.grid(column=17,row=0,padx=0, pady=0,sticky='EW')
        #-------------------IMAGEN DE CAPTURA DE LOS DATOS---------------------
        barra_secundaria = tkinter.Frame(self.fondo, width=300, height=200, bg = "light gray")
        barra_secundaria.grid(column=0, row = 2, padx=1, pady= 0)
        
        barra_camara = tkinter.Frame(barra_secundaria, width=300, height=200, bg = "light gray")
        barra_camara.grid(column=0, row = 0, padx=0, pady= 0)
        self.imagen_camara_c = tkinter.Label(barra_camara)
        self.imagen_camara_c.grid(column=0, row = 0, padx=0, pady= 0)
        self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (555,420), interpolation = cv2.INTER_AREA),1)
        #-------------------IMAGEN DE RESIDUO CLASIFICADO (ROI)----------------
        barra_residuo = tkinter.Frame(barra_secundaria, width=280, height=380, bg = "light gray")
        barra_residuo.grid(column=1, row = 0, padx=1, pady= 1)
        
        barra_clasificacion = tkinter.Frame(barra_residuo, width=280, height=380, bg = "light gray")
        barra_clasificacion.grid(column=0, row = 0, padx=1, pady= 1)
        
        self.imagen_r = tkinter.Label(barra_clasificacion)
        self.imagen_r.grid(column=0, row = 0, padx=0, pady= 0)
        self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (235,165), interpolation = cv2.INTER_AREA),2)
        #-------------------IMAGEN DEL LOGO DEL RESIDUO------------------------
        barra_logo = tkinter.Frame(barra_residuo, width=280, height=380, bg = "light gray")
        barra_logo.grid(column=0, row = 1, padx=1, pady= 1)
        
        self.imagen_l = tkinter.Label(barra_logo)
        self.imagen_l.grid(column=0, row = 0, padx=0, pady= 0)
        self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (235,165), interpolation = cv2.INTER_AREA),3)
        #--------------------TIEMPO DE ESPERA INGRESO--------------------------
        barra_tiempo = tkinter.Frame(barra_residuo, width=280, height=380, bg = "light gray")
        barra_tiempo.grid(column=0, row = 2, padx=0, pady= 0)
        
        self.tiempo = tkinter.StringVar()
        self.tiempo.set("TIEMPO: 00")
        tiempo_espera = tkinter.Label(barra_tiempo,textvariable=self.tiempo,anchor="w",fg="white",bg="blue", width=10,height = 2,font=letra_tiempo)
        tiempo_espera.grid(column=0,row=0,padx=0, pady=0,sticky='EW')
        #------ACTUALIZAR LOS PORCENTAJES DE CAPACIDAD DE LOS CONTENEDORES-----
        self.actualizacion_cantidad_residuos()
        #---------------PASAR A LOOP DE ACTUALIZACIÒN DE LA INTERFAZ-----------
        self.actualizar()
###############################################################################
###############################################################################
#---------------------LOOP DE ACTUALIZACIÒN DE LA INTERFAZ---------------------
    def actualizar(self):
        #--------------------ACTUALIZACIÒN DE LA HORA--------------------------
        hora_actual = datetime.now()
        hora_a = hora_actual.strftime(""+str(hora_actual.year)+"/%m/%d-%H:%M:%S")
        self.hora.set("HORA Y FECHA: "+hora_a)
        #----------ACTUALIZACIÒN DE DATOS DE LOS CONTENEDORES------------------
        if(hora_actual.minute % 1  == 0 and self.bandera_c is False):
            self.seg_ant_c = hora_actual.minute
            self.bandera_c = True
            self.actualizacion_cantidad_residuos()
        if(self.seg_ant_c != hora_actual.minute):
            self.bandera_c = False
        #-------------------VERIFICAR CONEXIÒN A INTERNET----------------------
        if(hora_actual.minute % 1 == 0 and self.bandera_i is False):
            self.seg_ant_i = hora_actual.minute
            self.bandera_i = True
            self.verificar_conexion_internet()
        if(self.seg_ant_i != hora_actual.minute):
            self.bandera_i = False
        #-----------------------LECTURA DE LA IMAGEN---------------------------
        if(sensor.LeerSensor() is True and self.bandera_s is False):
            self.bandera_s = True
            self.seg_ant_r = hora_actual.second
        try:
            if(self.bandera_s is True and self.detectado is False and self.menu is False):
                self.frame = self.vs.read()
                (fH, fW) = self.frame.shape[:2]
                #------------------ACTUALIZAR IMAGENES INTERFAZ------------------------
                self.actualizar_imagen(cv2.resize(self.frame, (555,420), interpolation = cv2.INTER_AREA),1)
            #-----------------RESPUESTA DE LA RED CONVOLUCIONAL--------------------
                if(self.seg_ant_r != hora_actual.second):
                    self.tiempo_toma-=1
                    self.seg_ant_r = hora_actual.second
            #------------------NO SE DETECTO RESIDUO RECICLABLE--------
                if(self.contador_tomas > 3 and self.detectado is False):
                    self.detectado = True
                    self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/GENERAL.png"), (235,165), interpolation = cv2.INTER_AREA),3)
                    self.reproducir_audio(12)
                    if(PORCENTAJES[12] < 95):
                        if(comunicacion_contenedor.publicar("contenedor/otros") is False):
                            self.estado_contenedor.set(u"FALLO DE CONEXIÓN A CONTENEDORES")    
                        else:
                            self.estado_contenedor.set(u"ESTADO DEL CONTENDOR E INFORMACIÓN DE FALLOS")
                    else:
                        #------------------CONTENDOR OTROS LLENO-----------
                        time.sleep(5)
                        self.reproducir_audio(13)
                        self.ventana_contenedor_lleno()
                        
                if(self.tiempo_toma == 0 and self.contador_tomas < 3):
                    self.contador_tomas+=1
                    self.tiempo_toma = 3
                    #---------------------EJECUCION MODELO---------------------
                    if inputQueue.empty():
                        inputQueue.put(self.frame)
                    if not outputQueue.empty():
                        self.detections = outputQueue.get()
                        
                    if self.detections is not None and self.detectado is False and self.contador_tomas != 1:
                        #---------LOGICA DE LA CLASIFICACIÒN-------------------
                        roi = self.frame
                        for i in np.arange(0, self.detections.shape[2]):
                            confidence = self.detections[0, 0, i, 2]
                            if confidence < 0.98:
                                continue
                            idx = int(self.detections[0, 0, i, 1])
                            dims = np.array([fW, fH, fW, fH])
                            box = self.detections[0, 0, i, 3:7] * dims
                            (startX, startY, endX, endY) = box.astype("int")
                            label = "{}: {:.2f}%".format(CLASSES[idx],confidence * 100)
                            cv2.rectangle(roi, (startX, startY), (endX, endY),COLORS[idx], 2)
                            startY = startY - 15 if startY - 15 > 15 else startY + 15
                            cv2.putText(self.frame, label, (startX, startY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                            #----------------ROI DE LA IMAGEN----------------------
                            self.indices.append(idx)
                            self.cajas.append(box)
                            self.tipo.append(TIPO[idx])
                            self.valores.append(confidence * 100)
                            self.actualizar_imagen(cv2.resize(roi, (235,165), interpolation = cv2.INTER_AREA),2)
                        
                    if(len(self.indices) >= 1):
                        self.detectado = True
                        imagen_todos = self.frame
                        for x in tipos:
                            imagen_copia = self.frame
                            encontrado = False
                            for i in range(0,len(self.tipo)):
                                if(x == self.tipo[i]):
                                    encontrado = True
                                    box = self.cajas[i]
                                    idx = self.indices[i]
                                    (startX, startY, endX, endY) = box.astype("int")
                                    cv2.rectangle(imagen_copia, (startX, startY), (endX, endY),COLORS[idx], 2)
                                    label = "{}: {:.2f}%".format(x,self.valores[i])
                                    startY = startY - 15 if startY - 15 > 15 else startY + 15
                                    cv2.putText(imagen_copia, label, (startX, startY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                                    cv2.putText(imagen_todos, label, (startX, startY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
                                    self.actualizar_imagen(cv2.resize(imagen_copia, (555,420), interpolation = cv2.INTER_AREA),1)
                            if(encontrado == True):
                                if x == "papel/carton":
                                    index = 4
                                elif x == "metal":
                                    index = 6
                                elif x == "plastico":
                                    index = 2
                                elif x == "vidrio":
                                    index = 3
                                elif x == "organico":
                                    index = 1
                                else:
                                    pass
                                self.actualizar_imagen(cv2.resize(cv2.imread(ruta+IMAGES[index]), (235,165), interpolation = cv2.INTER_AREA),3)
                                self.reproducir_audio(index)
                                if(PORCENTAJES[index] < 95):
                                    if(comunicacion_contenedor.publicar(TOPICS[index]) is False):
                                        self.estado_contenedor.set(u"FALLO DE CONEXIÓN A CONTENEDORES")    
                                    else:
                                        self.estado_contenedor.set(u"ESTADO DEL CONTENDOR E INFORMACIÓN DE FALLOS")
                                else:
                                    #------------------CONTENEDOR LLENO----------------
                                    time.sleep(5)
                                    self.reproducir_audio(13)
                                    self.ventana_contenedor_lleno()
                                time.sleep(10)
                                    
                        self.actualizar_imagen(cv2.resize(imagen_todos, (555,420), interpolation = cv2.INTER_AREA),1)
            #---------------------RESIDUO RECICLABLE DETECTADO-----------------            
            if self.detectado is True:
                self.tiempo.set("TIEMPO: "+str(self.tiempo_espera))
                seg_act = hora_actual.second
                if (seg_act != self.seg_ant):
                    self.tiempo_espera-=1
                    self.seg_ant = seg_act
                if(self.tiempo_espera == 0):
                    self.detectado = False
                    self.detections = None
                    self.indices = []
                    self.valores = []
                    self.tiempo.set("TIEMPO: 00")
                    self.tiempo_espera = 30
                    self.bandera_s = False
                    self.contador_tomas = 0
                    self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (555,420), interpolation = cv2.INTER_AREA),1)
                    self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (235,165), interpolation = cv2.INTER_AREA),2)
                    self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (235,165), interpolation = cv2.INTER_AREA),3)
                    if(self.contenedor_lleno is True):
                        self.ventana_lleno.withdraw()
                        self.contenedor_lleno = False
        except:
            self.estado_contenedor.set(u"MALA CONEXIÓN O DAÑO DE LA CÁMARA")
        #----------------------------FIN LOOP----------------------------------
        self.after(1, self.actualizar)
###############################################################################

    def actualizacion_cantidad_residuos(self):
        #--------------------ACTUALIZACIÒN DE INDICADORES----------------------
        cantidad, estado = self.leer_valores(ruta+"MEDIDA_CONTENEDORES/CPC.txt")
        self.residuo_1.set(self.calcular_porcentaje(cantidad,1)+"%")
        if(estado == "*"):
            self.indicador_contendor_1.create_oval(1, 1, 19, 19, width=1, fill='red')
        else:
            self.indicador_contendor_1.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        cantidad, estado = self.leer_valores(ruta+"MEDIDA_CONTENEDORES/CM.txt")
        self.residuo_2.set(self.calcular_porcentaje(cantidad,2)+"%")
        if(estado == "*"):
            self.indicador_contendor_2.create_oval(1, 1, 19, 19, width=1, fill='red')
        else:
            self.indicador_contendor_2.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        cantidad, estado = self.leer_valores(ruta+"MEDIDA_CONTENEDORES/COR.txt")
        self.residuo_3.set(self.calcular_porcentaje(cantidad,3)+"%")
        if(estado == "*"):
            self.indicador_contendor_3.create_oval(1, 1, 19, 19, width=1, fill='red')
        else:
            self.indicador_contendor_3.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        cantidad, estado = self.leer_valores(ruta+"MEDIDA_CONTENEDORES/CP.txt")
        self.residuo_4.set(self.calcular_porcentaje(cantidad,4)+"%")
        if(estado == "*"):
            self.indicador_contendor_4.create_oval(1, 1, 19, 19, width=1, fill='red')
        else:
            self.indicador_contendor_4.create_oval(1, 1, 19, 19, width=1, fill='green')
            
        cantidad, estado = self.leer_valores(ruta+"MEDIDA_CONTENEDORES/CV.txt")
        self.residuo_5.set(self.calcular_porcentaje(cantidad,5)+"%")
        if(estado == "*"):
            self.indicador_contendor_5.create_oval(1, 1, 19, 19, width=1, fill='red')
        else:
            self.indicador_contendor_5.create_oval(1, 1, 19, 19, width=1, fill='green')
        
        cantidad, estado = self.leer_valores(ruta+"MEDIDA_CONTENEDORES/CO.txt")
        self.residuo_6.set(self.calcular_porcentaje(cantidad,6)+"%")
        if(estado == "*"):
            self.indicador_contendor_6.create_oval(1, 1, 19, 19, width=1, fill='red')
        else:
            self.indicador_contendor_6.create_oval(1, 1, 19, 19, width=1, fill='green')
                
    def verificar_conexion_internet(self):
        if(comunicacion_contenedor.sondeo() == True):
            self.estado_internet.set("CONEXIÓN A INTERNET: SI")
        else:
            self.estado_internet.set("CONEXIÓN A INTERNET: NO")
            
    def verificar_conexion_camara(self):
        if(self.inicio_camara == False):
            self.estado_contenedor.set("ALERTA: CÁMARA CON MAL FUNCIONAMIENTO")
            
    def leer_valores(self,archivo):
        f = open(archivo)
        linea = f.readline()
        f.close()
        linea = linea.replace("\n","")
        linea = linea.split(",")
        return (linea[0],linea[1])
    
    def calcular_porcentaje(self,valor_volumen,contenedor):
        volumen_max = 0.121
        porcentaje = round((float(valor_volumen)*100/volumen_max),2)
        if(contenedor == 1):
            PORCENTAJES[4] = porcentaje
            PORCENTAJES[5] = porcentaje
            PORCENTAJES[7] = porcentaje
        elif(contenedor == 2):
            PORCENTAJES[6] = porcentaje
        elif(contenedor == 3):
            PORCENTAJES[1] = porcentaje
            PORCENTAJES[8] = porcentaje
            PORCENTAJES[9] = porcentaje
            PORCENTAJES[10] = porcentaje
            PORCENTAJES[11] = porcentaje
        elif(contenedor == 4):
            PORCENTAJES[2] = porcentaje
        elif(contenedor == 5):
            PORCENTAJES[3] = porcentaje
        elif(contenedor == 6):
            PORCENTAJES[12] = porcentaje
        else:
            pass
        return str(porcentaje)
        
    def reproducir_audio(self,audio):
        f = open(ruta+"SONIDOS/REPRODUCIR.txt",'w+')
        f.write(str(audio))
        f.close()
#-----------------VENTANA DE CONTENEDOR LLENO----------------------------------
    def ventana_contenedor_lleno(self):
        self.contenedor_lleno = True
        self.ventana_lleno = tkinter.Toplevel()
        self.ventana_lleno.config(bg="red", cursor="none")
        self.ventana_lleno.title("CONTENDOR LLENO")
        ancho_ventana = 450
        alto_ventana = 150
        self.ventana_lleno.geometry("%dx%d+%d+%d"%(ancho_ventana,alto_ventana,50,150))
        self.ventana_lleno.resizable(False,False)
        self.ventana_lleno.overrideredirect(True)        
        letra_error = font.Font(family='Helvetica', size=35, weight=font.BOLD)        
        fondo = tkinter.Frame(self.ventana_lleno, width=300, height=480, bg = "red")
        fondo.grid(column=0, row = 0, padx=5, pady=5)
        fondo_1 = tkinter.Frame(fondo, width=200, height=80, bg = "red")
        fondo_1.grid(column=0, row = 0, padx=10, pady=10)
        label = tkinter.Label(fondo_1,text= u"CONTENEDOR \nLLENO",anchor="w",fg="white",bg='black',font=letra_error)
        label.grid(column=0,row=0,sticky='EW', padx=30, pady= 5)
        
    def menu_configuracion(self):
        self.boton_configuracion.config(state="disabled")
        self.menu = True
        #self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (555,420), interpolation = cv2.INTER_AREA),1)
        #self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (235,165), interpolation = cv2.INTER_AREA),2)
        #self.actualizar_imagen(cv2.resize(cv2.imread(ruta+"IMAGENES/LOGO_EMPRESA.png"), (235,165), interpolation = cv2.INTER_AREA),3)
        self.ventana = tkinter.Toplevel()
        self.ventana.config(bg="blue", cursor="none")
        self.ventana.title("INGRESO DE CONTRASENA")
        ancho_ventana = 215
        alto_ventana = 90
        self.ventana.geometry("%dx%d+%d+%d"%(ancho_ventana,alto_ventana,150,200))
        self.ventana.resizable(False,False)
        self.ventana.overrideredirect(True)
        fondo = tkinter.Frame(self.ventana, width=300, height=480, bg = "gray")
        fondo.grid(column=0, row = 0, padx=5, pady=5)
        fondo_1 = tkinter.Frame(fondo, width=200, height=100, bg = "gray")
        fondo_1.grid(column=0, row = 1, padx=10, pady=10)
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/UNO.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.uno)
        boton_configuracion.grid(column=0,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/DOS.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.dos)
        boton_configuracion.grid(column=1,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/TRES.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.tres)
        boton_configuracion.grid(column=2,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/CERRAR.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.cerrar_menu)
        boton_configuracion.grid(column=3,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        
    def menu_opciones(self):
        self.ventana_menu = tkinter.Toplevel()
        self.ventana_menu.config(bg="blue", cursor="none")
        self.ventana_menu.title("OPCIONES SISTEMA")
        ancho_ventana = 215
        alto_ventana = 90
        self.ventana_menu.geometry("%dx%d+%d+%d"%(ancho_ventana,alto_ventana,150,200))
        self.ventana_menu.resizable(False,False)
        self.ventana_menu.overrideredirect(True)
        fondo = tkinter.Frame(self.ventana_menu, width=300, height=480, bg = "gray")
        fondo.grid(column=0, row = 0, padx=5, pady=5)
        fondo_1 = tkinter.Frame(fondo, width=200, height=100, bg = "gray")
        fondo_1.grid(column=0, row = 1, padx=10, pady=10)
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/INICIO.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.cerrar_interfaz)
        boton_configuracion.grid(column=0,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/REINICIAR.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.reiniciar)
        boton_configuracion.grid(column=1,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/APAGAR.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.apagar)
        boton_configuracion.grid(column=2,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        icono_configuracion = tkinter.PhotoImage(file=ruta+"IMAGENES/CERRAR.png")
        boton_configuracion = tkinter.Button(fondo_1, width=30, height=50, image=icono_configuracion, bg='white', command=self.cerrar_menu)
        boton_configuracion.grid(column=3,row=0,padx=5, pady=1)
        boton_configuracion.image = icono_configuracion
        
    def uno(self):
        self.contrasena+="1"
        self.validar_contrasena()
    def dos(self):
        self.contrasena+="2"
        self.validar_contrasena()
    def tres(self):
        self.contrasena+="3"
        self.validar_contrasena()
    def validar_contrasena(self):
        if(len(self.contrasena) >= 4):
            if(self.contrasena == "2213"):
                #Abrir otra ventana para apagar o reiniciar
                self.ventana.withdraw()
                self.menu_opciones()
                self.contrasena = ""
            else:
                self.contrasena = ""
                
    def cerrar_menu(self):
        self.menu = False
        self.boton_configuracion.config(state="active")
        self.contrasena = ""
        try:
            self.ventana.withdraw()
        except:
            pass
        try:
            self.ventana_menu.withdraw()
        except:
            pass
        
#----------------ACTUALIZACIÒN DE IMAGEN EN LA INTERFAZ------------------------
    def actualizar_imagen(self,toma,opcion):
        b,g,r = cv2.split(toma)
        gray_im = cv2.merge((r,g,b))
        a = Image.fromarray(gray_im)
        b = ImageTk.PhotoImage(image=a)
        if(opcion == 1):
            self.imagen_camara_c.configure(image=b)
            self.imagen_camara_c._image_cache = b
        if(opcion == 2):
            self.imagen_r.configure(image=b)
            self.imagen_r._image_cache = b
        if(opcion == 3):
            self.imagen_l.configure(image=b)
            self.imagen_l._image_cache = b

#-----------------------CERRAR INTERFAZ----------------------------------------
    def cerrar_interfaz(self):     
        try:
            self.vs.stop()
        except:
            pass
        self.destroy()
        
    def reiniciar(self):
        self.cerrar_interfaz()
        print("Reiniciando...")
        os.system("reboot");
    
    def apagar(self):
        self.cerrar_interfaz()
        print("Apagando...")
        os.system("shutdown now");
        
#--------------------CREACION DE LA VENTANA PRINCIPAL--------------------------
if __name__ == "__main__":
    app = Interfaz_grafica_usuario(None)
    app.title('PROGRAMA DE IDENTIFACIÓN DE RESIDUOS RECICLABLES')
    ancho_ventana = 800
    alto_ventana = 480
    app.geometry("%dx%d+%d+%d"%(ancho_ventana,alto_ventana,0,0))
    app.resizable(False,False)
    app.overrideredirect(True)
    app.config(bg= "black", cursor="none")
    app.mainloop()
#-------------------------FIN DEL PROGRAMA-------------------------------------
###############################################################################
###############################################################################
        #########           ###########                ###########            
        #        #      @        #                          # 
        #        #               #                          #
        #        #      #        #         #########        #
        #########       #        #        #         #       #
        #        #      #        #        #         #       #
        #        #      #        #        #         #       #
        #        #      #        #        #         #       #
        #########       #   ###########    #########        #
###############################################################################
###############################################################################
