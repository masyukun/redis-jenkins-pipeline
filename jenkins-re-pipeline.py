import os
import sys
import json
import requests # REST requests
import click    # command-line argument parsing



def getfile(filename):
    f = open(filename,)
    fileobject = json.load(f)
    f.close()
    return fileobject


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

    # Get pre-made t-shirt file
    dbsize = deployconfig["database"]["size"]
    tshirtfile = getfile("./redis-standard-size-"+dbsize.lower()+".json.template")
    print (tshirtfile)

    # Customize the t-shirt file with user specs
    tshirtfile["name"] = deployconfig["database"]["name"]
    print (tshirtfile)

    # Create the database
    url = "https://" + REDIS_SERVER_FQDN + ":" + REDIS_SERVER_PORT + "/v1/bdbs"
    print (url)
    #response = requests.post(url, json=tshirtfile)
    #print (response.json())




if __name__ == "__main__":
    runJenkinsPipeline()
    
    
