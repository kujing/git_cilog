#!/usr/bin/env python3  
#coding: utf-8  

from util import Util
import re
import datetime
import dbaccess

class File():
    def __init__(self):
        self.file_id=""
        self.file_name=""
        self.file_path=""
        self.file_creator=""
        self.file_create_date=""
        self.file_project_id=""
    
    @staticmethod
    def collect_file_list(branch,latest_commit_id):
        file_list=[]
        local_file_list=[]
        exist_file_list=File.get_file_list(branch.branch_project_id)
        if (branch.branch_last_commit_id and not branch.branch_last_commit_id.isspace()):
            local_file_change_list = Util.getpipeoutput(['git log --numstat %s --pretty=format:"%%at|^%%aN|^%%H|^%%s|^MARK" %s' % (" -m", branch.branch_last_commit_id+".."+latest_commit_id)]).split('\n')
        else:
            local_file_change_list = Util.getpipeoutput(['git log --numstat %s --pretty=format:"%%at|^%%aN|^%%H|^%%s|^MARK" %s' % (" -m", Util.getlogrange('HEAD'))]).split('\n')
        
        for item in local_file_change_list:
            if len(item) == 0:
                continue
            if re.search("MARK", item) == None:
                change = item.split()
                if len(change) == 3:
                    is_have=0
                    for item in local_file_list:
                        if item==change[2]:
                            is_have=1
                            break
                    if is_have==0:
                        local_file_list.append(change[2])
        for item in local_file_list:
            count=0
            is_have=0
            for file in exist_file_list:
                if item.strip()==file.file_path.strip():
                    is_have=1
                    break
            if is_have==0:
                file=File()
                filepaths=item.split("/")
                file.file_name=filepaths[len(filepaths)-1]
                file.file_path=item
                file.file_create_date=datetime.date.today().strftime("%Y-%m-%d")
                file.file_project_id=branch.branch_project_id
                file_list.append(file)
        File.insert_new_file_list(file_list)
        return local_file_change_list

    @staticmethod
    def get_file_list(project_id):
        file_list=[]
        dal=dbaccess.DBAccess()
        str_filter="where git_file_project_id="+str(project_id)
        sql="""select git_file_id, git_file_name, git_file_path, git_file_creator,git_file_create_date, git_file_project_id
            from git_file str_filter;"""
        sql=sql.replace("str_filter",str_filter)
        data_list=dal.execute_read_sql(sql) 
        #print(sql)
        for item in data_list:
            fileobj=File()
            fileobj.file_id=item[0]
            fileobj.file_name=item[1]
            fileobj.file_path=item[2]
            fileobj.file_creator=item[3]
            fileobj.file_create_date=item[4]
            fileobj.file_project_id=item[5]
            file_list.append(fileobj)
        return file_list
    
    @staticmethod
    def insert_new_file_list(file_list):
        dal=dbaccess.DBAccess()
        sql=""
        if len(file_list)>0:
            for item in file_list:
                str_parameters="'"+item.file_name+"','"+item.file_path+"','"+item.file_creator+"','"+item.file_create_date+"','"+str(item.file_project_id)+"'"
                sql+="insert into git_file(git_file_name, git_file_path, git_file_creator,git_file_create_date, git_file_project_id) values (%s);\r\n" % (''.join(str_parameters))
            dal.execute_write_sql(sql)

