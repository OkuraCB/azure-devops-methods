import AzureMethods, dotenv, os

dotenv.load_dotenv()
URL = os.getenv('URL')
PAT = os.getenv('PAT')
Project = os.getenv('Project')

WIT_Client = AzureMethods.clientAzure(URL, PAT).get_work_item_tracking_client()

#List Example
IdList = [1, 2, 3, 4]

for id in IdList:
    AzureMethods.updateItemChilds(WIT_Client, id, "State", "Done", Project)