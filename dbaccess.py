#!/usr/bin/env python3  
#coding: utf-8  
import psycopg2
import cx_Oracle
import os 
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8' 
class DBAccess():
    def __init__(self):
        pass
    
    @staticmethod
    def get_connection():
        conn = psycopg2.connect(database="TEST", user="postgres", password="postgres", host="172.16.51.206", port="5432")
        return conn
    def execute_write_sql(self,sql): 
        conn = DBAccess.get_connection()
        cur = conn.cursor()
        cur.execute(sql) 
        conn.commit()
        cur.close()
        conn.close()
    def execute_read_sql(self,sql): 
        conn = DBAccess.get_connection()
        cur = conn.cursor()
        cur.execute(sql) 
        items = cur.fetchall()
        cur.close()
        conn.close()
        return items
    def build_connection(self,server):
        if server.server_db_type.strip()=="postgresql":
            conn=psycopg2.connect(database=server.server_db_name, user=server.server_db_username, password=server.server_db_password, host=server.server_db_ip, port=server.server_db_port)
            return conn
        elif server.server_db_type.strip()=="oracle":
            tns=cx_Oracle.makedsn(server.server_db_ip,server.server_db_port,"orcl")
            conn=cx_Oracle.connect(server.server_db_username,server.server_db_password,tns)
            return conn
    def execute_read_sql_from_servers(self,conn,sql): 
        cur = conn.cursor()
        cur.execute(sql) 
        items = cur.fetchall()
        cur.close()
        conn.close() 
        return items   
