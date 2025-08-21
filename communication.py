from pymodbus.client import ModbusSerialClient
import csv
import time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

FILE_MODBUS_READINGTABLE = r"MODBUS_ReadingTable.csv"
FILE_MODBUS_INTERNALSTATE = r"MODBUS_InternalState.csv"
FILE_MODBUS_STATUS = r"MODBUS_Status.csv"

SAVE_ADDRESS_RAW = "log_"+time.strftime("%Y_%m_%d_%H%M%S")+".csv"
SAVE_ADDRESS_CONVERTED = SAVE_ADDRESS_RAW[:-4]+"_treated.csv"

def unsigned_to_signed(value):
    if value >= 2**15:
        value_signed = value - 2**16
    else:
        value_signed = value
    return value_signed

def acquisition():
    # Configuration du client Modbus RTU
    client = ModbusSerialClient(
        port='COM1',     # COM Port virtually created
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
    with open(SAVE_ADDRESS_RAW, "w", newline="") as f:
        writer = csv.writer(f, delimiter=",")
        writer.writerow(["time"] + [513+i for i in range(50)])

        try:
            while True:
                # lecture des données
                rr = client.read_holding_registers(address = 513, count=50, device_id=1)
                # check if no error while reading
                if rr.isError():
                    print("Erreur lecture Modbus")
                else:
                    # convert bits
                    values = rr.registers
                    # take date of reading
                    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                    # write in the CSV file the date + data
                    writer.writerow([timestamp] + values)
                    # print on screen
                    print(timestamp, values)
                # sampling delay    
                time.sleep(1)
        except KeyboardInterrupt:
            print("Arrêt du logging")

    client.close()

def conversion_data():
    # read the Excel table with comparisons
    df_readingTable = pd.read_csv(FILE_MODBUS_READINGTABLE, delimiter=";", header=0, index_col=0)
    df_internalState = pd.read_csv(FILE_MODBUS_STATUS, delimiter=";", header=0, index_col=0)
    df_status = pd.read_csv(FILE_MODBUS_STATUS, delimiter=";", header=0, index_col=0)

    # read saved data
    df = pd.read_csv(SAVE_ADDRESS_RAW, header = 0, index_col=0)

    # decimal adress to index
    mapping_dictionnary =  {str(v): k for k, v in df_readingTable['Decimal address'].to_dict().items()}
    df.rename(columns= mapping_dictionnary, inplace=True)

    # add MultiIndex
    df.columns = pd.MultiIndex.from_frame(df_readingTable.reset_index()[['Index', 'Signal']])

    # change the status with table
    mapperInternal = df_internalState.to_dict()['Description']
    df['Status Code']=df[1].map(lambda x: mapperInternal[x])

    # change the internal status with table
    mapperDescription = df_status.to_dict()['Description']
    df['Status Description']=df[2].map(lambda x: mapperDescription[x])

    # delete the "Not used"
    index_not_used = df_readingTable.index[df_readingTable.Signal =="Not used"].tolist()
    df.drop(columns = index_not_used, inplace = True)

    # change the unsigned INT to signed INT
    list_index_int = df_readingTable.index[df_readingTable['Data type']=="INT"]
    for col in list_index_int:
        df[col] = df[col].map(unsigned_to_signed)

    df.to_csv(SAVE_ADDRESS_CONVERTED)

if __name__=='__main__':
    acquisition()
    #conversion_data()