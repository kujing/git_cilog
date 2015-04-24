#!/usr/bin/env python3  
#coding: utf-8  
import dbaccess
import project
import datetime
import time

class Project():
    def __init__(self):
        self.project_id=""
        self.project_name=""
        self.project_path=""
        self.project_server_ip=""
        self.project_owner_username=""
        self.project_owner_name=""
        self.project_owner_email=""
        self.project_create_date=""
        self.project_repository_url=""
        #self.project_file_counts=0
        #self.project_total_size=0
        #self.project_total_loc=0

    @staticmethod
    def get_project_list(server_name=None): 
        dal=dbaccess.DBAccess()
        project_list=[]
        if server_name is not None and str(server_name) and not str(server_name).isspace():
            str_filter=server_name.strip()
            sql="""select git_project_id, git_project_name, git_project_path, git_project_server_ip, 
                   git_project_owner_username, git_project_owner_name, git_project_owner_email, 
                   git_project_create_date ,git_project_repo_url from git_project tp
                   left join git_server ts on tp.git_project_server_ip=ts.git_server_ip
                   where ts.git_server_name='str_filter' ;"""
            sql=sql.replace("str_filter",str_filter)
        else:
            sql="""select git_project_id, git_project_name, git_project_path, git_project_server_ip, 
                   git_project_owner_username, git_project_owner_name, git_project_owner_email, 
                   git_project_create_date ,git_project_repo_url from git_project  ;"""
        data_list=dal.execute_read_sql(sql) 
        for item in data_list:
            proj=project.Project()
            proj.project_id=item[0]
            proj.project_name=item[1]
            proj.project_path=item[2]
            proj.project_server_ip=item[3]
            proj.project_owner_username=item[4]
            proj.project_owner_name=item[5]
            proj.project_owner_email=item[6]
            proj.project_create_date=item[7]
            proj.project_repository_url=item[8]
            project_list.append(proj)
        return project_list
    
    @staticmethod
    def get_new_project_list(server_list): 
        dal=dbaccess.DBAccess()
        project_list=[]
        #get proejct list from each server
        for server in server_list:
            #get the last project create date
            sql_max_time="select 1,TO_CHAR(MAX(GIT_PROJECT_CREATE_DATE),'YYYY-MM-DD HH24:MI:SS.US') FROM GIT_PROJECT WHERE git_project_server_ip='"+server.server_ip+"'"
            max_time=dal.execute_read_sql(sql_max_time)
            str_max_time=""
            if len(max_time)>0 and max_time[0][1] !=None:
                str_max_time="WHERE TP.CREATED_AT > '"+str(max_time[0][1])+"'"
            conn=dal.build_connection(server)  
            sql=""
            if server.server_type=="gitlab":  
                sql="""SELECT TP.NAME, TN.PATH||'/'||TP.PATH,TU.USERNAME,TU.NAME,TU.EMAIL ,TP.CREATED_AT
                        FROM PROJECTS TP LEFT JOIN USERS TU ON TP.CREATOR_ID=TU.ID
                        LEFT JOIN NAMESPACES TN ON TP.NAMESPACE_ID=TN.ID str_filter;"""
            elif server.server_type=="gerrit":
                sql = "select TP.name,TP.name,' ',' ',' ',TP.CREATED_AT from (select distinct(dest_project_name) as name,to_char(min(created_on)-interval '8' hour,'yyyy-mm-dd hh24:mi:ss.ff6' ) as CREATED_AT from changes where instr(dest_project_name,'All')=0 group by dest_project_name) TP str_filter"
            sql=sql.replace("str_filter",str_max_time) 
            data_list=dal.execute_read_sql_from_servers(conn,sql) 
            for item in data_list:
                proj=project.Project()
                proj.project_name=item[0]
                proj.project_path=item[1]
                proj.project_server_ip=server.server_ip
                proj.project_owner_username=item[2]
                proj.project_owner_name=item[3]
                proj.project_owner_email=item[4]
                proj.project_create_date=item[5]
                if server.server_type=="gitlab":
                    proj.project_repository_url="git@"+proj.project_server_ip+":"+proj.project_path+".git"
                elif server.server_type=="gerrit":
                    proj.project_repository_url="ssh://ysdpadmin@"+proj.project_server_ip+":29418/"+proj.project_path
                project_list.append(proj)
        return project_list
    
    @staticmethod
    def insert_new_project_list(project_list):
        dal=dbaccess.DBAccess()
        sql=""
        for proj in project_list:
            str_parameters_project="'"+proj.project_name+"','"+proj.project_path+"','"+proj.project_server_ip+"','"+proj.project_repository_url+"','"+proj.project_owner_username+"','"+proj.project_owner_name+"','"+proj.project_owner_email+"','"+str(proj.project_create_date)+"','"+datetime.date.today().strftime("%Y-%m-%d %H:%M")+"'"
            sql+="insert into git_project (git_project_name, git_project_path,git_project_server_ip,git_project_repo_url,git_project_owner_username,git_project_owner_name,git_project_owner_email,git_project_create_date,git_project_insert_date) values (%s);\r\n" % (''.join(str_parameters_project))
        dal.execute_write_sql(sql)

