import os
from pathlib import Path
from os import system

mi_ruta = Path(
    Path.home(), "Desktop", "Nuevo proyecto", "Practicas", "Basico", "Dia 6", "Recetas"
)


def contar_recetas(ruta: Path) -> int:
    contador: int = 0
    for txt in Path(ruta).glob("**/*.txt"):
        contador += 1
    return contador


def inicio() -> int:
    system("cls")
    print("*" * 50)
    print("*" * 5 + " Bienvenido a la aplicación de recetas " + "*" * 5)
    print("*" * 50)
    print(f"Las recetas se encuentran en {mi_ruta}")
    print(f"Total de recetas: {contar_recetas(mi_ruta)}")

    eleccion_menu = "x"
    while not eleccion_menu.isnumeric() or int(eleccion_menu) not in range(1, 7):
        print("[1] - Ver recetas")
        print("[2] - Crear receta")
        print("[3] - Crear categoria")
        print("[4] - Eliminar receta")
        print("[5] - Eliminar categoria")
        print("[6] - Salir")
        eleccion_menu = input("Elija una opción: ")
    return int(eleccion_menu)


def mostrar_categorias(ruta: Path) -> list[Path]:
    print("Categorias:")
    ruta_categorias = Path(ruta)
    lista_categorias = []
    contador: int = 1

    for carpeta in ruta_categorias.iterdir():
        carpeta_str = str(carpeta.name)
        print(f"[{contador}] - {carpeta_str}")
        lista_categorias.append(carpeta)
        contador += 1
    return lista_categorias


def elegir_categoria(lista: list[Path]) -> Path:
    eleccion_correcta: str = "x"

    while not eleccion_correcta.isnumeric() or int(eleccion_correcta) not in range(
        1, len(lista) + 1
    ):
        eleccion_correcta = input("\nElija una categoria: ")

    return lista[int(eleccion_correcta) - 1]


def mostrar_recetas(ruta: Path) -> list[Path]:
    print("Recetas:")
    ruta_recetas = Path(ruta)
    lista_recetas = []
    contador: int = 0

    for receta in ruta_recetas.glob("*.txt"):
        receta_str = str(receta.name)
        print(f"[{contador}] - {receta_str}")
        lista_recetas.append(receta)
        contador += 1

    return lista_recetas


def elegir_receta(lista: list[Path]) -> Path:
    eleccion_receta: str = "x"

    while not eleccion_receta.isnumeric() or int(eleccion_receta) not in range(
        1, len(lista) + 1
    ):
        eleccion_receta = input("\nElija una receta: ")

    return lista[int(eleccion_receta) - 1]


def leer_receta(receta: Path) -> None:
    print(Path.read_text(receta))


def crear_receta(ruta: Path) -> None:
    existe = False

    while not existe:
        print("Escribe el nombre de tu receta ")
        nombre_categoria = input()
        nombre_categoria = nombre_categoria + ".txt"
        print("Escribe tu nueva receta: ")
        contenido_receta = input()
        ruta_nueva_receta = Path(ruta, nombre_categoria)
        if not os.path.exists(ruta_nueva_receta):
            Path.write_text(ruta_nueva_receta, contenido_receta)
            print(f"Tu receta {nombre_categoria} ha sido creada")
            existe = True
        else:
            print("Lo siento, esa receta ya existe")


def crear_categoria(ruta: Path) -> None:
    existe = False

    while not existe:
        print("Escribe el nombre de la nueva categoria: ")
        nombre_categoria = input()
        ruta_nueva = Path(ruta, nombre_categoria)
        if not os.path.exists(ruta_nueva):
            Path.mkdir(ruta_nueva)
            print(f"Tu nueva categoria {nombre_categoria} ha sido creada")
            existe = True
        else:
            print("Lo siento, esa categoria ya existe")


def eliminar_receta(receta: Path) -> None:
    Path(receta).unlink()
    print(f"La receta {receta} ha sido eliminada")


def eliminar_categoria(categoria: Path) -> None:
    Path(categoria).rmdir()
    print(f"La categoria {categoria} ha sido eliminada")


def volver_inicio() -> None:
    eleccion_regresar = "x"

    while eleccion_regresar.lower() != "v":
        eleccion_regresar = input("\nPresione 'V' para volver al inicio: ")


finalizar_programa: bool = False

while not finalizar_programa:

    menu: int = int(inicio())

    if menu == 1:
        mis_categorias = mostrar_categorias(mi_ruta)
        mi_categoria = elegir_categoria(mis_categorias)
        mis_recetas = mostrar_recetas(mi_categoria)
        if len(mis_recetas) == 0:
            print("No hay recetas en esta categoria.")
            volver_inicio()
        else:
            mi_receta = elegir_receta(mis_recetas)
            leer_receta(mi_receta)
            volver_inicio()

    elif menu == 2:
        mis_categorias = mostrar_categorias(mi_ruta)
        mi_categoria = elegir_categoria(mis_categorias)
        crear_receta(mi_categoria)
        volver_inicio()

    elif menu == 3:
        crear_categoria(mi_ruta)
        volver_inicio()

    elif menu == 4:
        mis_categorias = mostrar_categorias(mi_ruta)
        mi_categoria = elegir_categoria(mis_categorias)
        mis_recetas = mostrar_recetas(mi_categoria)

        if len(mis_recetas) == 0:
            print("No hay recetas en esta categoria.")
        else:
            eliminar_receta(mi_receta)
        volver_inicio()

    elif menu == 5:
        mis_categorias = mostrar_categorias(mi_ruta)
        mi_categoria = elegir_categoria(mis_categorias)
        eliminar_categoria(mi_categoria)
        volver_inicio()

    elif menu == 6:
        finalizar_programa = True
