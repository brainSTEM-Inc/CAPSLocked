from flask import Flask, request, jsonify, render_template, redirect, session, Response
import requests, pandas as pd, io, copy, sys, json, csv

sys.setrecursionlimit(20000)

import os
import psycopg2
import random

# Get the database URL from Render's environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Test query: Create a simple table (optional)
cur.execute("CREATE TABLE IF NOT EXISTS test (id SERIAL PRIMARY KEY, name TEXT);")
conn.commit()

print("Connected to Neon DB!")

def clear_table(table_name):
    global conn
    global cur
    """Deletes all rows in the specified table."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor() 
    cur.execute(f'DELETE FROM "{table_name}";')
    conn.commit()
    print("im doing something im not supposed to be doing yk wut these error messages are kinda funny lets write a story so basiclaly once upon a itme")
    print(f"Table '{table_name}' has been cleared!")

#clear_table("Accounts")

app = Flask(__name__)

app.secret_key = os.urandom(24) 

app.config['SESSION_PERMANENT'] = True  # Ensures session persists
app.config['SESSION_TYPE'] = 'filesystem'
cached_accounts=[]

@app.before_request
def initialize_session():
    if "user" not in session:
        session["user"] = "none"
    conn = psycopg2.connect(DATABASE_URL)
    db = conn.cursor()

    global cached_accounts
    cached_accounts = db.execute('SELECT * FROM public."Accounts"')
    print(cached_accounts)

@app.route('/')
def home():
    session["user"] = "none"
    return render_template('index.html')

@app.route('/logistics')
def logistics():
    return render_template('logistics.html')

@app.route('/login')
def login():
    session["user"] = "none"
    return render_template('login.html')

@app.route('/upload')
def upload():
    global rawdataDict
    try:
        rawdataDict={}
    except:
        print("welp")
    return render_template('upload.html')

@app.route('/select')
def select():
    return render_template('select.html')

@app.route('/bugreport')
def bugreport():
    return render_template('bugreport.html')

@app.route('/topicsByRoom')
def topicsByRoom():
    if session.get("user") != "Admin":
        return render_template('accessdenied.html')
    return render_template('topicsByRoom.html')

@app.route('/specialGroups')
def specialGroups():
    if session.get("user") != "Admin":
        return render_template('accessdenied.html')    
    return render_template('specialGroups.html')


@app.route('/seniorQuestionnaire')
def seniorQuestionnaire():
    if session.get("user") == "none" or session.get("class")=="Junior":
        return render_template('accessdenied.html')
    return render_template('seniorQuestionnaire.html')

@app.route('/juniorQuestionnaire')
def juniorQuestionnaire():
    if session.get("user") == "none" or session.get("class")=="Senior":
        return render_template('accessdenied.html')
    return render_template('juniorQuestionnaire.html')

@app.route('/projectTopics')
def projectTopics():
    if session.get("user") != "Admin":
        return render_template('accessdenied.html')
    return render_template('projectTopics.html')

@app.route('/moderator')
def moderator():
    if session.get("user") != "Admin":
        return render_template('accessdenied.html')
    return render_template('moderator.html')

@app.route('/viewResponses')
def viewResponses():
    if session.get("user") != "Admin":
        return render_template('accessdenied.html')
    return render_template('viewResponses.html')

@app.route('/availability')
def availability():
    if session.get("user") != "Admin":
        return render_template('accessdenied.html')
    return render_template('availability.html')

@app.route('/rosters')
def rosters():
    if session.get("user") != "Admin":
        return render_template('accessdenied.html')
    return render_template('rosters.html')

@app.route('/topics')
def topics():
    return render_template('topics.html')

@app.route('/addQuestion')
def addQuestion():
    return render_template('addQuestion.html')

@app.route('/generateStep1')
def generateStep1():
    return render_template('generateStep1.html')

@app.route('/generateStep2')
def generateStep2():
    return render_template('generateStep2.html')

@app.route('/4')
def goto4():
    return render_template('4.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')




@app.route('/checkLogin', methods=['POST'])
def checkLogin():
    global conn
    global cur
    global admin
    session.clear()
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor() 
    cur.execute('SELECT "Username" FROM public."Admin" LIMIT 1;')
    actualUsername=cur.fetchone()[0]
    cur.execute('SELECT "Password" FROM public."Admin" LIMIT 1;')
    actualPassword=cur.fetchone()[0]
    cur.execute('SELECT "Code" FROM public."Admin" LIMIT 1;')
    actualCode=cur.fetchone()[0]
    #print(actualUsername)
    #print(actualPassword)
    data = request.get_json()
    if data.get("username")==actualUsername and data.get("password")==actualPassword:
        session["user"]="Admin";
        print("u are the smartest person alive")
        session.modified = True
        return render_template('index.html')   
    if data.get("password")==actualCode:
        session["user"]="Admin";
        print("u are the smartest person alive")
        session.modified = True
        return render_template('index.html')   
        
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    #query = """SELECT Username, Name, Message, Class FROM Accounts WHERE Username = %s AND Password = %s;"""
    query = """SELECT "Username", "Name", "Message", "Class" FROM "Accounts" WHERE "Username" = %s AND "Password" = %s;"""
    cur.execute(query, (data.get("username"), data.get("password")))
    result = cur.fetchone()  # Fetch matched row

    if result:  # If user exists
        print("i gave a second chance to cupid jk im not that stupid thats why this works")
        session["user"] = result[0]  
        session["name"] = result[1] 
        session["message"] = result[2] 
        session["class"] = result[3] 
        session.modified = True

    print(session.get("user"))
    return render_template('index.html')    

@app.route('/getUser')
def isAdmin():
    print(session.get("user"))
    print(session.get("name"))
    print(session.get("message"))
    print(session.get("class"))
    return jsonify({
        "user":session.get("user"),
        "name":session.get("name"),
        "message":session.get("message"),
        "class":session.get("class"),
    })

@app.route('/committeeCredentials', methods=['POST'])
def committeeCredentials():
    global conn
    global cur
    session.pop("committeeMember", None)
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor() 
    cur.execute('SELECT "Code" FROM public."Admin" LIMIT 1;')
    actualCode=cur.fetchone()[0]
    print(actualCode)
    data = request.get_json()
    print(data.get("code"))
    if data.get("code")==actualCode:
        session["committeeMember"]="True";
        print("pleaides says ur a committee member! good job committing handsome")
        session.modified = True

    print(session.get("committeeMember"))
    return render_template('select.html')    

@app.route('/isCommitteeMember')
def isCommitteeMember():
    print(session.get("committeeMember"))
    return jsonify({
        "committeeMember":session.get("committeeMember")
    })



@app.route('/getStudents')
def getStudents():
    global conn
    global cur
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor() 
    cursor.execute('SELECT "Name" FROM "Senior Profiles";')
    seniors = [row[0] for row in cursor.fetchall()]  # Convert results into a list
    cursor.execute('SELECT "Name" FROM "Junior Profiles";')
    juniors = [row[0] for row in cursor.fetchall()]  # Convert results into a list
    
    if session.get("user")=="Admin":
        welcome="Welcome, Test User!"
    else:
        welcome="Welcome,  "+session["name"]+"!"

    setGlobalVariables()
    try:
        getRawData()
    except:
        print("whatever no biggie")
    day_periods_map = {}

    for room in roomToTimes.values():
        for day, periods in room.items():
            if day not in day_periods_map:
                day_periods_map[day] = set()
            day_periods_map[day].update(periods)  # Add periods, avoiding duplicates
    
    # Convert sets to lists for final output
    day_periods_map = {day: list(periods) for day, periods in day_periods_map.items()}
    
    updated_day_periods_map = {
        day: [str(periodMap[period]) for period in periods] for day, periods in day_periods_map.items()
    }

    
        
    return jsonify({
        "seniors":seniors,
        "juniors": juniors,
        "welcome": welcome,
        "projectTopics":rawMaintopics,
        "availability": updated_day_periods_map
    })



@app.route('/makeAccounts', methods=['POST'])
def makeJuniorAccounts():
    global conn
    global cur
    #clear_table("Accounts")
    clear_table("Senior Profiles")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    if request.files['seniorRoster']!="none":
        file = request.files['seniorRoster']
        rawData2 = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')), header=None)

    
    seniorAccounts=[]

    for i in range(len(rawData2)):
        x = [str(item).strip() for item in rawData2.iloc[i]]
        y=[x[2], "SMCS", x[1]+" "+x[0], x[3], "Senior"]
        seniorAccounts.append(y)
        


    for account in seniorAccounts:
        #print(account)
        username, password, name, message, class_name = account  # Unpack list

        # Ensure empty values are stored as empty strings
        cursor.execute("""
            INSERT INTO "Accounts" ("Username", "Password", "Name", "Message", "Class")
            VALUES (%s, %s, %s, %s, %s);
        """, (username or "", password or "", name or "", message or "", class_name or ""))

        cursor.execute("""
        INSERT INTO "Senior Profiles" ("Name", "Username")
        VALUES (%s, %s);
    """, (name or "", username or ""))

    conn.commit()  # Save changes
    print("Accounts inserted successfully!")

    
    return render_template('rosters.html')



@app.route('/makeJuniorAccounts', methods=['POST'])
def makeAccounts():
    global conn
    global cur
    #clear_table("Accounts")
    clear_table("Junior Profiles")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor() 
    if request.files['juniorRoster']!="none":
        file = request.files['juniorRoster']
        rawData = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')), header=None)
    
    juniorAccounts=[]
    for i in range(len(rawData)):
        x = [str(item).strip() for item in rawData.iloc[i]]
        y=[x[2], "SMCS", x[1]+" "+x[0], x[3], "Junior"]
        juniorAccounts.append(y)
        
    for account in juniorAccounts:
        #print(account)
        username, password, name, message, class_name = account  # Unpack list

        # Ensure empty values are stored as empty strings
        cursor.execute("""
            INSERT INTO "Accounts" ("Username", "Password", "Name", "Message", "Class")
            VALUES (%s, %s, %s, %s, %s);
        """, (username or "", password or "", name or "", message or "", class_name or ""))

        cursor.execute("""
        INSERT INTO "Junior Profiles" ("Name", "Username")
        VALUES (%s, %s);
    """, (name or "", username or ""))

    conn.commit()  # Save changes
    print("Accounts inserted successfully!")

    
    return render_template('rosters.html')


@app.route('/logResponse', methods=['POST'])
def logResponse():
    data = request.get_json()
    username=session.get("user")
    presentationTitle = data.get("presentationTitle")
    presider = data.get("presiderName")
    topic = data.get("selectedProjectTopic")
    additionalSlot = data.get("selectedAdditionalSlot")
    friends = data.get("selectedFriends")
    availability = data.get("availabilityList")
    availability = ', '.join(availability)
    friends = ', '.join(friends)
    presiderIntro = data.get("presiderIntro")
    presentationBlurb=data.get("presentationBlurb")
    
    global conn
    global cur
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor() 
    # SQL query 
    update_query = """ UPDATE "Senior Profiles" SET "Presentation Title" = %s, "Junior Presider" = %s, "Project Topic" = %s, "Additional Slot" = %s, "Friends" = %s, "Availability" = %s, "Presider Intro" = %s, "Presentation Blurb" = %s WHERE "Username" = %s; """ 
    data_tuple = (presentationTitle, presider, topic, additionalSlot, friends, availability, presiderIntro, presentationBlurb, username)
    #print(data_tuple)
    conn.rollback()
    cur.execute(update_query, data_tuple)
    conn.commit()
    return render_template('seniorQuestionnaire.html')



@app.route('/logJuniorResponse', methods=['POST'])
def logJuniorResponse():
    data = request.get_json()
    username=session.get("user")
    topics = data.get("topics")
    availabilityList = data.get("availabilityList")
    availability = ', '.join(availabilityList)
    topics = ', '.join(topics)
    global conn
    global cur
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor() 
    # SQL query 
    update_query = """ UPDATE "Junior Profiles" SET "Preferred Topics" = %s, "Availability" = %s WHERE "Username" = %s; """ 
    data_tuple = (topics, availability, username)
    #print(data_tuple)
    conn.rollback()
    cur.execute(update_query, data_tuple)
    conn.commit()
    return render_template("juniorQuestionnaire.html")



@app.route('/setCode', methods=['POST'])
def submit_code():
    """Receives the code from frontend and stores it in the Availability table."""
    data = request.get_json()
    code = data.get("code")

    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    cursor.execute("UPDATE \"Admin\" SET \"Code\" = %s WHERE \"id\" = 1", (code,))
    connection.commit()
    cursor.close()
    connection.close()
    print("ok inserted")
    return jsonify({"message": "Code successfully inserted into Availability table!"})

if __name__ == '__main__':
    app.run(debug=True)





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
juniorRawdataDict={}
juniorDisplayAllTimesFromData=[]
juniorDisplayHeaders=[]
juniorDisplayAllTimes=[]

presiderDict={}
juniorsList=[]
seniorsList=[]


periodMap = {}
dayOrder=[]
rawRoomData={}
topicQuantity={}
specialGroups=[]

topicsByRooms={}

rawMaintopics=[]

def getRawData():
    global rawdataDict
    global juniorRawdataDict
    global allTimes
    global seniorsList
    global juniorsList
    global presiderDict
    presiderDict={}
    seniorsList=[]
    juniorsList=[]
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor() 
    
    ordered_columns = [
        "Availability",
        "Project Topic",
        "Friends",
        # (placeholder for empty list)
        "Presentation Title",
        "Presentation Blurb",
        "Junior Presider",
        "Presider Intro",
        "Additional Slot",
        "Backup Presider",
        "Mentor Coming"
    ]
    
    column_str = ', '.join(f'"{col}"' for col in ordered_columns)
    sql = f'SELECT "Name", {column_str} FROM "Senior Profiles"'

    cursor.execute(sql)
    
    # Build the dictionary
    rawdataDict = {}
    
    for row in cursor.fetchall():
        name = row[0]
        values = list(row[1:])

        output_list = []
        for item in allTimes:
            if item in values[0]:
                output_list.append(item)
        
        values[0] = output_list if values[0] else []
        values[2] = [s.strip() for s in values[2].split(",")] if values[2] else []
    
        values.insert(3, [])
    
        rawdataDict[name] = values


    ordered_columns = [
    "Preferred Topics",  # index 0
    "Availability"       # index 1
    ]
    
    # Build the query
    column_str = ', '.join(f'"{col}"' for col in ordered_columns)
    sql = f'SELECT "Name", {column_str} FROM "Junior Profiles"'
    cursor.execute(sql)
    
    juniorRawdataDict = {}
    
    for row in cursor.fetchall():
        name = row[0]
        values = list(row[1:])
    
        # 💥 Split those comma-delimited strings into lists
        values[0] = [s.strip() for s in values[0].split(",")] if values[0] else []

        output_list = []
        for item in allTimes:
            if item in values[1]:
                output_list.append(item)
        
        values[1] = output_list if values[1] else []
    
        juniorRawdataDict[name] = values
    
    # Done and done!
    #print(juniorRawdataDict)
    for key, value in rawdataDict.items():
        if value[6] in juniorsList:
            sharedTimes=list(set(value[0]) & set(juniorRawdataDict[value[6]][1]))
            if len(sharedTimes)>0:
                rawdataDict[key][0]=sharedTimes
                presiderDict[key]=value[6]
            elif value[9] in juniorsList:
                sharedTimes=list(set(value[0]) & set(juniorRawdataDict[value[9]][1]))
                if len(sharedTimes)>0:
                    rawdataDict[key][0]=sharedTimes
                    presiderDict[key]=value[9]     
                
    seniorsList=list(rawdataDict.keys())
    for senior in seniorsList:
        if senior not in list(presiderDict.keys()):
            presiderDict[senior]=""
    print(presiderDict)
    juniorsList=list(juniorRawdataDict.keys())
    
    cursor.close()
    conn.close()

    #print(rawdataDict)

#getRawData()



@app.route('/setProjectTopics', methods=['POST'])
def setProjectTopics():
    global rawMaintopics
    data = request.json  # Extract JSON data from request
    rawMaintopics = data.get("topics", [])  # Get 'topics' list or default to empty

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE "Availability"
        SET "rawMaintopics" = %s
        WHERE "id" = 1;  --  Adjust the row ID accordingly!
    """, (json.dumps(rawMaintopics),))

    conn.commit()
    
    print("Received topics:", rawMaintopics)  # Debugging log
    return render_template('projectTopics.html')







@app.route('/setSymposiumAvailability', methods=['POST'])
def setSymposiumAvailability():
    global capacityDict
    global dayCapacityDict
    global personsPerTime
    global roomToTimes
    global allRooms
    global allTimes
    global days
    global periodMap
    
    data = request.get_json()
    roomToTimes = data.get('roomsToTimes')
    periodMap=data.get('periodMap')
    allRooms = data.get('allRooms')
    allTimes = data.get('allTimes')

    capacityDict={}
    dayCapacityDict={}
    
    for room, times in roomToTimes.items():
        capacityDict[room]=sum(len(values) for values in times.values())*personsPerTime
        dayCapacityDict[room]={}
        for day, daytimes in times.items():
            dayCapacityDict[room][day]=len(daytimes)*personsPerTime


    # Connect to the PostgreSQL database
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print(roomToTimes)
    print(periodMap)
    print(allRooms)
    print(allTimes)
    
    cursor.execute("""
        UPDATE "Availability"
        SET "roomToTimes" = %s,
            "periodMap" = %s,
            "allRooms" = %s,
            "allTimes" = %s
    """, (json.dumps(roomToTimes), json.dumps(periodMap), json.dumps(allRooms), json.dumps(allTimes)))

    # Commit transaction
    conn.commit()
    print("Data inserted successfully!")


    
    
    return render_template('availability.html')

def setGlobalVariables():
    global roomToTimes
    global periodMap
    global allTimes
    global allRooms
    global rawMaintopics
    global capacityDict
    global dayCapacityDict
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Fetch data from Availability table (assuming only one row)
    cursor.execute("""
        SELECT "roomToTimes", "periodMap", "allRooms", "allTimes", "rawMaintopics" FROM "Availability" LIMIT 1;
    """)
    
    row = cursor.fetchone()  # Get the first row

    if row:
        # Convert JSON strings back to Python objects
        roomToTimes = row[0]
        periodMap = row[1]
        allRooms = row[2]
        allTimes = row[3]
        rawMaintopics = row[4]

        print("roomToTimes:", roomToTimes)
        print("periodMap:", periodMap)
        print("allRooms:", allRooms)
        print("allTimes:", allTimes)
        print("rawMaintopics:", rawMaintopics)

    capacityDict={}
    dayCapacityDict={}
    
    for room, times in roomToTimes.items():
        capacityDict[room]=sum(len(values) for values in times.values())*personsPerTime
        dayCapacityDict[room]={}
        for day, daytimes in times.items():
            dayCapacityDict[room][day]=len(daytimes)*personsPerTime


@app.route('/getTopicDistribution', methods=['POST'])
def getTopicDistribution():    
    global rawMaintopics
    global rawdataDict
    global personsPerTime
    global roomToTimes
    global rawRoomData
    global topicQuantity

    rawRoomData={}
    for topic in rawMaintopics:
        rawRoomData[topic]=[]
    
    for key, value in rawdataDict.items():
        rawRoomData[value[1]].append(key)
        
    rawRoomData = dict(sorted(rawRoomData.items(), key=lambda item: len(item[1]),reverse=True))
    
    #print(rawRoomData)
    
    topicQuantity = {roomName:len(roomStudents) for roomName, roomStudents in rawRoomData.items()}

    
    return render_template('topics.html')


def getTopicQuantity():    
    global rawMaintopics
    global rawdataDict
    global personsPerTime
    global roomToTimes
    global rawRoomData
    global topicQuantity

    print(rawMaintopics)
    print(rawRoomData)
    rawRoomData={}
    for topic in rawMaintopics:
        rawRoomData[topic]=[]
    
    for key, value in rawdataDict.items():
        rawRoomData[value[1]].append(key)
        
    rawRoomData = dict(sorted(rawRoomData.items(), key=lambda item: len(item[1]),reverse=True))
    
    topicQuantity = {roomName:len(roomStudents) for roomName, roomStudents in rawRoomData.items()}



@app.route('/saveGroups', methods=['POST'])
def putSpecialGroupsInNeon():
    global specialGroups
    global rawRoomData
    global rawdataDict
    data = request.get_json()

    specialGroups = data.get('specialGroups')
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE "Availability"
        SET "specialGroups" = %s
        WHERE "id" = 1;  --  Adjust the row ID accordingly!
    """, (json.dumps(specialGroups),))

    conn.commit()

    return render_template('index.html')

def setSpecialGroups():
    global rawRoomData
    global specialGroups
    global rawdataDict

    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT "specialGroups" FROM "Availability" LIMIT 1;
    """)

    result = cursor.fetchone()

    if result:
        specialGroups = result[0]  # Convert JSON string to dictionary
        print("Special Groups:", specialGroups)
    else:
        specialGroups=[]
        
    for value in rawRoomData.values():
        if len(value)<=6 and len(value)>1:
            specialGroups.append(value)
    
    specialGroups = sorted(specialGroups, key=len, reverse=True)
    
    for specialGroup in specialGroups:
        for student1 in specialGroup:
                for student2 in specialGroup:
                    if student1 != student2:
                        if student2 not in rawdataDict[student1][3]:
                            rawdataDict[student1][3].append(student2)





@app.route('/setNewTopics', methods=['POST'])
def setNewTopics():
    #Roomdata topic: people, everyone who has only one topic
    #Rawroomdata contains topics like "Computer Science, Biology" in addition to "Computer Science" and "Biology"
    data = request.get_json()
    topicsByRoom=data.get('topicDistribution')
    print(topicsByRoom)
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE "Availability"
        SET "topicsByRoom" = %s
        WHERE "id" = 1;  --  Adjust the row ID accordingly!
    """, (json.dumps(topicsByRoom),))

    conn.commit()

    
    
    return render_template('moderator.html')


def setTopicsByRoom():
    global topicsByRoom
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT "topicsByRoom" FROM "Availability" LIMIT 1;
    """)

    result = cursor.fetchone()

    if result:
        topicsByRoom = result[0]  # Convert JSON string to dictionary
        print("Topics by Room:", topicsByRoom)

    cursor.close()
    conn.close()



    
def setRoomDistribution():
    global dayOrder
    global roomDistribution
    global capacityDict
    global dayCapacityDict
    global rawdataDict
    global personsPerTime
    global roomToTimes
    global periodMap
    global rawRoomData
    global topicQuantity
    global specialGroups
    global topicsByRoom
    #Roomdata topic: people, everyone who has only one topic
    #Rawroomdata contains topics like "Computer Science, Biology" in addition to "Computer Science" and "Biology"
    setTopicsByRoom();
    
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
                print("roomDistribution", roomDistribution)
                print("rooms",rooms)
                roomDistribution[rooms[0][0]].append(student)
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
    
    #topicsByRoom={'Room 195':{"Computer Science":20},
    #                   "Room 198":{"Biology":15,"Neuroscience":1, "Computer Science":2, "Data Science": 1},
    #                   "Room 199":{"Engineering":9,"Math":1,"Physics":1, "Material Science":1, "Astronomy":1, "Earth science/Geology":1, 'nan':1, "Soil Studies":1, 'Agriculture': 1}}
    
    topicDistribution={}
    for room, topics in topicsByRoom.items():
        for topic, size in topics.items():
            if topic not in list(topicDistribution.keys()):
                topicDistribution[topic]=[]
            topicDistribution[topic].append([room,size])

    print("U SLITTLE HIT", topicDistribution)
    
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

    return render_template('moderator.html')




def setAllGlobalVariables():
    setGlobalVariables()
    getRawData()
    getTopicQuantity()
    setSpecialGroups()


def generate_csv(table_name):
    """Fetches data from the specified table and returns correctly formatted CSV content."""
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    cursor.execute(f'SELECT * FROM "{table_name}"')
    rows = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    cursor.close()
    connection.close()

    # Use CSV writer to handle commas properly
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)  # Ensures values with commas are wrapped in quotes

    writer.writerow(column_names)  # Header row
    writer.writerows(rows)  # Data rows

    return output.getvalue()


@app.route('/downloadSeniorProfiles', methods=['GET'])
def download_senior_profiles():
    print("SENIORS LETS GO")
    csv_data = generate_csv("Senior Profiles")
    return Response(csv_data, mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=Senior_Profiles.csv"})

@app.route('/downloadJuniorProfiles', methods=['GET'])
def download_junior_profiles():
    print("JUNIORS LETS GO")
    csv_data = generate_csv("Junior Profiles")
    return Response(csv_data, mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=Junior_Profiles.csv"})


@app.route('/downloadBothProfiles', methods=['POST'])
def download_both_profiles():
    """Triggers both CSV downloads by serving JavaScript correctly."""
    print("bro im alive eh?")  # This will now actually print in Flask logs

    js_script = """
    <script>
        window.open('/downloadSeniorProfiles', '_blank');
        window.open('/downloadJuniorProfiles', '_blank');
    </script>
    """
    return Response(js_script, mimetype="text/html")  # Ensures proper execution

@app.route('/getSeniorRespondents')
def getSeniorRespondents():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Query to fetch data from "Senior Profiles"
    cursor.execute("""
        SELECT "Name", "Username", "Presentation Title"
        FROM "Senior Profiles";
    """)
    
    seniors=[]
    
    # Process each row
    for name, username, presentation_title in cursor.fetchall():
        if presentation_title is None or presentation_title.strip() == "":
            seniors.append([name, username, "No"])
        else:
            seniors.append([name, username, "Yes"])
    
    # Close database connection
    cursor.close()
    conn.close()
    
    # Debugging: Print results

    return jsonify({
        "seniors":seniors
    })

@app.route('/getJuniorRespondents')
def getJuniorRespondents():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Query to fetch data from "Senior Profiles"
    cursor.execute("""
        SELECT "Name", "Username", "Preferred Topics"
        FROM "Junior Profiles";
    """)
    
    seniors=[]
    
    # Process each row
    for name, username, presentation_title in cursor.fetchall():
        if presentation_title is None or presentation_title.strip() == "":
            seniors.append([name, username, "No"])
        else:
            seniors.append([name, username, "Yes"])
    
    # Close database connection
    cursor.close()
    conn.close()
    
    # Debugging: Print results

    return jsonify({
        "juniors":seniors
    })
















@app.route('/getParsedData')
def getParsedData():
    return jsonify({
        "dataDict": rawdataDict,
        "displayHeaders": displayHeaders,
        "allRooms": allRooms,
        "displayAllTimes": displayAllTimes,
        "displayAllTimesFromData": displayAllTimesFromData,
        "juniorDataDict": juniorRawdataDict,
        "juniorDisplayHeaders": juniorDisplayHeaders,
        "juniorDisplayAllTimesFromData": juniorDisplayAllTimesFromData,
        "juniorDisplayAllTimes": juniorDisplayAllTimes
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
    global juniorRawdataDict
    global juniorDisplayHeaders
    global juniorDisplayAllTimes
    global juniorDisplayAllTimesFromData
    global allTimes
    global days

    global presiderDict
    global juniorsList
    global seniorsList
    
    #data = request.get_json()
    print(request.form.get('json'))
    data = json.loads(request.form.get('json'))
    
    url = data.get('url')
    firstNameCol1 = data.get('firstNameCol')
    lastNameCol1 = data.get('lastNameCol')
    projectNameCol1 = data.get('projectNameCol')
    projectTopicCol1 = data.get('projectTopicCol')
    availabilityCol1 = data.get('availabilityCol')
    friendsCol1 = data.get('friendsCol')
    blurbCol1 = data.get('blurbCol')
    days = data.get('days')
    presiderCol1=data.get('presiderCol')
    presiderIntroCol1=data.get('presiderIntroCol')
    csv=data.get('csv')

    juniorCsv=data.get('juniorCsv')
    juniorUrl=data.get('juniorUrl')
    juniorFirstNameCol1 = data.get('juniorFirstNameCol')
    juniorLastNameCol1 = data.get('juniorLastNameCol')
    juniorTopicsCol1=data.get('juniorTopicsCol')
    juniorAvailabilityCol1=data.get('juniorAvailabilityCol')

    if csv!="none":
        file = request.files['file']
        rawData = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')), header=None)
    else:
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
    presiderCol = int(presiderCol1)-1
    presiderIntroCol = int(presiderIntroCol1)-1
    personsPerTime=2
    
    rawdataDict = {}


    
    if juniorCsv!="none":
        juniorFile = request.files['juniorFile']
        juniorRawData = pd.read_csv(io.StringIO(juniorFile.stream.read().decode('utf-8')), header=None)
    else:
        juniorUrlData = requests.get(juniorUrl).content
        juniorRawData = pd.read_csv(io.StringIO(juniorUrlData.decode('utf-8')),header=None)
    
    juniorDataHeaders = juniorRawData.iloc[0].tolist()
    juniorRawData = juniorRawData.iloc[1:]

    juniorFirstNameCol = int(juniorFirstNameCol1)-1
    juniorLastNameCol = int(juniorLastNameCol1)-1
    juniorAvailabilityCol = int(juniorAvailabilityCol1)-1
    juniorTopicsCol = int(juniorTopicsCol1)-1
    
    juniorRawdataDict = {}

    
    allTimes = data.get('allTimes')
    allRooms = data.get('allRooms')

    days1={}
    i=1
    for day in days:
        print(day)
        days1["Day "+str(i)]=day
        i+=1
    days=days1

    for i in range(len(juniorRawData)):
        x = [str(item) for item in juniorRawData.iloc[i]]
        target_string = x[juniorAvailabilityCol]
        output_list = []
        for item in allTimes:
            if item in target_string:
                output_list.append(item)
        juniorRawdataDict[x[juniorFirstNameCol].strip()+" "+x[juniorLastNameCol].strip()]=[x[juniorTopicsCol],output_list]
    juniorsList=list(juniorRawdataDict.keys())
    juniorAllTimesFromData = set(time for value in list(juniorRawdataDict.values()) for time in value[1])
    
    
    for i in range(len(rawData)):
        x = [str(item) for item in rawData.iloc[i]]
        target_string = x[availabilityCol]
        output_list = []
        for item in allTimes:
            if item in target_string:
                output_list.append(item)
        if x[presiderCol] in juniorsList:
            sharedTimes=list(set(output_list) & set(juniorRawdataDict[x[presiderCol]][1]))
            if len(sharedTimes)>0:
                output_list=sharedTimes
            presiderDict[x[firstNameCol].strip()+" "+x[lastNameCol].strip()]=x[presiderCol]

        '''
        if len(output_list) > 4:
            output_list = random.sample(output_list, 4)
        '''
        
        rawdataDict[x[firstNameCol].strip()+" "+x[lastNameCol].strip()]=[output_list,x[topicCol],x[friendsCol].split(", "),[],x[projectNameCol],x[blurbCol],x[presiderCol].strip(),x[presiderIntroCol]]
    seniorsList=list(rawdataDict.keys())
    for senior in seniorsList:
        if senior not in list(presiderDict.keys()):
            presiderDict[senior]=""
    print(presiderDict)
    allTimesFromData = set(time for value in list(rawdataDict.values()) for time in value[0])

    displayAllTimes=[]
    displayAllTimesFromData=[]
    juniorDisplayAllTimesFromData=[]
    
    for time in allTimesFromData:
        if time in allTimes:
            displayAllTimesFromData.append([time,1])
        else:
            displayAllTimesFromData.append([time,0])    

    displayHeaders=["Senior Name",dataHeaders[topicCol],dataHeaders[projectNameCol],dataHeaders[availabilityCol],dataHeaders[friendsCol],dataHeaders[blurbCol],dataHeaders[presiderCol],dataHeaders[presiderIntroCol]]


    for time in juniorAllTimesFromData:
        if time in allTimes:
            juniorDisplayAllTimesFromData.append([time,1])
        else:
            juniorDisplayAllTimesFromData.append([time,0])    

    for time in allTimes:
        if time in allTimesFromData and time in juniorAllTimesFromData:
            displayAllTimes.append([time,1])
        else:
            displayAllTimes.append([time,0])
    
    juniorDisplayHeaders=["Junior Name",juniorDataHeaders[juniorTopicsCol],juniorDataHeaders[juniorAvailabilityCol]]
    #print(juniorDisplayHeaders)
    #print(juniorRawdataDict)
    #print(juniorDisplayAllTimesFromData)

    #print(rawdataDict)
    
    return render_template('index.html')
    '''
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()
    
    for name, values in rawdataDict.items():
        availability = ", ".join(values[0]) if values[0] else ""  # Availability (comma-separated)
        project_topic = values[1] if values[1] else ""  # Project Topic
        friends = ", ".join(values[2]) if values[2] else ""  # Friends (comma-separated)
        presentation_title = values[4] if values[4] else ""  # Presentation Title
        presentation_blurb = values[5] if values[5] else ""  # Presentation Blurb
        junior_presider = values[6] if values[6] else ""  # Junior Presider
        presider_intro = values[7] if values[7] else ""  # Presider Intro
    
        # Update the row where "Name" matches
        cursor.execute("""
            UPDATE "Senior Profiles"
            SET "Availability" = %s,
                "Project Topic" = %s,
                "Friends" = %s,
                "Presentation Title" = %s,
                "Presentation Blurb" = %s,
                "Junior Presider" = %s,
                "Presider Intro" = %s
            WHERE "Name" = %s
        """, (availability, project_topic, friends, presentation_title, presentation_blurb, junior_presider, presider_intro, name))
    
    # Commit changes and close connection
    connection.commit()
    
    for name, values in juniorRawdataDict.items():
        preferred_topics = values[0] if values[0] else ""  # Preferred Topics (comma-separated)
        availability = ", ".join(values[1]) if values[1] else ""  # Availability (comma-separated)
    
        # Update the row where "Name" matches in "Junior Profiles"
        cursor.execute("""
            UPDATE "Junior Profiles"
            SET "Preferred Topics" = %s,
                "Availability" = %s
            WHERE "Name" = %s
        """, (preferred_topics, availability, name))
    
    # Commit changes and close connection
    connection.commit()
    cursor.close()
    connection.close()
    

    print("Profiles tables successfully updated!")
    '''




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
    global rawRoomData
    global topicQuantity
    global specialGroups
    
    print("submit_availability was called!")
    data = request.get_json()

    roomToTimes = data.get('roomsToTimes')
    periodMap = data.get('periodMap')
    roomToTimes = dict(sorted(roomToTimes.items(), key=lambda item: len(item[1]),reverse=True))
    #print(roomsToTimes)
    #dayOrder = list(data.get('dayOrder').values())
    #print(dayOrder)
    capacityDict={}
    
    for room, times in roomToTimes.items():
        capacityDict[room]=sum(len(values) for values in times.values())*personsPerTime
        dayCapacityDict[room]={}
        for day, daytimes in times.items():
            dayCapacityDict[room][day]=len(daytimes)*personsPerTime
        
    rawMaintopics = list({value[1] for value in rawdataDict.values()})

    rawRoomData={}
    for topic in rawMaintopics:
        rawRoomData[topic]=[]
    
    for key, value in rawdataDict.items():
        rawRoomData[value[1]].append(key)
        
    rawRoomData = dict(sorted(rawRoomData.items(), key=lambda item: len(item[1]),reverse=True))
    
    #print(rawRoomData)
    
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
    print("Topic quantity:", topicQuantity)
    print(rawdataDict)
    print("All rooms:", allRooms)
    print("rawRoomData:", rawRoomData)
    
    return render_template('topics.html')

@app.route('/set_topics', methods=['POST'])
def set_topics():
    global dayOrder
    global roomDistribution
    global capacityDict
    global dayCapacityDict
    global rawdataDict
    global personsPerTime
    global roomToTimes
    global periodMap
    global rawRoomData
    global topicQuantity
    global specialGroups
    #Roomdata topic: people, everyone who has only one topic
    #Rawroomdata contains topics like "Computer Science, Biology" in addition to "Computer Science" and "Biology"
    data = request.get_json()
    topicsByRoom=data.get('topicDistribution')
    print(topicsByRoom)
    
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
                #the below line is like really sus
                roomDistribution[rooms[0][0]].append(student)
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
    
    #topicsByRoom={'Room 195':{"Computer Science":20},
    #                   "Room 198":{"Biology":15,"Neuroscience":1, "Computer Science":2, "Data Science": 1},
    #                   "Room 199":{"Engineering":9,"Math":1,"Physics":1, "Material Science":1, "Astronomy":1, "Earth science/Geology":1, 'nan':1, "Soil Studies":1, 'Agriculture': 1}}
    
    topicDistribution={}
    for room, topics in topicsByRoom.items():
        for topic, size in topics.items():
            if topic not in list(topicDistribution.keys()):
                topicDistribution[topic]=[]
            topicDistribution[topic].append([room,size])
    
    roomDistribution={roomName:[] for roomName in list(topicsByRoom.keys())}
    
    print("please why does this work? topic distribution:", topicDistribution)
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
            
    return render_template('generateStep1.html')

@app.route('/get_data')
def get_data():
    global roomDistribution
    global topicDistribution

    #print(rawdataDict)
    if session.get("user") != "none":
        setAllGlobalVariables()
        try:
            setRoomDistribution()
        except:
            print("for the love of all that is holy please")
    
    return jsonify({
        "realInitRoomDistribution": roomDistribution,
        "capacityDict": capacityDict,
        "topics": topicQuantity
    })

@app.route('/getDataForStep2')
def getDataForStep2():
    return jsonify({
        "roomDayDistribution": roomDayDistribution,
        "capacityDict": capacityDict,
        "dayCapacityDict": dayCapacityDict
    })

@app.route('/getFinalDistribution')
def getDataForStep3():
    print(daysRoomsTimes);
    presiderInfo={}
    print(presiderDict)
    for senior, junior in presiderDict.items():
        presiderInfo[senior]=[junior,rawdataDict[senior][7]]
    print(presiderInfo)


    timeTopicDict = {}
    for name, (topics, times) in juniorRawdataDict.items():
        for time in times:
            if time not in timeTopicDict:
                timeTopicDict[time] = {}  # Initialize time slot
    
            for topic in topics:
                if topic not in timeTopicDict[time]:
                    timeTopicDict[time][topic] = []  # Initialize topic list
                
                timeTopicDict[time][topic].append(name)
    
    print(timeTopicDict)
    return jsonify({
        "daysRoomsTimes":daysRoomsTimes,
        "presiderInfo":presiderInfo,
        "fullPresiderDict": timeTopicDict
    })

allDayDistributions = []
highestScore=0
@app.route('/receive_schedule', methods=['POST'])
def receive_schedule():
    unboxedRoomData = request.get_json()
    #print("Received schedule:", unboxedRoomData)
    global roomToTimes
    global allDayDistributions
    global roomDayDistribution
    global days
    #print("roomToTimes", roomToTimes)

    global highestScore
    #highestScore=0
    
    def findDayDistributions(roomSchedule, studentAvailability, thisDayTimes, score):
        global allDayDistributions
        global highestScore 
        
        if not studentAvailability:
            newScore=score
            for students in list(roomSchedule.values()):
                for student in students:
                    if (len(set(students) & set(rawdataDict[student][2])))>0:
                        newScore+=5

            if len(allDayDistributions)<=100:
                if newScore > highestScore - 3:
                    if newScore > highestScore:
                        highestScore = newScore
                    if random.randint(1, 1)==1:
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
            if random.randint(1, 6)!=6:
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


    def solveDayDistribution():

        global roomToTimes
        global allDayDistributions
        global roomDayDistribution
        global days
        #print("roomToTimes", roomToTimes)
    
        global highestScore
        #highestScore=0
        
        roomDayDistribution={}
        for thisRoom, thisStudents in unboxedRoomData.items():
        
            thisDayTimesFull = roomToTimes[thisRoom]
            thisDayTimes = {key:len(value)*personsPerTime for key,value in roomToTimes[thisRoom].items()}
            thisDays = list(roomToTimes[thisRoom].keys())
            roomSchedule = {key:[] for key in thisDays}
        
            studentAvailability = {}
            for student in thisStudents:
                studentTimes = rawdataDict[student][0]
                
                if len(studentTimes) > 5:
                    studentTimes = random.sample(studentTimes, 5)
                
                availableDays = []
                for day, times in thisDayTimesFull.items():
                    if len(set(studentTimes) & set(times)) != 0:
                        availableDays.append(day)
                studentAvailability[student]=availableDays
            
            studentAvailability = dict(sorted(studentAvailability.items(), key=lambda item: len(item[1])))
            
            allDayDistributions = []
    
            highestScore=0
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
                n=20
                #while i<len(allDayDistributions) and allDayDistributions[i][1]==highScore:
                x=len(allDayDistributions)
                
                print("This is my girth", x)
                while i<200 and i<x and len(allDayDistributions[i])==2 and allDayDistributions[i][1]==highScore:
                #while i<100 and allDayDistributions[i][1]==highScore:
                    #print(i,allDayDistributions[i])
                    i+=1
                print("this is my length", x)
                if x<n:
                    print("uh wut")
                    for distribution in allDayDistributions:
                        consideredDistributions.append(distribution)
                elif i<=n:
                    print("dreaming abt all the things that we could be")
                    for distribution in allDayDistributions[:n]:
                        consideredDistributions.append(distribution)
                else:
                    print("lately ive been ive been losing sleep")
                    hop=(int)(i/n)
                    for j in range(0,i,hop):
                        distribution=allDayDistributions[j]
                        consideredDistributions.append(distribution)
                #print()
            print(thisRoom,"considered distributions",consideredDistributions)    
            roomDayDistribution[thisRoom]=consideredDistributions
            #print(roomDayDistribution)
    
        #print(dayOrder)
        for room, dayChoices in roomDayDistribution.items():
            for dayChoice in dayChoices:
                #ordered_dict={day: dayChoice[0][day] for day in dayOrder}
                #dayChoice[0]=ordered_dict
                for day, students in dayChoice[0].items():
                    for i in range(len(students)):
                        student=students[i]
                        students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
        
        print("my room day distribution yay!", roomDayDistribution) 

    while True:
        try:
            solveDayDistribution()
            break
        except Exception as e:
            print(f"Error occurred: {e}. Retrying...")
    
    #return jsonify({"status": "success", "message": "Schedule received"})
    return render_template('generateStep2.html')

offenders=[]

@app.route('/check_distribution', methods=['POST'])
def check_distribution():
    global rawdataDict
    global roomToTimes
    global offenders
    roomData = request.get_json()
    print("CHECKING FOR OFFENDERS:", roomData)
    offenders=[]
    for room, days in roomData.items():
        for day, students in days.items():
            for student in students:
                x=True
                for time in rawdataDict[student][0]:
                    print(day)
                    print(roomToTimes)
                    if time in roomToTimes[room][day]:
                        x=False
                        break
                if x:
                    offenders.append(student)
    print(offenders)
    return render_template('generateStep2.html')

@app.route('/get_offenders')
def get_offenders():
    global offenders
    return jsonify({
        "offenders": offenders
    })

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
        global roomToTimes
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
                if len(schedules)<2000:
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
        n=20
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

    abortion=False
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

            if thisSchedule:
                daysRoomsTimes[day][roomName]=thisSchedule
            else:
                print("ABORTION = TRUE")
                abortion=True
            #daysRoomsTimes[day][roomName]=f(thisRoom,roomName,day)
    
    print("WTF?",daysRoomsTimes)
    
    for day, rooms in daysRoomsTimes.items():
        for room, schedules in rooms.items():
            daysRoomsTimes[day][room]=[]
            for periods in schedules:
                updated_periods = {periodMap.get(period, period): value for period, value in periods.items()}
                
                for period, students in periods.items():
                    for i in range(len(students)):
                        student=students[i]
                        students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
                daysRoomsTimes[day][room].append(updated_periods)


    if abortion or session.get(user)=="Admin":
        dayRoomsTimes={'Thursday, December 21st': {'Room 195': [{'2': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']]}, {'2': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '3': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '3': [['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}, {'2': [['James Tan', 'Computer Science', 'Characterization of Breathing Types: Optimizing Data Collection and Cleaning Process for Spire Tag Sensor Analysis'], ['Akhil Raman', 'Computer Science', 'WRF HDF5 Reader Integration into Paraview']], '3': [['Sean Radimer', 'Computer Science', 'How CTF Skill Level Reception to Guidance Influences Performance'], ['Zory Teselko', 'Computer Science', 'Temporal Analysis of Respiratory Data for Investigating Speech Rate Variability in Health Monitoring']], '4': [['Eddie Wu', 'Computer Science', 'Optimizing Sensor Data Transmission in IoT Networks through MQTT Broker-Based Algorithmic Efficiency'], ['Pranav Gaddam', 'Computer Science', 'Hyperparameter Optimization and Performance Analysis of Convolutional Neural Networks']], '5': [['Patrick Foley', 'nan', 'Geolocation as a Language ID Proxy with Pre-trained Transformers'], ['Aditya Lahiri', 'Computer Science', 'A Preliminary Method for Identifying Ice Movement in the Arctic']], '6': [['Aaron Zhu', 'Computer Science', 'Emotion Recognition in MIDI Files: Leveraging Long Short-Term Memory with a Novel Feature-Extraction Technique'], ['Aidan Paul', 'Computer Science', 'Music Generation using Artificial Neural Networks']]}], 'Room 198': [{'2': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '3': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '4': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '3': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '4': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '3': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '4': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '4': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates']], '5': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates']], '5': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates']], '5': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '5': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '5': [['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '5': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '5': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '5': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '4': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '5': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '4': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '4': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '4': [['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '4': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security']], '4': [['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}, {'2': [['Daniel Ling', 'Biology', 'Unveiling the Role of AND-1 in Tumorigenesis'], ['Devon Chen', 'Biology', 'Role of Amygdala Projections to the Ventral Pallidum in Regulating Stress-Induced Behaviors']], '3': [['Michael Tsegaye', 'Biology', 'Using Phylogenetic Comparative Methods to Analyze Binary State Speciation/Extinction Data in Squamates'], ['Ryan Zhao', 'Computer Science', 'Using SpireTag Data and Breathing Patterns to Classify Respiratory Events with Human-Learn']], '4': [['Catherine Tenny', 'Computer Science', 'Assessing the Viability of Cisco Packet Tracer as Automotive Security'], ['Vincent Ha', 'Computer Science', 'Improving Depth Estimation In Video Frame Interpolation Using Stereo Vision and Epipolar Geometry']], '5': [['Alex Shelley', 'Biology', 'Effects of Biosolarization of Apple Pomace on Weed Suppression'], ['David Ruan', 'Computer Science', ' Utilizing Perceptron Learning to Classify and Characterize SpireTag Data of Diaphragm Contractions and Relaxations']], '6': [['Leavy Hu', 'Biology', 'Designing An Animal Model For V122I Transthyretin Amyloidosis'], ['Snigdha Chelluri', 'Biology', 'CRISPR-Based Mitochondrial Regulation in Neuro2a Cells']]}], 'Room 199': [{'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '3': [], '4': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '5': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization']]}, {'2': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '3': [], '4': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '5': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization']]}, {'2': [['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '3': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '4': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '5': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization']]}, {'2': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '3': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '4': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '5': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization']]}, {'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '3': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '4': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '5': [['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization']]}, {'2': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '3': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '4': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '5': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization']]}, {'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '3': [['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']], '5': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']]}, {'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '3': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '5': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']]}, {'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '3': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '5': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent']]}, {'2': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '3': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '5': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']]}, {'2': [['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '3': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '5': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent']]}, {'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '3': [], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '5': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']]}, {'2': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '3': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '5': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']]}, {'2': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '3': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n'], ['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '5': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent']]}, {'2': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '3': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '4': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization']], '5': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent']]}, {'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '3': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '4': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']], '5': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']]}, {'2': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '3': [], '4': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '5': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']]}, {'2': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']], '3': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '4': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '5': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent']]}, {'2': [['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips'], ['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '3': [['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '4': [['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '5': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent'], ['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology']]}, {'2': [['Larson Ozbun', 'Engineering', 'Validation of an Autonomous Dynamic Indoor Quadcopter Testing Methodology'], ['Tanya Bait', 'Astronomy', 'Kinematics of the Ionized Outflow in the Northwest of NGC 253']], '3': [['Avyukth Selvadurai', 'Engineering', 'The Effect of Cross Laminated Timber on Fire Dynamics'], ['Tarini Nagenalli', 'Material Science', 'Improvement of Electrolytes in Batteries Designed for Wearable Technology by Comparison of 20% and 30% PVA Solutions\n']], '4': [['Srinidhi Guruvayurappan', 'Earth science/Geology', 'Determining the Metamorphic Temperatures of Rocks in the Raspas Complex using Zirconium-in-Rutile Thermometry to Compare to Computer Models']], '5': [['Elizabeth Ivanova', 'Engineering', 'Enhancing CdSe Quantum Emitter Isolation via Spin Coating and Experimental Optimization'], ['Muhammad Ahmad', 'Engineering', 'Precise Light Coupling Apparatus for Optical Waveguide Chips']], '6': [['Rohun Sarkar', 'Data Science', 'Comparative Analysis of Machine Learning Methods for Predicting Global Sea Ice Extent']]}]}, 'Tuesday, December 19th': {'Room 195': [{'2': [['Archit Ashok', 'Computer Science', 'Using the Kalman Filter to Project the Motion of Ground-Based Obstacles to Prevent Collisions during Autonomous Drone Landings']], '3': [['Ritviik Ravi', 'Computer Science', 'Predicting the Stock Value of NFL Athletes: An Advanced Model Using Gradient-Boosted Trees'], ['Nikhil Kakani', 'Computer Science', 'Optimizing IP Geolocation Algorithm Accuracies: An Integrated Approach Using MLP Neural Network and Reverse DNS Querying Technique']], '4': [['Chris Ramos', 'Computer Science', 'Analyzing the Effects of Resampling Techniques on Multiclass Imbalanced Datasets using t-SNE visualizations'], ['Nicholas McGonigle', 'Computer Science', 'GPT-Verilog: Enhancing Verilog Generation Using Large Language Models']], '5': [['Jay Wankhede', 'Computer Science', 'Developing a Large Language Model Powered Algorithm for Enhanced Research Paper Summarization'], ['Aileen Sharma', 'Computer Science', 'Aligning Classroom Recording Transcripts with Common Core State Standards using Keyword Extraction']], '6': [['Sarah Yu', 'Computer Science', 'Dead Reckoning with TinyML'], ['Rachel Zhang', 'Computer Science', 'Automatic Color Flatting of Illustration Linearts']]}, {'2': [['Sarah Yu', 'Computer Science', 'Dead Reckoning with TinyML'], ['Rachel Zhang', 'Computer Science', 'Automatic Color Flatting of Illustration Linearts']], '3': [['Ritviik Ravi', 'Computer Science', 'Predicting the Stock Value of NFL Athletes: An Advanced Model Using Gradient-Boosted Trees'], ['Nikhil Kakani', 'Computer Science', 'Optimizing IP Geolocation Algorithm Accuracies: An Integrated Approach Using MLP Neural Network and Reverse DNS Querying Technique']], '4': [['Chris Ramos', 'Computer Science', 'Analyzing the Effects of Resampling Techniques on Multiclass Imbalanced Datasets using t-SNE visualizations']], '5': [['Jay Wankhede', 'Computer Science', 'Developing a Large Language Model Powered Algorithm for Enhanced Research Paper Summarization'], ['Aileen Sharma', 'Computer Science', 'Aligning Classroom Recording Transcripts with Common Core State Standards using Keyword Extraction']], '6': [['Archit Ashok', 'Computer Science', 'Using the Kalman Filter to Project the Motion of Ground-Based Obstacles to Prevent Collisions during Autonomous Drone Landings'], ['Nicholas McGonigle', 'Computer Science', 'GPT-Verilog: Enhancing Verilog Generation Using Large Language Models']]}, {'2': [['Sarah Yu', 'Computer Science', 'Dead Reckoning with TinyML'], ['Rachel Zhang', 'Computer Science', 'Automatic Color Flatting of Illustration Linearts']], '3': [['Ritviik Ravi', 'Computer Science', 'Predicting the Stock Value of NFL Athletes: An Advanced Model Using Gradient-Boosted Trees'], ['Nikhil Kakani', 'Computer Science', 'Optimizing IP Geolocation Algorithm Accuracies: An Integrated Approach Using MLP Neural Network and Reverse DNS Querying Technique']], '4': [['Chris Ramos', 'Computer Science', 'Analyzing the Effects of Resampling Techniques on Multiclass Imbalanced Datasets using t-SNE visualizations'], ['Nicholas McGonigle', 'Computer Science', 'GPT-Verilog: Enhancing Verilog Generation Using Large Language Models']], '5': [['Jay Wankhede', 'Computer Science', 'Developing a Large Language Model Powered Algorithm for Enhanced Research Paper Summarization'], ['Aileen Sharma', 'Computer Science', 'Aligning Classroom Recording Transcripts with Common Core State Standards using Keyword Extraction']], '6': [['Archit Ashok', 'Computer Science', 'Using the Kalman Filter to Project the Motion of Ground-Based Obstacles to Prevent Collisions during Autonomous Drone Landings']]}, {'2': [['Sarah Yu', 'Computer Science', 'Dead Reckoning with TinyML'], ['Rachel Zhang', 'Computer Science', 'Automatic Color Flatting of Illustration Linearts']], '3': [['Ritviik Ravi', 'Computer Science', 'Predicting the Stock Value of NFL Athletes: An Advanced Model Using Gradient-Boosted Trees'], ['Nikhil Kakani', 'Computer Science', 'Optimizing IP Geolocation Algorithm Accuracies: An Integrated Approach Using MLP Neural Network and Reverse DNS Querying Technique']], '4': [['Archit Ashok', 'Computer Science', 'Using the Kalman Filter to Project the Motion of Ground-Based Obstacles to Prevent Collisions during Autonomous Drone Landings'], ['Chris Ramos', 'Computer Science', 'Analyzing the Effects of Resampling Techniques on Multiclass Imbalanced Datasets using t-SNE visualizations']], '5': [['Jay Wankhede', 'Computer Science', 'Developing a Large Language Model Powered Algorithm for Enhanced Research Paper Summarization'], ['Aileen Sharma', 'Computer Science', 'Aligning Classroom Recording Transcripts with Common Core State Standards using Keyword Extraction']], '6': [['Nicholas McGonigle', 'Computer Science', 'GPT-Verilog: Enhancing Verilog Generation Using Large Language Models']]}]}}
         #print(daysRoomsTimes)
    #return jsonify({"status": "success", "message": "Schedule received"})
    return render_template('4.html')


if __name__ == '__main__':
    app.run(debug=True)
