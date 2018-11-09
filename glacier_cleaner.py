#!/usr/bin/python3

Days = 180
vault_name = "backup"
file_glacier = "/tmp/output_glacier.json"
file_created_job = "/tmp/output_glacier_job.json"
#
file_job_reveal = "/tmp/output_glacier_reveal.json"

import json
import datetime
import os

def delete_job(id):
    print ("delete archive ")+ str(id)
    cmd = "aws glacier delete-archive --account-id - --vault-name "+ \
          vault_name +" --archive-id"+ id
    print(cmd)
    #os.system(cmd)

def check_date(creat_date):
    print ("Check data")
    creat_date=datetime.datetime.strptime(creat_date,"%Y-%m-%dT%H:%M:%SZ")
    date = datetime.datetime.now() - datetime.timedelta(days=Days)
    if  date.strftime('%s') > creat_date.strftime('%s'):
        return True
    else:
        return False


def file_parse():
    print ("File parse")
    data_json = json.loads(open(file_glacier).read())
    for archive in data_json['ArchiveList']:
        if check_date(archive['CreationDate']):
            #print (archive['CreationDate']+" Description: "\
            #       +archive['ArchiveDescription']+" ID: "\
            #       +archive['ArchiveId'])
            delete_job(archive['ArchiveId'])
    rm_file()


def rm_file():
    print ("rm file")
    cmd_mv = "mv "+ file_glacier +" "+ file_glacier +".last"
    cmd_rm = "rm -rf "+ file_glacier
    os.system(cmd_mv)
    os.system(cmd_rm)
    global Done
    Done = "0"

def creat_job():
    print ("create a job file")
    #job_parm={"Type": "inventory-retrieval"}
    cmd="aws glacier initiate-job --account-id - --vault-name " + vault_name + \
    " --job-parameters \'{\"Type\": \"inventory-retrieval\"}\' > " + file_created_job
    print(cmd)
    os.system(cmd)

def reveal_job():
    print ("reveal job")
    cmd="aws glacier list-jobs --account-id - --vault-name " \
      + vault_name +" > " + file_job_reveal
    print(cmd)
    os.system(cmd)
    data_json=json.loads(open(file_job_reveal).read())
    for data in data_json['JobList']:
        #print(data['StatusCode'])
        if data['StatusCode'] == "Succeeded":
            #create_file_glacier (data['JobId'])
            create_file_glacier(data['JobId'])
        else:
            exit (0)


def create_file_glacier(id):
    print ("create glacier file")
    cmd="aws glacier get-job-output --account-id - --vault-name "+\
        vault_name +  " --job-id "+ id +" "+ file_glacier
    print(cmd)
    os.system(cmd)
    file_parse()


def main():
    print ("Start Glacier cleaner")
    if os.path.exists(file_glacier):
        file_parse()
    elif os.path.exists(file_created_job):
        reveal_job()
    else:
        creat_job()


main()

