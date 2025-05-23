from flask import Flask, request, jsonify, render_template, redirect
import requests, pandas as pd, io, copy, sys
sys.setrecursionlimit(2000)


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generateStep1')
def generateStep1():
    return render_template('generateStep1.html')

@app.route('/generateStep2')
def generateStep2():
    return render_template('generateStep2.html')

roomDistribution={}
capacityDict={}
rawdataDict={}
personsPerTime=2
roomToTimes={}
dayCapacityDict={}

@app.route('/submit_availability', methods=['POST'])
def submit_availability():

    global roomDistribution
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
    
    rawdataDict = {}
    #allTimes = ["PD 2 Tuesday, December 19th", "PD 3, Tuesday, December 19th", "PD 4, Tuesday, December 19th", "PD 5, Tuesday, December 19th", "PD 6, Tuesday, December 19th", "PD 2, Thursday, December 21st", "PD 3, Thursday, December 21st", "PD 4, Thursday, December 21st", "PD 5, Thursday, December 21st", "PD 6, Thursday, December 21st"]
    #roomToTimes={element:allTimes for element in ["Room 195","Room 198","Room 199"]}
    
    #roomToTimes = {"Room 195":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]},"Room 198":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]},"Room 199":{"Day 1":["PD 2 Tuesday, December 19th","PD 3, Tuesday, December 19th","PD 4, Tuesday, December 19th","PD 5, Tuesday, December 19th","PD 6, Tuesday, December 19th"],"Day 2":["PD 2, Thursday, December 21st","PD 3, Thursday, December 21st","PD 4, Thursday, December 21st","PD 5, Thursday, December 21st","PD 6, Thursday, December 21st"]}}
    allTimes = data.get('allTimes')
    roomToTimes = data.get('roomsToTimes')
    #print(allTimes)
    #print(roomToTimes)


    roomToTimes = dict(sorted(roomToTimes.items(), key=lambda item: len(item[1]),reverse=True))
    
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
    
    rawMaintopics = {value[1] for value in rawdataDict.values()}

    #Roomdata topic: people, everyone who has only one topic
    #Rawroomdata contains topics like "Computer Science, Biology" in addition to "Computer Science" and "Biology"
    
    def splitRooms(topic, rooms):
        roomDistribution={roomName:[] for roomName in list(topicsByRoom.keys())}
        students=rawRoomData[topic]
        #print(students)
        rooms= list(sorted(rooms, key=lambda item: item[1]))
        for specialGroup in specialGroups:
            if all(student in students for student in specialGroup):
                #print(rooms)
                for i in range(len(rooms)):
                    if rooms[i][1]>=len(specialGroup):
                        roomDistribution[rooms[i][0]].extend(specialGroup)
                        rooms[i][1]-=len(specialGroup)
                        for student in specialGroup:
                            students.remove(student)
                        break
        rooms= list(sorted(rooms, key=lambda item: item[1]))
        i=0
        while i<len(rooms) and rooms[i][1]==0:
            rooms.remove(rooms[i])
            i+=1
    
        noFriends=[]
        for student in students:
            if not rawdataDict[student][2]:
                roomDistribution[rooms[0]].append(student)
                rooms[0][1]-=1
                noFriends.append(student)
                rooms= list(sorted(rooms, key=lambda item: item[1]))
                i=0
                while i<len(rooms) and rooms[i][1]==0:
                    rooms.remove(rooms[i])
                    i+=1       
                    
        students=[student for student in students if student not in noFriends]
        for student in students:
            friends={}
            for room in rooms:
                if room[1]>0:
                    friends[room[0]]=len(set(roomDistribution[room[0]]) & set(rawdataDict[student][2]))
            friends=sorted(friends, key=lambda item: item[1])
            roomDistribution[friends[0]].append(student)
            for i in range(len(rooms)):
                if rooms[i][0]==friends[0]:
                    rooms[i][1]-=1
        #print(roomDistribution)
        return roomDistribution
    
    rawRoomData={}
    for topic in rawMaintopics:
        rawRoomData[topic]=[]
    
    for key, value in rawdataDict.items():
        rawRoomData[value[1]].append(key)
        
    rawRoomData = dict(sorted(rawRoomData.items(), key=lambda item: len(item[1]),reverse=True))
    
    #print(rawRoomData)
    
    specialGroups=[]
    
    for value in rawRoomData.values():
        if len(value)<=6 and len(value)>1:
            specialGroups.append(value)
    
    specialGroups = sorted(specialGroups, key=len, reverse=True)
    
    for specialGroup in specialGroups:
        for student1 in specialGroup:
                for student2 in specialGroup:
                    if student1 != student2:
                        rawdataDict[student1][3].append(student2)
    
    topicQuantity = {roomName:len(roomStudents) for roomName, roomStudents in rawRoomData.items()}
    topicsByRoom={'Room 195':{"Computer Science":20},
                       "Room 198":{"Biology":15,"Neuroscience":1, "Computer Science":2, "Data Science": 1},
                       "Room 199":{"Engineering":9,"Math":1,"Physics":1, "Material Science":1, "Astronomy":1, "Earth science/Geology":1, 'nan':1, "Soil Studies":1, 'Agriculture': 1}}
    
    topicDistribution={}
    for room, topics in topicsByRoom.items():
        for topic, size in topics.items():
            if topic not in list(topicDistribution.keys()):
                topicDistribution[topic]=[]
            topicDistribution[topic].append([room,size])
    
    roomDistribution={roomName:[] for roomName in list(topicsByRoom.keys())}
    print(topicDistribution)
    print(rawRoomData)
    for topic, rooms in topicDistribution.items():
        if len(rooms)==1:
            roomDistribution[rooms[0][0]].extend(rawRoomData[topic])
            continue
        for room, students in splitRooms(topic, rooms).items():
            roomDistribution[room].extend(students)
    
    for room, students in roomDistribution.items():
        for i in range(len(students)):
            student=students[i]
            students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
    '''
    for room, students in roomDistribution.items():
        print(room)
        print(len(students))
        print(students)
    '''
    print(roomDistribution)
    return render_template('generateStep1.html')

@app.route('/get_data')
def get_data():
    return jsonify({
        "realInitRoomDistribution": roomDistribution,
        "capacityDict": capacityDict
    })

@app.route('/get_data')
def getDataForStep2():
    return jsonify({
        "roomDayDistribution": roomDayDistribution,
        "capacityDict": capacityDict,
        "dayCapacityDict": dayCapacityDict
    })

@app.route('/receive_schedule', methods=['POST'])
def receive_schedule():
    unboxedRoomData = request.get_json()
    print("Received schedule:", unboxedRoomData)

    global roomDayDistribution

    def findDayDistributions(roomSchedule, studentAvailability, thisDayTimes, score):
        global allDayDistributions
    
        if not studentAvailability:
            newScore=score
            for students in list(roomSchedule.values()):
                for student in students:
                    if (len(set(students) & set(rawdataDict[student][2])))>0:
                        newScore+=5
            allDayDistributions.append([roomSchedule,newScore])
            return
        
        student = list(studentAvailability.keys())[0]
        days = studentAvailability[list(studentAvailability.keys())[0]]
    
        globalDays = [day for day, number in thisDayTimes.items() if number>0]
        
        availableDays = list(set(globalDays) & set(days))
        if len(availableDays)==0:
            #compromised.append(student)
            print(student)
            #availableDays=globalDays
            #break
            return
        for day in availableDays:
            roomSchedule1 = copy.deepcopy(roomSchedule)
            thisDayTimes1 = copy.deepcopy(thisDayTimes)
            roomSchedule1[day].append(student)
            thisDayTimes1[day]-=1
        
            studentAvailability1 = copy.deepcopy(studentAvailability)
            del studentAvailability1[student]
            newScore = score
            if len(set(roomSchedule[day]) & set(rawdataDict[student][2]))>0:
                newScore+=len(set(roomSchedule[day]) & set(rawdataDict[student][2]))
            
            findDayDistributions(roomSchedule1, studentAvailability1, thisDayTimes1, newScore)
    
    roomDayDistribution={}
    for thisRoom, thisStudents in unboxedRoomData.items():
    
        thisDayTimesFull = roomToTimes[thisRoom]
        thisDayTimes = {key:len(value)*personsPerTime for key,value in roomToTimes[thisRoom].items()}
        thisDays = list(roomToTimes[thisRoom].keys())
        roomSchedule = {key:[] for key in thisDays}
    
        studentAvailability = {}
        for student in thisStudents:
            studentTimes = rawdataDict[student][0]
            availableDays = []
            for day, times in thisDayTimesFull.items():
                if len(set(studentTimes) & set(times)) != 0:
                    availableDays.append(day)
            studentAvailability[student]=availableDays
        
        studentAvailability = dict(sorted(studentAvailability.items(), key=lambda item: len(item[1])))
        
        allDayDistributions = []
        
        findDayDistributions(roomSchedule, studentAvailability, thisDayTimes, 0)
        allDayDistributions = sorted(allDayDistributions, key=lambda x: x[1], reverse=True)
        print(len(allDayDistributions))
        
        print(thisRoom)
        if not allDayDistributions:
            print("unfortunately, it sucks")
        else:
            consideredDistributions = []
            highScore = allDayDistributions[0][1]
            i=0
            n=10
            while allDayDistributions[i][1]==highScore:
                i+=1
            if len(allDayDistributions)<n:
                for distribution in allDayDistributions:
                    consideredDistributions.append(distribution)
            elif i<=n:
                for distribution in allDayDistributions[:n]:
                    consideredDistributions.append(distribution)
            else:
                hop=(int)(i/n)
                for j in range(0,i,hop):
                    distribution=allDayDistributions[j]
                    consideredDistributions.append(distribution)
            print()
            
        roomDayDistribution[thisRoom]=consideredDistributions
    
    for room, dayChoices in roomDayDistribution.items():
        for dayChoice in dayChoices:
            for day, students in dayChoice[0].items():
                for i in range(len(students)):
                    student=students[i]
                    students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
    
    print(roomDayDistribution) 
    #return jsonify({"status": "success", "message": "Schedule received"})
    return render_template('generateStep2.html')

if __name__ == '__main__':
    app.run(debug=True)
