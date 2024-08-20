from flask import Flask
from flask_restful import Api
from Resource_api import Resource_API
import re

app = Flask(__name__)
api = Api(app)
#pass fields which file to be returned as response to the client in the Resource_API class if client requests for the file doctors_data_2.xml it will return doctors_data_2.xml file as response
#api.add_resource(Resource_API, "/doctors_data.xml", "/doctors_data_2.xml", "/doctors_data_3.xml", "/doctors_data_4.xml", "/doctors_data.json", "/doctors_data_2.json", "/doctors_data_3.json", "/doctors_data_4.json")

#any request to the server will be redirected to the home page if not ends with xml or json file for example if client requests for the file doctors_data it will be redirected to the home page 
@app.route("/")
def home():
    return "Welcome to the API Homepage! \n to access the doctors_data.xml file, <a href='/doctors_data.xml'>click here</a>"

@app.route("/doctors_data.xml")
def doctors_data():
    return Resource_API("doctors_data.xml").get()
@app.route("/doctors_data_2.xml")
def doctors_data_2():
    return Resource_API("doctors_data_2.xml").get()
@app.route("/doctors_data_3.xml")
def doctors_data_3():
    return Resource_API("doctors_data_3.xml").get()
@app.route("/doctors_data_4.xml")
def doctors_data_4():
    return Resource_API("doctors_data_4.xml").get()
@app.route("/doctors_data.json")
def doctors_data_json():
    return Resource_API("doctors_data.json").get()
@app.route("/doctors_data_2.json")
def doctors_data_2_json():
    return Resource_API("doctors_data_2.json").get()
@app.route("/doctors_data_3.json")
def doctors_data_3_json():
    return Resource_API("doctors_data_3.json").get()
@app.route("/doctors_data_4.json")
def doctors_data_4_json():
    return Resource_API("doctors_data_4.json").get()

if __name__ == "__main__":
    app.run(debug=True)



