import AzureMethods, dotenv, os
from azure.devops.v7_0.dashboard.models import Dashboard, TeamContext, Widget

dotenv.load_dotenv()
URL = os.getenv('URL')
PAT = os.getenv('PAT')
Team = os.getenv('Team')
Project = os.getenv('Project')
Assing = os.getenv('AssignTo')
Url = os.getenv('WorkItensLink')

Dash_Client = AzureMethods.clientAzure(URL, PAT).get_dashboard_client()
TeamC = TeamContext(team= Team, project= Project)

Dashs = Dash_Client.get_dashboards_by_project(TeamC)
print(Dashs[1].id)
Wids = Dash_Client.get_widgets(TeamC, Dashs[1].id)