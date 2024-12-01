import sqlite3

# Funciones de base de datos
def inicializar_db():
    conn = sqlite3.connect('inventario.db', detect_types=sqlite3.PARSE_DECLTYPES)
    cursor = conn.cursor()

    # Crear la tabla de productos con la nueva columna 'descripcion'
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        cantidad INTEGER NOT NULL,
        precio REAL NOT NULL,
        imagen TEXT,
        descripcion TEXT
    )
    ''')

    # Crear la tabla de historial
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS historial (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        producto_id INTEGER,
        nombre TEXT,
        operacion TEXT,
        cantidad INTEGER,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def agregar_producto(nombre, cantidad, precio, imagen, descripcion):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO productos (nombre, cantidad, precio, imagen, descripcion)
    VALUES (?, ?, ?, ?, ?)
    ''', (nombre, cantidad, precio, imagen, descripcion))

    # Obtener el ID del producto insertado
    producto_id = cursor.lastrowid

    # Registrar la operación en el historial
    cursor.execute('''
    INSERT INTO historial (producto_id, nombre, operacion, cantidad)
    VALUES (?, ?, ?, ?)
    ''', (producto_id, nombre, 'Agregado', cantidad))

    conn.commit()
    conn.close()

def obtener_productos():
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM productos')
    productos = cursor.fetchall()
    conn.close()
    return productos

def eliminar_producto(producto_id):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    # Obtener el nombre del producto antes de eliminarlo
    cursor.execute('SELECT nombre FROM productos WHERE id=?', (producto_id,))
    nombre_producto = cursor.fetchone()[0]

    # Registrar la operación en el historial
    cursor.execute('''
    INSERT INTO historial (producto_id, nombre, operacion, cantidad)
    VALUES (?, ?, ?, ?)
    ''', (producto_id, nombre_producto, 'Eliminado', 0))

    # Eliminar el producto
    cursor.execute('DELETE FROM productos WHERE id=?', (producto_id,))
    conn.commit()
    conn.close()

def actualizar_producto(id_producto, nueva_cantidad, cantidad_vendida):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    # Actualizar la cantidad del producto
    cursor.execute('''
    UPDATE productos
    SET cantidad = ?
    WHERE id = ?
    ''', (nueva_cantidad, id_producto))

    # Obtener el nombre del producto
    cursor.execute('SELECT nombre FROM productos WHERE id=?', (id_producto,))
    nombre_producto = cursor.fetchone()[0]

    # Registrar la operación en el historial
    cursor.execute('''
    INSERT INTO historial (producto_id, nombre, operacion, cantidad)
    VALUES (?, ?, ?, ?)
    ''', (id_producto, nombre_producto, 'Vendido', cantidad_vendida))

    conn.commit()
    conn.close()

def actualizar_cantidad_producto(producto_id, cantidad):
    conn = sqlite3.connect('inventario.db')
    cursor = conn.cursor()

    # Obtener la cantidad actual del producto antes de actualizarla
    cursor.execute('SELECT cantidad, nombre FROM productos WHERE id=?', (producto_id,))
    producto = cursor.fetchone()
    cantidad_actual = producto[0]
    nombre_producto = producto[1]

    # Calcular la nueva cantidad
    nueva_cantidad = cantidad_actual + cantidad

    # Actualizar la cantidad del producto
    cursor.execute('''
    UPDATE productos
    SET cantidad = ?
    WHERE id = ?
    ''', (nueva_cantidad, producto_id))

    # Registrar la operación en el historial
    operacion = 'Incrementado' if cantidad > 0 else 'Vendido'
    cursor.execute('''
    INSERT INTO historial (producto_id, nombre, operacion, cantidad)
    VALUES (?, ?, ?, ?)
    ''', (producto_id, nombre_producto, operacion, abs(cantidad)))

    conn.commit()
    conn.close()
