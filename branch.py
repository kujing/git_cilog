#!/usr/bin/env python3  
#coding: utf-8  

from util import Util
import datetime
import dbaccess

class Branch():
    def __init__(self):
        self.branch_id=""
        self.branch_owner=""
        self.branch_name=""
        self.branch_start_date=""
        self.branch_file_counts=0
        self.branch_total_size=0
        self.branch_total_line=0
        self.branch_contributor_counts=0
        self.branch_last_commit_id=""
        self.branch_project_id=""
        #need update or not
        self.branch_type=""
    @staticmethod
    def collect_branch_list(project_id):
        branch_list=[]
        repo_reomte_branch_list=Branch.get_remote_branch_list()
        exist_branch_list=Branch.get_branch_list(project_id)
        for branch_item in repo_reomte_branch_list:
            is_have=0
            if len(exist_branch_list)>0:
                for item in exist_branch_list:
                    if item.branch_name==branch_item.strip():
                        is_have=1
                        break
            if is_have==0:
                branch=Branch()
                branch.branch_name=branch_item.strip()
                branch.branch_owner=""
                branch.branch_start_date=datetime.date.today().strftime("%Y-%m-%d") 
                branch.branch_last_commit_id=""
                branch.branch_project_id=project_id
                branch_list.append(branch)
        if len(branch_list)>0:
            Branch.insert_new_branch_list(branch_list)
    @staticmethod
    def get_remote_branch_list():
        branch_list=[]
        branchs=Util.getpipeoutput(["git branch -a"]).replace("*","").split("\n")
        for branch_item in branchs:
            if "remotes/origin" in branch_item and "remotes/origin/HEAD" not in branch_item:
                branch_list.append(branch_item.replace("remotes/origin/",""))
        return branch_list       
    
    @staticmethod
    def get_branch_list(project_id):
        branch_list=[]
        dal=dbaccess.DBAccess()
        str_filter="where git_branch_project_id="+str(project_id)
        sql="""select git_branch_id,git_branch_name, git_branch_owner, git_branch_start_date,git_branch_file_counts, 
        git_branch_total_size, git_branch_total_line,git_branch_contributor_counts, git_branch_last_commit_id, 
        git_branch_project_id from git_branch str_filter;"""
        sql=sql.replace("str_filter",str_filter)
        data_list=dal.execute_read_sql(sql) 
        #print(sql)
        for item in data_list:
            branch=Branch()
            branch.branch_id=item[0]
            branch.branch_name=item[1]
            branch.branch_owner=item[2]
            branch.branch_start_date=item[3]
            branch.branch_file_counts=item[4]
            branch.branch_total_size=item[5]
            branch.branch_total_line=item[6]
            branch.branch_contributor_counts=item[7]
            branch.branch_last_commit_id=item[8]
            branch.branch_project_id=item[9]
            branch_list.append(branch)
        return branch_list
    
    @staticmethod
    def update_branch_list(branch_list):
        sql=""
        dal=dbaccess.DBAccess()
        if len(branch_list)>0:
            for branch in branch_list:
                sql+="update git_branch set git_branch_file_counts="+str(branch.branch_file_counts)+", git_branch_total_size="+str(branch.branch_total_size)+", git_branch_total_line="+str(branch.branch_total_line)+", git_branch_contributor_counts="+str(branch.branch_contributor_counts)+", git_branch_last_commit_id='"+branch.branch_last_commit_id+"' where git_branch_id="+str(branch.branch_id)+";\r\n" 
            #print(sql)
            dal.execute_write_sql(sql)    
    
    @staticmethod
    def insert_new_branch_list(branch_list):
        dal=dbaccess.DBAccess()
        sql=""
        if len(branch_list)>0:
            for branch in branch_list:
                str_parameters="'"+branch.branch_name+"','"+branch.branch_owner+"','"+str(branch.branch_start_date)+"','"+str(branch.branch_file_counts)+"','"+str(branch.branch_total_size)+"','"+str(branch.branch_total_line)+"','"+str(branch.branch_contributor_counts)+"','"+branch.branch_last_commit_id+"','"+str(branch.branch_project_id)+"'"
                sql+="insert into git_branch(git_branch_name, git_branch_owner, git_branch_start_date,git_branch_file_counts, git_branch_total_size, git_branch_total_line,git_branch_contributor_counts, git_branch_last_commit_id, git_branch_project_id) values (%s);\r\n" % (''.join(str_parameters))
            dal.execute_write_sql(sql)

