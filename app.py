from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    rooms_to_times = {}
    all_times = request.form.getlist('times')

    for key, value in request.form.items():
        if key.startswith('checkbox-') and value == 'on':
            parts = key.split('-', 2)
            if len(parts) == 3:
                room = parts[1]
                time = parts[2]
                rooms_to_times.setdefault(room, []).append(time)

    print('Rooms to Times:', rooms_to_times)
    print('All Times:', all_times)

    # Send the data to the frontend
    return render_template('availability_submitted.html', rooms_to_times=rooms_to_times, all_times=all_times)
    
if __name__ == '__main__':
    app.run(debug=True)
