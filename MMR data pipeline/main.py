from pymetawear.client import MetaWearClient
#from model import BodyAccX, BodyAccY, BodyAccZ, BodyGyroX, BodyGyroY, BodyGyroZ
import time
import pyodbc
import pandas as pd
import os, uuid, sys
from datetime import datetime as dt
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from pymetawear.discover import select_device
from utils import stream_data


# Connect to SQL Server
#conn = pyodbc.connect(DATABASE_URI)
#cursor = conn.cursor()


def record_data(label: str, device: MetaWearClient, time_: int) -> None:
    """
    This function commits the data streamed to the database
    :param label:
    :param device:
    :return None:
    """
    print(f"Logging data for {label}")
    acc, gyr = stream_data(device=device, time_=time_)
    print("Finished!")
    
    #Getting filename 
    now = dt.now()
    dt_string = now.strftime("%Y-%m-%dT%H.%M.%S")
    acc_file_name = label+'_'+dt_string+'_'+'accelerometer'+'.csv'
    gyr_file_name = label+'_'+dt_string+'_'+'gyroscope'+'.csv'
    
    #Write dataframe in csv
    #Set path to where you are storing the data as a Environment variable like C:\\Users\\User\\Desktop\\PROJECT\\Sensor_data\\
    #Then GET the path
    acc_path = os.environ.get('ACC_PATH') 
    acc_data_path = acc_path + acc_file_name

    gyr_path = os.environ.get('GYR_PATH') 
    gyr_data_path = gyr_path + gyr_file_name

    #Convert pandaframes to CSV files
    acc.to_csv(acc_data_path, index=False)
    gyr.to_csv(gyr_data_path, index=False)
    
    
    #Create Client
    CONN = os.environ.get('CONN_STRING')
    service = BlobServiceClient.from_connection_string(conn_str=CONN)
    
    #Upload Blob
    #Accelorometer
    container_name = label
    blob_name = 'acc/'+acc_file_name
    blob = BlobClient.from_connection_string(conn_str=CONN, container_name = container_name, blob_name = blob_name)
    
    data_path = r'{}'.format(acc_data_path)
    with open(data_path, "rb") as data:
            blob.upload_blob(data)
    
    
    #Gyroscope
    blob_name = 'gyr/'+gyr_file_name
    blob = BlobClient.from_connection_string(conn_str=CONN, container_name = container_name, blob_name = blob_name)
    
    data_path = r'{}'.format(gyr_data_path)
    with open(data_path, "rb") as data:
            blob.upload_blob(data)
    
    print("Sucessfully uploaded!")
    
    os.remove(acc_data_path)
    os.remove(gyr_data_path)


def run() -> None:
    """
    Starts the program
    :return None:
    """
    # Create a MetaWear device
    address = select_device()
    d = MetaWearClient(str(address))

    proceed = True

    prompt = """
    \nChoose a number for an exercise below
    1. Standing
    2. Walking
    3. Sitting
    4. Laying Down
    """

    while proceed:
        exercise = int(input(prompt))

        while exercise not in [1, 2, 3, 4]:
            exercise = int(input(prompt))

        if exercise == 1:
            action = 'standing'
        elif exercise == 2:
            action = 'walking'
        elif exercise == 3:
            action = 'sitting'
        else:
            action = 'laying'
            
        time_ = int(input(f"\nEnter Seconds You'll do {action}:\n"))
        # time_ = 60

        # Start to stream and record data
        try:
            record_data(label=action, device=d, time_=time_)
            choice = input('Continue or exit\n1. Continue\n2. Exit\n')
            if choice != '1':
                print("Exiting...")
                proceed = False
        except Exception as message:
            print("Commit to storage failed terribly due to\n", message)
            choice = input('Repeat or exit\n1. Repeat\n2. Exit\n')
            if choice != '1':
                print("Exiting...")
                proceed = False

        # Disconnect device
    d.disconnect()


run()
