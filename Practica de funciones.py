from random import choice

palabras: list[str] = ["panadero", "dinosaurio", "helipuerto", "tiburon"]
letras_correctas: list[str] = []
letras_incorrectas: list[str] = []
intentos: int = 6
aciertos: int = 0
juego_terminado: bool = False


def elegir_palabra(lista_palabra: list[str]) -> tuple[str, int]:

    palabra_elegida = choice(lista_palabra)
    letras_unicas = len(set(palabra_elegida))

    return palabra_elegida, letras_unicas


def pedir_letra() -> str:

    letra_elegida: str = ""
    es_valida: bool = False
    abecedario: str = "abcdefghijklmnñopqrstuvwxyz"

    while not es_valida:
        letra_elegida: str = input("Introduce una letra: ").lower()
        if letra_elegida in abecedario and len(letra_elegida) == 1:
            es_valida = True
        else:
            print("Letra no válida")

    return letra_elegida


def mostrar_nuevo_tablero(palabra_elegida: str) -> None:

    lista_oculta: list[str] = []

    for l in palabra_elegida:
        if l in letras_correctas:
            lista_oculta.append(l)
        else:
            lista_oculta.append("-")

    print(" ".join(lista_oculta))


def chequear_letra(letra_elegida, palabra_oculta, vidas, coincidencias):

    fin = False

    if letra_elegida in palabra_oculta and letra_elegida not in letras_correctas:
        letras_correctas.append(letra_elegida)
        coincidencias += 1
    elif letra_elegida in palabra_oculta and letra_elegida in letras_correctas:
        print("Ya has introducido esa letra")
    else:
        letras_incorrectas.append(letra_elegida)
        vidas -= 1

    if vidas == 0:
        fin = perder()
    elif coincidencias == letras_unicas:
        fin = ganar(palabra_oculta)

    return vidas, fin, coincidencias


def perder() -> bool:

    print("Te has quedado sin vidas")
    print(f"La palabra oculta era {palabra_oculta}")

    return True


def ganar(palabra_descubierta: str) -> bool:

    mostrar_nuevo_tablero(palabra_descubierta)
    print("¡Felicidades! Has ganado")

    return True


palabra_oculta, letras_unicas = elegir_palabra(palabras)

while not juego_terminado:

    print("\n" + "*" * 20 + "\n")
    mostrar_nuevo_tablero(palabra_oculta)
    print("\n")
    print("Letras incorrectas: " + "-".join(letras_incorrectas))
    print(f"Vidas restantes: {intentos}")
    print("\n" + "*" * 20 + "\n")
    letra = pedir_letra()

    intentos, terminado, aciertos = chequear_letra(
        letra, palabra_oculta, intentos, aciertos
    )

    juego_terminado = terminado
