import os
import sys
import json
import requests # REST requests
from requests.auth import HTTPBasicAuth
import click    # command-line argument parsing
import time


def getfile(filename):
    f = open(filename,)
    fileobject = json.load(f)
    f.close()
    return fileobject

def createStandardDatabase(fqdn, port, user, pw, deployconfig):
    # Get pre-made t-shirt file
    dbsize = deployconfig["database"]["size"]
    tshirtfile = getfile("./redis-standard-size-"+dbsize.lower()+".json.template")
    print (tshirtfile)

    # Customize the t-shirt file with user specs
    tshirtfile["name"] = deployconfig["database"]["name"]
    tshirtfile["port"] = deployconfig["database"]["port"]
    print (tshirtfile)


    # Create the database
    url = "https://" + fqdn + ":" + port + "/v1/bdbs"
    print (url)
    response = requests.post(url, verify=False, auth = HTTPBasicAuth(user, pw),
        json=tshirtfile
        )
    try:
        result = response.json()
        print(result)
        return result
    except:
        print ('Response is not JSON.')
        print (response)
        return response

def createCrdbDatabase(fqdn, port, user, pw, deployconfig):
    # Get pre-made t-shirt file
    dbsize = deployconfig["database"]["size"]
    tshirtfile = getfile("./redis-crdb-size-"+dbsize.lower()+".json.template")
    print (tshirtfile)

    # Customize the t-shirt file with user specs
    tshirtfile["name"] = deployconfig["database"]["name"]
    tshirtfile["default_db_config"]["name"] = deployconfig["database"]["name"]
    tshirtfile["default_db_config"]["port"] = deployconfig["database"]["port"]

    # Customize cluster info, if given
    # if (deployconfig["database"]["clusters"]):
    #     deployconfig["database"]["clusters"]
    print (tshirtfile)


    # Create the CRDB database
    url = "https://" + fqdn + ":" + port + "/v1/crdbs"
    print (url)
    response = requests.post(url, verify=False, auth = HTTPBasicAuth(user, pw),
        json=tshirtfile
    )
    try:
        result = response.json()
        print(result)
        # {
        #     "id": "d3827d24-fb14-4c97-b9d3-0d8f521ce2af",
        #     "status": "queued"
        # }
        if (result["status"] == "queued"):
            taskId = result["id"]
            taskStatus = "queued"

            # Poll for status on this task ID
            while (taskStatus != "failed" and taskStatus != "finished"):
                # Wait this number of seconds between status polls
                time.sleep(0.5) 
                taskResponse = requests.get( "https://" + fqdn + ":" + port + "/v1/crdb_tasks/" + taskId, verify=False, auth = HTTPBasicAuth(user, pw) )
                # {
                #     "crdb_guid": "eab221b4-77cd-4e28-9a40-3fab361a87c5",
                #     "errors": [
                #         {
                #         "cluster_name": "cluster2.local",
                #         "description": "Unavailable or invalid port",
                #         "error_code": "db_create_failed"
                #         }
                #     ],
                #     "id": "d3827d24-fb14-4c97-b9d3-0d8f521ce2af",
                #     "status": "failed"
                # }
                taskResult = taskResponse.json()
                taskStatus = taskResult["status"]
                print (taskResult)

        else:
            print("No need to check job status.")

        return result
    except:
        print ('Response is not JSON.')
        print (response)
        return response


@click.command()
@click.option('--deployfile', help='Path to the deployment configuration file.')
def runJenkinsPipeline(deployfile):
    """Jenkins pipeline script for creating databases."""

    # Get environment variables
    REDIS_SERVER_FQDN = os.environ.get('REDIS_SERVER_FQDN')
    REDIS_SERVER_PORT = os.environ.get('REDIS_SERVER_PORT')
    REDIS_USER = os.environ.get('REDIS_USER')
    REDIS_PASS = os.environ.get('REDIS_PASS')

    # Make sure environment variables are set
    needsEnv = False
    if REDIS_SERVER_FQDN is None:
        print("ERROR: This script requires the REDIS_SERVER_FQDN environment variable set to the https://<server-address> of the target Redis instance.")
        needsEnv = True
    if REDIS_SERVER_PORT is None:
        print("ERROR: This script requires the REDIS_SERVER_PORT environment variable set to the Redis REST API port (default 9443).")
        needsEnv = True
    if REDIS_USER is None:
        print("ERROR: This script requires the REDIS_USER environment variable set to the Redis user allowed to create databases.")
        needsEnv = True
    if REDIS_PASS is None:
        print("ERROR: This script requires the REDIS_PASS environment variable set to the Redis user's password.")
        needsEnv = True
    if needsEnv:
        return

    # Get the deployment config file from the user
    deployconfig = getfile(deployfile)
    print (deployconfig["database"]["name"])
    
    if (deployconfig["database"]["type"] == "crdb"):
        print("Create CRDB database")
        return createCrdbDatabase(REDIS_SERVER_FQDN, REDIS_SERVER_PORT, REDIS_USER, REDIS_PASS, deployconfig)
    else:
        print("Create standard database")
        return createStandardDatabase(REDIS_SERVER_FQDN, REDIS_SERVER_PORT, REDIS_USER, REDIS_PASS, deployconfig)



if __name__ == "__main__":
    runJenkinsPipeline()
    
    
