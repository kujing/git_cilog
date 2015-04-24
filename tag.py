#!/usr/bin/env python3  
#coding: utf-8  

import dbaccess
import datetime
from util import Util
from revision import Revision

class Tag():
    def __init__(self):
        self.tag_id=""
        self.tag_name=""
        self.tag_branch_id=""
        self.tag_project_id=""
        self.tag_creater=""
        self.tag_create_date=""
        self.tag_hash_id=""
     
    @staticmethod
    def collect_tag_list(project_id):
        tag_list=[]
        local_tag_list=[]
        redundancy_tag_list = Util.getpipeoutput(['git show-ref --tags --dereference']).split('\n')
        ##find the right tags and hash ids
        redundancy_tag_list.reverse()
        for item in redundancy_tag_list:
            is_have=0
            for tag in local_tag_list:
                (hash, tagname) = tag.split(" ")
                if tagname in item:
                    is_have=1
                    break
            if is_have==1:
                continue
            if "^{}" in item:
                item=item.replace("^{}","")
            local_tag_list.append(item)
        
        for tag_item in local_tag_list:
            tag=Tag()
            if len(tag_item) == 0:
                continue
            (hash, tagname) = tag_item.split()
            tag_hash_list=Tag.get_tag_list(project_id)
            ##don't store repeated tags
            bool_repeat_tag="false"
            for item in tag_hash_list:
                if hash==item.tag_hash_id:
                    bool_repeat_tag="true"
                    break
            if bool_repeat_tag=="true":
                continue
            tag_name = tagname.replace('refs/tags/', '')
            output = Util.getpipeoutput(['git log "%s" --pretty=format:"%%at %%aN" -n 1' % hash])       
            if len(output) > 0:
                parts = output.split(' ')
                stamp = 0
                try:
                    stamp = int(parts[0])
                except ValueError:
                    stamp = 0
                #It's high priority to query old revision,new revisions mostly are not tag commit
                project_revision_list=Revision.get_revision_list(project_id,"")
                if len(project_revision_list)>0:
                    for revision in project_revision_list:
                        if revision.revision_hash_id.strip()==hash.strip():
                            tag.tag_branch_id=revision.revision_branch_id
                            break
                if tag.tag_branch_id=="":
                    #sometimes we can't find out the branch,maybe it's a exception
                    tag.tag_branch_id=0
                tag.tag_project_id=project_id
                tag.tag_name=tag_name
                tag.tag_creater=parts[1]
                tag.tag_create_date=datetime.datetime.fromtimestamp(float(stamp))
                tag.tag_hash_id=hash
                tag_list.append(tag)
        
        if len(tag_list)>0:    
            Tag.insert_tag_list(tag_list)  

    @staticmethod
    def insert_tag_list(tag_list):
        dal=dbaccess.DBAccess()
        sql=""
        if len(tag_list)>0:
            for tag in tag_list:
                str_parameters="'"+tag.tag_name+"','"+tag.tag_hash_id+"','"+str(tag.tag_project_id)+"','"+str(tag.tag_branch_id)+"','"+tag.tag_creater+"','"+str(tag.tag_create_date)+"'"
                sql+="insert into git_tag(git_tag_name, git_tag_hash_id , git_tag_project_id, git_tag_branch_id, git_tag_author_username, git_tag_create_date) values (%s);\r\n" % (''.join(str_parameters))
            dal.execute_write_sql(sql)
    
    @staticmethod
    def get_tag_list(project_id):
        tag_list=[]
        dal=dbaccess.DBAccess()
        sql=""  
        str_filter="where git_tag_project_id="+str(project_id)
        sql="""select git_tag_id, git_tag_name,git_tag_hash_id,git_tag_project_id,git_tag_branch_id,git_tag_author_username,git_tag_create_date from git_tag str_filter;"""
        sql=sql.replace("str_filter",str_filter)
        data_list=dal.execute_read_sql(sql) 
        for item in data_list:
            tag=Tag()
            tag.tag_id=item[0]
            tag.tag_name=item[1]
            tag.tag_hash_id=item[2]     
            tag.tag_project_id=item[3]
            tag.tag_branch_id=item[4]
            tag.tag_creater=item[5]
            tag.tag_create_date=item[6]
            tag_list.append(tag)        
        return tag_list
