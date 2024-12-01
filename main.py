#Librerías por instalar:
#pip install matplotlib
#pip install pillow
#pip install statsmodels
#pip install tk

#Y aparte se necesita python:
#https://www.python.org/downloads/

#Ejecutar lo siguiente para abrir el programa:
#python main.py














# main.py
import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime, timedelta
import os
from database import inicializar_db, agregar_producto, obtener_productos, eliminar_producto, actualizar_producto, actualizar_cantidad_producto
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import statistics
import statsmodels.api as sm
import numpy as np




# Constante para el archivo que guarda la fecha
FECHA_ARCHIVO = "fecha.txt"

# Adaptadores y conversores para datetime
def adapt_datetime(ts):
    return ts.strftime('%Y-%m-%d %H:%M:%S')

def convert_datetime(ts):
    return datetime.strptime(ts.decode('utf-8'), '%Y-%m-%d %H:%M:%S')

sqlite3.register_adapter(datetime, adapt_datetime)
sqlite3.register_converter("timestamp", convert_datetime)

def obtener_fecha_guardada():
    if os.path.exists(FECHA_ARCHIVO):
        with open(FECHA_ARCHIVO, "r") as archivo:
            fecha_str = archivo.read().strip()
            return datetime.strptime(fecha_str, "%d/%m/%Y").date()
    return None

def guardar_fecha(fecha):
    with open(FECHA_ARCHIVO, "w") as archivo:
        archivo.write(fecha.strftime("%d/%m/%Y"))

def obtener_fecha_actualizada():
    fecha_hoy = datetime.now().date()
    guardar_fecha(fecha_hoy)
    return fecha_hoy


def mostrar_inventario():
    def eliminar_y_actualizar(producto_id):
        eliminar_producto(producto_id)
        nueva_ventana.destroy()
        mostrar_inventario()

    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("Inventario")
    nueva_ventana.geometry("1300x900")

    productos = obtener_productos()

    # Crear un contenedor con scrollbar
    contenedor_canvas = tk.Canvas(nueva_ventana)
    contenedor_frame = tk.Frame(contenedor_canvas)
    scrollbar = tk.Scrollbar(nueva_ventana, orient="vertical", command=contenedor_canvas.yview)
    contenedor_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    contenedor_canvas.pack(side="left", fill="both", expand=True)
    contenedor_canvas.create_window((0, 0), window=contenedor_frame, anchor="nw")

    def ajustar_scroll(event):
        contenedor_canvas.configure(scrollregion=contenedor_canvas.bbox("all"))

    contenedor_frame.bind("<Configure>", ajustar_scroll)

    columnas = 5
    for i, producto in enumerate(productos):
        frame = tk.Frame(contenedor_frame, relief=tk.RAISED, borderwidth=2)
        frame.grid(row=i // columnas, column=i % columnas, padx=10, pady=10)

        # Mostrar la imagen del producto
        if producto[4]:  # Verificar si hay una ruta de imagen
            try:
                imagen = Image.open(producto[4])
                imagen = imagen.resize((200, 200), Image.LANCZOS)
                imagen_tk = ImageTk.PhotoImage(imagen)
                etiqueta_imagen = tk.Label(frame, image=imagen_tk)
                etiqueta_imagen.image = imagen_tk  # Guardar una referencia para evitar que se elimine la imagen
                etiqueta_imagen.pack(pady=5)
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")

        # Mostrar los detalles del producto
        etiqueta_detalles = tk.Label(frame, text=f"Nombre: {producto[1]}\nCantidad: {producto[2]}\nPrecio: {producto[3]}")
        etiqueta_detalles.pack(pady=5)

        # Botón para eliminar el producto
        boton_eliminar = tk.Button(frame, text="Eliminar", command=lambda pid=producto[0]: eliminar_y_actualizar(pid))
        boton_eliminar.pack(pady=5)







def mostrar_vender(ventana_existente=None):
    def obtener_productos_vender():
        productos = obtener_productos()
        return [(producto[0], producto[1], producto[2], producto[3], producto[4], producto[5]) for producto in productos]

    def actualizar_informacion_producto(producto):
        for widget in izquierda_frame.winfo_children():
            widget.destroy()

        # Mostrar la imagen del producto
        if producto[4]:  # Verificar si hay una ruta de imagen
            try:
                imagen = Image.open(producto[4])
                imagen = imagen.resize((300, 300), Image.LANCZOS)
                imagen_tk = ImageTk.PhotoImage(imagen)
                etiqueta_imagen = tk.Label(izquierda_frame, image=imagen_tk)
                etiqueta_imagen.image = imagen_tk  # Guardar una referencia para evitar que se elimine la imagen
                etiqueta_imagen.pack(pady=5)
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")

        # Mostrar los detalles del producto
        etiqueta_nombre = tk.Text(izquierda_frame, height=1, width=50, wrap="word")
        etiqueta_nombre.insert(tk.END, f"Nombre: {producto[1]}")
        etiqueta_nombre.config(state=tk.DISABLED)
        etiqueta_nombre.pack(pady=5)
        
        etiqueta_precio = tk.Text(izquierda_frame, height=1, width=50, wrap="word")
        etiqueta_precio.insert(tk.END, f"Precio: {producto[3]}")
        etiqueta_precio.config(state=tk.DISABLED)
        etiqueta_precio.pack(pady=5)

        etiqueta_descripcion = tk.Text(izquierda_frame, height=5, width=50, wrap="word")
        etiqueta_descripcion.insert(tk.END, f"Descripción: {producto[5]}")
        etiqueta_descripcion.config(state=tk.DISABLED)
        etiqueta_descripcion.pack(pady=5)

        # Sección para cambiar las cantidades a elegir
        cantidad_label = tk.Label(izquierda_frame, text="Cantidad a vender:")
        cantidad_label.pack(pady=5)
        cantidad_entry = tk.Entry(izquierda_frame)
        cantidad_entry.pack(pady=5)

        # Botón para vender
        vender_boton = tk.Button(izquierda_frame, text="Vender", command=lambda: vender_producto(producto, cantidad_entry))
        vender_boton.pack(pady=5)
        
    def vender_producto(producto, cantidad_entry):
        try:
            cantidad_a_vender = int(cantidad_entry.get())
            if cantidad_a_vender <= 0:
                raise ValueError("La cantidad debe ser un número positivo.")
            
            nueva_cantidad = producto[2] - cantidad_a_vender
            if nueva_cantidad < 0:
                raise ValueError("No hay suficiente cantidad en inventario.")
            
            # Actualizar la cantidad en la base de datos y registrar la venta
            actualizar_producto(producto[0], nueva_cantidad, cantidad_a_vender)
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", "Producto vendido exitosamente.")
            
            # Cerrar la ventana existente si hay una
            if ventana_existente is not None:
                ventana_existente.destroy()
            
            # Mostrar la ventana de vender actualizada
            mostrar_vender()
        except ValueError as ve:
            messagebox.showerror("Error", str(ve))

    if ventana_existente is not None:
        ventana_existente.destroy()
        
    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("Vender")
    nueva_ventana.geometry("1300x900")
    
    panedwindow = tk.PanedWindow(nueva_ventana, orient=tk.HORIZONTAL)
    panedwindow.pack(fill=tk.BOTH, expand=True)
    
    izquierda_frame = tk.Frame(panedwindow, width=390)
    derecha_frame = tk.Frame(panedwindow, width=910)
    
    panedwindow.add(izquierda_frame)
    panedwindow.add(derecha_frame)
    
    linea_divisoria = tk.Frame(panedwindow, width=2, background="black")
    panedwindow.add(linea_divisoria)
    
    panedwindow.paneconfig(izquierda_frame, minsize=390)
    panedwindow.paneconfig(linea_divisoria, minsize=2)
    panedwindow.paneconfig(derecha_frame, minsize=908)

    contenedor_canvas = tk.Canvas(derecha_frame)
    contenedor_frame = tk.Frame(contenedor_canvas)
    scrollbar = tk.Scrollbar(derecha_frame, orient="vertical", command=contenedor_canvas.yview)
    contenedor_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    contenedor_canvas.pack(side="left", fill="both", expand=True)
    contenedor_canvas.create_window((0, 0), window=contenedor_frame, anchor="nw")

    def ajustar_scroll(event):
        contenedor_canvas.configure(scrollregion=contenedor_canvas.bbox("all"))

    contenedor_frame.bind("<Configure>", ajustar_scroll)

    productos = obtener_productos_vender()
    columnas = 4
    for i, producto in enumerate(productos):
        frame = tk.Frame(contenedor_frame, relief=tk.RAISED, borderwidth=2)
        frame.grid(row=i // columnas, column=i % columnas, padx=10, pady=10)

        if producto[4]:
            try:
                imagen = Image.open(producto[4])
                imagen = imagen.resize((200, 200), Image.LANCZOS)
                imagen_tk = ImageTk.PhotoImage(imagen)
                etiqueta_imagen = tk.Label(frame, image=imagen_tk)
                etiqueta_imagen.image = imagen_tk
                etiqueta_imagen.pack(pady=5)
                etiqueta_imagen.bind("<Button-1>", lambda e, p=producto: actualizar_informacion_producto(p))
            except Exception as e:
                print(f"Error al cargar la imagen: {e}")

        etiqueta_nombre = tk.Label(frame, text=f"{producto[1]}")
        etiqueta_nombre.pack(pady=5)
        etiqueta_precio = tk.Label(frame, text=f"Precio: {producto[3]}")
        etiqueta_precio.pack(pady=5)
        etiqueta_cantidad = tk.Label(frame, text=f"Cantidad: {producto[2]}")
        etiqueta_cantidad.pack(pady=5)














def mostrar_agregar():
    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("Agregar y Aumentar Cantidad")
    nueva_ventana.geometry("1300x900")

    # Crear un PanedWindow
    panedwindow = tk.PanedWindow(nueva_ventana, orient=tk.HORIZONTAL)
    panedwindow.pack(fill=tk.BOTH, expand=True)

    # Crear los frames para cada sección
    izquierda_frame = tk.Frame(panedwindow, width=650)
    derecha_frame = tk.Frame(panedwindow, width=650)

    # Añadir los frames al PanedWindow
    panedwindow.add(izquierda_frame)
    panedwindow.add(derecha_frame)

    # Línea divisoria (Frame delgado con fondo negro)
    linea_divisoria = tk.Frame(panedwindow, width=2, background="black")
    panedwindow.add(linea_divisoria)

    # Ajustar los tamaños de las secciones
    panedwindow.paneconfig(izquierda_frame, minsize=650)
    panedwindow.paneconfig(linea_divisoria, minsize=2)
    panedwindow.paneconfig(derecha_frame, minsize=648)

    # Parte izquierda
    tk.Label(izquierda_frame, text="Nuevo Producto", font=("Helvetica", 16, "bold")).pack(pady=10)

    tk.Label(izquierda_frame, text="Nombre del Producto").pack(pady=5)
    nombre_entry = tk.Entry(izquierda_frame)
    nombre_entry.pack(pady=5)

    tk.Label(izquierda_frame, text="Cantidad").pack(pady=5)
    cantidad_entry = tk.Entry(izquierda_frame)
    cantidad_entry.pack(pady=5)

    tk.Label(izquierda_frame, text="Precio").pack(pady=5)
    precio_entry = tk.Entry(izquierda_frame)
    precio_entry.pack(pady=5)

    tk.Label(izquierda_frame, text="Imagen").pack(pady=5)
    imagen_entry = tk.Entry(izquierda_frame)
    imagen_entry.pack(pady=5)

    def seleccionar_imagen():
        ruta_imagen = filedialog.askopenfilename(filetypes=[("Archivos de imagen", "*.jpg;*.jpeg;*.png;*.bmp")])
        imagen_entry.delete(0, tk.END)
        imagen_entry.insert(0, ruta_imagen)

    tk.Button(izquierda_frame, text="Seleccionar Imagen", command=seleccionar_imagen).pack(pady=5)

    # Campo de texto para la descripción
    tk.Label(izquierda_frame, text="Descripción (máximo 100 palabras)").pack(pady=5)
    descripcion_text = tk.Text(izquierda_frame, height=5, width=50)
    descripcion_text.pack(pady=5)

    def agregar():
        nombre = nombre_entry.get()
        cantidad = int(cantidad_entry.get())
        precio = float(precio_entry.get())
        imagen = imagen_entry.get()
        descripcion = descripcion_text.get("1.0", tk.END).strip()

        # Limitar la descripción a 100 palabras
        if len(descripcion.split()) > 100:
            descripcion = ' '.join(descripcion.split()[:100])

        agregar_producto(nombre, cantidad, precio, imagen, descripcion)
        tk.Label(izquierda_frame, text="Producto agregado", fg="green").pack(pady=5)
        cargar_productos_derecha()

    tk.Button(izquierda_frame, text="Agregar Producto", command=agregar).pack(pady=20)

    # Parte derecha para aumentar la cantidad de productos existentes
    tk.Label(derecha_frame, text="Aumentar Cantidad de Productos", font=("Helvetica", 16, "bold")).pack(pady=10)

    contenedor_canvas = tk.Canvas(derecha_frame)
    contenedor_frame = tk.Frame(contenedor_canvas)
    scrollbar = tk.Scrollbar(derecha_frame, orient="vertical", command=contenedor_canvas.yview)
    contenedor_canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side="right", fill="y")
    contenedor_canvas.pack(side="left", fill="both", expand=True)
    contenedor_canvas.create_window((0, 0), window=contenedor_frame, anchor="nw")

    def ajustar_scroll(event):
        contenedor_canvas.configure(scrollregion=contenedor_canvas.bbox("all"))

    contenedor_frame.bind("<Configure>", ajustar_scroll)

    def cargar_productos_derecha():
        # Limpiar el frame antes de recargar los productos
        for widget in contenedor_frame.winfo_children():
            widget.destroy()

        productos = obtener_productos()
        for producto in productos:
            frame = tk.Frame(contenedor_frame, relief=tk.RAISED, borderwidth=2)
            frame.pack(pady=10, padx=10, fill="x", expand=True)

            # Mostrar la imagen del producto
            if producto[4]:  # Verificar si hay una ruta de imagen
                try:
                    imagen = Image.open(producto[4])
                    imagen = imagen.resize((100, 100), Image.LANCZOS)
                    imagen_tk = ImageTk.PhotoImage(imagen)
                    etiqueta_imagen = tk.Label(frame, image=imagen_tk)
                    etiqueta_imagen.image = imagen_tk  # Guardar una referencia para evitar que se elimine la imagen
                    etiqueta_imagen.pack(side="left", padx=10)
                except Exception as e:
                    print(f"Error al cargar la imagen: {e}")

            detalles_frame = tk.Frame(frame)
            detalles_frame.pack(side="left", fill="y")

            tk.Label(detalles_frame, text=f"Nombre: {producto[1]}").pack(anchor="w")
            tk.Label(detalles_frame, text=f"Cantidad actual: {producto[2]}").pack(anchor="w")
            tk.Label(detalles_frame, text=f"Precio: {producto[3]}").pack(anchor="w")

            cantidad_entry = tk.Entry(detalles_frame)
            cantidad_entry.pack(pady=5)
            tk.Button(detalles_frame, text="Aumentar Cantidad", command=lambda p=producto[0], e=cantidad_entry: aumentar_cantidad(p, e)).pack(pady=5)

    def aumentar_cantidad(producto_id, cantidad_entry):
        cantidad = int(cantidad_entry.get())
        actualizar_cantidad_producto(producto_id, cantidad)
        tk.Label(derecha_frame, text="Cantidad actualizada", fg="green").pack(pady=5)
        cargar_productos_derecha()

    cargar_productos_derecha()










def mostrar_estadisticas():
    def obtener_datos_estadisticos(rango, operacion, producto):
        conn = sqlite3.connect('inventario.db')
        cursor = conn.cursor()

        if rango == "Día":
            fecha_inicio = datetime.now() - timedelta(days=1)
        elif rango == "Semana":
            fecha_inicio = datetime.now() - timedelta(weeks=1)
        elif rango == "Mes":
            fecha_inicio = datetime.now() - timedelta(days=30)
        else:
            fecha_inicio = datetime.now() - timedelta(days=365)

        query = '''SELECT nombre, operacion, SUM(cantidad) as cantidad_total
                   FROM historial
                   WHERE fecha >= ?'''

        params = [fecha_inicio]

        if operacion != "Todos":
            query += " AND operacion = ?"
            params.append(operacion)

        if producto != "Todos los productos":
            query += " AND nombre = ?"
            params.append(producto)

        query += " GROUP BY nombre, operacion"

        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        return resultados

    def actualizar_grafico():
        rango = rango_tiempo.get()
        operacion = tipo_operacion.get()
        producto = producto_seleccionado.get()

        resultados = obtener_datos_estadisticos(rango, operacion, producto)

        # Verificar si la operación es "Todos" para ajustar la visualización
        if operacion == "Todos":
            # Agrupar resultados por nombre de producto
            agrupados = {}
            for resultado in resultados:
                nombre = resultado[0]
                cantidad = resultado[2]
                if nombre in agrupados:
                    agrupados[nombre] += cantidad
                else:
                    agrupados[nombre] = cantidad

            nombres = list(agrupados.keys())
            cantidades = list(agrupados.values())
        else:
            nombres = [resultado[0] for resultado in resultados]
            cantidades = [resultado[2] for resultado in resultados]

        for widget in derecha_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(nombres, cantidades, color='skyblue')
        ax.set_xlabel('Cantidad')
        ax.set_ylabel('Productos')
        ax.set_title(f'{operacion} de productos en {rango.lower()}')

        canvas = FigureCanvasTkAgg(fig, master=derecha_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Calcular estadísticas
        if cantidades:
            media = statistics.mean(cantidades)
            mediana = statistics.median(cantidades)
            desviacion_estandar = statistics.stdev(cantidades) if len(cantidades) > 1 else 0

            # Mostrar estadísticas en el frame izquierdo
            for widget in estadisticas_frame.winfo_children():
                widget.destroy()

            tk.Label(estadisticas_frame, text=f"Media: {media:.2f}", font=("Helvetica", 12)).pack(pady=5)
            tk.Label(estadisticas_frame, text=f"Mediana: {mediana:.2f}", font=("Helvetica", 12)).pack(pady=5)
            tk.Label(estadisticas_frame, text=f"Desviación Estándar: {desviacion_estandar:.2f}", font=("Helvetica", 12)).pack(pady=5)

    def analizar_ventas():
        conn = sqlite3.connect('inventario.db')
        cursor = conn.cursor()
        
        # Obtener ventas del último mes
        fecha_inicio = datetime.now() - timedelta(days=30)
        cursor.execute('''SELECT fecha, nombre, SUM(cantidad) as cantidad_total
                          FROM historial
                          WHERE operacion = 'Vendido' AND fecha >= ?
                          GROUP BY fecha, nombre''', (fecha_inicio,))
        
        ventas = cursor.fetchall()
        conn.close()

        if not ventas:
            messagebox.showinfo("Información", "No hay suficientes datos para realizar la predicción.")
            return

        # Preparar los datos para el modelo
        productos = list(set([venta[1] for venta in ventas]))
        datos = {producto: [] for producto in productos}
        fechas = sorted(list(set([venta[0] for venta in ventas])))

        for fecha in fechas:
            for producto in productos:
                cantidad = next((venta[2] for venta in ventas if venta[0] == fecha and venta[1] == producto), 0)
                datos[producto].append(cantidad)

        predicciones = {}
        for producto in productos:
            y = np.array(datos[producto])
            X = np.arange(len(y))
            X = sm.add_constant(X)
            model = sm.OLS(y, X).fit()
            prediccion = model.predict([1, len(y) + 1])[0]
            predicciones[producto] = prediccion

        nombres_pred = list(predicciones.keys())
        cantidades_pred = list(predicciones.values())

        for widget in derecha_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(nombres_pred, cantidades_pred, color='lightgreen')
        ax.set_xlabel('Cantidad Predicha')
        ax.set_ylabel('Productos')
        ax.set_title('Predicción de productos más vendidos para el próximo mes')

        canvas = FigureCanvasTkAgg(fig, master=derecha_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("Estadísticas")
    nueva_ventana.geometry("1300x900")

    panedwindow = tk.PanedWindow(nueva_ventana, orient=tk.HORIZONTAL)
    panedwindow.pack(fill=tk.BOTH, expand=True)

    izquierda_frame = tk.Frame(panedwindow, width=390)
    derecha_frame = tk.Frame(panedwindow, width=910)
    estadisticas_frame = tk.Frame(izquierda_frame)

    panedwindow.add(izquierda_frame)
    panedwindow.add(derecha_frame)

    linea_divisoria = tk.Frame(panedwindow, width=2, background="black")
    panedwindow.add(linea_divisoria)

    panedwindow.paneconfig(izquierda_frame, minsize=390)
    panedwindow.paneconfig(linea_divisoria, minsize=2)
    panedwindow.paneconfig(derecha_frame, minsize=908)

    tk.Label(izquierda_frame, text="Seleccione el rango de tiempo:", font=("Helvetica", 12)).pack(pady=10)

    rango_tiempo = ttk.Combobox(izquierda_frame, values=["Día", "Semana", "Mes", "Año"], state="readonly")
    rango_tiempo.pack(pady=10)

    tk.Label(izquierda_frame, text="Seleccione el tipo de operación:", font=("Helvetica", 12)).pack(pady=10)

    tipo_operacion = ttk.Combobox(izquierda_frame, values=["Todos", "Agregado", "Incrementado", "Vendido", "Eliminado"], state="readonly")
    tipo_operacion.pack(pady=10)

    tk.Label(izquierda_frame, text="Seleccione el producto:", font=("Helvetica", 12)).pack(pady=10)

    nombres_productos = [producto[1] for producto in obtener_productos()]
    nombres_productos.insert(0, "Todos los productos")

    producto_seleccionado = ttk.Combobox(izquierda_frame, values=nombres_productos, state="readonly")
    producto_seleccionado.pack(pady=10)

    boton_actualizar = tk.Button(izquierda_frame, text="Actualizar", command=actualizar_grafico)
    boton_actualizar.pack(pady=10)

    boton_analizar = tk.Button(izquierda_frame, text="Analizar", command=analizar_ventas)
    boton_analizar.pack(pady=10)

    estadisticas_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)













def mostrar_fecha():
    fecha_label.config(text=f"Fecha de hoy: {fecha_actual.strftime('%d/%m/%Y')}")

ventana = tk.Tk()
ventana.title("Mi Ventana")
ventana.geometry("500x350")

# Inicializar la base de datos
inicializar_db()

# Fecha actual
fecha_actual = obtener_fecha_actualizada()

boton_inventario = tk.Button(ventana, text="Inventario", command=mostrar_inventario, width=50, height=2)
boton_inventario.pack(pady=10)

boton_vender = tk.Button(ventana, text="Vender", command=mostrar_vender, width=50, height=2)
boton_vender.pack(pady=10)

boton_agregar = tk.Button(ventana, text="Agregar", command=mostrar_agregar, width=50, height=2)
boton_agregar.pack(pady=10)

boton_estadisticas = tk.Button(ventana, text="Estadisticas", command=mostrar_estadisticas, width=50, height=2)
boton_estadisticas.pack(pady=10)

boton_salir = tk.Button(ventana, text="Salir", command=ventana.quit, width=50, height=2)
boton_salir.pack(pady=10)

fecha_label = tk.Label(ventana, text="")
fecha_label.pack(pady=10)
mostrar_fecha()

ventana.mainloop()
