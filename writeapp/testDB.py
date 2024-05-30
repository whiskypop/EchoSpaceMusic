from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import sys
import requests
import pyodbc
import uuid
sys.stdout.reconfigure(encoding='utf-8')
from openai import AzureOpenAI

# Azure SQL Database 配置
server = 'echo-server.database.windows.net'
database = 'echoSpace'
username = 'echoSpace'
password = '3ch0Space'
driver = '{ODBC Driver 18 for SQL Server}'

def get_db_connection():
    conn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
    return conn

def test_connection():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT @@version;')
        row = cursor.fetchone()
        print('Successfully connected to the database. Server version:', row[0])
        conn.close()
    except Exception as e:
        print('Connection failed:', str(e))

test_connection()