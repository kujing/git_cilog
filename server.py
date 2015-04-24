#!/usr/bin/env python3  
#coding: utf-8  
import dbaccess

class Server():
    def __init__(self):
        self.server_ip=""
        self.server_type=""
        self.server_app_port=""
        self.server_db_type=""
        self.server_db_ip=""
        self.server_db_name=""
        self.server_db_username=""
        self.server_db_password=""
        self.server_db_port=""
        self.server_create_date=""
    @staticmethod
    def get_server_list(ip=None):
        dal=dbaccess.DBAccess()
        str_filter=""
        if ip is not None and str(ip) and not str(ip).isspace():
            str_filter=" and git_server_ip='"+str(ip)+"'"
        sql="""select git_server_ip, git_server_type, git_server_app_port,git_server_db_type, git_server_db_ip,
            git_server_db_name, git_server_db_username, git_server_db_password, 
            git_server_db_port, git_server_create_date from git_server where 1=1 str_filter;"""
        sql=sql.replace("str_filter",str_filter)
        data_list=dal.execute_read_sql(sql)
        server_list=[]
        for arrayindex,array in enumerate(data_list):
            srv=Server()
            srv.server_ip=array[0]
            srv.server_type=array[1]
            srv.server_app_port=array[2]
            srv.server_db_type=array[3]
            srv.server_db_ip=array[4]
            srv.server_db_name=array[5]
            srv.server_db_username=array[6]
            srv.server_db_password=array[7]
            srv.server_db_port=array[8]
            srv.server_create_date=array[9]
            server_list.append(srv)
        return server_list            
