import csv
import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from datetime import datetime as dt
from time import sleep

from mbientlab.metawear import libmetawear
from pymetawear.client import MetaWearClient
from pymetawear.discover import select_device

'''
cwd = os.getcwd()
acc_data_dir = cwd + "/data/acc"
gyro_data_dir = cwd + "/data/gyro"
'''
data_path = os.environ.get('DATA_PATH')
acc_data_dir = os.path.join(data_path, 'acc')
gyro_data_dir = os.path.join(data_path, 'gyro')


def upload_csv(fname: str):
    # Create Client
    try:
        CONN = os.environ.get('CONN_STRING')
        service = BlobServiceClient.from_connection_string(conn_str=CONN)

        # Upload Blob
        container_name = fname.split('_')[0]

        if fname.split('_')[-1].startswith('acc'):
            os.chdir(acc_data_dir)
            data_path = os.path.join(acc_data_dir, fname)
            blob_name = 'acc/' + fname

        else:
            os.chdir(gyro_data_dir)
            data_path = os.path.join(gyro_data_dir, fname)
            blob_name = 'gyr/' + fname

        blob = BlobClient.from_connection_string(conn_str=CONN, container_name=container_name, blob_name=blob_name)

        with open(data_path, "rb") as data:
            blob.upload_blob(data)
        print(f"{fname} uploaded successfully!")
        os.remove(data_path)

    except Exception as m:
        print("Failed to upload data: ", m)


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


def stream_data(device: MetaWearClient, time_: int, data_rate: float = 50.0, acc_data_range: float = 16.0,
                gyr_data_range: int = 500):
    """
    This function streams accelerometer data
    :param time_:
    :param gyr_data_range:
    :param device: MetaWearClient
    :param data_rate: float
    :param acc_data_range: float
    :return accelerometer tuples of x, y, z axis:
    """
    acc_data_points = []
    gyr_data_points = []

    counter = 0

    # Set data rate and measuring range
    device.accelerometer.set_settings(data_rate=data_rate, data_range=acc_data_range)
    device.gyroscope.set_settings(data_rate=data_rate, data_range=gyr_data_range)

    # Enable notifications and register a callback for them.
    device.accelerometer.notifications(callback=lambda data: acc_data_points.append(data))
    device.gyroscope.notifications(callback=lambda data: gyr_data_points.append(data))

    print_progress_bar(0, time_, prefix='Collecting Data:', suffix='Complete', length=30)
    while counter <= time_:
        sleep(0.02)
        print_progress_bar(counter, time_, prefix='Collecting Data:', suffix='Complete', length=30)
        counter += 0.02
    print_progress_bar(time_, time_, prefix='Collecting Data:', suffix='Complete', length=30)

    device.accelerometer.notifications(None)
    device.gyroscope.notifications(None)

    acc = (str([i['value'].x for i in acc_data_points]), str([j['value'].y for j in acc_data_points]),
           str([k['value'].z for k in acc_data_points]))

    gyr = (str([i['value'].x for i in gyr_data_points]), str([j['value'].y for j in gyr_data_points]),
           str([k['value'].z for k in gyr_data_points]))

    print(len(acc_data_points))
    print(len(gyr_data_points))

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


def write_data_csv(device: MetaWearClient, time_: int, title: str):
    acc_data, gyro_data = stream_data(device=device, time_=time_)

    acc_x = acc_data[0].replace('[', '').replace(']', '').split(', ')
    acc_y = acc_data[1].replace('[', '').replace(']', '').split(', ')
    acc_z = acc_data[2].replace('[', '').replace(']', '').split(', ')

    gyro_x = gyro_data[0].replace('[', '').replace(']', '').split(', ')
    gyro_y = gyro_data[1].replace('[', '').replace(']', '').split(', ')
    gyro_z = gyro_data[2].replace('[', '').replace(']', '').split(', ')

    # Getting filename
    now = dt.now()
    dt_string = now.strftime("%Y-%m-%dT%H.%M.%S")
    acc_file_name = title + '_' + dt_string + '_' + 'accelerometer' + '.csv'
    gyr_file_name = title + '_' + dt_string + '_' + 'gyroscope' + '.csv'

    os.chdir(acc_data_dir)
    with open(acc_file_name, 'w', newline='') as a_file:
        writer = csv.writer(a_file)
        for accDataPoint in range(len(acc_x)):
            row = [acc_x[accDataPoint], acc_y[accDataPoint], acc_z[accDataPoint]]
            writer.writerow(row)

    os.chdir(gyro_data_dir)
    with open(gyr_file_name, 'w', newline='') as g_file:
        writer = csv.writer(g_file)
        for gyroDataPoint in range(len(gyro_x)):
            row = [gyro_x[gyroDataPoint], gyro_y[gyroDataPoint], gyro_z[gyroDataPoint]]
            writer.writerow(row)

    return acc_file_name, gyr_file_name


def run() -> None:
    """kjsk
    Starts the program
    :return None:
    """
    # Create a MetaWear device
    address = select_device()
    # d = MetaWearClient('EE:50:E7:BF:21:83')
    d = MetaWearClient(str(address))

    proceed = True

    prompt = """
    \nChoose a number for an exercise below
    1. Walking
    2. Sitting
    3. Lying down
    4. Standing
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
            action = 'laying'
        else:
            action = 'standing'

        time_ = int(input(f"\nEnter Seconds You'll do {action}:\n"))
        # time_ = 60

        # Start to stream and record data
        try:
            acc_fname, gyro_fname = write_data_csv(title=action, device=d, time_=time_)

            upload_choice = input("\nUpload data?\n1. Yes\n2. No\n")
            if upload_choice == '1':
                upload_csv(acc_fname)
                upload_csv(gyro_fname)

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
    reset(d)
    # d.disconnect()


run()
