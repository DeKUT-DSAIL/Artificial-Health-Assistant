import os
from urllib.parse import quote_plus

CONN_STR = os.environ.get('CONN_STR')

PARAMS = quote_plus(CONN_STR)

# Construct as database uri

# Azure MySQL
DATABASE_URI = 'mssql+pyodbc:///?odbc_connect={}'.format(PARAMS)

# Local Postgresql
# DATABASE_URI = 'postgres+psycopg2://postgres:postgres@localhost:5432/data'
