import tkinter as tk

def mostrar_ip():
    ip_ingresada = entrada_ip.get()
    etiqueta_resultado.config(text=f"Tu IP: {ip_ingresada}")

# Crear la ventana principal
root = tk.Tk()
root.title("Ingreso de IP")
root.geometry('300x200')

# Crear un Label para el texto "IP"
etiqueta_ip = tk.Label(root, text="IP")
etiqueta_ip.grid(row=0, column=0, sticky=tk.W)  # Alineación a la izquierda

# Crear un Entry para la entrada de la IP
entrada_ip = tk.Entry(root, width=20)  # Ancho fijo para el Entry
entrada_ip.grid(row=0, column=1)

# Crear un botón para confirmar la entrada
boton = tk.Button(root, text="Ingresar", command=mostrar_ip)
boton.grid(row=0, column=2)

# Crear un Label para mostrar el resultado
etiqueta_resultado = tk.Label(root, text="Tu IP: ")
etiqueta_resultado.grid(row=1, column=0, columnspan=3, sticky=tk.W)  # Extiende el Label a través de tres columnas

root.mainloop()
