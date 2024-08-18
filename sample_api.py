# app.py
from flask import Flask, send_file, make_response
import pandas as pd
import os

class FLASK_APP:
    def __init__(self):
        self.app = Flask(__name__)
        self.doctor_data.get_current_date()
        self.doctor_data.run()
        self.app.add_url_rule('/download', 'download', self.download)
        
    def download(self):
        # Check if the file exists
        if os.path.exists("doctors_data.csv"):
            # Load the data
            data = pd.read_csv("doctors_data.csv")
            # Convert the data to a CSV file
            response = make_response(data.to_csv())
            response.headers["Content-Disposition"] = "attachment; filename=doctors_data.csv"
            response.headers["Content-Type"] = "text/csv"
            return response
        else:
            return "File not found"
        
    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)