#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
#from model import Base

import pyodbc
import pandas as pd
from time import sleep
from mbientlab.metawear import libmetawear
from pymetawear.client import MetaWearClient




#engine = create_engine(DATABASE_URI)
#Session = sessionmaker(bind=engine)



# Print iterations progress
def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', print_end="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix}\t |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()

        
        
def stream_data(device: MetaWearClient, data_rate: float = 25.0, acc_data_range: float = 16.0,
                gyr_data_range: int = 500,time_ : int = 60):
    """
    This function streams accelerometer and gyroscope data
    :param device: MetaWearClient
    :param data_rate: float
    :param acc_data_range: float
    :param gyr_data_range: int
    :return accelerometer and gyroscope Dataframes:
    """
    acc_data_points = []
    gyr_data_points = []

    # Set data rate and measuring range
    device.accelerometer.set_settings(data_rate=data_rate, data_range=acc_data_range)
    device.gyroscope.set_settings(data_rate=data_rate, data_range=gyr_data_range)


    # Enable notifications and register a callback for them.
    device.accelerometer.notifications(callback=lambda data: acc_data_points.append(data))
    device.gyroscope.notifications(callback=lambda data: gyr_data_points.append(data))
    
    print_progress_bar(0, time_, prefix='Collecting Data:', suffix='Complete', length=30)
    counter = 0.001
    while counter <= time_:
        sleep(0.02)
        print_progress_bar(counter, time_, prefix='Collecting Data:', suffix='Complete', length=30)
        counter += 0.02
    print_progress_bar(time_, time_, prefix='Collecting Data:', suffix='Complete', length=30)

    device.accelerometer.notifications()
    device.gyroscope.notifications()


    acc = pd.DataFrame(acc_data_points)

    gyr = pd.DataFrame(gyr_data_points)

    return acc, gyr

def reset(device) -> None:
    """
    This function resets your device if its stuck in a bad state
    :param device:
    :return None:
    """
    # Stops data logging
    libmetawear.mbl_mw_logging_stop(device.board)
    # Clear the logger of saved entries
    libmetawear.mbl_mw_logging_clear_entries(device.board)
    # Remove all macros on the flash memory
    libmetawear.mbl_mw_macro_erase_all(device.board)
    # Restarts the board after performing garbage collection
    libmetawear.mbl_mw_debug_reset_after_gc(device.board)
    libmetawear.mbl_mw_debug_disconnect(device.board)
    device.disconnect()
