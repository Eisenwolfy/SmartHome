# Smart Home OS

Smart Home OS is a **modern smart home management platform** that lets you control, monitor, and simulate devices in real-time—all from a sleek web dashboard.

---

## Features

- Real-time device simulation (temperature, brightness, charge, CO2 levels, etc.)
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

## Installation & Usage

1. Configure PostgreSQL and create a database
2. Set environment variables in `.env`
3. Reset database (optional):
   ```bash
   python db_reset.py
