from flask import Flask, request, jsonify, render_template
import requests, pandas as pd, io, copy

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit_availability', methods=['POST'])
def submit_availability():
    print("🔔 submit_availability was called!")
    data = request.get_json()

    url = data.get('url')
    firstNameCol1 = data.get('firstNameCol')
    lastNameCol1 = data.get('lastNameCol')
    projectNameCol1 = data.get('projectNameCol')
    projectTopicCol1 = data.get('projectTopicCol')
    availabilityCol1 = data.get('availabilityCol')
    friendsCol1 = data.get('friendsCol')
    blurbCol1 = data.get('blurbCol')

    urlData = requests.get(url).content
    rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')))
    firstNameCol = int(firstNameCol1)-1
    lastNameCol = int(lastNameCol1)-1
    availabilityCol = int(availabilityCol1)-1
    topicCol = int(projectTopicCol1)-1
    friendsCol = int(friendsCol1)-1
    blurbCol= int(blurbCol1)-1
    projectNameCol = int(projectNameCol1)-1

    personsPerTimes=2
    
    rawdataDict = {}
    #allTimes = ["PD 2 Tuesday, December 19th", "PD 3, Tuesday, December 19th", "PD 4, Tuesday, December 19th", "PD 5, Tuesday, December 19th", "PD 6, Tuesday, December 19th", "PD 2, Thursday, December 21st", "PD 3, Thursday, December 21st", "PD 4, Thursday, December 21st", "PD 5, Thursday, December 21st", "PD 6, Thursday, December 21st"]
    #roomToTimes={element:allTimes for element in ["Room 195","Room 198","Room 199"]}

    roomToTimes = data.get('roomsToTimes')
    allTimes = data.get('allTimes')
    
    roomToTimes = dict(sorted(roomToTimes.items(), key=lambda item: len(item[1]),reverse=True))
    capacityDict = {room: len(times)*personsPerTime for room, times in roomToTimes.items()}
    
    for i in range(len(rawData)):
        x = [str(item) for item in rawData.iloc[i]]
        target_string = x[availabilityCol]
        output_list = []
        for item in allTimes:
            if item in target_string:
                output_list.append(item)
        rawdataDict[x[firstNameCol]+" "+x[lastNameCol]]=[output_list,x[topicCol],x[friendsCol].split(", "),[],x[projectNameCol]]
    
    
    maintopics = {element for value in rawdataDict.values() for element in value[1].split(", ")}
    rawMaintopics = {value[1] for value in rawdataDict.values()}
    roomData = {}
    for maintopic in maintopics:
        roomData[maintopic]=[]
    
    
    #Roomdata topic: people, everyone who has only one topic
    #Rawroomdata contains topics like "Computer Science, Biology" in addition to "Computer Science" and "Biology"

    backupRoomDict={}
    rawRoomData={}
    for topic in rawMaintopics:
        rawRoomData[topic]=[]
        if topic not in maintopics:
            backupRoomDict[topic]=[]
    
    for key, value in rawdataDict.items():
        if "," not in value[1]:
            roomData[value[1]].append(key)
        else:
            backupRoomDict[value[1]].append([key,value[4]])
        rawRoomData[value[1]].append(key)
    
    roomData = dict(sorted(roomData.items(), key=lambda item: len(item[1]),reverse=True))
    rawRoomData = dict(sorted(rawRoomData.items(), key=lambda item: len(item[1]),reverse=True))
    
    initRoomDistribution = {room: [] for room in list(roomToTimes.keys())}
    capacityDictCopy = copy.deepcopy(capacityDict)

    print(maintopics)
    for maintopic in maintopics:
        capacityDictCopy = dict(sorted(capacityDictCopy.items(), key=lambda item: item,reverse=True))
        initRoomDistribution[list(capacityDictCopy.keys())[0]].append([maintopic, [[name,rawdataDict[name][4]] for name in roomData[maintopic]]])
        capacityDictCopy[list(capacityDictCopy.keys())[0]]-=len(roomData[maintopic])
    
    specialGroups=[]
    
    for value in rawRoomData.values():
        if len(value)<=6 and len(value)>1:
            specialGroups.append(value)
    
    for specialGroup in specialGroups:
        for student1 in specialGroup:
                for student2 in specialGroup:
                    if student1 != student2:
                        rawdataDict[student1][3].append(student2)
    
    print(initRoomDistribution)
    #print(rawRoomData)
    print(backupRoomDict)
    
    # Send the data to the frontend
    return render_template(
            "index.html"
        )

if __name__ == '__main__':
    app.run(debug=True)
