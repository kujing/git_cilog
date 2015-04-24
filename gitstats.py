#!/usr/bin/env python
# Copyright (c) 2007-2014 Heikki Hokkanen <hoxu@users.sf.net> & others (see doc/AUTHOR)
# GPLv2 / GPLv3

import re
import sys
import os
import time
import datetime
from tag import Tag
from util import Util
from file import File
from push import Push
from branch import Branch
from server import Server 
from project import Project
from revision import Revision
from revision_file_link import Revision_File_Link


class Gitstats():
	def __int__(self):
		return
	def collect(project):
		#1.Server
		server_list=Server.get_server_list()
		#2.Project_Insert new projects
		new_project_list=Project.get_new_project_list(server_list)
		if len(new_project_list) >0:
			Project.insert_new_project_list(new_project_list)
		#2.Project_Get all projects
		serial_number=0
		#Collect data by server_name
		server_name=""
		if len(sys.argv)>1:
			server_name=sys.argv[1]
		if server_name=="":
			project_list=Project.get_project_list()
		else:
			project_list=Project.get_project_list(server_name)	   
		for project in project_list:
			serial_number=serial_number+1
			print (">>>>>>No%s.Git project url: %s " %(len(project_list)-serial_number, project.project_repository_url))
			print (">>>>>>0_Collecting push records")
			is_have_new_push=Push.collect_push_list(project)
			if is_have_new_push==0:
				print (">>>>>>There is nothing new in repository \n")
				continue
			# clean workspace
			git_home=os.getcwd()
			git_path=git_home+"/"+project.project_name
			if os.path.isdir(git_path):
				Util.getpipeoutput(["rm -rf %s " % git_path ])   
			print (">>>>>>1_Git path: %s" % git_path)
			print (">>>>>>2_Clone git repository")
			Util.getpipeoutput(["git clone %s " % project.project_repository_url+project.project_name ])
			print (">>>>>>3_Collecting git data")
			if os.path.isdir(git_path):
				os.chdir(git_path)
				#########Begin to collect
				#Collect new branchs 
				Branch.collect_branch_list(project.project_id)		
				#Query all branchs from database
				all_branch_list=Branch.get_branch_list(project.project_id)
				branch_list=[]
				for branch in all_branch_list:
					revision_list=[]
					print("   >>>>>>>>Branch Name:"+branch.branch_name)
					current_branch=Util.getpipeoutput(["git rev-parse --abbrev-ref HEAD"])
					if current_branch!=branch.branch_name:
						Util.getpipeoutput(["git checkout %s" % branch.branch_name])
					# if last_commit_id is empty ,it means that it's a new branch
					latest_commit_id=Util.getpipeoutput(["git rev-parse HEAD"])
					if branch.branch_last_commit_id!=latest_commit_id:
						#Collect all the Revisions(all commits)
						branch_total_line=Revision.collect_revision_list(branch,latest_commit_id)
						#Collect all the files
						local_file_change_list=File.collect_file_list(branch,latest_commit_id)
						#Collect all the link
						Revision_File_Link.collect_link_list(local_file_change_list,branch,latest_commit_id)
						#Update branch info
						branch.branch_type="update"
						branch.branch_total_line=branch_total_line
						branch.branch_last_commit_id=latest_commit_id
						branch.branch_contributor_counts = int(Util.getpipeoutput(["git shortlog -s %s" % Util.getlogrange(), "wc -l"]))
						branch.branch_file_counts=int(Util.getpipeoutput(["git ls-files | wc -l"]))
						branch_list.append(branch)
				Branch.update_branch_list(branch_list)
				Tag.collect_tag_list(project.project_id)
				# Merge Request
				# Project LOC
				#########End
				os.chdir(git_home)
			print (">>>>>>4.Delete the git repository diretory\n")
			if os.path.isdir(git_path):
				Util.getpipeoutput(["rm -rf %s " % git_path ])
if __name__=='__main__':
	gitstats = Gitstats()
	gitstats.collect()
