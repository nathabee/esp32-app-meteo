from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/status', methods=['GET'])
def status():
    response = {
        "uptime_ms": 100000,
        "free_heap": 223484,
        "wifi_strength": -89,
        "status": "OK"
    }
    print("DEBUG: Simulating internal request to /status")
    return jsonify(response)

@app.route('/lastreport', methods=['GET'])
def last_report():
    response = {
        "temperature": 24.00,
        "humidity": 40.00
    }
    print("DEBUG: Simulating internal request to /lastreport")
    return jsonify(response)

@app.route('/maximahistory', methods=['GET'])
def maxima_history():
    response = {
        "history": [
            {"date": "2025-2-17", "minTemp": 18.3, "maxTemp": 39.40001, "minHum": 37.1, "maxHum": 43.89999},
            {"date": "2025-2-16", "minTemp": 13.1, "maxTemp": 36.5, "minHum": 35.2, "maxHum": 43.59999},
            {"date": "2025-2-15", "minTemp": 15.09999, "maxTemp": 41.3, "minHum": 34.8, "maxHum": 41.99999},
            {"date": "2025-2-14", "minTemp": 12.89999, "maxTemp": 36.2, "minHum": 34.09999, "maxHum": 38.49999},
            {"date": "2025-2-13", "minTemp": 13.19999, "maxTemp": 36.99999, "minHum": 30.49999, "maxHum": 36.59999},
            {"date": "2025-2-12", "minTemp": 13.19999, "maxTemp": 36.09999, "minHum": 29.39999, "maxHum": 35.39999},
            {"date": "2025-2-11", "minTemp": 14.49999, "maxTemp": 40.89999, "minHum": 28.39999, "maxHum": 35.79998},
            {"date": "2025-2-10", "minTemp": 23.3, "maxTemp": 29.5, "minHum": 33.19999, "maxHum": 34.19999}
        ]
    }
    print("DEBUG: Simulating internal request to /maximahistory")
    return jsonify(response)

@app.route('/history', methods=['GET'])
def history():
    response = {
        "history": [
            {"timestamp": "2025-02-10 21:21:11", "temperature": 24.9, "humidity": 33.39999},
            {"timestamp": "2025-02-10 21:51:11", "temperature": 26.7, "humidity": 33.39999},
            {"timestamp": "2025-02-10 22:21:11", "temperature": 27, "humidity": 33.49999},
            {"timestamp": "2025-02-10 22:51:11", "temperature": 27.6, "humidity": 33.89999},
            {"timestamp": "2025-02-10 23:21:11", "temperature": 27.6, "humidity": 33.89999},
            {"timestamp": "2025-02-10 23:51:11", "temperature": 29.5, "humidity": 34.19999},
            {"timestamp": "2025-02-11 00:21:11", "temperature": 30.3, "humidity": 34.19999},
            {"timestamp": "2025-02-11 00:51:11", "temperature": 30.3, "humidity": 34.19999},
            {"timestamp": "2025-02-11 01:21:11", "temperature": 31.8, "humidity": 34.29999},
            {"timestamp": "2025-02-11 01:51:11", "temperature": 33.5, "humidity": 34.29999},
            {"timestamp": "2025-02-11 02:21:11", "temperature": 34, "humidity": 34.59999},
            {"timestamp": "2025-02-11 02:51:11", "temperature": 35.3, "humidity": 34.69999}
        ]
    }
    print("DEBUG: Simulating internal request to /history")
    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
