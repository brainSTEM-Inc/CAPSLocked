from flask import Flask, request, jsonify, render_template, redirect, session
import requests, pandas as pd, io, copy, sys, json

sys.setrecursionlimit(2000)

import os
import psycopg2

# Get the database URL from Render's environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Connect to the database
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Test query: Create a simple table (optional)
cur.execute("CREATE TABLE IF NOT EXISTS test (id SERIAL PRIMARY KEY, name TEXT);")
conn.commit()

print("✅ Connected to Neon DB!")

def clear_table(table_name):
    global conn
    global cur
    """Deletes all rows in the specified table."""
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor() 
    cur.execute(f'DELETE FROM "{table_name}";')
    conn.commit()
    print("im doing something im not supposed to be doing yk wut these error messages are kinda funny lets write a story so basiclaly once upon a itme")
    print(f"✅ Table '{table_name}' has been cleared!")

#clear_table("Accounts")

app = Flask(__name__)

app.secret_key = os.urandom(24) 

app.config['SESSION_PERMANENT'] = True  # ✅ Ensures session persists
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
    return render_template('login.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/select')
def select():
    return render_template('select.html')


@app.route('/seniorQuestionnaire')
def seniorQuestionnaire():
    return render_template('seniorQuestionnaire.html')

@app.route('/juniorQuestionnaire')
def juniorQuestionnaire():
    return render_template('juniorQuestionnaire.html')

@app.route('/moderator')
def moderator():
    return render_template('moderator.html')

@app.route('/viewResponses')
def viewResponses():
    return render_template('viewResponses.html')

@app.route('/availability')
def availability():
    return render_template('availability.html')

@app.route('/rosters')
def rosters():
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
    #print(actualUsername)
    #print(actualPassword)
    data = request.get_json()
    if data.get("username")==actualUsername and data.get("password")==actualPassword:
        session["user"]="Admin";
        print("u are the smartest person alive")
        session.modified = True

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    #query = """SELECT Username, Name, Message, Class FROM Accounts WHERE Username = %s AND Password = %s;"""
    query = """SELECT "Username", "Name", "Message", "Class" FROM "Accounts" WHERE "Username" = %s AND "Password" = %s;"""
    cur.execute(query, (data.get("username"), data.get("password")))
    result = cur.fetchone()  # ✅ Fetch matched row

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
    seniors = [row[0] for row in cursor.fetchall()]  # 🔥 Convert results into a list
    cursor.execute('SELECT "Name" FROM "Junior Profiles";')
    juniors = [row[0] for row in cursor.fetchall()]  # 🔥 Convert results into a list
    welcome="Welcome,  "+session["name"]+"!"
    return jsonify({
        "seniors":seniors,
        "juniors": juniors,
        "welcome": welcome
    })



@app.route('/makeAccounts', methods=['POST'])
def makeJuniorAccounts():
    global conn
    global cur
    clear_table("Accounts")
    clear_table("Senior Profiles")
    clear_table("Junior Profiles")
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor() 
    if request.files['juniorRoster']!="none":
        file = request.files['juniorRoster']
        rawData = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')), header=None)
    if request.files['seniorRoster']!="none":
        file = request.files['seniorRoster']
        rawData2 = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')), header=None)

    
    juniorAccounts=[]
    seniorAccounts=[]
    for i in range(len(rawData)):
        x = [str(item).strip() for item in rawData.iloc[i]]
        y=[x[2], "SMCS", x[1]+" "+x[0], x[3], "Junior"]
        juniorAccounts.append(y)
        
    for i in range(len(rawData2)):
        x = [str(item).strip() for item in rawData2.iloc[i]]
        y=[x[2], "SMCS", x[1]+" "+x[0], x[3], "Senior"]
        seniorAccounts.append(y)
        

    for account in juniorAccounts:
        #print(account)
        username, password, name, message, class_name = account  # Unpack list

        # ✅ Ensure empty values are stored as empty strings
        cursor.execute("""
            INSERT INTO "Accounts" ("Username", "Password", "Name", "Message", "Class")
            VALUES (%s, %s, %s, %s, %s);
        """, (username or "", password or "", name or "", message or "", class_name or ""))

        cursor.execute("""
        INSERT INTO "Junior Profiles" ("Name", "Username")
        VALUES (%s, %s);
    """, (name or "", username or ""))


    for account in seniorAccounts:
        #print(account)
        username, password, name, message, class_name = account  # Unpack list

        # ✅ Ensure empty values are stored as empty strings
        cursor.execute("""
            INSERT INTO "Accounts" ("Username", "Password", "Name", "Message", "Class")
            VALUES (%s, %s, %s, %s, %s);
        """, (username or "", password or "", name or "", message or "", class_name or ""))

        cursor.execute("""
        INSERT INTO "Senior Profiles" ("Name", "Username")
        VALUES (%s, %s);
    """, (name or "", username or ""))

    conn.commit()  # ✅ Save changes
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
    global conn
    global cur
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor() 
    # SQL query 
    update_query = """ UPDATE "Senior Profiles" SET "Presentation Title" = %s, "Junior Presider" = %s, "Project Topic" = %s, "Additional Slot" = %s, "Friends" = %s, "Availability" = %s WHERE "Username" = %s; """ 
    data_tuple = (presentationTitle, presider, topic, additionalSlot, friends, availability, username)
    print(data_tuple)
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
    print(data_tuple)
    conn.rollback()
    cur.execute(update_query, data_tuple)
    conn.commit()
    return render_template("juniorQuestionnaire.html")






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

rawMaintopics=[
      "Biology/Biotech", "Chemistry/Materials Science", "Computer Science/AI",
      "Engineering", "Math", "Physics", "Earth Space Systems Science", "Economics/Social Issues"
    ]

def getRawData():
    global rawdataDict
    global juniorRawdataDict
    global allTimes
    
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
    print(juniorRawdataDict)
        
    
    cursor.close()
    conn.close()

    print(rawdataDict)

getRawData()




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
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    # Fetch data from Availability table (assuming only one row)
    cursor.execute("""
        SELECT "roomToTimes", "periodMap", "allRooms", "allTimes" FROM "Availability" LIMIT 1;
    """)
    
    row = cursor.fetchone()  # Get the first row

    if row:
        # Convert JSON strings back to Python objects
        roomToTimes = json.loads(row[0])
        periodMap = json.loads(row[1])
        allRooms = json.loads(row[2])
        allTimes = json.loads(row[3])

        print("roomToTimes:", roomToTimes)
        print("periodMap:", periodMap)
        print("allRooms:", allRooms)
        print("allTimes:", allTimes)


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

    rawRoomData={}
    for topic in rawMaintopics:
        rawRoomData[topic]=[]
    
    for key, value in rawdataDict.items():
        rawRoomData[value[1]].append(key)
        
    rawRoomData = dict(sorted(rawRoomData.items(), key=lambda item: len(item[1]),reverse=True))
    
    topicQuantity = {roomName:len(roomStudents) for roomName, roomStudents in rawRoomData.items()}


@app.route('/fixSpecialGroups', methods=['POST'])
def fixSpecialGroups():
    global specialGroups
    global rawRoomData
    global rawdataDict
    
    for value in rawRoomData.values():
        if len(value)<=6 and len(value)>1:
            specialGroups.append(value)
    
    specialGroups = sorted(specialGroups, key=len, reverse=True)
    
    for specialGroup in specialGroups:
        for student1 in specialGroup:
                for student2 in specialGroup:
                    if student1 != student2:
                        rawdataDict[student1][3].append(student2)


    return render_template('index.html')













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
        rawdataDict[x[firstNameCol].strip()+" "+x[lastNameCol].strip()]=[output_list,x[topicCol],x[friendsCol].split(", "),[],x[projectNameCol],x[blurbCol],x[presiderCol].strip(),x[presiderIntroCol]]
    seniorsList=list(rawdataDict.keys())
    for senior in seniorsList:
        if senior not in list(presiderDict.keys()):
            presiderDict[senior]=""
    print(presiderDict)
    allTimesFromData = set(time for value in list(rawdataDict.values()) for time in value[0])
    
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
    
    return render_template('index.html')


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
    
    print("🔔 submit_availability was called!")
    data = request.get_json()

    roomToTimes = data.get('roomsToTimes')
    periodMap = data.get('periodMap')
    roomToTimes = dict(sorted(roomToTimes.items(), key=lambda item: len(item[1]),reverse=True))
    #print(roomsToTimes)
    dayOrder = list(data.get('dayOrder').values())
    print(dayOrder)
    
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
            
    return render_template('generateStep1.html')

@app.route('/get_data')
def get_data():
    setGlobalVariables()
    getRawData()
    getTopicQuantity()
    
    return jsonify({
        "realInitRoomDistribution": roomDistribution,
        "capacityDict": capacityDict,
        "topics": topicQuantity
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
    presiderInfo={}
    print(presiderDict)
    for senior, junior in presiderDict.items():
        presiderInfo[senior]=[junior,rawdataDict[senior][7]]
    return jsonify({
        "daysRoomsTimes":daysRoomsTimes,
        "presiderInfo":presiderInfo
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
            ordered_dict={day: dayChoice[0][day] for day in dayOrder}
            dayChoice[0]=ordered_dict
            for day, students in dayChoice[0].items():
                for i in range(len(students)):
                    student=students[i]
                    students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
    
    #print(roomDayDistribution) 
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
                if len(schedules)<1000:
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
    
    print(daysRoomsTimes)
    
    for day, rooms in daysRoomsTimes.items():
        for room, periods in rooms.items():
            updated_periods = {periodMap.get(period, period): value for period, value in periods.items()}
            daysRoomsTimes[day][room]=updated_periods
            for period, students in periods.items():
                for i in range(len(students)):
                    student=students[i]
                    students[i]=[student,rawdataDict[student][1],rawdataDict[student][4]]
    
    
    #print(daysRoomsTimes)
    #return jsonify({"status": "success", "message": "Schedule received"})
    return render_template('4.html')


if __name__ == '__main__':
    app.run(debug=True)
