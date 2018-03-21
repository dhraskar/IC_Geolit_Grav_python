# -*- coding: utf-8 -*-

#--------------------------------------------------
#Import das bibliotecas
#--------------------------------------------------
import numpy as np
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
from tkinter import *
from datetime import datetime
from math import sqrt, atan, asin, acos, sin, cos, radians



#--------------------------------------------------
#Ambiente Correção de Maré por John Leeman
#--------------------------------------------------
# PT----------------------------------------------------------------
            
# Código de cálculo de  séculos julianos e  Correção de Maré Terrestre
# por John Leeman  (contato: <john@leemangeophysical.com> )
# disponível em: <https://github.com/jrleeman/LongmanTide>


# EN----------------------------------------------------------------

# Code of calculation of Julian centuries and Earth Tidal Correction
# by John Leeman  (contact: <john@leemangeophysical.com>  )
# available at: <https://github.com/jrleeman/LongmanTide>

"""
This part of the code provided by John Leeman uses the MIT License, which is written just below:

+MIT License
 +
 +Copyright (c) 2017 John Leeman
 +
 +Permission is hereby granted, free of charge, to any person obtaining a copy
 +of this software and associated documentation files (the "Software"), to deal
 +in the Software without restriction, including without limitation the rights
 +to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 +copies of the Software, and to permit persons to whom the Software is
 +furnished to do so, subject to the following conditions:
 +
 +The above copyright notice and this permission notice shall be included in all
 +copies or substantial portions of the Software.
 +
 +THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 +IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 +FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 +AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 +LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 +OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 +SOFTWARE.
"""           

class TideModel():
    def calculate_julian_century(self, timestamp):
        """
        Take a datetime object and returns the decimal Julian century and
        floating point hour. This is in reference to noon on December 31,
        1899 as stated in the paper.
        """
        origin_date = datetime(1899, 12, 31, 12, 00, 00)  # Noon Dec 31, 1899
        dt = timestamp - origin_date
        days = dt.days + dt.seconds/3600./24.
        return days/36525, timestamp.hour + timestamp.minute/60. + timestamp.second/3600.

    def solve_longman(self, lat, lon, alt, time):
        """
        Given the location and datetime object, computes the current
        gravitational tide and associated quantities. Latitude and longitude
        and in the traditional decimal notation, altitude is in meters, time
        is a datetime object.
        """

        T, t0 = self.calculate_julian_century(time)

        if t0 < 0:
            t0 += 24.
        if t0 >= 24:
            t0 -= 24.

        mu = 6.673e-8  # Newton's gravitational constant
        M = 7.3537e25  # Mass of the moon in grams
        S = 1.993e33  # Mass of the sun in grams
        e = 0.05490  # Eccentricity of the moon's orbit
        m = 0.074804  # Ratio of mean motion of the sun to that of the moon
        c = 3.84402e10  # Mean distance between the centers of the earth and the moon
        c1 = 1.495e13  # Mean distance between centers of the earth and sun in cm
        h2 = 0.612  # Love parameter
        k2 = 0.303  # Love parameter
        a = 6.378270e8  # Earth's equitorial radius in cm
        i = 0.08979719  # (i) Inclination of the moon's orbit to the ecliptic
        omega = radians(23.452)  # Inclination of the Earth's equator to the ecliptic 23.452 degrees
        L = -1 * lon  # For some reason his lat/lon is defined with W as + and E as -
        lamb = radians(lat)  # (lambda) Latitude of point P
        H = alt * 100.  # (H) Altitude above sea-level of point P in cm

        # Lunar Calculations
        # (s) Mean longitude of moon in its orbit reckoned from the referred equinox
        s = 4.72000889397 + 8399.70927456 * T + 3.45575191895e-05 * T * T + 3.49065850399e-08 * T * T * T
        # (p) Mean longitude of lunar perigee
        p = 5.83515162814 + 71.0180412089 * T + 0.000180108282532 * T * T + 1.74532925199e-07 * T * T * T
        # (h) Mean longitude of the sun
        h = 4.88162798259 + 628.331950894 * T + 5.23598775598e-06 * T * T
        # (N) Longitude of the moon's ascending node in its orbit reckoned from the referred equinox
        N = 4.52360161181 - 33.757146295 * T + 3.6264063347e-05 * T * T +  3.39369576777e-08 * T * T * T
        # (I) Inclination of the moon's orbit to the equator
        I = acos(cos(omega)*cos(i) - sin(omega)*sin(i)*cos(N))
        # (nu) Longitude in the celestial equator of its intersection A with the moon's orbit
        nu = asin(sin(i)*sin(N)/sin(I))
        # (t) Hour angle of mean sun measured west-ward from the place of observations
        t = radians(15. * (t0 - 12) - L)

        # (chi) right ascension of meridian of place of observations reckoned from A
        chi = t + h - nu
        # cos(alpha) where alpha is defined in eq. 15 and 16
        cos_alpha = cos(N)*cos(nu)+sin(N)*sin(nu)*cos(omega)
        # sin(alpha) where alpha is defined in eq. 15 and 16
        sin_alpha = sin(omega)*sin(N)/sin(I)
        # (alpha) alpha is defined in eq. 15 and 16
        alpha = 2*atan(sin_alpha/(1+cos_alpha))
        # (xi) Longitude in the moon's orbit of its ascending intersection with the celestial equator
        xi = N-alpha

        # (sigma) Mean longitude of moon in radians in its orbit reckoned from A
        sigma = s - xi
        # (l) Longitude of moon in its orbit reckoned from its ascending intersection with the equator
        l = sigma + 2*e*sin(s-p)+(5./4)*e*e*sin(2*(s-p)) + (15./4)*m*e*sin(s-2*h+p) + (11./8)*m*m*sin(2*(s-h))

        # Sun
        # (p1) Mean longitude of solar perigee
        p1 = 4.90822941839 + 0.0300025492114 * T +  7.85398163397e-06 * T * T + 5.3329504922e-08 * T * T * T
        # (e1) Eccentricity of the Earth's orbit
        e1 = 0.01675104-0.00004180*T - 0.000000126*T*T
        # (chi1) right ascension of meridian of place of observations reckoned from the vernal equinox
        chi1 = t+h
        # (l1) Longitude of sun in the ecliptic reckoned from the vernal equinox
        l1 = h + 2*e1*sin(h-p1)
        # cosine(theta) Theta represents the zenith angle of the moon
        cos_theta = sin(lamb)*sin(I)*sin(l) + cos(lamb)*(cos(0.5*I)**2 * cos(l-chi) + sin(0.5*I)**2 * cos(l+chi))
        # cosine(phi) Phi represents the zenith angle of the run
        cos_phi = sin(lamb)*sin(omega)*sin(l1) + cos(lamb)*(cos(0.5*omega)**2 * cos(l1-chi1)+sin(0.5*omega)**2*cos(l1+chi1))

        # Distance
        # (C) Distance parameter, equation 34
        C = sqrt(1./(1+0.006738*sin(lamb)**2))
        # (r) Distance from point P to the center of the Earth
        r = C*a + H
        # (a') Distance parameter, equation 31
        aprime = 1./(c*(1-e*e))
        # (a1') Distance parameter, equation 31
        aprime1 = 1./(c1*(1-e1*e1))
        # (d) Distance between centers of the Earth and the moon
        d = 1./((1./c) + aprime*e*cos(s-p)+aprime*e*e*cos(2*(s-p)) + (15./8)*aprime*m*e*cos(s-2*h+p) + aprime*m*m*cos(2*(s-h)))
        # (D) Distance between centers of the Earth and the sun
        D = 1./((1./c1) + aprime1*e1*cos(h-p1))

        # (gm) Vertical componet of tidal acceleration due to the moon
        gm = (mu*M*r/(d*d*d))*(3*cos_theta**2-1) + (3./2)*(mu*M*r*r/(d*d*d*d))*(5*cos_theta**3 - 3*cos_theta)
        # (gs) Vertical componet of tidal acceleration due to the sun
        gs = mu*S*r/(D*D*D) * (3*cos_phi**2-1)

        love = (1+h2-1.5*k2)
        g0 = (gm+gs)*1e3*love
        return g0

#--------------------------------------------------
#Ambiente Tkinter
#--------------------------------------------------
class Packing:
    def __init__(self, toplevel):
        self.frame=Frame(toplevel).grid()

        
        #Variáveis de entrada      
        self.var_tipo=StringVar(toplevel)
        self.var_tipo.set('excel')
        self.var_aba=StringVar(toplevel)
        self.var_aba.set('Plan1')
        self.var_entrada=StringVar(toplevel)
        self.var_entrada.set('GRARED_P_exemplo.xlsx')
        self.var_conv=StringVar(toplevel)
        self.var_conv.set('Tab_conv_G996.txt')

        self.var_dia=DoubleVar(toplevel)
        self.var_dia.set(int(1))
        self.var_mes=DoubleVar(toplevel)
        self.var_mes.set(int(1))
        self.var_ano=DoubleVar(toplevel)
        self.var_ano.set(int(2017))
        self.var_fuso_horario=DoubleVar(toplevel)
        self.var_fuso_horario.set(int(-3))
        self.var_densidade=DoubleVar(toplevel)
        self.var_densidade.set(float(2.67))
        self.var_acel_absoluta=DoubleVar(toplevel)

        self.var_free_air=IntVar(toplevel)
        self.var_free_air.set(int(1))
        self.var_bouguer=IntVar(toplevel)
        self.var_bouguer.set(int(1))

        self.var_elipsoide=StringVar(toplevel)
        self.var_elipsoide.set('grs84')

        self.var_saida_txt=StringVar(toplevel)
        self.var_saida_txt.set('dados_reduzidos.dat')
        self.var_saida_excel=StringVar(toplevel)
        self.var_saida_excel.set('dados_reduzidos.xlsx')

        #ENTRADA DE DADOS
        #*******************************************************************************
        self.T_entrada_de_dados=Label(self.frame,font=('Arial','10','bold','underline'),
                                     text='Entrada de dados')
        self.T_entrada_de_dados.grid(row=0,column=11,columnspan=9,sticky=S,pady=27)
        
        self.T_tipo_arquivo_entrada=Label(self.frame,font=('Arial','10','bold'),
                          text='Tipo de Arquivo: ')
        self.T_tipo_arquivo_entrada.grid(row=1,column=0,columnspan=4,rowspan=2,sticky=E)
        def muda_valor_aba_excel():
            self.var_aba.set('Plan1')
            self.var_entrada.set('GRARED_P_exemplo.xlsx')
        def muda_valor_aba_txt():
            self.var_aba.set('-------------Não Há--------------')
            self.var_entrada.set('GRARED_P_exemplo.txt')
        self.RB_excel=Radiobutton(self.frame, text='Excel', value='excel', variable=self.var_tipo, command=muda_valor_aba_excel)
        self.RB_excel.grid(row=1,column=4,columnspan=4,sticky=W)
        self.RB_txt=Radiobutton(self.frame, text='DAT/TXT', value='txt', variable=self.var_tipo, command=muda_valor_aba_txt)
        self.RB_txt.grid(row=2,column=4,columnspan=4,sticky=W)
        self.T_entrada=Label(self.frame, font=('Arial','10','bold'), text='Arquivo de dados:')
        self.T_entrada.grid(row=1,column=8,columnspan=4,sticky=E)
        self.E_entrada=Entry(self.frame, width=30,textvar=self.var_entrada)
        self.E_entrada.grid(row=1,column=12,columnspan=6,sticky=W)
        self.T_aba=Label(self.frame, font=('Arial','10','bold'), text='Se excel, qual aba?')
        self.T_aba.grid(row=2,column=8,columnspan=4,sticky=E)
        self.E_aba=Entry(self.frame, width=30,textvar=self.var_aba)
        self.E_aba.grid(row=2,column=12,columnspan=6,sticky=W)
  
        self.T_conv=Label(self.frame, font=('Arial','10','bold'), text='    Tabela de Conversão:')
        self.T_conv.grid(row=1,column=18,columnspan=4,rowspan=2,sticky=E)
        self.E_conv=Entry(self.frame, width=30,textvar=self.var_conv)
        self.E_conv.grid(row=1,column=22,columnspan=6,rowspan=2,sticky=E,padx=15)

        #DADOS DO LEVANTAMENTO
        #********************************************************************
        self.T_dados_do_l=Label(self.frame,font=('Arial','10','bold','underline'),
                        text='Dados do levantamento')
        self.T_dados_do_l.grid(row=3,column=11,columnspan=9,sticky=S,pady=27)
        #Dia
        self.T_dia=Label(self.frame,font=('Arial','10','bold'),
                        text='Dia')
        self.T_dia.grid(row=4,column=2,rowspan=2)
        self.E_dia=Entry(self.frame, width=4, textvar=self.var_dia)
        self.E_dia.grid(row=6,column=2)

        #Mes
        self.T_mes=Label(self.frame,font=('Arial','10','bold'),
                        text='Mês')
        self.T_mes.grid(row=4,column=3,rowspan=2)
        self.E_mes=Entry(self.frame, width=4, textvar=self.var_mes)
        self.E_mes.grid(row=6,column=3)

        #Ano
        self.T_ano=Label(self.frame,font=('Arial','10','bold'),
                        text='Ano')
        self.T_ano.grid(row=4,column=4,columnspan=2,rowspan=2)
        self.E_ano=Entry(self.frame, width=6, textvar=self.var_ano)
        self.E_ano.grid(row=6,column=4,columnspan=2)

        #Fuso-Horário
        self.T_fuso=Label(self.frame,font=('Arial','10','bold'),
                        text='Fuso')
        self.T_fuso.grid(row=4,column=8,columnspan=2)
        self.T_horario=Label(self.frame,font=('Arial','10','bold'),
                        text='Horário')
        self.T_horario.grid(row=5,column=8,columnspan=2)
        self.E_fuso_horario=Entry(self.frame, width=5, textvar=self.var_fuso_horario)
        self.E_fuso_horario.grid(row=6,column=8,sticky=E)

        #Densidade crustal local
        self.T_densidade=Label(self.frame,font=('Arial','10','bold'),
                        text='Densidade')
        self.T_densidade.grid(row=4,column=11,columnspan=3)
        self.T_crustal=Label(self.frame,font=('Arial','10','bold'),
                        text='Crust. (cgs)')
        self.T_crustal.grid(row=5,column=11,columnspan=3)
        self.E_densidade=Entry(self.frame, width=6, textvar=self.var_densidade)
        self.E_densidade.grid(row=6,column=11,columnspan=3)


        #Aceleração grav. absoluta da Primeira estação
        self.T_acel_absoluta=Label(self.frame,font=('Arial','10','bold'),
                        text='Aceleração grav. absoluta da Primeira estação (mGal)')
        self.T_acel_absoluta.grid(row=4,column=19,columnspan=9,rowspan=2, padx=10)
        self.E_acel_absoluta=Entry(self.frame, textvar=self.var_acel_absoluta)
        self.E_acel_absoluta.grid(row=6,column=19,columnspan=9)

        #ESCOLHA DAS CORREÇÕES
        #********************************************************************
        self.T_edas=Label(self.frame,font=('Arial','10','bold','underline'),
                        text='Escolha das correções')
        self.T_edas.grid(row=7,column=11,columnspan=9,sticky=S,pady=27)

        self.CB_free_air=Checkbutton(text='Free-Air', var=self.var_free_air)
        self.CB_free_air.grid(row=8,column=10,columnspan=4,sticky=N,pady=15)
        self.CB_bouguer=Checkbutton(text='Bouguer Simples', var=self.var_bouguer)
        self.CB_bouguer.grid(row=8,column=17,columnspan=5,sticky=N,pady=15)             

        self.T_elipsoide=Label(self.frame, font=('Arial','10','bold'), text='Elipsoide de referência:')
        self.T_elipsoide.grid(row=9,column=8,columnspan=6)
        self.RB_grs67=Radiobutton(self.frame, text='GRS67', value='grs67', variable=self.var_elipsoide)
        self.RB_grs67.grid(row=9,column=13,columnspan=3)
        self.RB_grs80=Radiobutton(self.frame, text='GRS80', value='grs80', variable=self.var_elipsoide)
        self.RB_grs80.grid(row=9,column=17,columnspan=3)
        self.RB_grs84=Radiobutton(self.frame, text='GRS84', value='grs84', variable=self.var_elipsoide)
        self.RB_grs84.grid(row=9,column=21,columnspan=3)

        #SAÍDA DOS DADOS
        #********************************************************************        
        self.T_erdas=Label(self.frame,font=('Arial','10','bold','underline'),
                        text='Saída de dados')
        self.T_erdas.grid(row=10,column=11,columnspan=9,sticky=S,pady=27)

        self.T_saida_txt=Label(self.frame, font=('Arial','10','bold'),text='Saída DAT/TXT:')
        self.T_saida_txt.grid(row=11,column=5, columnspan=3)
        self.E_saida_txt=Entry(self.frame, width=30,textvar=self.var_saida_txt)
        self.E_saida_txt.grid(row=11,column=8, columnspan=6)
        self.T_saida_excel=Label(self.frame, font=('Arial','10','bold'),text='Saída Excel:')
        self.T_saida_excel.grid(row=11,column=15, columnspan=3)
        self.E_saida_excel=Entry(self.frame, width=30,textvar=self.var_saida_excel)
        self.E_saida_excel.grid(row=11,column=18, columnspan=6)
            #_______________________________________
            #_______________________________________        
        def gerar_saida():
            #Captura das informações da GUI
            tipo_arquivo=self.var_tipo.get()
            aba=self.var_aba.get()
            nome_arquivo=self.E_entrada.get()
            planilha_conv=self.var_conv.get()

            dia=float(self.E_dia.get())
            mes=float(self.E_mes.get())
            ano=float(self.E_ano.get())
            fuso_horario=float(self.E_fuso_horario.get())
            densidade=float(self.E_densidade.get())
            g_ref=float(self.E_acel_absoluta.get())

            wx_free_air=int(self.var_free_air.get())
            wx_bouguer=int(self.var_bouguer.get())
            elipsoide=self.var_elipsoide.get()
            
            saida_txt=self.E_saida_txt.get()
            saida_excel=self.E_saida_excel.get()

            
            #Importação condicional da tabela de dados
            if tipo_arquivo=='excel':
                planilha_entrada=nome_arquivo 

                p_mat_ler = pd.read_excel(planilha_entrada, sheetname=aba,header=None,skiprows=2,dtype=float) #Leitura interna da planilha
                p_matriz=p_mat_ler.values.T #Salvamento da planilha lida em matriz transposta de arrays

                ponto = p_matriz[0]#Identificador do ponto
                g_l1= p_matriz[1]#Primeira Leitura
                g_l2= p_matriz[2]#Segunda Leitura
                g_l3= p_matriz[3]#Terceira Leitura

                hora = p_matriz[4]#Hora Local da leitura
                minuto = p_matriz[5]#Minuto Local da leitura

                h_instrumento=p_matriz[6]

                Lat_gra = p_matriz[7]#Latitude Graus
                Lat_min = p_matriz[8]#Latitude Minutos
                Lat_seg = p_matriz[9]#Latitude segundos

                Lon_gra = p_matriz[10]#Longitude Graus
                Lon_min = p_matriz[11]#Longitude Minutos
                Lon_seg = p_matriz[12]#Longitude segundos
    
                alt_m = p_matriz[13]#Altitude geométrica obtida pelos receptores GNSS em metros


                
            elif tipo_arquivo=='txt':
                planilha_entrada=nome_arquivo
                ponto,g_l1,g_l2,g_l3,hora,minuto,h_instrumento,Lat_gra,Lat_min,Lat_seg,Lon_gra,Lon_min,Lon_seg,alt_m=np.loadtxt(planilha_entrada, skiprows=1,unpack=True)


            gc1,gc2,gf0=np.loadtxt(planilha_conv,skiprows=1,unpack=True)
            
        #Conversões e cálculos preliminares
        #--------------------------------------------------
            Lat_graus_dec=[]
            cont_lat=int(0)
            while len(Lat_graus_dec) != len(ponto):
                if Lat_gra[cont_lat]>=0:    
                    Lat_gd = Lat_gra[cont_lat]+(Lat_min[cont_lat]/60)+(Lat_seg[cont_lat]/3600) #Latitude em Graus decimais
                else:
                    Lat_gd = Lat_gra[cont_lat]-(Lat_min[cont_lat]/60)-(Lat_seg[cont_lat]/3600) #Latitude em Graus decimais
                Lat_graus_dec=np.append(Lat_graus_dec,Lat_gd)
                cont_lat=cont_lat+1
            Lat_rad=np.radians(Lat_graus_dec)
           
            Lon_graus_dec=[]
            cont_lon=int(0)
            while len(Lon_graus_dec) != len(ponto):
                if Lon_gra[cont_lon]>=0:    
                    Lon_gd = Lon_gra[cont_lon]+(Lon_min[cont_lon]/60)+(Lon_seg[cont_lon]/3600) #Latitude em Graus decimais
                else:
                    Lon_gd = Lon_gra[cont_lon]-(Lon_min[cont_lon]/60)-(Lon_seg[cont_lon]/3600) #Latitude em Graus decimais
                Lon_graus_dec=np.append(Lon_graus_dec,Lon_gd)
                cont_lon=cont_lon+1
            Lon_rad=np.radians(Lon_graus_dec)

            alt_cm = alt_m*100 #Altitude geométrica obtida pelos receptores GNSS em centimetros

            hora_dec=(hora)+(minuto/(60))
            hora_utc=(hora-fuso_horario)
            print(Lon_graus_dec[1],Lat_graus_dec[1])
            
        #Correções e Transformações importantes
        #--------------------------------------------------
            #Média das 3 leituras
            g_med_lido = (g_l1+g_l2+g_l3)/3 

            #Conversão de acel. Grav. instrumental para mGal
            g_conv=[]
            contador=int(0)
            while len(g_conv) != len(g_med_lido): #Até a lista de acel. Grav. em mGals, não tiver o mesmo tamanho que a lista da acel. Grav. lida faça isso:
                for item in gc1:                                #   Pegue um valor N de sua tabela de leituras, iniciando com o primeiro valor e indo até o ultimo,
                    diferença=g_med_lido[contador]-item         # faça a diferença entre esse N e todos os valores de gc1, se 0<=Diferença<100, então aplique a conversão
                    if diferença < 100 and diferença>=0:        # e adicione o resultado na lista de acel. Grav. em mGals, até ter feito tudo isto com todos os valores da
                        gc1l=gc1.tolist()                       # tabela de leitura.
                        gc_pos=gc1l.index(item)                 
                        gp=gc2[gc_pos]+(gf0[gc_pos]*(diferença))
                        g_conv=np.append(g_conv,gp) 
                contador=contador+1

            #Correção de Altura Instrumental
            c_ai=0.308596*h_instrumento
            g_ai=g_conv+c_ai
                
            #Correção de maré
            cont2=int(0)
            cls=np.array([])
            tide=TideModel()
            while len(cls) != len(ponto):
                data_l=datetime(int(ano),int(mes),int(dia),int(hora_utc[cont2]),int(minuto[cont2]))
                cls_a=tide.solve_longman(Lat_graus_dec[cont2],Lon_graus_dec[cont2],alt_m[cont2],data_l)
                cls=np.append(cls,cls_a)
                cont2=cont2+1               
            g_cls=g_ai+cls

            #######################################################################
            #---------------Aqui podem ser colocadas outras correções,------------#
            #---------------como a de pressão atm, precipitação, entre outras-----#
            #######################################################################
            
            #Correção da deriva instrumental
            delta_t=np.zeros(1)
            contador2=int(1)
            while len(delta_t)!=len(hora_dec):
                dt=hora_dec[contador2]-hora_dec[0]
                delta_t=np.append(delta_t,dt)
                contador2=contador2+1 
            if ponto[0] == ponto[-1]:
                delta_t[-1]=hora_dec[-1]-hora_dec[0]
                delta_g=g_cls[-1]-g_cls[0]
                cd=(-delta_g/delta_t[-1])*delta_t
                g_cd=g_cls+cd

                
            #Cálculo de Aceleração lida absoluta
            g_abs=g_ref+(g_cd-g_cd[0])

            #Acelerações teóricas
            if elipsoide=='grs67':
                #Cálculo de Aceleração do GRS67
                g_teor=978031.8*(1+0.0053024*((np.sin(Lat_rad))**2)-0.0000059*((np.sin(2*Lat_rad))**2))
            elif elipsoide=='grs80':
                #Cálculo de Aceleração do GRS80
                g_teor=978032.7*(1+0.0053024*((np.sin(Lat_rad))**2)-0.0000058*((np.sin(2*Lat_rad))**2))
            elif elipsoide=='grs84':
                #Cálculo de Aceleração do GRS84
                g_teor=(9.7803267714*((1+0.00193185138639*((np.sin(Lat_rad))**2))/((1-0.00669437999013*((np.sin(Lat_rad))**2)**(1/2)))))*(100000)
            

            #Correção Ar-livre
            if wx_free_air==0:
                ca=np.zeros(len(ponto))
                g_ca=np.zeros(len(ponto))
            elif wx_free_air==1:
                ca=0.308596*alt_m
                g_ca=g_abs+ca-g_teor            

            #Correção Bouguer Simples
            if wx_bouguer==0:
                cb=np.zeros(len(ponto))
                g_cb=np.zeros(len(ponto))
            elif wx_bouguer==1:
                cb=[]
                for item in alt_m:
                    if item>0:
                        c_b=0.04192*densidade*item
                        cb=np.append(cb,c_b)
                    elif item<0:
                        c_b=0.08384*densidade*item
                        cb=np.append(cb,c_b)
                    else:
                        c_b=0
                        cb=np.append(cb,c_b)
                g_cb=g_abs+ca-cb-g_teor

                
        #Sáida dos dados
        #--------------------------------------------------
            #Excel
            dec=3 #Numero de casa decimais
            df_pt1=pd.DataFrame({'Ponto':ponto})
            df_pt2=pd.DataFrame({'Leitura média Gravímetro':np.around(g_med_lido, decimals=dec)})
            df_pt3=pd.DataFrame({'Leitura média mGal':np.around(g_conv, decimals=dec)})
            df_pt4=pd.DataFrame({'Corr. Alt. Instr.':np.around(c_ai, decimals=dec)})
            df_pt5=pd.DataFrame({'g. Corr. Alt. Instrum.':np.around(g_ai, decimals=dec)})            
            df_pt6=pd.DataFrame({'Correção de Maré':np.around(cls, decimals=dec)}) 
            df_pt7=pd.DataFrame({'g. Corr. Maré ':np.around(g_cls, decimals=dec)})
            df_pt8=pd.DataFrame({'Corr. Deriva':np.around(cd, decimals=dec)})
            df_pt9=pd.DataFrame({'g. corr. Deriva':np.around(g_cd, decimals=dec)})
            df_pt10=pd.DataFrame({'g. Obs.':np.around(g_abs, decimals=dec)})            
            df_pt11=pd.DataFrame({'g Teórico':np.around(g_teor, decimals=dec)})
            df_pt12=pd.DataFrame({'Corr. Ar-livre':np.around(ca, decimals=dec)})
            df_pt13=pd.DataFrame({'Anom. Ar-livre':np.around(g_ca, decimals=dec)})
            df_pt14=pd.DataFrame({'Corr. Bouguer':np.around(cb, decimals=dec)})
            df_pt15=pd.DataFrame({'Anom. Bouguer':np.around(g_cb, decimals=dec)})

            
            excel_writer=ExcelWriter(saida_excel)
            cont_df=0
            for df in (df_pt1,df_pt2, df_pt3, df_pt4,df_pt5,df_pt6,df_pt7,df_pt8,df_pt9,df_pt10,df_pt11,df_pt12,df_pt13,df_pt14,df_pt15):
                df.to_excel(excel_writer, sheet_name='Plan1', startcol=cont_df,index=False)
                cont_df=cont_df+1
            excel_writer.save()
            #DAT/TXT
            dec2=3
            df={'00_Pt':ponto,'01_LG':np.around(g_med_lido, decimals=dec2),'02_LC':np.around(g_conv, decimals=dec2),
                '03_C.HI':np.around(c_ai, decimals=dec2),'04_g.HI':np.around(g_ai, decimals=dec2),
                '05_C.Mar':np.around(cls, decimals=dec2),'06_g.Mar':np.around(g_cls, decimals=dec2),
                '07_C.Der':np.around(cd, decimals=dec2),'08_g.Der':np.around(g_cd, decimals=dec2),
                '09_g.Obs':np.around(g_abs, decimals=dec2),'10_g.Teo':np.around(g_teor, decimals=dec2),
                '11_C.FrA':np.around(ca, decimals=dec2),'12_A.FrA':np.around(g_ca, decimals=dec2),
                '13_C.Bg':np.around(cb, decimals=dec2),'14_A.Bg':np.around(g_cb, decimals=dec2)}
            df_pt=pd.DataFrame(data=df)
            #np.savetxt("PRT_"+saida_txt, df_pt.values,fmt='%1.3f',delimiter='\t')
            df_pt.to_csv(saida_txt,sep="\t",header=True,index=False, mode='a')
            #_______________________________________
            #_______________________________________            
        self.B_entrada_import=Button(text='Reduzir Dados e Gerar Arquivos',command=gerar_saida)
        self.B_entrada_import.grid(row=12,column=11,columnspan=9,pady=20)

        self.T_autoria=Label(self.frame, font=('Times New Roman','7','bold','italic'),foreground="gray",
                             text='Programa  por  Danilo  de  Paula (danilo_p@usp.br),  do  GEOLIT-IAG-USP')
        self.T_autoria.grid(row=13,column=0,columnspan=11,sticky=W)


raiz=Tk()
raiz.wm_title("GRARED   v.Hawking 1.0")
raiz.geometry("+10+10")
Packing(raiz)
raiz.mainloop()
