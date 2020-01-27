# -*- coding: utf-8 -*-
"""
Author : Jacques Flores
Created : October 17th,2019
About:  Script for creating datasets in Dataverse. 
        An Empty JSON file with Dataverse structure is imported and converted into a JSON dict
        Metadata is imported from an excel file into a pandas dataframe and written into the empty JSON formatted string.
"""


from pyDataverse import api
from pyDataverse.utils import read_file_json
from pyDataverse.utils import dict_to_json
import pandas as pd
import copy

def create_datasets(dataverse, xl, template):
        dataset = 0
        entries = xl['paperID'].count()
        handles_list = []
        while dataset < entries:
            #Make a copy of the dataverse json template as metadata
            metadata = copy.deepcopy(template)
            #Store metadata from excel into variables
            authorname = xl.loc[:, xl.columns.str.endswith('name')]
            authoraffiliations = xl.loc[:, xl.columns.str.endswith('organisation')]
            contactname = xl.loc[dataset,'submitting_author']
            title = xl.loc[dataset]['title']
            contactemail = xl.loc[dataset]['authors_formatted_1_email']
            subject = 'Arts and Humanities'
            poster = xl.loc[dataset]['contribution_type'] == 'Poster'
            fileid = xl.loc[dataset]['paperID']
            
            #modify metadata
            
            #title
            metadata['datasetVersion']['metadataBlocks']['citation']['fields'][0]\
                    ['value'] = title
                    
            #Authorname and affiliation
            for author, affiliation in zip(authorname.iloc[dataset].dropna(), authoraffiliations.iloc[dataset].dropna()):
                    metadata['datasetVersion']['metadataBlocks']['citation']['fields'][1]\
                            ['value'].append({\
                            'authorName': {'value': author , 'typeClass': 'primitive', 'multiple': False, 'typeName': 'authorName'},\
                            'authorAffiliation':{'value': affiliation , 'typeClass': 'primitive', 'multiple': False, 'typeName': 'authorAffiliation'}})
            #E-mail contact
            metadata['datasetVersion']['metadataBlocks']['citation']['fields'][2]\
                    ['value'][0]['datasetContactEmail']['value'] = contactemail
            #Dataset contact name
            metadata['datasetVersion']['metadataBlocks']['citation']['fields'][2]\
                    ['value'][0]['datasetContactName']['value'] = contactname
            #Description
            if poster:
                metadata['datasetVersion']['metadataBlocks']['citation']['fields'][3]\
                    ['value'][0]['dsDescriptionValue']['value'] = "Abstract and poster of paper %s presented at the Digital Humanities Conference 2019 (DH2019), Utrecht , the Netherlands 9-12 July, 2019." % fileid
            else:
                metadata['datasetVersion']['metadataBlocks']['citation']['fields'][3]\
                    ['value'][0]['dsDescriptionValue']['value'] = "Abstract of paper %s presented at the Digital Humanities Conference 2019 (DH2019), Utrecht , the Netherlands 9-12 July, 2019." % fileid             
            
            #Subject (controlled vocabulary: only set values are allowed; check dataverse for these )
            metadata['datasetVersion']['metadataBlocks']['citation']['fields'][4]\
                    ['value'][0]= subject
            
            
            #converting dictionary into a json formatted string
            metadata1 = dict_to_json(metadata)
            
            #creating Dataset in "RDMtest"dateverse with metadata and print response
            dset = dataverse.create_dataset( "DH2019",  metadata1)
            
            print ('-' * 40)
            print (dset.json())
            print (dset.status_code)
            
            #store persistent identifier from newly created dataset
            handle = dset.json()['data']['persistentId']
            handles_list.append((handle,fileid))
            
            #upload files ( I had to edit the api upload file function (pkg: pydataverse) cause it kept raising an error, as a result it does not return a response)
            #if there is a poster it will upload the abstract and the poster ELSE it will only upload the abstract
            #The abstarct should be named as " (paperID).pdf [e.g. 100.pdf] and the poster as "paperIDp.pdf" [e.g. 100p.pdf] for it to work. 
            #If named differently this can be changed below
            
            if poster:
                dataverse.upload_file(handle , 'filesa/%sa.pdf' % (fileid))
                dataverse.upload_file(handle , 'filesa/%sp.pdf' % (fileid)) 
            else:
                dataverse.upload_file(handle , 'filesa/%sa.pdf' % (fileid))
              
            #publish dataset and print response
            pubdset = dataverse.publish_dataset(handle, type = "major", auth = True)

            print ('-' * 40)
            print (pubdset.json())
            print (pubdset.status_code)
            
            #Counter for datsets and emptying metadata template
            dataset = dataset + 1
            metadata = {}
            
        return(handles_list)

def publish_datasets(dataverse, handles_list) :
    #publish dataset and print response
    dataset = 0
    entries = handles_list[0].count()
    while dataset < entries:
        handle = handles_list.iloc[dataset][0]
        pubdset = dataverse.publish_dataset(handle, type = "major", auth = True)
    
        print ('-' * 40)
        print (pubdset.json())
        print (pubdset.status_code)
        
  
    
    
    
# Confidential API Token (Do Not Distribute) ****last four digits removed)
apitoken = "38404b17-46f9-4fe5-808e-a4a38bd80aea"

# Demo Dataverse server
dtvserver = "https://dataverse.nl"

#Loading connection and authentication
dataverse = api.Api(dtvserver,apitoken)

#reading json file as dict
template = read_file_json('dataversetemplate.json')

#read excel file with metadata as pandas dataframe
xlfile = "DH2019_paperswithfiles.xlsx"
xl = pd.read_excel(xlfile, converters={'paperID': str})

handles = create_datasets(dataverse, xl, template)
handles_df = pd.DataFrame(handles)
handles_df.to_excel("handles.xlsx")


