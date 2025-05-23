from flask import Flask, request, jsonify, render_template, redirect
import requests, pandas as pd, io, copy, sys
sys.setrecursionlimit(2000)


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/hola')
def generateStep1():
    return render_template('generateStep1.html')

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
    
    specialGroups=[["Catherine Tenny","Ryan Zhao","Vincent Ha"]]
    
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
                       "Room 198":{"Biology":11,"Neuroscience":1, "Computer Science":2, "Computer Science, Data Science": 1,'Computer Science, Biology': 4},
                       "Room 199":{"Engineering":6,"Math":1,"Physics":1, "Material Science":1, "Astronomy":1, "Computer Science, Engineering":3, "Earth science/Geology":1, 'nan':1, "Soil Studies":1, 'Computer Science, Agriculture': 1}}
    
    topicDistribution={}
    for room, topics in topicsByRoom.items():
        for topic, size in topics.items():
            if topic not in list(topicDistribution.keys()):
                topicDistribution[topic]=[]
            topicDistribution[topic].append([room,size])
    
    roomDistribution={roomName:[] for roomName in list(topicsByRoom.keys())}
    #print(topicDistribution)
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
    
    for room, students in roomDistribution.items():
        print(room)
        print(len(students))
        print(students)
    
    return render_template('generateStep1.html')

@app.route('/get_data')
def get_data():
    return jsonify({
        "realInitRoomDistribution": roomDistribution,
        "capacityDict": capacityDict
    })

limit=10

@app.route('/receive_schedule', methods=['POST'])
def receive_schedule():
    roomData = request.get_json()
    del roomData["Multiple Topics"]
    print("Received schedule:", roomData)
    #print(rawdataDict)

    unboxedRoomData={}
    for room, days in roomData.items():
        thisRoom=[]
        for students in list(days.values()):
            thisRoom.extend(students)
        unboxedRoomData[room]=thisRoom
    
    print(unboxedRoomData)
    
    unboxedRoomData={'Room 195': ['Vincent Ha', 'Catherine Tenny', 'Akhil Raman', 'Sean Radimer', 'Sarah Yu', 'Aaron Zhu', 'Eddie Wu', 'Nicholas McGonigle', 'Zory Teselko', 'Jay Wankhede', 'Ritviik Ravi', 'Nikhil Kakani', 'Aileen Sharma', 'Archit Ashok', 'Rachel Zhang', 'Pranav Gaddam', 'James Tan', 'Aditya Lahiri', 'Chris Ramos', 'Aidan Paul'], 'Room 198': ['Alex Shelley', 'Leavy Hu', 'Esme Liao', 'Veera Singh', 'Michael Tsegaye', 'Kelly Chen', 'Hannah Chen', 'Katherine Saeed', 'Priscilla Kim', 'Snigdha Chelluri', 'Daniel Ling', 'Ryan Zhao', 'Elizabeth Issac', 'Daniel Mathew', 'Devon Chen', 'Neel Bhattacharyya', 'David Ruan'], 'Room 199': ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee', 'Tarini Nagenalli', 'Tanya Bait', 'Andrew Sha', 'Patrick Foley', 'sumedh vangara', 'Milo Stammers', 'Lakshmi Sangireddi', 'Srinidhi Guruvayurappan', 'Rohun Sarkar', 'Elizabeth Ivanova', 'Jeffery Westlake', 'Sanvika Thimmasamudram', 'Lahari Bandaru']}
    #{'Room 195': ['Vincent Ha', 'Catherine Tenny', 'Akhil Raman', 'Sean Radimer', 'Sarah Yu', 'Aaron Zhu', 'Eddie Wu', 'Nicholas McGonigle', 'Zory Teselko', 'Aidan Paul', 'Chris Ramos', 'Nikhil Kakani', 'Pranav Gaddam', 'Ritviik Ravi', 'Aileen Sharma', 'James Tan', 'Archit Ashok', 'Rachel Zhang', 'Aditya Lahiri', 'Jay Wankhede'], 'Room 198': ['Alex Shelley', 'Leavy Hu', 'Esme Liao', 'Veera Singh', 'Michael Tsegaye', 'Kelly Chen', 'Hannah Chen', 'Katherine Saeed', 'Priscilla Kim', 'Snigdha Chelluri', 'Daniel Ling', 'Andrew Sha', 'Elizabeth Issac', 'Daniel Mathew', 'Devon Chen', 'Neel Bhattacharyya', 'Ryan Zhao', 'David Ruan'], 'Room 199': ['Sachet Korada', 'Avyukth Selvadurai', 'Larson Ozbun', 'Muhammad Ahmad', 'Patrick Le', 'Ethan Nee', 'Milo Stammers', 'Patrick Foley', 'sumedh vangara', 'Tanya Bait', 'Srinidhi Guruvayurappan', 'Rohun Sarkar', 'Elizabeth Ivanova', 'Jeffery Westlake', 'Sanvika Thimmasamudram', 'Lahari Bandaru', 'Tarini Nagenalli', 'Lakshmi Sangireddi']}
    #unboxedRoomData={'Room 195': ['Vincent Ha', 'Catherine Tenny', 'Akhil Raman', 'Sean Radimer', 'Sarah Yu']}
    for thisRoom, thisStudents in unboxedRoomData.items():
    
        thisDayTimesFull = roomToTimes[thisRoom]
        thisDayTimes = {key:len(value)*personsPerTime for key,value in roomToTimes[thisRoom].items()}
        thisDays = list(roomToTimes[thisRoom].keys())
        roomSchedule = {key:[] for key in thisDays}
        print(thisDayTimes)
        
        #compromised = []
        
        
        studentAvailability = {}
        for student in thisStudents:
            studentTimes = rawdataDict[student][0]
            availableDays = []
            for day, times in thisDayTimesFull.items():
                if len(set(studentTimes) & set(times)) != 0:
                    availableDays.append(day)
            studentAvailability[student]=availableDays
        
        studentAvailability = dict(sorted(studentAvailability.items(), key=lambda item: len(item[1])))
        #print(studentAvailability)
        
        for student, days in studentAvailability.items():
            
            globalDays = [day for day, number in thisDayTimes.items() if number>0]
            
            '''print(thisDayTimes)
            print(roomSchedule)
            print(globalDays)'''
            
            availableDays = list(set(globalDays) & set(days))
            if len(availableDays)==0:
                #compromised.append(student)
                print(student)
                #availableDays=globalDays
                break
            if len(availableDays)==1:
                roomSchedule[availableDays[0]].append(student)
                thisDayTimes[availableDays[0]]-=1
                continue
            friendDays=[]
            for day in availableDays:
                if len(set(roomSchedule[day]) & set(rawdataDict[student][2]))>0:
                    friendDays.append(day)
            if not friendDays:
                day=sorted(availableDays, key=lambda x: thisDayTimes[x], reverse=True)[0]
            else:
                day=sorted(friendDays, key=lambda x: thisDayTimes[x], reverse=True)[0]
                
            roomSchedule[day].append(student)
            thisDayTimes[day]-=1     
    
        #print(roomSchedule)
        roomData[thisRoom]=roomSchedule
        
    def g(current, students, score, maintopic, day):
        global dataDict
        global schedules
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
    
    allSchedules={}
    
    for maintopic, dayTimes in roomData.items():
    #maintopic=list(roomData.keys())[0]
    #dayTimes=roomData[list(roomData.keys())[0]]
        allSchedules[maintopic]={}
    #day=list(dayTimes.keys())[0]
        for day in list(dayTimes.keys()):
            allSchedules[maintopic][day]=[]
            room = roomData[maintopic][day]
            #print(room)
            schedules=[]
            dataDict ={}
        
            print(maintopic)
            print(day)
            print(room)
            print()
        
        
            firstTry = f(room,maintopic,day)
            if firstTry:
                pass
                allSchedules[maintopic][day].append(["",firstTry])
            else:
                x=True
                for sacrifice in room:
                    newRoom = copy.deepcopy(room)
                    newRoom.remove(sacrifice)
                    secondTry = f(newRoom,maintopic,day)
                    if secondTry:
                       allSchedules[maintopic][day].append([sacrifice,secondTry])
                       print("Sacrifice: "+sacrifice)
                       x=False
        
                if x:
                    print("yeah so it sucks")
        
            print()
            print()

                
        
    return jsonify({"status": "success", "message": "Schedule received"})

if __name__ == '__main__':
    app.run(debug=True)
