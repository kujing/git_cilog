#!/usr/bin/env python3  
#coding: utf-8  

import re
import dbaccess
from util import Util
from file import File


class Revision_File_Link():
    def __init__(self):
        self.link_id=""
        self.link_file_id=""
        self.link_revision_hash_id=""
        self.link_file_line_added=""
        self.link_file_line_deleted=""
        self.link_project_id=""
    
    @staticmethod
    def collect_link_list(local_file_change_list,branch,latest_commit_id):
        revision_file_link_list=[]
        exist_file_list=File.get_file_list(branch.branch_project_id)
        exist_link_list=Revision_File_Link.get_link_list(branch.branch_project_id)
        #To avoid repeating to execute  git log --numstat
        if len(local_file_change_list)==0:
            if (branch.branch_last_commit_id and not branch.branch_last_commit_id.isspace()):
                local_file_change_list = Util.getpipeoutput(['git log --numstat %s --pretty=format:"%%at|^%%aN|^%%H|^%%s|^MARK" %s' % (" -m", branch.branch_last_commit_id+".."+latest_commit_id)]).split('\n')
            else:
                local_file_change_list = Util.getpipeoutput(['git log --numstat %s --pretty=format:"%%at|^%%aN|^%%H|^%%s|^MARK" %s' % (" -m", Util.getlogrange('HEAD'))]).split('\n')
        hash_id_value=""
        commit_note=""
        for item in local_file_change_list:
            if len(item) == 0:
                continue
            if re.search("MARK", item) != None:
                change = item.split("|^")
                if len(change)!=0:
                    try:
                        (stamp,author, hashid,note) = (int(change[0]), change[1],change[2],change[3])  
                        hash_id_value=hashid  
                        commit_note=note          
                    except ValueError:
                        print ('Warning: unexpected line "%s"' % item)
                else:
                    print ('Warning: unexpected line "%s"' % item)
            else:
                change = item.split()
                file_id_value=""
                if len(change) == 3:
                    if "Merge" in commit_note:
                        continue
                    filepaths=change[2].split("/")
                    (inserted, deleted,filename,filepath) = (change[0],change[1],filepaths[len(filepaths)-1],change[2])
                    for item in exist_file_list:
                        if item.file_path.strip()==change[2].strip():
                            file_id_value=item.file_id
                            break
                    is_have=0
                    for item in exist_link_list:
                        if item.link_revision_hash_id==hash_id_value and item.link_file_id==file_id_value:
                            is_have=1
                            #do not store the same hash id and file id record,the same revision in each branchs only store once
                            break
                    if is_have==0:
                        link=Revision_File_Link()
                        link.link_file_id=file_id_value
                        link.link_revision_hash_id=hash_id_value
                        link.link_file_line_added=inserted
                        link.link_file_line_deleted=deleted
                        link.link_project_id=branch.branch_project_id
                        revision_file_link_list.append(link)
                else:
                    print('Warning: unexpected line "%s"' % item)
        Revision_File_Link.insert_new_link_list(revision_file_link_list)
    
    @staticmethod
    def insert_new_link_list(link_list):
        dal=dbaccess.DBAccess()
        sql=""
        if len(link_list)>0:
            for item in link_list:
                str_parameters="'"+str(item.link_file_id)+"','"+str(item.link_revision_hash_id)+"','"+str(item.link_file_line_added)+"','"+str(item.link_file_line_deleted)+"','"+str(item.link_project_id)+"'"
                sql+="insert into git_revision_file_link (git_link_file_id, git_link_revision_hash_id, git_link_file_line_added,git_link_file_line_deleted,git_link_project_id) values (%s);\r\n" % (''.join(str_parameters))
            #print(sql)           
            dal.execute_write_sql(sql)
    
    @staticmethod
    def get_link_list(project_id):
        link_list=[]
        dal=dbaccess.DBAccess()
        str_filter="where git_link_project_id="+str(project_id)
        sql="""select git_link_id,git_link_file_id, git_link_revision_hash_id, git_link_file_line_added, git_link_file_line_deleted,git_link_project_id
            from git_revision_file_link str_filter;"""
        sql=sql.replace("str_filter",str_filter)
        data_list=dal.execute_read_sql(sql) 
        #print(sql)
        for item in data_list:
            link=Revision_File_Link()
            link.link_id=item[0]
            link.link_file_id=item[1]
            link.link_revision_hash_id=item[2]
            link.link_file_line_added=item[3]
            link.link_file_line_deleted=item[4]
            link.link_project_id=item[5]
            link_list.append(link)
        return link_list
