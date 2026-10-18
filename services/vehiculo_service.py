from database import Database

class VehiculoService:
    @staticmethod
    def _ejecutar_consulta(query, params=None, fetch_one=False, commit=False):
        db = Database()
        connection = db.get_connection()
        try:
            cursor = connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if commit:
                connection.commit()
                resultado = {"estado": "Operación realizada exitosamente"}
            elif fetch_one:
                resultado = cursor.fetchone()
            else:
                resultado = cursor.fetchall()
            
            while cursor.nextset():
                pass
                
            cursor.close()
            return resultado
        except Exception as e:
            if commit:
                connection.rollback()
            print(f"--- ERROR EN BASE DE DATOS ---: {e}")
            raise e
        finally:
            connection.close()

    @staticmethod
    def obtener_todos():
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_vehiculos();")

    @staticmethod
    def obtener_por_id(vehiculo_id):
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_vehiculo(%s);", (vehiculo_id,), fetch_one=True)

    @staticmethod
    def registrar_movimiento(vehiculo_id, comando_id):
        return VehiculoService._ejecutar_consulta("CALL sp_agregar_movimiento_demo(%s, %s);", (vehiculo_id, comando_id), commit=True)

    @staticmethod
    def obtener_comandos(vehiculo_id):
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_comandos_vehiculo(%s);", (vehiculo_id,))

    @staticmethod
    def obtener_estado(vehiculo_id):
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_estado(%s);", (vehiculo_id,), fetch_one=True)

    @staticmethod
    def obtener_historial(vehiculo_id):
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_historial(%s);", (vehiculo_id,))

    # --- COMANDOS ---
    @staticmethod
    def crear_comando(vehiculo_id, nombre_comando, codigo_accion, descripcion):
        return VehiculoService._ejecutar_consulta("CALL sp_crear_comando(%s, %s, %s, %s);", (vehiculo_id, nombre_comando, codigo_accion, descripcion), commit=True)

    @staticmethod
    def obtener_comandos_global():
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_comandos();")

    @staticmethod
    def actualizar_comando(comando_id, descripcion, tipo):
        return VehiculoService._ejecutar_consulta("CALL sp_actualizar_comando(%s, %s, %s);", (comando_id, descripcion, tipo), commit=True)

    @staticmethod
    def eliminar_comando(comando_id):
        return VehiculoService._ejecutar_consulta("CALL sp_eliminar_comando(%s);", (comando_id,), commit=True)

    # --- ESTADO ---
    @staticmethod
    def actualizar_estado(vehiculo_id, ultimo_comando_id, en_linea):
        return VehiculoService._ejecutar_consulta("CALL sp_actualizar_estado(%s, %s, %s);", (vehiculo_id, ultimo_comando_id, en_linea), commit=True)

    # --- DEMOS ---
    @staticmethod
    def crear_demo(vehiculo_id, nombre, descripcion):
        return VehiculoService._ejecutar_consulta("CALL sp_crear_demo(%s, %s, %s);", (vehiculo_id, nombre, descripcion), commit=True)

    @staticmethod
    def obtener_demos(vehiculo_id):
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_demos(%s);", (vehiculo_id,))

    @staticmethod
    def actualizar_demo(demo_id, nombre, descripcion):
        return VehiculoService._ejecutar_consulta("CALL sp_actualizar_demo(%s, %s, %s);", (demo_id, nombre, descripcion), commit=True)

    @staticmethod
    def eliminar_demo(demo_id):
        return VehiculoService._ejecutar_consulta("CALL sp_eliminar_demo(%s);", (demo_id,), commit=True)

    # --- PROCEDIMIENTOS ADICIONALES Y DE MOVIMIENTOS DEMO ---
    @staticmethod
    def crear_vehiculo(nombre, modelo, descripcion, tipo_conexion):
        return VehiculoService._ejecutar_consulta("CALL sp_crear_vehiculo(%s, %s, %s, %s);", (nombre, modelo, descripcion, tipo_conexion), commit=True)

    @staticmethod
    def actualizar_vehiculo(vehiculo_id, placa, modelo, estado):
        return VehiculoService._ejecutar_consulta("CALL sp_actualizar_vehiculo(%s, %s, %s, %s);", (vehiculo_id, placa, modelo, estado), commit=True)

    @staticmethod
    def eliminar_vehiculo(vehiculo_id):
        return VehiculoService._ejecutar_consulta("CALL sp_eliminar_vehiculo(%s);", (vehiculo_id,), commit=True)

    @staticmethod
    def obtener_movimientos_demo():
        return VehiculoService._ejecutar_consulta("CALL sp_obtener_movimientos_demo();")

    @staticmethod
    def obtener_movimientos_demo_por_id(demo_id: int):
        db = Database()
        connection = db.get_connection()
        try:
            cursor = connection.cursor()
            cursor.callproc("sp_obtener_movimientos_demo", [demo_id])
            movimientos = []
            for result in cursor.stored_results():
                movimientos = result.fetchall()
            cursor.close()
            return movimientos
        except Exception as e:
            print(f"Error al obtener movimientos de demo: {e}")
            return []
        finally:
            connection.close()

    @staticmethod
    def actualizar_movimiento_demo(movimiento_id, vehiculo_id, comando_id):
        return VehiculoService._ejecutar_consulta("CALL sp_actualizar_movimiento_demo(%s, %s, %s);", (movimiento_id, vehiculo_id, comando_id), commit=True)

    @staticmethod
    def eliminar_movimiento_demo(movimiento_id):
        return VehiculoService._ejecutar_consulta("CALL sp_eliminar_movimiento_demo(%s);", (movimiento_id,), commit=True)

    @staticmethod
    def registrar_historial(vehiculo_id, comando_id, origen):
        return VehiculoService._ejecutar_consulta("CALL sp_registrar_historial(%s, %s, %s);", (vehiculo_id, comando_id, origen), commit=True)