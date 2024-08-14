from azure.devops.v7_0.py_pi_api import JsonPatchOperation
from azure.devops.v7_0.work_item_tracking.models import Wiql, WorkItemDeleteUpdate
from msrest.authentication import BasicAuthentication
from azure.devops.connection import Connection

def createRelationship(url, Id, reference="System.LinkTypes.Hierarchy-Reverse"):

    return {"rel": reference, "url": url + str(Id)}

def updateWorkItem(wit, id, field, value, project):
    document = []

    #add title
    document.append(JsonPatchOperation(from_=None,op='add',path="/fields/System." + field, value=value))

    #Request to update a work item for DevOps
    print(wit.update_work_item(document, id, project, validate_only=None, bypass_rules=None, suppress_notifications=None, expand=None))

def GetChildIdList(wit, id, project):

    relations = wit.get_work_item(id, project=project, expand='Relations').relations

    ChildList = []
    for item in relations:
        url = item.url

        if item.attributes['name'] != "Parent":
            for index in range(1, 10):
                if url[-index] != '0' and url[-index] != '1' and url[-index] != '2' and url[-index] != '3' and url[-index] != '4' and url[-index] != '5' and url[-index] != '6' and url[-index] != '7' and url[-index] != '8' and url[-index] != '9': 
                    ChildList.append(int(url[-index+1:]))
                    break

    
    return ChildList

def updateItemChilds(wit, id, field, value, project, include=True, recursively=True):
    if recursively:
        Type = wit.get_work_item(id, project=project).fields['System.WorkItemType']
        if Type == "Epic":
            FeatureIds = GetChildIdList(wit, id, project)
            for IdFeature in FeatureIds:
                PbIds = GetChildIdList(wit, IdFeature, project)
                for IdPbi in PbIds:
                    TaskIds = GetChildIdList(wit, IdPbi, project)
                    for IdTask in TaskIds:
                        updateWorkItem(wit, IdTask, field, value, project)
                    updateWorkItem(wit, IdPbi, field, value, project)
                
                updateWorkItem(wit, IdFeature, field, value, project)

        elif Type == "Feature":
            PbIds = GetChildIdList(wit, id, project)
            for IdPbi in PbIds:
                TaskIds = GetChildIdList(wit, IdPbi, project)
                for IdTask in TaskIds:
                    updateWorkItem(wit, IdTask, field, value, project)                    
                updateWorkItem(wit, IdPbi, field, value, project)
        
        elif Type == "Product Backlog Item":
            TaskIds = GetChildIdList(wit, id, project)
                
            for IdTask in TaskIds:
                updateWorkItem(wit, IdTask, field, value, project)
        
        else:
            updateWorkItem(wit, id, field, value, project)

    else:
        ChildIds = GetChildIdList(wit, id, project)
        for Id in ChildIds:
            updateWorkItem(wit, Id, field, value, project)
        
    if include:
        updateWorkItem(wit, id, field, value, project)

def createFeature(wit, title, assign, project):
    document = []

    #add title
    document.append(JsonPatchOperation(from_=None,op='add',path="/fields/System.Title",value=title))
    #add assignTo
    document.append(JsonPatchOperation(from_=None,op='add',path="/fields/System.AssignedTo",value=assign))

    #Request to create a work item for DevOps
    response = wit.create_work_item(document, project, "Feature", validate_only=None, bypass_rules=None, suppress_notifications=None, expand=None)
    return response.id

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

def createTask(wit, rel, title, assign, project):
    document = []

    #add title
    document.append(JsonPatchOperation(from_=None,op='add',path="/fields/System.Title",value=title))
    #add assignTo
    document.append(JsonPatchOperation(from_=None,op='add',path="/fields/System.AssignedTo",value=assign))
    #add relationship child-parent
    document.append(JsonPatchOperation(from_=None,op='add',path="/relations/-", value=rel))

    #Request to create a work item for DevOps
    response = wit.create_work_item(document, project, "Task", validate_only=None, bypass_rules=None, suppress_notifications=None, expand=None)
    return response.id

def clientAzure(url, pat):

    return Connection(base_url=url, creds=BasicAuthentication('', pat)).clients

def FetchListLimboWIT(wit, project, HasEpic=True):

    def deleteFeature(wit, delist, FeatureList):
        for Feature in FeatureList:
            workItem = wit.get_work_item(Feature, project=project, expand='Relations')

            if workItem.relations == None:
                delist.append(workItem.id)
                continue

            flag = 0
            for relation in workItem.relations:
                if relation.attributes['name'] == "Parent":
                    flag = 1
                    break
            
            if flag == 1:
                continue
            else:
                Childs = GetChildIdList(wit, workItem.id, project=project)
                for Child in Childs:
                    ChildC = GetChildIdList(wit, Child, project=project)

                    for ChildCId in ChildC:
                        delist.append(ChildCId)

                    delist.append(Child)
                
                delist.append(workItem.id)

    def deletePbi(wit, delist, PbiList):
        for Pbi in PbiList:
            workItem = wit.get_work_item(Pbi, project=project, expand='Relations')

            if workItem.relations == None:
                delist.append(workItem.id)
                continue

            flag = 0
            for relation in workItem.relations:
                if relation.attributes['name'] == "Parent":
                    flag = 1
                    break
            
            if flag == 1:
                continue
            else:
                Childs = GetChildIdList(wit, workItem.id, project=project)
                for Child in Childs:
                    ChildC = GetChildIdList(wit, Child, project=project)
                    
                    for ChildCId in ChildC:
                        delist.append(ChildCId)

                    delist.append(Child)
                
                delist.append(workItem.id)

    def deleteTask(wit, delist, TaskList):
        for Task in TaskList:
            workItem = wit.get_work_item(Task, project=project, expand='Relations')

            if workItem.relations == None:
                delist.append(workItem.id)
                continue

    FeatureWiql = Wiql(query="select [System.Id] From WorkItems Where [System.WorkItemType] = 'Feature' AND [System.TeamProject] = '" + project + "'")
    PbiWiql = Wiql(query="select [System.Id] From WorkItems Where [System.WorkItemType] = 'Product Backlog Item' AND [System.TeamProject] = '" + project + "'")
    TaskWiql = Wiql(query="select [System.Id] From WorkItems Where [System.WorkItemType] = 'Task' AND [System.TeamProject] = '" + project + "'")

    Feature = []
    Pbi = []
    Task = []
    deleteList = []

    for workitem in wit.query_by_wiql(FeatureWiql).work_items:
        Feature.append(workitem.id)
    
    for workitem in wit.query_by_wiql(PbiWiql).work_items:
        Pbi.append(workitem.id)
    
    for workitem in wit.query_by_wiql(TaskWiql).work_items:
        Task.append(workitem.id)

    if HasEpic:
        deleteFeature(wit, deleteList, Feature)
    deletePbi(wit, deleteList, Pbi)
    deleteTask(wit, deleteList, Task)

    return deleteList

def MoveItemsToRecybleBin(wit, ids, recover=False):
    
    if recover:
        Recovering = WorkItemDeleteUpdate(is_deleted=False)
        ToRecover = open("log.txt", "r").readlines()
        for id in ToRecover:
            print(id)
            wit.restore_work_item(Recovering, id)
        
        return "Recovering Succeed"
    else:
        Trash = []
        for id in ids:
            wit.delete_work_item(id)
            Trash.append(id)
    
    return Trash