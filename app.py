from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json()
    rooms_to_times = data['roomsToTimes']
    all_times = data['allTimes']

    print("Rooms to Times:", rooms_to_times)
    print("All Times:", all_times)

    return 'Data received successfully!'
    
if __name__ == '__main__':
    app.run(debug=True)
