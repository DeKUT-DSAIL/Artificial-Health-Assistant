from time import sleep

from mbientlab.metawear import libmetawear
from pymetawear.client import MetaWearClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import Base

from config import DATABASE_URI

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)


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


def stream_acc_data(device: MetaWearClient, data_rate: float = 50.0, acc_data_range: float = 16.0):
    """
    This function streams accelerometer data
    :param device: MetaWearClient
    :param data_rate: float
    :param acc_data_range: float
    :return accelerometer tuples of x, y, z axis:
    """
    acc_data_points = []

    # Set data rate and measuring range
    device.accelerometer.set_settings(data_rate=data_rate, data_range=acc_data_range)

    print_progress_bar(0, 200, prefix='Accelerometer: ', suffix='Complete', length=40)

    def acc_callback(data_struct):
        """Handle a (epoch, (x,y,z)) data tuple."""
        if len(acc_data_points) <= 199:
            acc_data_points.append(data_struct)
            print_progress_bar(len(acc_data_points), 200, prefix='Accelerometer: ', suffix='Complete', length=40)

    # Enable notifications and register a callback for them.
    device.accelerometer.notifications(callback=acc_callback)

    while len(acc_data_points) < 200:
        sleep(0.02)
    device.accelerometer.notifications()

    acc = (str([i['value'].x for i in acc_data_points]), str([j['value'].y for j in acc_data_points]),
           str([k['value'].z for k in acc_data_points]))

    return acc


def stream_gyr_data(device: MetaWearClient, data_rate: float = 50.0, gyr_data_range: int = 500):
    """
    This function streams gyroscope data
    :param device: MetaWearClient
    :param data_rate: float
    :param gyr_data_range: int
    :return gyroscope tuples of x, y, z axis:
    """
    gyr_data_points = []

    # Set data rate and measuring range
    device.gyroscope.set_settings(data_rate=data_rate, data_range=gyr_data_range)

    print_progress_bar(0, 200, prefix='Gyroscope: ', suffix='Complete', length=40)

    def gyr_callback(data_struct):
        """Handle a (epoch, (x,y,z)) data tuple."""
        if len(gyr_data_points) <= 199:
            gyr_data_points.append(data_struct)
            print_progress_bar(len(gyr_data_points), 200, prefix='Gyroscope: ', suffix='Complete', length=40)

    # Enable notifications and register a callback for them.
    device.gyroscope.notifications(callback=gyr_callback)

    while len(gyr_data_points) < 200:
        sleep(0.02)
    device.gyroscope.notifications()

    gyr = (str([i['value'].x for i in gyr_data_points]), str([j['value'].y for j in gyr_data_points]),
           str([k['value'].z for k in gyr_data_points]))

    return gyr


def recreate_database() -> None:
    """
    his function creates tables in a database in None exist
    else it deletes and creates them again
    :return None:
    """
    try:
        Base.metadata.drop_all(engine)
    except:
        pass
    Base.metadata.create_all(engine)


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
