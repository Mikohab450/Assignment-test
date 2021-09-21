import json
import csv
import sys
from configparser import ConfigParser
from datetime import datetime
from flask import Flask, render_template

msg={
   "sensor_id": "some uuid",  
   "model": "WS-0004",
   "payload": "some data"
}

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


    

models_list=[]
handlers_list=[]
outputs_list=[]

config=ConfigParser()
config.read("config.ini")
output_file = config.get("files","output_file")
sensors_filename=output_file = config.get("files","sensor_config_file")
padding_char=config.get("settings","padding_char")
padding_n=int(config.get("settings","padding_n"))



def trim(payload):
    """ Removes whitespaces form both sides of the payload"""
    return payload.strip()

def padToMultiple(payload,char=padding_char,n=padding_n):
    """ Pads payload with given character on the right to the lenght of n"""
    return payload.ljust(n,char)

def addTimestamp(payload):
    """adds current timestamp is seconds to the payload"""
    now = datetime.now()
    timestamp = datetime.timestamp(now) 
    return payload+'_'+str(int(timestamp))



def read_sensors_conf():
    """Reads configuration of sensors from the .csv file"""
    with open(sensors_filename,'r') as csvfile:
        reader=csv.DictReader(csvfile)
        for col in reader:
            models_list.append(col['Sensor model'])
            handlers_list.append(col['Handlers'])
            outputs_list.append(col['Outputs'])



def process_sensor(json):
    """Processes the json messege, applies corresponding handlers and saves the output"""
    model=json["model"]
    payload=json["payload"]
    index=models_list.index(model)
    handlers_func = handlers_list[index].split(',')
    output_func= outputs_list[index].split(',')
    for h in handlers_func:
        payload=getattr(sys.modules[__name__],h.strip())(payload)
    for out in output_func:
        getattr(sys.modules[__name__],out.strip())(payload)

@app.route('/single_config')
def get_single_sensor_config(sensor):
    """Gets a configuration for given sensor"""
    index=models_list.index(model)
    handlers_func = handlers_list[index]
    output_func= outputs_list[index]
    return handlers_func,output_func

@app.route('/all_config')
def get_all_sensors_config():
    return handlers_list,outputs_list


def add_configuration(row):
    with open(sensors_filename,'a') as csvfile:
        csvfile.write(row)


def Console(result):
    """Prints the result the console"""
    print(result)
def File(result):
    """Saves the result to the file"""
    with open(output_file, "w") as text_file:
        text_file.write(result)

if __name__ == "__main__":
    read_sensors_conf()   
    app.run(debug="True")