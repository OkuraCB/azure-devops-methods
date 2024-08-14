import dotenv, os, AzureMethods
import pandas as pd

#load credentials
dotenv.load_dotenv()
URL = os.getenv('URL')
PAT = os.getenv('PAT')

#load paths
Videos_Path = os.getenv('Videos_Path')
Spreadsheet_Path = os.getenv('Spreadsheet_Path')

#load info
AssignTo = os.getenv('AssignTo')
Project = os.getenv('Project')
WorkItensLink = os.getenv('WorkItensLink')

#load videos titles
videos = open(Videos_Path).readlines()
nothing = videos[15]

#Connect to Azure DevOps
WIT_client = AzureMethods.clientAzure(URL, PAT).get_work_item_tracking_client()

#Load courses to Memory 
file = pd.read_excel(Spreadsheet_Path, dtype=str).fillna('0')
column = file['Development Trainings'].values

courses = []
course = []
for name in column:
    if name == '0':
        courses.append(course)
        course = []
        continue

    course.append(name)
courses.append(course)

#Create the courses and their videos
for name in courses[0]:
    if name == courses[0][0]:
        FeatureId = AzureMethods.createFeature(WIT_client, name, AssignTo, Project)
        continue
        
    rel = AzureMethods.createRelationship(WorkItensLink, FeatureId)
    PbiId = AzureMethods.createPBI(WIT_client, rel, name, AssignTo, Project)

    delete = 0
    for video in videos:
        if video == nothing:
            delete+=1
            break
        
        delete += 1

        video = video[:-1]
        rel = AzureMethods.createRelationship(WorkItensLink, PbiId)
        AzureMethods.createTask(WIT_client, rel, video, AssignTo, Project)
        
    for i in range(0, delete):
        videos.pop(0)