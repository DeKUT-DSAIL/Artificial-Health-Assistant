# MMR Data Pipeline
This 'pipeline' streams data and commits it an azure SQL database

## Installation
- Install [ODBC driver for SQL server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?redirectedfrom=MSDN&view=sql-server-ver15)

- Make sure The python API is set up correctly.
    1. Linux [API Installation](https://mbientlab.com/tutorials/PyLinux.html)
    2. Windows [API Installation](https://mbientlab.com/tutorials/PyWindows.html)

To install required packages, run the following command after creating a virtual env.

```python
pip install -r requirements.txt
```

Before continuing, you need to have the CONN_STR to the database.

Run the following in a terminal

- Unix

```
$ export CONN_STR=pastethereallyreallylongconnectionstringhere
```
- Windows
```
$ set CONN_STR=pastethereallyreallylongconnectionstringhere
```

## Usage
Turn on bluetooth and you are good to go.

Run the following and choose an option for an exercise
```
python main.py
```
```
Connected
Services disconvered
Characteristics discovered
Descriptors found

Choose a number for an exercise below
1. Jumping Jacks
2. Squats
3. Jogs
4. Body Stretch(Arms)
3
Enter number of Rounds You'll do jogs: 3


```

Then the output will be something like this
```
Logging and adding data for squats to database
(Approx. 32 seconds)
Round 1
Accelerometer: 	 |████████████████████████████████████████| 100.0% Complete
Gyroscope: 	 |████████████████████████████████████████| 100.0% Complete
Finished!
Round 2
Accelerometer: 	 |████████████████████████████████████████| 100.0% Complete
Gyroscope: 	 |████████████████████████████████████████| 100.0% Complete
Finished!


```
Then you can choose to continue or Exit the program
```
Continue or exit
1. Continue
2. Exit

1
```

## Some challenges you might face
After running the program you might get something like this
```
error 1600154639.663913: Error on line: 296 (src/blestatemachine.cc): Operation now in progress
*** buffer overflow detected ***: terminated
Aborted (core dumped)

```
I'm not sure what the problem is, but if you run it one more time, boom. fixed :)

### Another Challenge I've faced
The bluetooth may disconnect mid program. Just hit ```ctrl + C``` to stop program and restart again

## Querying data
To query data you can create a notebook or just run along with a script

### import required packages

```python
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

from model import BodyAccX, BodyAccY, BodyAccZ
from utils import Session
```
### Query first row of data
```python
s = Session()

x = s.query(BodyAccX).first().row_data
y = s.query(BodyAccY).first().row_data
z = s.query(BodyAccZ).first().row_data
```
### Prepare data
```python
def prep_data(x, y, z):
    x_list = x.split(', ')
    y_list = y.split(', ')
    z_list = z.split(', ')

    for i in range(len(x_list)):
        x_list[i] = float(x_list[i])
        y_list[i] = float(y_list[i])
        z_list[i] = float(z_list[i])

    new_x = np.array(x_list)
    new_y = np.array(y_list)
    new_z = np.array(z_list)
    
    return new_x, new_y, new_z

newx, newy, newz = prep_data(x, y, z)
```

### Visualize the data
```python
%matplotlib inline

fig = plt.figure()
ax = plt.axes()
ax.plot(newx, 'r', label='acc in x-axis')
ax.plot(newy, 'g', label='acc in y-axis')
ax.plot(newz, 'b', label='acc in z-axis')
ax.grid(True, which='both')
ax.set_ylabel('Acceleration')
ax.set_xlabel('Time Steps')
ax.legend()
```
![alt text](files/plot.png)