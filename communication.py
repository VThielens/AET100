from pymodbus.client import ModbusSerialClient
import csv
import time

# Configuration du client Modbus RTU
client = ModbusSerialClient(
    port='COM1',     # remplace par ton port (ex: /dev/ttyUSB0 sous Linux)
    baudrate=19200,
    timeout=1,
    parity='N',
    stopbits=2,
    bytesize=8
)

if not client.connect():
    print("Erreur de connexion au périphérique Modbus")
    exit(1)

# Fichier CSV pour logger les données
with open("log_modbus.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Coil_1", "Coil_2", "Coil_3", "Coil_4"])  # adapte au nombre de sorties

    try:
        while True:
            rr = client.read_holding_registers(513, count=50, device_id=1)  # lire 4 coils à partir de l’adresse 0 de l’esclave 1
            if rr.isError():
                print("Erreur lecture Modbus")
            else:
                values = rr.bits
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                writer.writerow([timestamp] + values)
                print(timestamp, values)

            time.sleep(1)  # intervalle d’échantillonnage
    except KeyboardInterrupt:

        print("Arrêt du logging")

client.close()
