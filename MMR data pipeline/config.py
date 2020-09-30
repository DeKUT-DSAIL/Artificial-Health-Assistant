import os

#CONN_STR = os.environ.get('CONN_STR')

server = 'health-assist.database.windows.net'
database = 'MmrSensorData'
username = 'mmruser'
password = 'Metadata123'
DATABASE_URI = 'DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password
