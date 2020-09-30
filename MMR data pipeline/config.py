'''
import os
from urllib.parse import quote_plus

"""
add the PASSWORD of database and UID to path.
e.g export PASSWORD=pass123
    export USERID=awesomeuser101
"""

CONN_STR = os.environ.get('CONN_STR')

PARAMS = quote_plus(CONN_STR)
#If 'TypeError: quote_from_bytes() expected bytes' occurs try
#PARAMS = quote_plus(str(CONN_STR))

# Azure MySQL
DATABASE_URI = 'mssql+pyodbc:///?odbc_connect={}'.format(PARAMS)    # Construct as database uri

# Local Postgresql
# DATABASE_URI = 'postgres+psycopg2://postgres:postgres@localhost:5432/data'
'''