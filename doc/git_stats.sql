-- Table: git_project

-- DROP TABLE git_project;

CREATE TABLE git_project
(
  git_project_id serial NOT NULL,
  git_project_name character varying,
  git_project_path character varying,
  git_project_server_ip character varying,
  git_project_owner_username character(30),
  git_project_owner_name character varying,
  git_project_owner_email character(50),
  git_project_create_date timestamp without time zone,
  git_project_insert_date timestamp without time zone,
  git_project_repo_url character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_project
  OWNER TO postgres;

-- Table: git_branch

-- DROP TABLE git_branch;

CREATE TABLE git_branch
(
  git_branch_id serial NOT NULL,
  git_branch_name character varying,
  git_branch_owner character(20),
  git_branch_start_date date,
  git_branch_file_counts integer,
  git_branch_total_size integer,
  git_branch_total_line integer,
  git_branch_contributor_counts integer,
  git_branch_last_commit_id character(40),
  git_branch_project_id integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_branch
  OWNER TO postgres;

-- Table: git_push

-- DROP TABLE git_push;

CREATE TABLE git_push
(
  git_push_id serial NOT NULL,
  git_push_author_name character(30),
  git_push_author_username character(30),
  git_push_author_email character varying,
  git_push_date timestamp without time zone,
  git_push_revision_before character(41),
  git_push_revision_after character(40),
  git_push_project_id integer,
  git_push_type character(10),
  git_push_source character(6)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_push
  OWNER TO postgres;

-- Table: git_file

-- DROP TABLE git_file;

CREATE TABLE git_file
(
  git_file_id serial NOT NULL,
  git_file_name character varying,
  git_file_path character varying,
  git_file_creator character(20),
  git_file_create_date timestamp without time zone,
  git_file_project_id integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_file
  OWNER TO postgres;
-- Table: git_revision

-- DROP TABLE git_revision;

CREATE TABLE git_revision
(
  git_revision_id serial NOT NULL,
  git_revision_hash_id character(40),
  git_revision_project_id integer,
  git_revision_branch_id integer,
  git_revision_author_username character(50),
  git_revision_author_email character(50),
  git_revision_date timestamp without time zone,
  git_revision_line_added integer,
  git_revision_line_deleted integer,
  git_revision_file_changed integer,
  git_revision_commit_note character varying
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_revision
  OWNER TO postgres;
-- Table: git_revision_file_link

-- DROP TABLE git_revision_file_link;

CREATE TABLE git_revision_file_link
(
  git_link_id serial NOT NULL,
  git_link_revision_hash_id character(40),
  git_link_file_id integer,
  git_link_file_line_added integer,
  git_link_file_line_deleted integer,
  git_link_project_id integer
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_revision_file_link
  OWNER TO postgres;
-- Table: git_server

-- DROP TABLE git_server;

CREATE TABLE git_server
(
  git_server_id serial NOT NULL,
  git_server_name character(20),
  git_server_ip character varying,
  git_server_type character(6),
  git_server_db_type character(10),
  git_server_db_name character varying,
  git_server_db_username character varying,
  git_server_db_password character varying,
  git_server_db_port character(4),
  git_server_create_date timestamp without time zone,
  git_server_db_ip character varying,
  git_server_app_port character(5)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_server
  OWNER TO postgres;
-- Table: git_tag

-- DROP TABLE git_tag;

CREATE TABLE git_tag
(
  git_tag_id serial NOT NULL,
  git_tag_name character(50),
  git_tag_hash_id character(40),
  git_tag_project_id integer,
  git_tag_branch_id integer,
  git_tag_author_username character(20),
  git_tag_create_date timestamp without time zone
)
WITH (
  OIDS=FALSE
);
ALTER TABLE git_tag
  OWNER TO postgres;
