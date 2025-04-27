from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_availability', methods=['POST'])
def submit_availability():
    data = request.get_json()

    roomsToTimes = data.get('roomsToTimes', {})
    allTimes = data.get('allTimes', [])

    print("Rooms to Times:", roomsToTimes)
    print("All Times:", allTimes)

    # Now you have both structures ready to use!
    return jsonify({"message": "Success!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
