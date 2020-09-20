from pymetawear.client import MetaWearClient

from model import BodyAccX, BodyAccY, BodyAccZ, BodyGyroX, BodyGyroY, BodyGyroZ
from utils import Session, stream_acc_data, stream_gyr_data


def record_data(label: str, device: MetaWearClient, rounds: int) -> None:
    """
    This function commits the data streamed to the database
    :param label:
    :param device:
    :param rounds:
    :return None:
    """
    s = Session()

    print(f"Logging and adding data for {label} to database")
    print(f"(Approx. {rounds * 8} seconds)")
    for i in range(rounds):
        print(f'Round {i + 1}')
        acc, gyr = stream_acc_data(device=device), stream_gyr_data(device=device)
        print("Finished!")

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

    print(f"Committing {label} of {rounds} Round(s) data to database...")

    s.commit()
    print("Finished!")
    s.close()


def run() -> None:
    """
    Starts the program
    :return None:
    """
    # Create a MetaWear device
    d = MetaWearClient('EE:50:E7:BF:21:83')  # Substitute with your MAC

    proceed = True

    while proceed:
        exercise = int(input(
            "\nChoose a number for an exercise below\n"
            "1. Jumping Jacks\n"
            "2. Squats\n"
            "3. Jogs\n"
            "4. Body Stretch(Arms)\n"
        ))

        while exercise not in [1, 2, 3, 4]:
            exercise = int(input(
                "\nChoose a number for an exercise below\n"
                "1. Jumping Jacks\n"
                "2. Squats\n"
                "3. Jogs\n"
                "4. Body Stretch(Arms)\n"
            ))

        if exercise == 1:
            action = 'jumping jacks'
        elif exercise == 2:
            action = 'squats'
        elif exercise == 3:
            action = 'jogs'
        else:
            action = 'body stretch'

        rounds = int(input(
            f"Enter number of Rounds You'll do {action}: "
        ))

        # Start to stream and record data
        try:
            record_data(label=action, device=d, rounds=rounds)
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
