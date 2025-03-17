import pyttsx3
import speech_recognition as sr
import pywhatkit
import yfinance as yf
import pyjokes
import webbrowser
import datetime
import wikipedia


## escuchar nuestor microfono y devolver el audio como texto
def transformar_audio_en_texto():

    ## almacenar recognizer en variable
    r = sr.Recognizer()

    ## configurar el microfono
    with sr.Microphone() as origen:

        ## tiempo de espera
        r.pause_threshold = 0.8

        ## informar que comenzo grabacion
        print("Escuchando...")

        ## guardar audio
        audio = r.listen(origen)

        try:

            ## buscar en google
            pedido = r.recognize_google(audio, language="es-AR")  ## type: ignore

            ## prueba de que ingreso y transformo
            print(  "Usted dijo: " + pedido)

            ## devolver pedido
            return pedido

        ## en caso de que no comprenda el audio
        except sr.UnknownValueError:

            ### prueba de que no entendio
            print("No hay servicio de google")

            ## devolver error
            return "sigo esperando"

        ## en caso de no poder resolver el pedido
        except:

            ### prueba de que no entendio
            print("Algo salio mal")

            ## devolver error
            return "sigo esperando"


## funcion para que el asistente pueda ser escuchado
def hablar(mensaje: str):

    ## encender el motor de pyttsx3
    engine = pyttsx3.init()

    ## pronunciar el mensaje
    engine.say(mensaje)
    engine.runAndWait()


## informar el dia de la semana
def pedir_dia():

    ##crear variable con la fecha actual
    dia = datetime.datetime.today()

    ## crear variable para el dia de la semana
    dia_semana = dia.weekday()

    ## crear diccionario con los dias de la semana
    calendario = {
        0: "Lunes",
        1: "Martes",
        2: "Miércoles",
        3: "Jueves",
        4: "Viernes",
        5: "Sábado",
        6: "Domingo",
    }

    ## decir dia de la semana
    hablar("Hoy es " + calendario[dia_semana])


## informar hora
def pedir_hora():

    ## crear variable con la hora actual
    hora = datetime.datetime.now().strftime("%I:%M %p")

    ## decir hora
    hablar("Son las " + hora)


## saludo inicial
def saludo_inicial():

    ## crear variables con datos hora
    hora = datetime.datetime.now().hour
    if hora < 6 or hora > 20:
        momento = "Buenas noches"
    elif hora >= 6 and hora < 13:
        momento = "Buenos días"
    else:
        momento = "Buenas tardes"

    ## decir el saludo
    hablar(f"{momento}, soy tu asistente de voz, en que puedo ayudarte?")


## funcion central del asistente
def pedir_cosas():

    ## activar saludo inicial
    saludo_inicial()

    ## variable de corte
    comenzar = True

    ## loop central
    while comenzar:

        ## activar el micro y guardar en un string
        pedido = transformar_audio_en_texto().lower()

        if "abrir youtube" in pedido:
            hablar("Abriendo youtube")
            webbrowser.open("https://www.youtube.com")
            continue
        elif "abrir navegador" in pedido:
            hablar("Abriendo navegador")
            webbrowser.open("https://www.google.com")
            continue
        elif "qué día es hoy" in pedido:
            pedir_dia()
            continue
        elif "qué hora es" in pedido:
            pedir_hora()
            continue
        elif "busca en wikipedia" in pedido:
            hablar("Buscando eso en wikipedia")
            pedido = pedido.replace("busca en wikipedia", "")
            wikipedia.set_lang("es")
            resultado = wikipedia.summary(pedido, sentences=1)
            hablar(f"Wikipedia dice lo siguiente {resultado}")
            continue
        elif "busca en internet" in pedido:
            hablar("Ya mismo estoy en eso")
            pywhatkit.search(pedido)  ## type: ignore
            continue
        elif "reproducir" in pedido:
            hablar("Buena idea, ya comienzo a reproducirlo")
            pywhatkit.playonyt(pedido)  ## type: ignore
            continue
        elif "chiste" in pedido:
            hablar(pyjokes.get_joke("es"))
            continue
        elif "cotización de acciones" in pedido:
            accion = pedido.split("de")[-1].strip()
            cartera = {
                "apple": "AAPL",
                "amazon": "AMZN",
                "google": "GOOGL",
                "tesla": "TSLA",
            }
            try:
                accion_buscada = cartera[accion]
                accion_buscada = yf.Ticker(accion_buscada)
                precio_actual = accion_buscada.info["regularMarketPrice"]
                hablar(f"El precio actual de {accion} es de {precio_actual} dólares")
                continue
            except:
                hablar("No se encontro la accion")
                continue
        elif "adiós" in pedido:
            hablar("Hasta luego, espero haberte ayudado")
            break


pedir_cosas()
