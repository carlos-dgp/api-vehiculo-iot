import asyncio
import websockets

async def escuchar_vehiculo():
    uri = "ws://127.0.0.1:8000/ws/vehiculos/1"
    print(f"Intentando conectar a {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("¡Conectado al WebSocket del vehículo 1 con éxito!")
            while True:
                mensaje = await websocket.recv()
                print(f"\n[EVENTO RECIBIDO]: {mensaje}")
    except Exception as e:
        print(f"Error en la conexión WebSocket: {e}")

if __name__ == "__main__":
    asyncio.run(escuchar_vehiculo())