import AzureMethods, dotenv, os

dotenv.load_dotenv()
URL = os.getenv('URL')
PAT = os.getenv('PAT')
Team = os.getenv('Team')
Project = os.getenv('Project')
Assing = os.getenv('AssignTo')
Url = os.getenv('WorkItensLink')

WIT_Client = AzureMethods.clientAzure(URL, PAT).get_work_item_tracking_client()

result = open("NestJSCourse.txt", 'r').readlines()

CourseID = AzureMethods.createFeature(WIT_Client, "NestJS: The Complete Developer's Guide", Assing, Project)

SectionID = 0
for content in result:
    if content[0] == '1' or content[0] == '2' or content[0] == '3' or content[0] == '4' or content[0] == '5' or content[0] == '6' or content[0] == '7' or content[0] == '8' or content[0] == '9' or content[0] == '0':
        AzureMethods.createTask(WIT_Client, AzureMethods.createRelationship(Url, SectionID), content, Assing, Project)
    else:
        SectionID = AzureMethods.createPBI(WIT_Client, AzureMethods.createRelationship(Url, CourseID), content, Assing, Project)