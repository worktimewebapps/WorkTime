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
	id INT AUTO_INCREMENT,
	username VARCHAR(100) NULL, 
	dayofweek VARCHAR(100) NULL,
   	starttime VARCHAR(100) NULL,
  	endtime VARCHAR(100) NULL,
	primary key (id));


