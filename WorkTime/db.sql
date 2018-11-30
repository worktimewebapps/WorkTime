drop database if exists work;
create database work;
create table work.tbl_user( 
	id INT AUTO_INCREMENT, 
	name VARCHAR(100) NULL, 
	username VARCHAR(100) NULL, 
	password VARCHAR(100) NULL, 
	admin boolean,
	primary key (id));
		     
create table work.tbl_times( 
	username VARCHAR(100) NULL, 
	dayofweek VARCHAR(100) NULL,
   	starttime VARCHAR(100) NULL,
  	endtime VARCHAR(100) NULL);

insert into work.tbl_user(name, username, password, admin) VALUES
	('admin', 'admin', sha2('admin', 256), true),
	('Matthew Silversmith', 'msilvers', sha2('123456', 256), false);

insert into work.tbl_times(username, dayofweek, starttime, endtime) VALUES
	('admin', 'Monday', '9', '5');
