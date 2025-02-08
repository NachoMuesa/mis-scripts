from os import system


class Persona:
    def __init__(self, nombre: str, apellido: str):
        self.nombre = nombre
        self.apellido = apellido


class Cliente(Persona):
    def __init__(self, nombre: str, apellido: str, numero_cuenta: int, balance: int):
        super().__init__(nombre, apellido)
        self.numero_cuenta = numero_cuenta
        self.balance = balance

    def __str__(self):
        return f"Cliente: {self.apellido}, {self.nombre} -- Cuenta: {self.numero_cuenta} -- Balance: ${self.balance}"

    def depositar(self, cantidad: int):
        self.balance += cantidad

    def retirar(self, cantidad: int):
        if cantidad > self.balance:
            return False

        self.balance += cantidad
        return True


def crear_cliente() -> Cliente:
    """_summary_

    Returns:
        Cliente: Crea una clase de tipo Cliente, con datos como el nombre, apellido, numero de cuenta y su balance
    """
    nombre = input("Nombre: ")
    apellido = input("Apellido: ")
    numero_cuenta = int(input("Numero de cuenta: "))
    balance = int(input("Balance: "))

    return Cliente(nombre, apellido, numero_cuenta, balance)


def buscar_cliente(clientes: list[Cliente], cuenta: int) -> Cliente:
    for cliente in clientes:
        if cliente.numero_cuenta == cuenta:
            return cliente

    return None  ## type: ignore


def inicio() -> None:

    clientes: list[Cliente] = []
    while True:
        system("cls")
        print("1. Crear cliente")
        print("2. Consultar cuenta")
        print("3. Depositar")
        print("4. Retirar")
        print("5. Salir")
        opcion: str = input("Opcion: ")

        if opcion == "1":
            clientes.append(crear_cliente())
            print("Cliente creado")
            input("Presiona Enter para continuar...")

        elif opcion == "2":
            cuenta = int(input("Ingresa tu numero de cuenta: "))
            cliente = buscar_cliente(clientes, cuenta)
            if cliente is not None:
                print(cliente)
            else:
                print("Cliente no encontrado")
            input("Presiona Enter para continuar...")

        elif opcion == "3":
            cuenta = int(input("Numero de cuenta: "))
            cantidad = int(input("Cantidad a depositar: "))
            cliente = buscar_cliente(clientes, cuenta)
            if cliente is not None:
                cliente.depositar(cantidad)
                print(f"Tu saldo actual es {cliente.balance}")
            else:
                print("Cliente no encontrado")
            input("Presiona Enter para continuar...")

        elif opcion == "4":
            cuenta = int(input("Numero de cuenta: "))
            cantidad = int(input("Cantidad a retirar: "))
            cliente = buscar_cliente(clientes, cuenta)
            if cliente is not None:
                if cliente.retirar(cantidad):
                    print(f"Tu saldo actual es {cliente.balance}")
                else:
                    print("No tienes suficiente saldo")
            else:
                print("Cliente no encontrado")
            input("Presiona Enter para continuar...")

        elif opcion == "5":
            break


inicio()
