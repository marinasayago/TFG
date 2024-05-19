from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone, timedelta
import pytz
from appWeb import predictQubitsCalibration
from appWeb import predictQubitsError
from appWeb import predictGatesCalibration
from appWeb import predictGatesError
from typing import List, Dict, Union

router = APIRouter()

class PredictionData(BaseModel):
    machine: str
    date: Optional[str] = None
    selection: Optional[str] = None
    depth: Optional[str] = None

@router.post("/")
async def predict(data: PredictionData) -> Dict[str, List[Dict[str, Union[float, str, str, str, str, str, str]]]]:
    # Aquí realizas la predicción con los datos recibidos
    print("Datos recibidos predict error:", data)
    
    if data.selection == "Qubits":
        prediction = predict_qubits(data)
    elif data.selection == "Puertas":
        prediction = predict_puertas(data)
    else:
        prediction = None
        
    return {"prediction": prediction}

def predict_qubits(data: PredictionData) -> List[Dict[str, Union[float, str, str, str, str, str, str]]]:
    n_steps = calculate_time_difference(data.date) 
    future_T1, future_T2, future_Prob0, future_Prob1, future_error = predictQubitsCalibration.predict_qubits_calibration(n_steps, data.machine)
    
    predictions = []
    for i in range(n_steps):
        prediction = {
            "T1": future_T1.iloc[i, future_T1.columns.get_loc('y')],
            "T2": future_T2.iloc[i, future_T2.columns.get_loc('y')],
            "Prob0": future_Prob0.iloc[i, future_Prob0.columns.get_loc('y')],
            "Prob1": future_Prob1.iloc[i, future_Prob1.columns.get_loc('y')],
            "Error": future_error.iloc[i, future_error.columns.get_loc('y')]
        }
        predictions.append(prediction)

    predictions = predictQubitsError.predict_qubits_error(predictions, data.machine, data.depth)
    print("Diccionario")
    print(predictions)
    return predictions


def predict_puertas(data: PredictionData) -> List[Dict[str, Union[float, str]]]:
    current_date = datetime.now(timezone.utc)
    end_date = datetime.fromisoformat(data.date.replace('Z', '+00:00'))

    predictions = []

    while(current_date <= end_date):
        print(current_date)
        gate_error1, gate_error2 = predictGatesCalibration.predict(data.machine, current_date)
        print(gate_error1)
        print(gate_error2)
        error_prediction = predictGatesError.predict(data.machine, [[gate_error1, gate_error2]])
        new_prediction = {'Date': current_date.strftime('%Y-%m-%d %H:%M:%S'), 'divergence': error_prediction[0]}
        predictions.append(new_prediction)
        current_date += timedelta(hours=2)

    print("Diccionario")
    print(predictions)
    return predictions


def calculate_time_difference(selected_date_str):
    local_timezone = pytz.timezone('Europe/Madrid')  # Reemplaza 'Europe/Madrid' con tu zona horaria local real
    current_date = datetime.now(local_timezone)  # Obtener la hora actual en la zona horaria local

    # Convertir la fecha seleccionada de cadena ISO a datetime
    selected_date = datetime.fromisoformat(selected_date_str.replace('Z', '+00:00'))

    # Calcular la diferencia de tiempo en horas
    time_difference = (selected_date - current_date).total_seconds() / 3600
    
    # Redondear la cantidad de horas al múltiplo de 2 más cercano
    rounded_hours = round(time_difference / 2)
    print(rounded_hours)
    return rounded_hours
