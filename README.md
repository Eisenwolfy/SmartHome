# Smart Home OS

Smart Home OS is a **modern smart home management platform** that lets you control, monitor, and simulate devices in real-time—all from a sleek web dashboard.

---

## Features

- Real-time device simulation (temperature, brightness, charge, etc.)
- Device management: turn on/off, adjust brightness, volume, temperature
- Room management and device assignment
- Save and run **scenarios** and **custom user mods**
- Device statistics logging with charts
- Simple web-based interface

---

## Tech Stack

- Backend: Python, FastAPI, PostgreSQL
- Simulation engine: Python
- Frontend: HTML, CSS, JavaScript
- Charts: Chart.js for device stats

---

## Project Structure

1. `sh_core.py` – defines classes for all devices.  
2. `sh_errors.py` – defines special error types.  
3. `sh_db.py` – creates the database containing information about all devices, rooms, and scenarios.  
4. `db_reset.py` – resets the database if needed (optional).  
5. `work_simulation.py` – simulates the behavior of all devices.  
6. `sh_api.py` – handles API logic and communication between backend and frontend.  
7. `sh_main.py` – starts the FastAPI server and manages all API routes.  
8. `index.html` – frontend dashboard for interacting with the smart home system.
9. `.env.example` - example of your `.env` file.
10. 

---

## Installation & Usage

1. Configure PostgreSQL and create a database.
2. Set environment variables in `.env`, `.env.example` is an example for your `.env` file.
3. Reset database (optional):
   Before using this file you need to put password of your data base instead of "put your password here" in 6th line.
   ```bash
   python db_reset.py
5. Run `sh_main.py`
6. Open `index.html`
