from flask import Flask, request, jsonify, render_template, redirect
import requests, pandas as pd, io, copy

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hola')
def hola():
    return render_template('hola.html')

realInitRoomDistribution={}
capacityDict={}
rawdataDict={}
personsPerTime=2
roomToTimes={}
dayCapacityDict={}

@app.route('/submit_availability', methods=['POST'])
def submit_availability():
    global realInitRoomDistribution
    global capacityDict
    global dayCapacityDict
    global rawdataDict
    global personsPerTime
    global roomToTimes
    
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
    
    personsPerTime=2
    bigGroupLowerBound = 10
    
    rawdataDict = {}
    allTimes = ["PD 2 Tuesday, December 19th", "PD 3, Tuesday, December 19th", "PD 4, Tuesday, December 19th", "PD 5, Tuesday, December 19th", "PD 6, Tuesday, December 19th", "PD 2, Thursday, December 21st", "PD 3, Thursday, December 21st", "PD 4, Thursday, December 21st", "PD 5, Thursday, December 21st", "PD 6, Thursday, December 21st"]
    #roomToTimes={element:allTimes for element in ["Room 195","Room 198","Room 199"]}
    
    roomToTimes = {"Room 195":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]},"Room 198":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]},"Room 199":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]}}
    #allTimes = data.get('allTimes')
    
    roomToTimes = dict(sorted(roomToTimes.items(), key=lambda item: len(item[1]),reverse=True))
    capacityDict={"Multiple Topics":0}
    dayCapacityDict={"Multiple Topics": {"Day 1":0}}
    
    for room, times in roomToTimes.items():
        capacityDict[room]=sum(len(values) for values in times.values())*personsPerTime
        dayCapacityDict[room]={}
        for day, daytimes in times.items():
            dayCapacityDict[room][day]=len(daytimes)*personsPerTime
        
    for i in range(len(rawData)):
        x = [str(item) for item in rawData.iloc[i]]
        target_string = x[availabilityCol]
        output_list = []
        for item in allTimes:
            if item in target_string:
                output_list.append(item)
        rawdataDict[x[firstNameCol].strip()+" "+x[lastNameCol].strip()]=[output_list,x[topicCol],x[friendsCol].split(", "),[],x[projectNameCol]]
    
    
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
    
    for maintopic in list(roomData.keys()):
        #print(capacityDictCopy)
        capacityDictCopy = dict(sorted(capacityDictCopy.items(), key=lambda item: item[1],reverse=True))
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
    
    backupRoomList = []
    for key, value in backupRoomDict.items():
        backupRoomList.append([key,value])
    
    #print(initRoomDistribution)
    #print(rawRoomData)
    #print(backupRoomDict)
    
    realInitRoomDistribution={"Multiple Topics":{"Day 1": backupRoomList}}
    for room, days in roomToTimes.items():
        realInitRoomDistribution[room]={"Day 1":initRoomDistribution[room]}
        for day in list(days.keys())[1:]:
            realInitRoomDistribution[room][day]=[];

    print(realInitRoomDistribution)
    print(dayCapacityDict)
    # Send the data to the frontend
    #return render_template(
           # "hola.html"
       # )
    return render_template('hola.html')

@app.route('/get_data')
def get_data():
    return jsonify({
        "realInitRoomDistribution": realInitRoomDistribution,
        "capacityDict": capacityDict,
        "dayCapacityDict": dayCapacityDict
    })

limit=10

@app.route('/receive_schedule', methods=['POST'])
def receive_schedule():
    roomData = request.get_json()
    del roomData["Multiple Topics"]
    print("Received schedule:", roomData)
    maintopics = list(roomToTimes.keys())
    print(rawdataDict)
    print(roomToTimes)

    def g(current, students, score, maintopic, day):
        if not students:
            schedules.append([current,score])
            return
        #try:  
        for time in list(set(dataDict[students[0]][0]) & set(roomToTimes[maintopic][day])):
            #print(current)
            if len(current[time]) < personsPerTime:
                newSchedule = copy.deepcopy(current)
                newStudents = copy.deepcopy(students)
                newScore=score
                newScore+=len(set(newSchedule[time]) & set(dataDict[students[0]][2]))
                if dataDict[students[0]][3]:
                    newScore+=5*len(set(newSchedule[time]) & set(dataDict[students[0]][3]))
                newSchedule[time].append(students[0])
                newStudents.remove(students[0])
                g(newSchedule, newStudents,newScore, maintopic, day)
    
    failures=[]
    
    def f(room, maintopic, day):
        global schedules
        global dataDict
        schedules=[]
        dataDict ={}
        
        for key, value in rawdataDict.items():
            if key in room:
                dataDict[key] = value
        
        realFlexibility = sorted(dataDict, key=lambda x: len(dataDict[x][0]))
        
        currentSchedule = {}
        for time in roomToTimes[maintopic][day]:
            currentSchedule[time]=[]
            
        schedules=[]
        g(currentSchedule, realFlexibility,0, maintopic, day)
        if not schedules:
            return False
        sorted_schedules = sorted(schedules, key=lambda x: x[1], reverse=True)
        print("Schedule w/ nemesi")
        for x in sorted_schedules[:10]:
            print(x)
        print()
        return True
    
    for maintopic, dayTimes in roomData.items():
        for day in list(dayTimes.keys()):
            room = roomData[maintopic][day]
            #print(room)
            schedules=[]
            dataDict ={}
    
            print(maintopic)
            print(day)
            
            if not f(room,maintopic,day):
                x=True
                for sacrifice in room:
                    newRoom = copy.deepcopy(room)
                    newRoom.remove(sacrifice)
                    if f(newRoom,maintopic,day):
                       print("Sacrifice: "+sacrifice)
                       x=False
    
                if x:
                    print("yeah so it sucks")
            print()
            print()
                
        
    return jsonify({"status": "success", "message": "Schedule received"})

if __name__ == '__main__':
    app.run(debug=True)
