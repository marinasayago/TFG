from pymongo import MongoClient
import csv
import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri = os.getenv("MONGO_URI_IVAN_PART1")
client = MongoClient(mongo_uri)

collection_name_Origen = "derivado"

db = client["TFG"]


def create_dataframe(machine):
    formatted_name = machine.split("_")[1].capitalize()
    dataframe_gates = [
        ['date', 'gate_error_1', 'gate_error_2']
    ]
    items = db[collection_name_Origen].find({"name": machine})
    for item in items:
      dataframe_gates.append([item['date'], item['properties']['gates'][0]['mediana'], item['properties']['gates'][1]['mediana']])

    directory = 'backend/dataframes_gates/'

    file_name = directory + 'dataframe_Gates' + formatted_name + '.csv'

    with open(file_name, 'w', newline='') as csv_file:
        
        csv_writer = csv.writer(csv_file)
        
        for row in dataframe_gates:
            csv_writer.writerow(row)


machines = ["ibm_brisbane", "ibm_kyoto", "ibm_osaka"] 

for machine in machines:
    create_dataframe(machine)

print("Dataframes created")