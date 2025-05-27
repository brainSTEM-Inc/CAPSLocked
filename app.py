from flask import Flask, request, jsonify, render_template, redirect
import requests, pandas as pd, io, copy, sys
sys.setrecursionlimit(2000)


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/logistics')
def logistics():
    return render_template('logistics.html')

@app.route('/generateStep1')
def generateStep1():
    return render_template('generateStep1.html')

@app.route('/generateStep2')
def generateStep2():
    return render_template('generateStep2.html')

@app.route('/4')
def goto4():
    return render_template('4.html')

roomDistribution={}
capacityDict={}
rawdataDict={}
personsPerTime=2
roomToTimes={}
dayCapacityDict={}
displayAllTimes=[]
displayAllTimesFromData=[]
allRooms=[]
displayHeaders=[]
days=[]
allTimes=[]
dayOrder=[]

@app.route('/getParsedData')
def getParsedData():
    return jsonify({
        "dataDict": rawdataDict,
        "displayHeaders": displayHeaders,
        "allRooms": allRooms,
        "displayAllTimes": displayAllTimes,
        "displayAllTimesFromData": displayAllTimesFromData
    })

@app.route('/getRoomsAndTimes')
def getRoolsAndTimes():
    return jsonify({
        "rooms": allRooms,
        "times": allTimes,
        "days": days
    })

@app.route('/parse_data', methods=['POST'])
def parse_data():
    global roomDistribution
    global capacityDict
    global dayCapacityDict
    global rawdataDict
    global personsPerTime
    global roomToTimes
    global displayHeaders
    global allRooms
    global displayAllTimes
    global displayAllTimesFromData
    global allTimes
    global days
    
    data = request.get_json()

    url = data.get('url')
    firstNameCol1 = data.get('firstNameCol')
    lastNameCol1 = data.get('lastNameCol')
    projectNameCol1 = data.get('projectNameCol')
    projectTopicCol1 = data.get('projectTopicCol')
    availabilityCol1 = data.get('availabilityCol')
    friendsCol1 = data.get('friendsCol')
    blurbCol1 = data.get('blurbCol')
    days = data.get('days')

    urlData = requests.get(url).content
    rawData = pd.read_csv(io.StringIO(urlData.decode('utf-8')),header=None)
    
    dataHeaders = rawData.iloc[0].tolist()
    rawData = rawData.iloc[1:]

    firstNameCol = int(firstNameCol1)-1
    lastNameCol = int(lastNameCol1)-1
    availabilityCol = int(availabilityCol1)-1
    topicCol = int(projectTopicCol1)-1
    friendsCol = int(friendsCol1)-1
    blurbCol= int(blurbCol1)-1
    projectNameCol = int(projectNameCol1)-1
    
    personsPerTime=2
    
    rawdataDict = {}
    allTimes = data.get('allTimes')
    allRooms = data.get('allRooms')

    days1={}
    i=1
    for day in days:
        print(day)
        days1["Day "+str(i)]=day
        i+=1
    days=days1
    
    for i in range(len(rawData)):
        x = [str(item) for item in rawData.iloc[i]]
        target_string = x[availabilityCol]
        output_list = []
        for item in allTimes:
            if item in target_string:
                output_list.append(item)
        rawdataDict[x[firstNameCol].strip()+" "+x[lastNameCol].strip()]=[output_list,x[topicCol],x[friendsCol].split(", "),[],x[projectNameCol]]

    allTimesFromData = set(time for value in list(rawdataDict.values()) for time in value[0])
    print(allTimesFromData)
    for time in allTimes:
        if time in allTimesFromData:
            displayAllTimes.append([time,1])
        else:
            displayAllTimes.append([time,0])
    for time in allTimesFromData:
        if time in allTimes:
            displayAllTimesFromData.append([time,1])
        else:
            displayAllTimesFromData.append([time,0])    

    displayHeaders=["Senior Name",dataHeaders[topicCol],dataHeaders[projectNameCol],dataHeaders[availabilityCol],dataHeaders[friendsCol],dataHeaders[blurbCol]]
    return render_template('index.html')


periodMap = {}
dayOrder=[]
@app.route('/submit_availability', methods=['POST'])
def submit_availability():
    global dayOrder
    global roomDistribution
    global capacityDict
    global dayCapacityDict
    global rawdataDict
    global personsPerTime
    global roomToTimes
    global periodMap
    
    print("🔔 submit_availability was called!")
    data = request.get_json()

    roomToTimes = data.get('roomsToTimes')
    periodMap = data.get('periodMap')
    roomToTimes = dict(sorted(roomToTimes.items(), key=lambda item: len(item[1]),reverse=True))
    #print(roomToTimes)
    dayOrder = list(data.get('dayOrder').values())
    
    for room, times in roomToTimes.items():
        capacityDict[room]=sum(len(values) for values in times.values())*personsPerTime
        dayCapacityDict[room]={}
        for day, daytimes in times.items():
            dayCapacityDict[room][day]=len(daytimes)*personsPerTime
        
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
    #print(topicDistribution)
    #print(rawRoomData)
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
    #print(roomDistribution)
    return render_template('generateStep1.html')

@app.route('/get_data')
def get_data():
    return jsonify({
        "realInitRoomDistribution": roomDistribution,
        "capacityDict": capacityDict
    })

@app.route('/getDataForStep2')
def getDataForStep2():
    #print(roomDayDistribution);
    return jsonify({
        "roomDayDistribution": roomDayDistribution,
        "capacityDict": capacityDict,
        "dayCapacityDict": dayCapacityDict
    })

@app.route('/getFinalDistribution')
def getDataForStep3():
    #print(daysRoomsTimes);
    return jsonify({
        "daysRoomsTimes":daysRoomsTimes
    })

allDayDistributions = []
@app.route('/receive_schedule', methods=['POST'])
def receive_schedule():
    unboxedRoomData = request.get_json()
    print("Received schedule:", unboxedRoomData)

    global allDayDistributions
    global roomDayDistribution
    global days

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
            #print(student)
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
        #print(len(allDayDistributions))
        
        #print(thisRoom)
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
            #print()
            
        roomDayDistribution[thisRoom]=consideredDistributions

    print(dayOrder)
    for room, dayChoices in roomDayDistribution.items():
        for dayChoice in dayChoices:
            dayChoice[0]={day: dayChoice[0][day] for day in dayOrder}
            for day, students in dayChoice[0].items():
                for i in range(len(students)):
                    student=students[i]
                    students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
    
    print(roomDayDistribution) 
    #return jsonify({"status": "success", "message": "Schedule received"})
    return render_template('generateStep2.html')

daysRoomsTimes={}
schedules=[]
dataDict ={}
@app.route('/final_distribution', methods=['POST'])
def final_distribution():
    global daysRoomsTimes
    global dataDict
    global rawdataDict
    global roomToTimes 
    global personsPerTime
    global schedules
    global periodMap
    roomData = request.get_json()
    print("Received schedule:", roomData)
    #roomData={'Room 195': {'Day 1': ['Sarah Yu', 'Jay Wankhede', 'Nikhil Kakani', 'Ritviik Ravi', 'Aileen Sharma', 'Rachel Zhang', 'Archit Ashok', 'Catherine Tenny', 'Sean Radimer', 'Chris Ramos'], 'Day 2': ['Eddie Wu', 'Aditya Lahiri', 'James Tan', 'Ryan Zhao', 'Akhil Raman', 'Aaron Zhu', 'Nicholas McGonigle', 'Zory Teselko', 'Aidan Paul', 'Pranav Gaddam']}, 'Room 198': {'Day 1': ['Elizabeth Issac', 'Veera Singh', 'Priscilla Kim', 'David Ruan', 'Vincent Ha', 'Alex Shelley', 'Esme Liao', 'Michael Tsegaye', 'Kelly Chen', 'Hannah Chen'], 'Day 2': ['Leavy Hu', 'Snigdha Chelluri', 'Daniel Ling', 'Daniel Mathew', 'Katherine Saeed', 'Devon Chen', 'Neel Bhattacharyya', 'Andrew Sha', 'Rohun Sarkar']}, 'Room 199': {'Day 1': ['Lahari Bandaru', 'Sachet Korada', 'Larson Ozbun', 'Patrick Le', 'Jeffery Westlake', 'Sanvika Thimmasamudram', 'Ethan Nee', 'Milo Stammers', 'sumedh vangara', 'Tarini Nagenalli'], 'Day 2': ['Elizabeth Ivanova', 'Avyukth Selvadurai', 'Muhammad Ahmad', 'Patrick Foley', 'Tanya Bait', 'Srinidhi Guruvayurappan', 'Lakshmi Sangireddi']}}
    #roomData={'Room 198': {'Day 1': ['Elizabeth Issac', 'Veera Singh', 'Priscilla Kim', 'David Ruan', 'Vincent Ha', 'Alex Shelley', 'Esme Liao', 'Michael Tsegaye', 'Kelly Chen', 'Hannah Chen']}}
    #periodMap={'PD 2, Tuesday, December 19th':"2", 'PD 3, Tuesday, December 19th':"3", 'PD 4, Tuesday, December 19th':"4", 'PD 5, Tuesday, December 19th':"5", 'PD 6, Tuesday, December 19th':"6", 'PD 2, Thursday, December 21st':"2", 'PD 3, Thursday, December 21st':"3", 'PD 4, Thursday, December 21st':"4", 'PD 5, Thursday, December 21st':"5", 'PD 6, Thursday, December 21st':"6"}


    def g(current, students, score, maintopic, day):
        global schedules
        global dataDict
        global roomsToTimes
        global personsPerTime
        if not students:
            #print([current,score])
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
                if len(schedules)<100:
                    g(newSchedule, newStudents,newScore, maintopic, day)
                
    
    def f(room, maintopic, day, debug=False):
        global schedules
        global dataDict
        global rawdataDict
        global roomToTimes
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
        #print(schedules)
        if not schedules:
            return []
        sorted_schedules = sorted(schedules, key=lambda x: x[1], reverse=True)
        #print(schedules)
        #print("Schedule w/ nemesi")
        highScore = sorted_schedules[0][1]
        #print(highScore)
        i=0
        n=10
        schedulesToReturn = []
        while i<len(sorted_schedules) and sorted_schedules[i][1]==highScore:
            i+=1
        if len(sorted_schedules)<n:
            for schedule in sorted_schedules:
                #print(schedule)
                schedulesToReturn.append(schedule[0])
        elif i<=n:
            for schedule in sorted_schedules[:n]:
                #print(schedule)
                schedulesToReturn.append(schedule[0])
        else:
            hop=(int)(i/n)
            for j in range(0,i,hop):
                #print(sorted_schedules[j])
                schedulesToReturn.append(sorted_schedules[j][0])
        #print()
        return schedulesToReturn
    
    daysRoomsTimes = {}
    
    for roomName, roomInfo in roomData.items():
        for day, thisRoom in roomInfo.items():
            schedules=[]
            dataDict ={}
            if day not in list(daysRoomsTimes.keys()):
                daysRoomsTimes[day]={}
            #print(thisRoom)
            #print(roomName)
            #print(day)
            try:
                thisSchedule=f(thisRoom,roomName,day)
            except:
                print(f(thisRoom,roomName,day,True))
                
            daysRoomsTimes[day][roomName]=f(thisRoom,roomName,day)[0]
    
    #print(daysRoomsTimes)
    
    for day, rooms in daysRoomsTimes.items():
        for room, periods in rooms.items():
            updated_periods = {periodMap.get(period, period): value for period, value in periods.items()}
            daysRoomsTimes[day][room]=updated_periods
            for period, students in periods.items():
                for i in range(len(students)):
                    student=students[i]
                    students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
    
    
    print(daysRoomsTimes)
    #return jsonify({"status": "success", "message": "Schedule received"})
    return render_template('4.html')


if __name__ == '__main__':
    app.run(debug=True)
