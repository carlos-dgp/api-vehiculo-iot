import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from database import Database
from services.vehiculo_service import VehiculoService
from services.websocket_manager import manager

app = FastAPI(title="API IoT Vehículo", version="1.0")

# Modelos para recibir los datos de las peticiones
class MovimientoRequest(BaseModel):
    vehiculo_id: int
    comando_id: int

class ComandoRequest(BaseModel):
    vehiculo_id: int
    nombre_comando: str
    codigo_accion: int
    descripcion: str

class ComandoUpdateRequest(BaseModel):
    descripcion: str
    tipo: str

class EstadoRequest(BaseModel):
    ultimo_comando_id: int
    en_linea: int

class DemoRequest(BaseModel):
    vehiculo_id: int
    nombre: str
    descripcion: str

class VehiculoRequest(BaseModel):
    nombre: str
    modelo: str
    descripcion: str
    tipo_conexion: str

class VehiculoUpdateRequest(BaseModel):
    placa: str
    modelo: str
    estado: str

class MovimientoDemoUpdateRequest(BaseModel):
    vehiculo_id: int
    comando_id: int

class HistorialRequest(BaseModel):
    vehiculo_id: int
    comando_id: int
    origen: str

class DemoEjecucionRequest(BaseModel):
    vehiculo_id: int
    demo_id: int

@app.get("/")
def read_root():
    return {"mensaje": "API de Vehículo IoT funcionando correctamente en entorno de desarrollo"}

@app.get("/probar-conexion")
def test_connection():
    try:
        db = Database()
        connection = db.get_connection()
        connection.close()
        return {"estado": "Conexión exitosa a Amazon RDS"}
    except Exception as e:
        return {"estado": "Error de conexión", "detalle": str(e)}

@app.get("/vehiculos")
def listar_vehiculos():
    try:
        vehiculos = VehiculoService.obtener_todos()
        return {"vehiculos": vehiculos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos/{vehiculo_id}")
def obtener_vehiculo(vehiculo_id: int):
    try:
        vehiculo = VehiculoService.obtener_por_id(vehiculo_id)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="Vehículo no encontrado")
        return {"vehiculo": vehiculo}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vehiculos/movimiento")
def crear_movimiento(request: MovimientoRequest):
    try:
        vehiculo = VehiculoService.obtener_por_id(request.vehiculo_id)
        if not vehiculo:
            raise HTTPException(status_code=404, detail="El vehículo no existe o no está activo")
        
        resultado = VehiculoService.registrar_movimiento(request.vehiculo_id, request.comando_id)
        return {"mensaje": "Transacción confirmada en RDS", "resultado": resultado}
    
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos/{vehiculo_id}/comandos")
def listar_comandos_vehiculo(vehiculo_id: int):
    try:
        comandos = VehiculoService.obtener_comandos(vehiculo_id)
        return {"vehiculo_id": vehiculo_id, "comandos": comandos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos/{vehiculo_id}/estado")
def obtener_estado_vehiculo(vehiculo_id: int):
    try:
        estado = VehiculoService.obtener_estado(vehiculo_id)
        if not estado:
            raise HTTPException(status_code=404, detail="Estado no encontrado para el vehículo")
        return {"vehiculo_id": vehiculo_id, "estado": estado}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vehiculos/{vehiculo_id}/historial")
def obtener_historial_vehiculo(vehiculo_id: int):
    try:
        historial = VehiculoService.obtener_historial(vehiculo_id)
        return {"vehiculo_id": vehiculo_id, "historial": historial}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINTS PARA COMANDOS Y DEMOS ---

@app.post("/comandos")
def crear_comando(request: ComandoRequest):
    try:
        return VehiculoService.crear_comando(request.vehiculo_id, request.nombre_comando, request.codigo_accion, request.descripcion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/comandos")
def listar_comandos():
    try:
        return {"comandos": VehiculoService.obtener_comandos_global()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/comandos/{comando_id}")
def actualizar_comando(comando_id: int, request: ComandoUpdateRequest):
    try:
        return VehiculoService.actualizar_comando(comando_id, request.descripcion, request.tipo)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/comandos/{comando_id}")
def eliminar_comando(comando_id: int):
    try:
        return VehiculoService.eliminar_comando(comando_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/vehiculos/{vehiculo_id}/estado")
def actualizar_estado_vehiculo(vehiculo_id: int, request: EstadoRequest):
    try:
        return VehiculoService.actualizar_estado(vehiculo_id, request.ultimo_comando_id, request.en_linea)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/demos")
def crear_demo(request: DemoRequest):
    try:
        return VehiculoService.crear_demo(request.vehiculo_id, request.nombre, request.descripcion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/demos/{vehiculo_id}")
def listar_demos(vehiculo_id: int):
    try:
        return {"demos": VehiculoService.obtener_demos(vehiculo_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/demos/{demo_id}")
def actualizar_demo(demo_id: int, request: DemoRequest):
    try:
        return VehiculoService.actualizar_demo(demo_id, request.nombre, request.descripcion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/demos/{demo_id}")
def eliminar_demo(demo_id: int):
    try:
        return VehiculoService.eliminar_demo(demo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- ENDPOINTS PARA LOS PROCEDIMIENTOS ---

@app.post("/vehiculos")
def crear_vehiculo(request: VehiculoRequest):
    try:
        return VehiculoService.crear_vehiculo(request.nombre, request.modelo, request.descripcion, request.tipo_conexion)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/vehiculos/{vehiculo_id}")
def actualizar_vehiculo(vehiculo_id: int, request: VehiculoUpdateRequest):
    try:
        return VehiculoService.actualizar_vehiculo(vehiculo_id, request.placa, request.modelo, request.estado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vehiculos/{vehiculo_id}")
def eliminar_vehiculo(vehiculo_id: int):
    try:
        return VehiculoService.eliminar_vehiculo(vehiculo_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/movimientos-demo")
def listar_movimientos_demo():
    try:
        return {"movimientos_demo": VehiculoService.obtener_movimientos_demo()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/movimientos-demo/{movimiento_id}")
def actualizar_movimiento_demo(movimiento_id: int, request: MovimientoDemoUpdateRequest):
    try:
        return VehiculoService.actualizar_movimiento_demo(movimiento_id, request.vehiculo_id, request.comando_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/movimientos-demo/{movimiento_id}")
def eliminar_movimiento_demo(movimiento_id: int):
    try:
        return VehiculoService.eliminar_movimiento_demo(movimiento_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/historial")
def registrar_historial(request: HistorialRequest):
    try:
        return VehiculoService.registrar_historial(request.vehiculo_id, request.comando_id, request.origen)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- WEBSOCKET Y EJECUCIÓN DE DEMOS ---

@app.websocket("/ws/vehiculos/{vehiculo_id}")
async def websocket_endpoint(websocket: WebSocket, vehiculo_id: int):
    await manager.connect(vehiculo_id, websocket)
    try:
        estado = VehiculoService.obtener_estado(vehiculo_id)
        await websocket.send_json({
            "tipo_evento": "conexion_establecida",
            "vehiculo_id": vehiculo_id,
            "estado_actual": estado,
            "marca_temporal": datetime.utcnow().isoformat()
        })
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(vehiculo_id, websocket)

@app.post("/demos/ejecutar")
async def ejecutar_demo(request: DemoEjecucionRequest):
    try:
        movimientos = VehiculoService.obtener_movimientos_demo_por_id(request.demo_id)
        if not movimientos:
            raise HTTPException(status_code=404, detail="No se encontraron movimientos para la DEMO especificada")

        await manager.broadcast_to_vehicle(request.vehiculo_id, {
            "tipo_evento": "demo_inicio",
            "vehiculo_id": request.vehiculo_id,
            "demo_id": request.demo_id,
            "marca_temporal": datetime.utcnow().isoformat()
        })

        for mov in movimientos:
            duracion = mov.get("duracion_ms", 1000) / 1000.0
            pausa = mov.get("pausa_ms", 500) / 1000.0

            VehiculoService.actualizar_estado(request.vehiculo_id, mov.get('comando_id'), 1)

            await manager.broadcast_to_vehicle(request.vehiculo_id, {
                "tipo_evento": "movimiento_demo",
                "vehiculo_id": request.vehiculo_id,
                "comando_id": mov.get("comando_id"),
                "duracion_ms": mov.get("duracion_ms"),
                "marca_temporal": datetime.utcnow().isoformat()
            })

            await asyncio.sleep(duracion)
            await asyncio.sleep(pausa)

        await manager.broadcast_to_vehicle(request.vehiculo_id, {
            "tipo_evento": "demo_finalizacion",
            "vehiculo_id": request.vehiculo_id,
            "demo_id": request.demo_id,
            "marca_temporal": datetime.utcnow().isoformat()
        })

        return {"mensaje": "DEMO ejecutada y transmitida por WebSocket sin alterar el historial"}

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/test", response_class=HTMLResponse)
async def get_test_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Prueba WebSocket Vehículo</title>
    </head>
    <body>
        <h1>Monitoreo de Vehículo por WebSocket</h1>
        <div id="mensajes" style="background: #111; color: #0f0; padding: 15px; font-family: monospace; height: 300px; overflow-y: scroll;"></div>

        <script>
            const ws = new WebSocket("ws://localhost:8000/ws/vehiculos/1");
            const divMensajes = document.getElementById("mensajes");

            ws.onopen = function() {
                divMensajes.innerHTML += "<br>[Conexión establecida con éxito]";
            };

            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                divMensajes.innerHTML += `<br>Recibido: ${JSON.stringify(data)}`;
            };
        </script>
    </body>
    </html>
    """