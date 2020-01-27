# -*- coding: utf-8 -*-
"""
Author : Jacques Flores
Created : October 17th,2019
About:  Script for creating datasets in Dataverse. 
        An Empty JSON file with Dataverse structure is imported and converted into a JSON dict
        Metadata is imported from an excel file into a pandas dataframe and written into the empty JSON formatted string.
"""


from pyDataverse import api
import pandas as pd



# Confidential API Token (Do Not Distribute) ****last four digits removed)
apitoken = "38404b17-46f9-4fe5-808e-a4a38bd80aea"

# Demo Dataverse server
dtvserver = "https://dataverse.nl"

#Loading connection and authentication
dataverse = api.Api(dtvserver,apitoken)


#read excel file with metadata as pandas dataframe
xlfile = "DH2019_paperswithfilesandhandlesCopy.xlsx"
xl = pd.read_excel(xlfile, converters={'paperID': str})

dataset = 0
entries = xl['paperID'].count()


while dataset < entries:
    #Make a copy of the dataverse json template as metadata
    poster = xl.loc[dataset]['contribution_type'] == 'Poster'
    fileid = xl.loc[dataset]['paperID']
    handle = xl.loc[dataset]['handle']

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
    
            
        

        
  
    
      





