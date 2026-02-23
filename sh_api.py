from fastapi import FastAPI, HTTPException
from sh_core import DeviceFactory
from sh_db import DatabaseHandler
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from work_simulation import Simulator
import threading
import json


load_dotenv()

app = FastAPI(title="Smart Home API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


db = DatabaseHandler(
    db_name=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST", "localhost")
)

active_devices = db.load_all_devices(DeviceFactory)


simulator = Simulator(db, active_devices)

def start_simulation():
    simulator.run(interval=10)

threading.Thread(target=start_simulation, daemon=True).start()



@app.get("/")
def read_root():
    return {"message": "Welcome to Smart Home API", "status": "online"}


@app.post("/devices/create/{device_type}")
def create_device(device_type: str, name: str):
    try:
        device = DeviceFactory.create(device_type, index=1, mods={"name": name})
        db.add_device(device)
        active_devices[device.id] = device
        return {"status": "created", "device": device.get_state()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/devices")
def list_devices():
    return {d_id: dev.get_state() for d_id, dev in active_devices.items()}


@app.post("/devices/{device_id}/turn_on")
def turn_on(device_id: int):
    if device_id not in active_devices:
        raise HTTPException(status_code=404, detail="Device not found in active session")

    device = active_devices[device_id]
    device.turn_on()
    db.update_device(device)
    return {"status": "success", "device": device.get_state()}


@app.post("/devices/{device_id}/vacuum/clean")
def start_cleaning(device_id: int):
    device = active_devices.get(device_id)
    if not device or device.device_type() != 'vacuum_cleaner':
        raise HTTPException(status_code=400, detail="Not a vacuum cleaner")

    try:
        device.start_cleaning()
        db.update_device(device)
        return {"status": "cleaned", "charge": device.charge}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

'''
@app.patch("/devices/{device_id}/update")
async def update_device_params(device_id: int, mods: dict):
    if device_id not in active_devices:
        raise HTTPException(status_code=404, detail="Device not found")

    device = active_devices[device_id]
    try:
        device.apply_mods(mods)
        db.update_device(device)
        return {"status": "success", "device": device.get_state()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))'''


@app.patch("/devices/{device_id}/update")
async def update_device_params(device_id: int, mods: dict):
    if device_id not in active_devices:
        raise HTTPException(status_code=404, detail="Device not found")

    device = active_devices[device_id]

    forbidden_fields = {'id', 'did', 'type', 'name'}

    clean_mods = {
        k: v for k, v in mods.items()
        if hasattr(device, k) and k not in forbidden_fields
    }

    try:
        device.apply_mods(clean_mods)
        db.update_device(device)
        return {"status": "success", "device": device.get_state()}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/devices/{device_id}/turn_off")
def turn_off(device_id: int):
    if device_id not in active_devices:
        raise HTTPException(status_code=404, detail="Device not found")

    device = active_devices[device_id]
    device.turn_off()
    db.update_device(device)

    return {"status": "success", "device": device.get_state()}



#MODS
@app.post("/scenarios/save")
def save_scenario(data: dict):
    # data: {"name": "My Party", "configs": [{"id": 1, "power": true, "brightness": 20}, ...]}
    db.add_scenario(data['name'], data['configs'])
    return {"status": "Scenario saved"}


@app.post("/scenarios/run/{name}")
def run_custom_scenario(name: str):

    db.cursor.execute("SELECT configs FROM scenarios WHERE name = %s", (name,))
    result = db.cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Scenario not found")

    configs = result[0]

    for item in configs:
        dev_id = item.get('id')
        if dev_id in active_devices:
            device = active_devices[dev_id]


            device.apply_mods(item)


            db.update_device(device)

    return {"status": f"Scenario {name} applied"}


@app.get("/scenarios")
def get_all_scenarios():
    rows = db.get_scenarios()
    return [{"name": row[0], "configs": row[1]} for row in rows]


@app.delete("/scenarios/{name}")
def delete_scenario(name: str):
    try:
        db.cursor.execute("DELETE FROM scenarios WHERE name = %s", (name,))
        return {"status": "Deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/devices/{device_id}/stats")
def get_stats(device_id: int):
    db.cursor.execute("""
        SELECT timestamp, temperature, brightness, charge
        FROM device_logs
        WHERE device_id = %s
        ORDER BY timestamp DESC
        LIMIT 100
    """, (device_id,))

    rows = db.cursor.fetchall()

    return [
        {
            "time": str(r[0]),
            "temperature": r[1],
            "brightness": r[2],
            "charge": r[3]
        }
        for r in rows
    ]




#WORK SIMULATION
@app.get("/simulations")
def get_simulations():
    db.cursor.execute("SELECT * FROM simulations;")
    rows = db.cursor.fetchall()

    simulations = []
    for r in rows:
        simulations.append({
            "id": r[0],
            "name": r[1],
            "configs": r[2]
        })

    return simulations


@app.post("/simulations")
def add_simulation(data: dict):
    """
    data: {"name": "Morning Routine", "configs": [{"id": 1, "power": True, "brightness": 30}, ...]}
    """
    try:
        db.cursor.execute(
            "INSERT INTO simulations (name, configs) VALUES (%s, %s) RETURNING id;",
            (data['name'], json.dumps(data['configs']))
        )
        new_id = db.cursor.fetchone()[0]
        db.conn.commit()
        return {"status": "created", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/simulations/{sim_id}")
def delete_simulation(sim_id: int):
    try:
        db.cursor.execute("DELETE FROM simulations WHERE id = %s;", (sim_id,))
        db.conn.commit()
        return {"status": "deleted", "id": sim_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulations/run/{sim_id}")
def run_simulation(sim_id: int):
    db.cursor.execute("SELECT configs FROM simulations WHERE id = %s;", (sim_id,))
    result = db.cursor.fetchone()
    if not result:
        raise HTTPException(status_code=404, detail="Simulation not found")

    configs = result[0]
    for item in configs:
        dev_id = item.get('id')
        if dev_id in active_devices:
            device = active_devices[dev_id]
            device.apply_mods(item)
            db.update_device(device)

    return {"status": f"Simulation {sim_id} applied"}


