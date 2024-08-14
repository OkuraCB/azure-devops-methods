# Introduction

The Azure DevOps is lacking a feature easy to use and which is capable of upload massive quantities of work itens in the backlog of the project.
So, this collection of functions can help you to upload your whole spreadsheet (as exemplified in the `Create_WorkItems_From_Spreadsheet.py` file) to the project as work items in a fully automated fashion.

## How does it work?

This project was made out of need for a tool to upload courses and modules and videos on the Azure DevOps environment, so it will not be able to handle every situation, but it is for sure easily adaptable with some Python knowledge.
In any case, if any questions arise during the process, don't hesitate to email me: arthur.souza@orange.com

To make it work, we will make use of the Azure DevOps Python API, which is just a thin wrapper to all the requisitions that the Azure REST API can handle.
The two links for the documentations are bellow.

1.  https://learn.microsoft.com/en-us/rest/api/azure/devops/?view=azure-devops-rest-7.1
2.  https://github.com/microsoft/azure-devops-python-api

And the API itself can be installed with the following command (if you have pip):

```
pip install azure-devops
```

## How to start?

To start development with the `AzureMethods` functions, you will need first to fill up some environment variables.
Python for sure has a module for that. It is called `dotenv` and can be easily installed with:

```
pip install dotenv
```

The next step is to create a file called `.env`. That file will set which variables will be loaded to memory on the startup of the script. For all of that to work, you'll need 2 essential informations to be loaded up:

```.env
PAT = {PERSONAL_ACCESS_TOKEN}
URL = https://dev.azure.com/{ORGANIZATION}

```

Fill in the fields within brackets with the Organization of your project and the your own [pat](https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/use-personal-access-tokens-to-authenticate?view=azure-devops&viewFallbackFrom=vsts&tabs=Windows)

For the example script to work properly, you'll also need to set up some "sensitive" information of your project and/or operation:

```.env
WorkItensLink = https://dev.azure.com/{ORGANIZATION}/{PROJECT}/_apis/wit/workItems/

#More on these two bellow
Videos_Path = {PATH_TO_VIDEOS_TXT}
Spreadsheet_Path = {PATH_TO_COURSES_SPREADSHEET}

AssignTo = {PERSON_ASSIGNED_TO_THE_ITEM}
Project = {PROJECT}
```

# And how to I use it?

In the .py archives on this repo you can find a collection of functions which can make all sorts of stuff if you have the correct input.
To connect to Azure DevOps in you python script, take this snippet from `AzureMethods.py` and the following snippet from the application exemplified

```python
def clientAzure(url, pat):

    return Connection(base_url=url, creds=BasicAuthentication('', pat)).clients
```

```python
#load credentials
dotenv.load_dotenv()
URL = os.getenv('URL')
PAT = os.getenv('PAT')
[...]
#Connect to Azure DevOps
WIT_client = AzureMethods.clientAzure(URL, PAT).get_work_item_tracking_client()
```

You will need the provide the `WIT_client` for all of the operations you may want to perform on a work item. Alternativelly, if you want a macro vision on the organization for exemple, you can call the function `get_core_client()` from the return of the `clientAzure` function and be capable to see the whole thing.
Take for example too the `createPBI()` function, which is the one who create a Product Backlog Item:

```python
def createPBI(wit, rel, title, assign, project):
    document = []

    #add title
    document.append(JsonPatchOperation(from_=None,op='add',path="/fields/System.Title",value=title))
    #add assignTo
    document.append(JsonPatchOperation(from_=None,op='add',path="/fields/System.AssignedTo",value=assign))
    #add relationship child-parent
    document.append(JsonPatchOperation(from_=None,op='add',path="/relations/-", value=rel))

    #Request to create a work item for DevOps
    response = wit.create_work_item(document, project, "Product Backlog Item", validate_only=None, bypass_rules=None, suppress_notifications=None, expand=None)
    return response.id
```

- You can see that the first parameter is asking for our `WIT_Client` and that's because the method `create_work_item()` which is reponsible to send the request for Azure to create a item (please refer to the documentation for more details)
- The `rel` parameter is the relantionship created with the `createRelationship` function
- The `title` is the name of the PBI
- The `assign` field is reponsible to automatically assign the PBI to someone on the team (you can ommit that without any consequences)
- And for the last we have the `project` field, which will put the PBI in the right project

We need to also create a list with all the requisitions we want to make (using the `JsonPatchOperation`) and send that to Azure. In the case we don't send this list of requisitions, we will need to update the PBI multiple times to set all the fields and relations correctly
The response of this requisiton is stored in the `response` variable, from which I only save the ID, to create the subsequent child tasks of the project.

## What about the videos and spreadsheet path?

The way that the `Create_WorkItems_From_Spreadsheet` was implemented is very specific for my own use case, and I'm gonna to explain here how does this two documents are utilized on the script, but keep in mind that this can be easily changed to be anything you want with a little effort.
Starting with the Spreadsheet, for this project i've used a Excel file, and more specifically a Excel file with a line heading that says "Development Trainings", so in the snippet bellow I was able to extract the list of values from that specific column, and that was the name of all the Courses and it's modules.

```python
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
```

Provided that the spreadsheet I was working on followed this structure:

| Development Trainings |
| --------------------- |
| Course 1              |
| Module 1              |
| Module 2              |
| Module 3              |
|                       |
| Course 2              |
| Module 1              |
| Module 2              |
| ...                   |

And for the videos names, I opted for not to use a Spreadsheet, but a normal .txt plain text document which followed this structure:

```
Video name 1
Video name 2
Video name 3

Video name 1
Video name 2
...
```

How do I know if the videos are assigned to the correctly modules? I create them sequencially like that:
Feature 1 -> Module 1 -> Video 1 -> Video 2 -> ... -> Module 2 -> Video 1 -> Video 2 -> ... -> Feature 2 -> ...

Here's the snippet:

```python
#Create the courses and their videos
for number in range(1, len(courses)):
    for name in courses[number]:
        if name == courses[number][0]:
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
```
