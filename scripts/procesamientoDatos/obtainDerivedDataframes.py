from pymongo import MongoClient
import joblib
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from dotenv import load_dotenv
import os

load_dotenv()


def generate_dataframe(machine_name):
    formatted_name = machine_name.split("_")[1].capitalize()
    mongo_uri_1 = os.getenv("MONGO_URI_IVAN_PART1")
    client_1 = MongoClient(mongo_uri_1)
    origin_collection_name = "derivado"
    db_1 = client_1["TFG"]
    data = db_1[origin_collection_name].find({"name": machine_name})

    data_qubits_T1 = []
    data_qubits_T2 = []
    data_qubits_Prob0 = []
    data_qubits_Prob1 = []
    data_qubits_error = []

    data_gates_gate_error_1 = []
    data_gates_gate_error_2 = []

    for item in data:
        date = item['date']
        T1 = item['properties']['qubits'][0]['mediana']
        T2 = item['properties']['qubits'][1]['mediana']
        probMeas0Prep1 = item['properties']['qubits'][2]['mediana']
        probMeas1Prep0 = item['properties']['qubits'][3]['mediana']
        readout_error = item['properties']['qubits'][4]['mediana']

        error_1 = item['properties']['gates'][0]['mediana']
        error_2 = item['properties']['gates'][1]['mediana']

        data_qubits_T1.append([date, T1, T2, probMeas0Prep1, probMeas1Prep0, readout_error])
        data_qubits_T2.append([date, T2, T1, probMeas0Prep1, probMeas1Prep0, readout_error])
        data_qubits_Prob0.append([date, probMeas0Prep1, T1, T2, probMeas1Prep0, readout_error])
        data_qubits_Prob1.append([date, probMeas1Prep0, T1, T2, probMeas0Prep1, readout_error])
        data_qubits_error.append([date, readout_error, T1, T2, probMeas0Prep1, probMeas1Prep0])

        data_gates_gate_error_1.append([date, error_1, error_2])
        data_gates_gate_error_2.append([date, error_2, error_1])
    
    df_T1 = pd.DataFrame(data_qubits_T1, columns=['ds', 'y', 'T2', 'probMeas0Prep1', 'probMeas1Prep0', 'readout_error'])
    df_T2 = pd.DataFrame(data_qubits_T2, columns=['ds', 'y', 'T1', 'probMeas0Prep1', 'probMeas1Prep0', 'readout_error'])
    df_Prob0 = pd.DataFrame(data_qubits_Prob0, columns=['ds', 'y', 'T1', 'T2', 'probMeas1Prep0', 'readout_error'])
    df_Prob1 = pd.DataFrame(data_qubits_Prob1, columns=['ds', 'y', 'T1', 'T2', 'probMeas0Prep1', 'readout_error'])
    df_error = pd.DataFrame(data_qubits_error, columns=['ds', 'y', 'T1', 'T2', 'probMeas0Prep1', 'probMeas1Prep0'])

    df_error_1 = pd.DataFrame(data_gates_gate_error_1, columns=['ds', 'y', 'error_2'])
    df_error_2 = pd.DataFrame(data_gates_gate_error_2, columns=['ds', 'y', 'error_1'])

    scaler = MinMaxScaler()

    df_T1.iloc[:, 1:] = scaler.fit_transform(df_T1.iloc[:, 1:])
    joblib.dump(scaler, '../../backend/dataframes_neuralProphet/scalerT1' + formatted_name + '.pkl')

    scaler = MinMaxScaler()
    df_T2.iloc[:, 1:] = scaler.fit_transform(df_T2.iloc[:, 1:])
    joblib.dump(scaler, '../../backend/dataframes_neuralProphet/scalerT2' + formatted_name + '.pkl')

    scaler = MinMaxScaler()
    df_Prob0.iloc[:, 1:] = scaler.fit_transform(df_Prob0.iloc[:, 1:])
    joblib.dump(scaler, '../../backend/dataframes_neuralProphet/scalerProb0' + formatted_name + '.pkl')

    scaler = MinMaxScaler()
    df_Prob1.iloc[:, 1:] = scaler.fit_transform(df_Prob1.iloc[:, 1:])
    joblib.dump(scaler, '../../backend/dataframes_neuralProphet/scalerProb1' + formatted_name + '.pkl')

    scaler = MinMaxScaler()    
    df_error.iloc[:, 1:] = scaler.fit_transform(df_error.iloc[:, 1:])
    joblib.dump(scaler, 'backend/dataframes_neuralProphet/scalerError' + formatted_name + '.pkl')

    directory = '../../backend/dataframes_neuralProphet/'

    df_T1.to_csv(os.path.join(directory, f'dataframeT1{formatted_name}.csv'), index=False)
    df_T2.to_csv(os.path.join(directory, f'dataframeT2{formatted_name}.csv'), index=False)
    df_Prob0.to_csv(os.path.join(directory, f'dataframeProb0{formatted_name}.csv'), index=False)
    df_Prob1.to_csv(os.path.join(directory, f'dataframeProb1{formatted_name}.csv'), index=False)
    df_error.to_csv(os.path.join(directory, f'dataframeError{formatted_name}.csv'), index=False)

    df_error_1.to_csv(os.path.join(directory, f'dataframeError1{formatted_name}.csv'), index=False)
    df_error_2.to_csv(os.path.join(directory, f'dataframeError2{formatted_name}.csv'), index=False)

    print("Extraction completed")


maquinas = ["ibm_brisbane", "ibm_kyoto", "ibm_osaka"] 

for maquina in maquinas:
    generate_dataframe(maquina)

