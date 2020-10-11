from pymetawear.client import MetaWearClient
#from model import BodyAccX, BodyAccY, BodyAccZ, BodyGyroX, BodyGyroY, BodyGyroZ
import time
import pyodbc
import pandas as pd
import os, uuid, sys
from datetime import datetime as dt
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from pymetawear.discover import select_device
from utils import conn, stream_data

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
    acc_file_name = label+'_'+dt_string+'accelerometer'+'.csv'
    gyr_file_name = label+'_'+dt_string+'gyroscope'+'.csv'
    
    #Write dataframe in csv
    acc_csv = acc.to_csv(acc_file_name, index=False)
    gyr_csv = gyr.to_csv(gyr_file_name, index=False)
    
    #Create Client
    CONN = "your_connection_string"
    service = BlobServiceClient.from_connection_string(conn_str=CONN)
    
    #Upload Blob
    #Accelorometer
    container_name = label
    blob_name = 'acc/'+acc_file_name
    blob = BlobClient.from_connection_string(conn_str=CONN, container_name=container_name, blob_name=blob_name)
    #Gyroscope
    blob.upload_blob(acc_csv)
    blob_name = 'gyr/'+gyr_file_name
    blob = BlobClient.from_connection_string(conn_str=CONN, container_name=container_name, blob_name=blob_name)
    blob.upload_blob(acc_gyr)
    
    print("Sucessfully uploaded!")
    


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
    1. Walking
    2. Sitting
    3. Matching
    4. Body Stretch(Arms)
    """

    while proceed:
        exercise = int(input(prompt))

        while exercise not in [1, 2, 3, 4]:
            exercise = int(input(prompt))

        if exercise == 1:
            action = 'walking'
        elif exercise == 2:
            action = 'sitting'
        elif exercise == 3:
            action = 'matching'
        else:
            action = 'body stretch'

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
            print("Commit to database failed terribly due to\n", message)
            choice = input('Repeat or exit\n1. Repeat\n2. Exit\n')
            if choice != '1':
                print("Exiting...")
                proceed = False

        # Disconnect device
    d.disconnect()


run()
