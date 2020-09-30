#from pymetawear.client import MetaWearClient
#from model import BodyAccX, BodyAccY, BodyAccZ, BodyGyroX, BodyGyroY, BodyGyroZ
import pyodbc
import pandas as pd
from pymetawear.discover import select_device
#from utils import conn, stream_data

# Connect to SQL Server
conn = pyodbc.connect(DATABASE_URI)
cursor = conn.cursor()



def record_data(label: str, device: MetaWearClient) -> None:
    """
    This function commits the data streamed to the database
    :param label:
    :param device:
    :return None:
    """
    print(f"Logging data for {label}")
    acc, gyr = stream_data(device=device)
    print("Finished!")

    #Removing unnecessary columns 
    acc_df = acc(['elapsed (s)', 'time (06:00)'], axis = 1)
    gyr_df = gyr(['elapsed (s)', 'time (06:00)'], axis = 1)

    #Renaming columns
    acc_df.rename(columns = {'epoch (ms)': 'Epoch', 'x-axis (g)':'X_axis', 'y-axis (g)': 'Y_axis', 'z-axis (g)': 'Z_axis'}, inplace = True) 
    gyr_df.rename(columns = {'epoch (ms)': 'Epoch', 'x-axis (deg/s)':'X_axis', 'y-axis (deg/s)': 'Y_axis', 'z-axis (deg/s)': 'Z_axis'}, inplace = True) 

    #Add activity label
    acc_df =acc_df.assign(Label = label)
    gyr_df = gyr_df.assign(Label = label)
    
    # Create Table if one doesnt already exist
    cursor.execute('''
    IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES
           WHERE TABLE_NAME = N'body_acc_all')
    BEGIN
     CREATE TABLE body_acc_all (Epoch bigint, X_axis float, Y_axis float, Z_axis float, Label varchar(50))
    END '''
    )
    
    print(f"Committing {label} data to database...")
    
    # Insert DataFrame to Table
    for row in acc_df.itertuples():
        cursor.execute('''
                    INSERT INTO MmrSensorData.dbo.body_acc_all (Epoch, X_axis, Y_axis, Z_axis, Label)
                    VALUES (?,?,?,?,?)
                    ''',
                    row.Epoch, 
                    row.X_axis,
                    row.Y_axis,
                    row.Z_axis,
                    row.Label
                    )
    
    conn.commit()
    cursor.close()
    
    print("Finished!")
    
    cursor.close()


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
