#!/usr/bin/env python3  
#coding: utf-8  
import re
import dbaccess
from server import Server

class Push():
    def __init__( self ):
        self.push_id=""
        self.push_project_id=""
        self.push_author_username=""
        self.push_author_name=""
        self.push_author_email=""
        self.push_date=""
        self.push_revision_before=""
        self.push_revision_after=""
        self.push_revision_counts=0
        self.push_type=""
        self.push_source=""

    @staticmethod
    def collect_push_list(project):
        dal=dbaccess.DBAccess()
        server_list=Server.get_server_list(project.project_server_ip)
        is_have_new_push=0
        if len(server_list)==1:
            server=server_list[0]
            conn=dal.build_connection(server) 
            sql_max_time="select 1,TO_CHAR(MAX(git_push_date),'YYYY-MM-DD HH24:MI:SS.US') FROM GIT_PUSH WHERE git_push_project_id='"+str(project.project_id)+"'"
            max_time=dal.execute_read_sql(sql_max_time)
            str_filter=""
            sql=""
            if server.server_type=="gitlab": 
                items=project.project_path.split("/")
                if len(items)==2:
                    str_filter+=" and tn.path='"+items[0]+"' and  tp.path='"+items[1]+"'"
                if len(max_time)>0 and max_time[0][1] !=None:
                    str_filter+=" and te.created_at > '"+str(max_time[0][1])+"'"
                sql="""select tn.path||'/'||tp.path as path,tu.username,tu.name,tu.email,te.created_at,te.data
                        from events te 
                        left join projects tp on tp.id=te.project_id 
                        left join users tu on tu.id=te.author_id
                        left join namespaces tn on tp.namespace_id=tn.id
                        where te.action=5 str_filter;"""
            elif server.server_type=="gerrit":
                if len(max_time)>0 and max_time[0][1] !=None:
                    str_filter+=" and to_char(tp.created_on-interval '8' hour,'yyyy-mm-dd hh24:mi:ss.ff6') > '"+str(max_time[0][1])+"'"
                str_filter+=" and tc.dest_project_name='"+project.project_path+"'"
                sql="""select tc.dest_project_name,tae.external_id,ta.full_name,ta.preferred_email,to_char(tp.created_on-interval '8' hour,'yyyy-mm-dd hh24:mi:ss.ff6') as created_on ,tc.change_key,tp.revision
                        from patch_sets tp 
                        left join changes tc on tc.change_id=tp.change_id
                        left join accounts ta on ta.account_id=tp.uploader_account_id  
                        left join account_external_ids tae on ta.account_id=tae.account_id and tae.external_id like 'gerrit%'
                        where tae.email_address is not null str_filter """
            sql=sql.replace("str_filter",str_filter)
            data_list=dal.execute_read_sql_from_servers(conn,sql) 
            if len(data_list)>0:
                push_list=[]
                for item in data_list:
                    push=Push()
                    push.push_project_id=project.project_id
                    push.push_author_username=item[1].replace("gerrit:","")
                    push.push_author_name=item[2]
                    push.push_author_email=item[3]
                    push.push_date=item[4]
                    if server.server_type=="gitlab": 
                        items=item[5].split("\n")
                        for item in items:
                            # do not loop useless rows
                            if push.push_type!="" and push.push_revision_before!="" and push.push_revision_after!="":
                                break
                            fields=item.split(":")
                            hash_id_value=""
                            if len(fields)==3 and len(fields[2])>=40:
                                #replace first resivision's double quotation mark
                                if "'" in fields[2]:
                                    hash_id_value=fields[2].replace("'","").strip()
                                else:
                                    hash_id_value=fields[2].strip()
                            if re.search(":before", item) != None:
                                push.push_revision_before=hash_id_value
                            elif re.search(":after", item) != None:
                                push.push_revision_after=hash_id_value
                            elif re.search(":ref", item) != None:
                                fields=item.split(":")
                                if len(fields)==3 and "refs/tags/" in fields[2]:
                                    push.push_type="tag"
                                else:
                                    push.push_type="revision"
                        push.push_source="gitlab"
                    elif server.server_type=="gerrit":
                        push.push_revision_before=item[5]
                        push.push_revision_after=item[6]
                        push.push_type="revision"
                        push.push_source="gerrit"
                    push_list.append(push)
                Push.insert_push_list(push_list)
                is_have_new_push=1
        else:
            print ('Warning: unexpected exception "%s"' % server_list)
        return is_have_new_push
    
    @staticmethod
    def insert_push_list(push_list):
        dal=dbaccess.DBAccess()
        sql=""
        if len(push_list)>0:
            for item in push_list:
                str_parameters="'"+str(item.push_project_id)+"','"+item.push_author_username+"','"+item.push_author_name+"','"+item.push_author_email+"','"+item.push_revision_before+"','"+item.push_revision_after+"','"+str(item.push_date)+"','"+item.push_type+"','"+item.push_source+"'"
                sql+="insert into git_push(git_push_project_id, git_push_author_username, git_push_author_name, git_push_author_email,git_push_revision_before,git_push_revision_after, git_push_date,git_push_type,git_push_source) values (%s);\r\n" % (''.join(str_parameters))
            dal.execute_write_sql(sql)
        return  
    
    @staticmethod 
    #get_push_list isn't used
    def get_push_list(project_id):
        dal=dbaccess.DBAccess()
        str_filter=""
        sql="""SELECT git_push_id, git_push_project_id,git_push_author_username,git_push_author_name,  
                git_push_author_email, git_push_date, git_push_revision_before, 
                git_push_revision_after,  git_push_type
                FROM git_push where 1=1 str_filter;"""
        if project_id is not None and str(project_id) and not str(project_id).isspace():
            str_filter=" and git_push_project_id='"+str(project_id)+"'"
        sql=sql.replace("str_filter",str_filter)
        data_list=dal.execute_read_sql(sql)
        push_list=[]
        for arrayindex,array in enumerate(data_list):
            push=Push()
            push.push_id=array[0]
            push.push_project_id=array[1]
            push.push_author_username=array[2].strip()
            push.push_author_name=array[3].strip()
            push.push_author_email=array[4].strip()
            push.push_date=array[5]
            push.push_revision_before=array[6].strip()
            push.push_revision_after=array[7].strip()
            push.push_type=array[8].strip()
            push_list.append(push)
        return push_list
        