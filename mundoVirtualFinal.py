import mysql.connector
import json
import heapq
import hashlib

# Conexión a la base de datos
def conectar_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  
        password="12345",  
        database="mundo_virtual"
    )

def menu():
    while True:
        print("\nMenú:")
        print("1. Gestion de jugadores")
        print("2. gestion de mundos")
        print("3. Gestion de partidas")
        print("4. menu de inventario")
        print("5. Ranking global")
        print("6. Salir")
        
        opcion = input("Elige una opción: ")

        if opcion == "1":
            menu_jugador()
        elif opcion == "2":
            menu_mundos()
        elif opcion == "3":
            menu_partidas()
        elif opcion == "4":
            menu_inventario()
        elif opcion == "5":
            consultar_jugadores_por_puntuacion()
        elif opcion == "6":
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

menu()

def menu_jugador():
    while True:
        print("\nGestion de jugador:")
        print("1. Crear Jugador")
        print("2. Modificar Jugador")
        print("3. Eliminar Jugador")
        print("4. Consultar Jugador")
        print("5. Salir")
        
        opcion = input("Elige una opción: ")

        if opcion == "1":
            crear_jugador()
        elif opcion == "2":
            modificar_jugador()
        elif opcion == "3":
            eliminar_jugador()
        elif opcion == "4":
            consultar_jugador()
        elif opcion == "5":
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

def crear_jugador():
    conn = conectar_db()
    cursor = conn.cursor()

    nombre_usuario = input("Ingresa el nombre de usuario del jugador: ")
    nivel = int(input("Ingresa el nivel del jugador: "))
    puntuacion = int(input("Ingresa la puntuación del jugador: "))
    equipo = input("Ingresa el equipo del jugador: ")

 
    query = """
    INSERT INTO jugadores (nombre_usuario, nivel, puntuacion, equipo)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (nombre_usuario, nivel, puntuacion, equipo))
    conn.commit()
    print(f"Jugador {nombre_usuario} creado exitosamente.")

    cursor.close()
    conn.close()

def modificar_jugador():
    conn = conectar_db()
    cursor = conn.cursor()

    nombre_usuario = input("Ingresa el nombre del jugador a modificar: ")
    nuevo_nombre_usuario = input("Ingresa el nuevo nombre de usuario (o presiona Enter para no cambiarlo): ")
    nivel = input("Ingresa el nuevo nivel (o presiona Enter para no cambiarlo): ")
    puntuacion = input("Ingresa la nueva puntuación (o presiona Enter para no cambiarlo): ")
    equipo = input("Ingresa el nuevo equipo (o presiona Enter para no cambiarlo): ")

    set_clause = []
    params = []

    if nuevo_nombre_usuario:
     set_clause.append("nombre_usuario = %s")
     params.append(nuevo_nombre_usuario)
    if nivel:
     set_clause.append("nivel = %s")
     params.append(int(nivel))
    if puntuacion:
     set_clause.append("puntuacion = %s")
     params.append(int(puntuacion))
    if equipo:
     set_clause.append("equipo = %s")
     params.append(equipo)

    if set_clause:
        query = f"UPDATE jugadores SET {', '.join(set_clause)} WHERE nombre_usuario = %s"
        params.append(nombre_usuario)
        cursor.execute(query, tuple(params))
        conn.commit()
        print(f"Jugador con nombre {nombre_usuario} modificado exitosamente.")

    cursor.close()
    conn.close()

def eliminar_jugador():
    conn = conectar_db()
    cursor = conn.cursor()

    nombre_usuario = input("Ingresa el nombre del jugador a eliminar: ")
    
    query = "DELETE FROM jugadores WHERE nombre_usuario = %s"
    cursor.execute(query, (nombre_usuario,))
    conn.commit()

    print(f"Jugador con nombre {nombre_usuario} eliminado exitosamente.")

    cursor.close()
    conn.close()

def consultar_jugador():
    conn = conectar_db()
    cursor = conn.cursor()

    nombre_usuario = input("Ingresa el nombre del jugador a consultar: ")

    query = "SELECT * FROM jugadores WHERE nombre_usuario = %s"
    cursor.execute(query, (nombre_usuario,))
    jugador = cursor.fetchone()

    if jugador:
        print(f"Jugador encontrado: {jugador}")
    else:
        print(f"No se encontró un jugador con nombre {nombre_usuario}.")

    cursor.close()
    conn.close()

def menu_mundos():
    while True:
        print("\nGestion de mundos")
        print("1. Crear mundo")
        print("2. Consultar mundos disponibles")
        print("3. Consultar la ruta mas optima de un mundo")
        print("4. Eliminar mundo")
        print("5. Salir")

        opcion = input("Elige una opcion: ")

        if opcion == "1":
            crear_mundo_virtual()
        elif opcion == "2":
            consultas_mundos_disponibles()
        elif opcion == "3":
            encontrar_ruta_mas_corta()
        elif opcion == "4":
            eliminar_mundo()
        elif opcion == "5":
            break
        else:
            print("Opcion no valida. Intenta de nuevo.")

def crear_mundo_virtual():
    conn = conectar_db()
    cursor = conn.cursor()

    try:
        cantidad_ubicaciones = int(input("Ingresa la cantidad de ubicaciones: "))
        cantidad_conexiones = cantidad_ubicaciones

        grafo = {}

        for i in range(cantidad_ubicaciones):
            ubicacion = input(f"Ingresa el nombre de la ubicación {i + 1 - 1}: ").strip().lower()
            if ubicacion in grafo:
                print(f"La ubicación '{ubicacion}' ya existe. Intenta con otro nombre.")
                return
            grafo[ubicacion] = {}

        for i in range(cantidad_conexiones):
            conexion = input(f"Ingresa la conexión {i+1} (formato: ubicacion{i+1-1}-ubicacion{i+1}:distancia): ").strip()
            try:
                ubicaciones, distancia = conexion.split(":")
                ubicacion1, ubicacion2 = [u.strip().lower() for u in ubicaciones.split("-")]

                distancia = int(distancia.strip())

                if ubicacion1 not in grafo or ubicacion2 not in grafo:
                    print(f"Una de las ubicaciones '{ubicacion1}' o '{ubicacion2}' no existe. Verifica y vuelve a intentarlo.")
                    return

                grafo[ubicacion1][ubicacion2] = distancia
                grafo[ubicacion2][ubicacion1] = distancia

            except ValueError:
                print(f"Error en la conexión {i + 1}, formato incorrecto. Asegúrate de ingresar en el formato adecuado.")
                return

        try:
            grafo_json = json.dumps(grafo)
        except json.JSONDecodeError:
            print("Error al serializar el grafo.")
            return

        query = """
        INSERT INTO mundos (grafo_serializado)
        VALUES (%s)
        """
        cursor.execute(query, (grafo_json,))
        conn.commit()

        print("Mundo virtual creado exitosamente.")
        print("Grafo guardado:", grafo)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    finally:
        cursor.close()
        conn.close()

def consultas_mundos_disponibles():
    conn = conectar_db()
    cursor = conn.cursor()

    query = "SELECT grafo_serializado FROM mundos;"
    cursor.execute(query)
    mundos = cursor.fetchall()

    print("Mundos disponibles:")
    for mundo in mundos:
        grafo_serializado = mundo[0]

        if isinstance(grafo_serializado, str):
            try:
                
                grafo = json.loads(grafo_serializado)
                
                for ubicacion, conexiones in grafo.items():
                    print(f"\nUbicación: {ubicacion}")
                    print("Conexiones:")
                    for conexion, distancia in conexiones.items():
                        print(f"  {conexion}: {distancia} km")
            except json.JSONDecodeError:
                print("Error al deserializar el grafo.")
        else:
            print("El grafo_serializado no es un string JSON válido.")

    cursor.close()
    conn.close()

def encontrar_ruta_mas_corta():
    conn = conectar_db()
    cursor = conn.cursor()

    try:
        try:
        # Consulta para obtener el grafo serializado de cada mundo
            cursor.execute("SELECT id, grafo_serializado FROM mundos")
            mundos = cursor.fetchall()

            if not mundos:
                print("No hay mundos disponibles. Crea uno primero.")
                return

            print("Mundos y sus conexiones:")
            for mundo in mundos:
                mundo_id, grafo_serializado = mundo
                print(f"\nMundo ID: {mundo_id}")

                # Convertir el grafo de JSON a un diccionario
                grafo = json.loads(grafo_serializado)

                for ubicacion, conexiones in grafo.items():
                    print(f"Ubicación: {ubicacion}")
                    if conexiones:
                        print("Conexiones:")
                        for destino, distancia in conexiones.items():
                            print(f"  {destino}: {distancia} km")
                    else:
                        print("Conexiones: Ninguna")
        except Exception as e:
            print(f"Error: {e}")


        mundo_id = int(input("Ingresa el ID del mundo que deseas usar: "))

        cursor.execute("SELECT grafo_serializado FROM mundos WHERE id = %s", (mundo_id,))
        result = cursor.fetchone()

        if not result:
            print("Mundo no encontrado.")
            return

        grafo = json.loads(result[0])

        punto_inicio = input("Ingresa el punto de inicio: ").strip().lower()
        punto_destino = input("Ingresa el punto de destino: ").strip().lower()

        if punto_inicio not in grafo or punto_destino not in grafo:
            print("Una de las ubicaciones no existe en el grafo.")
            return

 
        def dijkstra(grafo, inicio, destino):
            distancias = {nodo: float('inf') for nodo in grafo}
            distancias[inicio] = 0
            previo = {nodo: None for nodo in grafo}
            nodos_no_visitados = set(grafo.keys())

            while nodos_no_visitados:
                nodo_actual = min(nodos_no_visitados, key=lambda nodo: distancias[nodo])

                if distancias[nodo_actual] == float('inf'):
                    break

                nodos_no_visitados.remove(nodo_actual)

                for vecino, peso in grafo[nodo_actual].items():
                    nueva_distancia = distancias[nodo_actual] + peso
                    if nueva_distancia < distancias[vecino]:
                        distancias[vecino] = nueva_distancia
                        previo[vecino] = nodo_actual


            camino = []
            nodo = destino
            while nodo is not None:
                camino.insert(0, nodo)
                nodo = previo[nodo]

            return distancias[destino], camino

        distancia, camino = dijkstra(grafo, punto_inicio, punto_destino)

        if distancia == float('inf'):
            print("No hay ruta disponible entre los puntos especificados.")
        else:
            print(f"La distancia más corta de {punto_inicio} a {punto_destino} es: {distancia} km")
            print(f"El camino más corto es: {' -> '.join(camino)}")

    except Exception as e:
        print(f"Ocurrió un error: {e}")

    finally:
        cursor.close()
        conn.close() 

def dijkstra(grafo, origen, destino):
   
    origen = origen.lower()
    destino = destino.lower()

    pq = [(0, origen)]  

    distancias = {origen: 0}
 
    previos = {origen: None}

    while pq:
        
        distancia_actual, nodo_actual = heapq.heappop(pq)

        
        if nodo_actual == destino:
            camino = []
            while nodo_actual is not None:
                camino.insert(0, nodo_actual)
                nodo_actual = previos[nodo_actual]
            return distancias[destino], camino

        
        if distancia_actual > distancias.get(nodo_actual, float('inf')):
            continue

        
        for vecino, peso in grafo.get(nodo_actual, {}).items():
            distancia = distancia_actual + peso
            
            if distancia < distancias.get(vecino, float('inf')):
                distancias[vecino] = distancia
                previos[vecino] = nodo_actual
                heapq.heappush(pq, (distancia, vecino))

    return float('inf'), [] 

def eliminar_mundo():
    conn = conectar_db()
    cursor = conn.cursor()

    try:
        try:
        # Consulta para obtener el grafo serializado de cada mundo
            cursor.execute("SELECT id, grafo_serializado FROM mundos")
            mundos = cursor.fetchall()

            if not mundos:
                print("No hay mundos disponibles. Crea uno primero.")
                return

            print("Mundos y sus conexiones:")
            for mundo in mundos:
                mundo_id, grafo_serializado = mundo
                print(f"\nMundo ID: {mundo_id}")

                # Convertir el grafo de JSON a un diccionario
                grafo = json.loads(grafo_serializado)

                for ubicacion, conexiones in grafo.items():
                    print(f"Ubicación: {ubicacion}")
                    if conexiones:
                        print("Conexiones:")
                        for destino, distancia in conexiones.items():
                            print(f"  {destino}: {distancia} km")
                    else:
                        print("Conexiones: Ninguna")
        except Exception as e:
            print(f"Error: {e}")

        # Solicitar al usuario el ID del mundo a eliminar
        mundo_id = int(input("Ingresa el ID del mundo que deseas eliminar: "))

        # Verificar si el mundo existe
        cursor.execute("SELECT id FROM mundos WHERE id = %s", (mundo_id,))
        result = cursor.fetchone()

        if not result:
            print("El mundo con ese ID no existe.")
            return

        # Eliminar el mundo
        cursor.execute("DELETE FROM mundos WHERE id = %s", (mundo_id,))
        conn.commit()
        print(f"Mundo con ID {mundo_id} eliminado correctamente.")

    except Exception as e:
        print(f"Error al eliminar el mundo: {e}")
    finally:
        cursor.close()
        conn.close()

def menu_partidas():
    while True:
        print("\nGestion de partidas")
        print("1. registrar partida")
        print("2. Consultar partidas")
        print("3. Salir")

        opcion = input("Elige una opcion: ")

        if opcion == "1":
            registrar_partida()
        elif opcion == "2":
            consultar_partidas()
        elif opcion == "3":
            break
        else:
            print("Opcion no valida")

def registrar_partida():
    conn = conectar_db()
    cursor = conn.cursor()

    equipo1 = input("Ingresa el nombre del primer equipo: ")
    equipo2 = input("Ingresa el nombre del segundo equipo: ")
    resultado = input("Ingresa el resultado (gana equipo1, gana equipo2, empate): ")
    fecha = input("Ingresa la fecha de la partida (YYYY-MM-DD): ")

    query = """
    INSERT INTO partidas (fecha, equipo1, equipo2, resultado)
    VALUES (%s, %s, %s, %s)
    """
    cursor.execute(query, (fecha, equipo1, equipo2, resultado))
    conn.commit()

    print(f"Partida registrada exitosamente entre {equipo1} y {equipo2}. Resultado: {resultado}")

   
    cursor.callproc('registrar_partida', [equipo1, equipo2, resultado, fecha])
    
    conn.commit()

    cursor.close()
    conn.close()

def consultar_partidas():
    conn = conectar_db()
    cursor = conn.cursor()

    fecha_inicio = input("Ingresa la fecha de inicio (YYYY-MM-DD): ")
    fecha_fin = input("Ingresa la fecha de fin (YYYY-MM-DD): ")

    query = "SELECT * FROM partidas WHERE fecha BETWEEN %s AND %s"
    cursor.execute(query, (fecha_inicio, fecha_fin))
    partidas = cursor.fetchall()

    if partidas:
        print("Partidas encontradas:")
        for partida in partidas:
            print(partida)
    else:
        print("No se encontraron partidas en ese rango de fechas.")

    cursor.close()
    conn.close()

def menu_inventario():
    while True:
        print("\nMenú Inventario:")
        print("1. agregar inventario")
        print("2. consultar inventario")
        print("3. Salir")
        
        opcion = input("Elige una opción: ")

        if opcion == "1":
            agregar_inventario()
        elif opcion == "2":
            consultar_inventario()
        elif opcion == "3":
            break
        else:
            print("Opcion invalida")

def agregar_inventario():
    conn = conectar_db()
    cursor = conn.cursor()

    nombre_usuario = input("Ingresa el nombre del jugador para agregar su inventario: ")
    nombre_item = input("Ingresa el nombre del ítem: ")
    
    valor_hash_item = obtener_valor_hash_numerico(nombre_item)

    cursor.execute("SELECT inventario FROM jugadores WHERE id = %s", (nombre_usuario,))
    inventario_actual = cursor.fetchone()

    if inventario_actual:

        inventario = inventario_actual[0]
        inventario += f', "{nombre_item}": {valor_hash_item}' 
    else:
     
        inventario = f'{{"{nombre_item}": {valor_hash_item}}}'

    query = "UPDATE jugadores SET inventario = %s WHERE nombre_usuario = %s"
    cursor.execute(query, (inventario, nombre_usuario))

    conn.commit()

    print(f"Ítem '{nombre_item}' con índice {valor_hash_item} agregado al inventario del jugador {nombre_usuario}.")

    cursor.close()
    conn.close()

def consultar_inventario():
    conn = conectar_db()
    cursor = conn.cursor()
   
    nombre_usuario = input("Ingrese el nombre del jugador que desea consultar: ")
    cursor.execute("SELECT inventario FROM jugadores WHERE nombre_usuario = %s", (nombre_usuario,))
    inventario = cursor.fetchone()
    
   
    if inventario:
        print(f"El inventario del jugador {nombre_usuario} es:")
        print(inventario)  
    else:
        print(f"No se encontró ningún jugador con el nombre {nombre_usuario}")
    
    cursor.close()
    conn.close()


def obtener_valor_hash_numerico(item):
    
    hash_objeto = hashlib.md5()
    hash_objeto.update(item.encode())
    hash_hex = hash_objeto.hexdigest()
    valor_hash = int(hash_hex, 16)
    valor_hash_pequeno = valor_hash % 10000  
    return valor_hash_pequeno

def consultar_jugadores_por_puntuacion():
    conn = conectar_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            SELECT j.nombre_usuario, j.nivel, j.puntuacion, j.equipo
            FROM jugadores j
            ORDER BY j.puntuacion DESC
        """)
        jugadores = cursor.fetchall()

        if not jugadores:
            print("No hay jugadores registrados.")
            return

        
        print("Jugadores registrados (ordenados por puntuación):")
        print(f"{'Jugador':<20}{'Nivel':<10}{'Puntuación':<10}{'Equipo':<20}")
        print("-" * 60)
        for nombre_usuario, nivel, puntuacion, equipo in jugadores:
            equipo = equipo if equipo else "Sin equipo"  
            print(f"{nombre_usuario:<20}{nivel:<10}{puntuacion:<10}{equipo:<20}")

    except mysql.connector.Error as e:
        print(f"Error al consultar los jugadores: {e}")

    finally:
        cursor.close()
        conn.close()