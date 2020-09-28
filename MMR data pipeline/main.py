from pymetawear.client import MetaWearClient

from model import BodyAccX, BodyAccY, BodyAccZ, BodyGyroX, BodyGyroY, BodyGyroZ
from pymetawear.discover import select_device
from utils import Session, stream_data
# from testing_utils import stream_data


def record_data(label: str, device: MetaWearClient, time_: int) -> None:
    """
    This function commits the data streamed to the database
    :param time_:
    :param label:
    :param device:
    :return None:
    """
    s = Session()

    print(f"Logging and adding data for {label} to database")
    acc, gyr = stream_data(device=device, time_=time_)
    print("Finished!\n")

    gx = gyr[0].replace('[', '').replace(']', '')
    gy = gyr[1].replace('[', '').replace(']', '')
    gz = gyr[2].replace('[', '').replace(']', '')

    ax = acc[0].replace('[', '').replace(']', '')
    ay = acc[1].replace('[', '').replace(']', '')
    az = acc[2].replace('[', '').replace(']', '')

    s.add(BodyAccX(row_data=ax, label=label))
    s.add(BodyAccY(row_data=ay, label=label))
    s.add(BodyAccZ(row_data=az, label=label))

    s.add(BodyGyroX(row_data=gx, label=label))
    s.add(BodyGyroY(row_data=gy, label=label))
    s.add(BodyGyroZ(row_data=gz, label=label))

    print(f"Committing {label} data to database...")

    s.commit()
    print("Finished!\n")
    s.close()


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
