#!/usr/bin/env python3  
#coding: utf-8  

import dbaccess
import datetime
import re
from util import Util

class Revision():
    def __init__( self ):
        self.revision_hash_id=""
        self.revision_project_id=""
        self.revision_branch_id=""
        self.revision_author_username=""
        self.revision_author_email=""
        self.revision_date=""
        self.revision_line_added=0
        self.revision_file_changed=0
        self.revision_line_deleted=0
        self.revision_commit_note=""
   
    @staticmethod
    def collect_revision_list(branch,latest_commit_id):
        revision_list=[]
        if (branch.branch_last_commit_id and not branch.branch_last_commit_id.isspace()):
            local_revision_list = Util.getpipeoutput(['git rev-list --pretty=format:"%%H|^%%at|^%%ai|^%%s|^%%aN|^<%%aE>" %s' % branch.branch_last_commit_id+".."+latest_commit_id, 'grep -v ^commit']).split('\n')
            local_revision_file_changeset_list = Util.getpipeoutput(['git log --shortstat %s --pretty=format:"%%at|^%%aN|^%%H " %s' % (" -m", branch.branch_last_commit_id+".."+latest_commit_id)]).split('\n')
        else:
            local_revision_list = Util.getpipeoutput(['git rev-list --pretty=format:"%%H|^%%at|^%%ai|^%%s|^%%aN|^<%%aE>" %s' % Util.getlogrange('HEAD'), 'grep -v ^commit']).split('\n')
            local_revision_file_changeset_list = Util.getpipeoutput(['git log --shortstat %s --pretty=format:"%%at|^%%aN|^%%H " %s' % (" -m", Util.getlogrange('HEAD'))]).split('\n')
        #revision list
        for item in local_revision_list:
            if "Merge" in item:
                continue
            revision= Revision()
            parts = item.split('|^', 6)
            try:
                stamp = int(parts[1])
            except ValueError:
                stamp = 0
            hash_id = parts[0]
            note = parts[3]
            author = parts[4]
            mail = parts[5].lstrip('<').rstrip('>')
            date = datetime.datetime.fromtimestamp(float(stamp))
            revision.revision_project_id=branch.branch_project_id
            revision.revision_branch_id=branch.branch_id
            revision.revision_hash_id=hash_id
            revision.revision_author_username=author
            revision.revision_author_email=mail
            revision.revision_date=date
            revision.revision_commit_note=note
            revision_list.append(revision)
        #revision list with file changeset
        hash_id_value=""
        for changeset in local_revision_file_changeset_list:
            if len(changeset) == 0:
                continue
            files = 0; inserted = 0; deleted = 0
            author = None
            if re.search('files? changed', changeset) == None:
                changes = changeset.split("|^")
                if len(changes)!=0:
                    try:
                        (stamp,author, hashid) = (int(changes[0]), changes[1],changes[2])   
                        hash_id_value=hashid
                        files, inserted, deleted = 0, 0, 0
                    except ValueError:
                        print ('Warning: unexpected line "%s"' % changeset)
                else:
                    print ('Warning: unexpected line "%s"' % changeset)
            else:
                numbers = Util.getstatsummarycounts(changeset)
                if len(numbers) == 3:
                    (files, inserted, deleted) = map(lambda el : int(el), numbers)
                    branch.branch_total_line += inserted
                    branch.branch_total_line -= deleted
                else:
                    print ('Warning: failed to handle line "%s"' % line)
                    (files, inserted, deleted) = (0, 0, 0)
                for revision in revision_list:
                    if revision.revision_hash_id.strip()==hash_id_value.strip():
                        revision.revision_line_added+=inserted
                        revision.revision_line_deleted+=deleted
                        revision.revision_file_changed+=files
        
        Revision.insert_revision_list(revision_list)
        return branch.branch_total_line

    @staticmethod
    def insert_revision_list(revision_list):
        dal=dbaccess.DBAccess()
        sql=""
        if len(revision_list)>0:
            for revision in revision_list:
                str_parameters="'"+revision.revision_hash_id+"','"+str(revision.revision_project_id)+"','"+str(revision.revision_branch_id)+"','"+revision.revision_author_username+"','"+revision.revision_author_email+"','"+str(revision.revision_date)+"','"+str(revision.revision_line_added)+"','"+str(revision.revision_line_deleted)+"','"+str(revision.revision_file_changed)+"','"+revision.revision_commit_note.replace("'","''")+"'"
                sql+="insert into git_revision(git_revision_hash_id, git_revision_project_id, git_revision_branch_id, git_revision_author_username, git_revision_author_email, git_revision_date, git_revision_line_added, git_revision_line_deleted, git_revision_file_changed, git_revision_commit_note) values (%s);\r\n" % (''.join(str_parameters))
            #print(sql)
            dal.execute_write_sql(sql)
    
    @staticmethod
    def get_revision_list(project_id,branch_id):
        revision_list=[]
        dal=dbaccess.DBAccess()
        str_filter=""
        if str(project_id) and not str(project_id).isspace():
            str_filter=" and git_revision_project_id="+str(project_id)
        if str(branch_id) and not str(branch_id).isspace():
            str_filter+=" and git_revision_branch_id="+str(branch_id)

        sql="""select git_revision_id, git_revision_hash_id, git_revision_project_id, git_revision_branch_id, 
            git_revision_author_username, git_revision_author_email,git_revision_date, git_revision_line_added, 
            git_revision_line_deleted,git_revision_file_changed, git_revision_commit_note
            from git_revision where 1=1 str_filter;"""
        sql=sql.replace("str_filter",str_filter)
        data_list=dal.execute_read_sql(sql) 
        #print(sql)
        for item in data_list:
            revision=Revision()

            revision.revision_hash_id=item[1]
            revision.revision_project_id=item[2]
            revision.revision_branch_id=item[3]
            revision.revision_author_username=item[4]
            revision.revision_author_email=item[5]
            revision.revision_date=item[6]
            revision.revision_line_added=item[7]
            revision.revision_line_deleted=item[8]
            revision.revision_file_changed=item[9]
            revision.revision_commit_note=item[10]
            revision_list.append(revision)
        return revision_list
