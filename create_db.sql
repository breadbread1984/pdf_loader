#!/usr/bin/psql

create table references (
  ref_id serial primary key,
  url varchar(500),         /*original download url*/
  filename varchar(500),    /*original name of the file*/
  description varchar(500), /*description on the requirement table*/
  object_url varchar(500)   /*url on object storing service*/
);

