import psycopg2
import json

class DatabaseHandler:
    def __init__(self, db_name, user, password, host="localhost", port="5432"):
        try:
            self.conn = psycopg2.connect(
                dbname = db_name,
                user = user,
                password = password,
                host = host,
                port = port
            )
            self.conn.autocommit = True
            self.cursor = self.conn.cursor()
            self.create_table()
            print("Connection to DB successful")
        except Exception as e:
            print(f"Connection failed: {e}")


    def load_all_devices(self, factory):
        self.cursor.execute("SELECT id, name, type, power, params FROM devices;")
        rows = self.cursor.fetchall()

        devices_dict = {}
        for row in rows:
            did, name, d_type, power, params = row
            mods = {"name": name, "power": power, "did": did}
            if params:
                mods.update(params)

            device = factory.create(d_type, index=None, mods=mods)
            devices_dict[did] = device
        return devices_dict


    def create_table(self):
        #DEVICES
        query_devices = """
        CREATE TABLE IF NOT EXISTS devices (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            type VARCHAR(50) NOT NULL,
            power BOOLEAN DEFAULT FALSE,
            params JSONB
        );
        """
        self.cursor.execute(query_devices)

        #SCENARIOS
        query_scenarios = """
        CREATE TABLE IF NOT EXISTS scenarios (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            configs JSONB NOT NULL  -- : [{id: 1, action: "brightness", value: 30}, ...]
        );
        """
        self.cursor.execute(query_scenarios)

        #DEVICE LOGS
        query_logs = """
        CREATE TABLE IF NOT EXISTS device_logs (
            id SERIAL PRIMARY KEY,
            device_id INT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            power BOOLEAN,
            brightness INT,
            volume INT,
            temperature FLOAT,
            charge FLOAT,
            co2_lvl FLOAT,
            filter_life INT,
            FOREIGN KEY (device_id) REFERENCES devices(id) ON DELETE CASCADE
        );
        """
        self.cursor.execute(query_logs)

#SAVING DEVICE IN DB
    def add_device(self, device):
        state = device.get_state()

        exclude = {'id', 'name', 'type', 'power'}
        params = {k: v for k, v in state.items() if k not in exclude}

        query = """
        INSERT INTO devices (name, type, power, params)
        VALUES (%s, %s, %s, %s)
        RETURNING id;
        """

        try:
            self.cursor.execute(query, (state['name'], state['type'], state['power'], json.dumps(params)))
            new_id = self.cursor.fetchone()[0]
            device.id = new_id
            print(f"Saved {device.name} with ID: {new_id}")
        except Exception as e:
            print(f"Error saving device: {e}")

    def update_device(self, device):
        if device.id is None:
            print(f"Cannot update {device.name}: No ID (save it first).")
            return

        state = device.get_state()
        exclude = {'id', 'name', 'type', 'power'}
        params = {k: v for k, v in state.items() if k not in exclude}

        query = """
        UPDATE devices 
        SET power = %s, params = %s
        WHERE id = %s;
        """
        try:
            self.cursor.execute(query, (state['power'], json.dumps(params), device.id))
            print(f"Updated DB for {device.name} (ID: {device.id})")

            #LOGGING DEVICE STATE
            self.log_device_state(device)

        except Exception as e:
            print(f"Error updating: {e}")

    def log_device_state(self, device):
        state = device.get_state()
        query = """
        INSERT INTO device_logs (
            device_id, power, brightness, volume, temperature, charge, co2_lvl, filter_life
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """
        self.cursor.execute(
            query,
            (
                device.id,
                state.get("power"),
                state.get("brightness"),
                state.get("volume"),
                state.get("temperature"),
                state.get("charge"),
                state.get("co2_lvl"),
                state.get("filter_life")
            )
        )

    def close(self):
        self.cursor.close()
        self.conn.close()
