SELECT '<info_to_display>' AS ' ';

drop database lctdb;

create database lctdb;
GRANT ALL PRIVILEGES ON lctdb.* to 'lctusr'@'127.0.0.1' identified by 'lctpwd';
use lctdb;

CREATE TABLE user (
	user CHAR(80) NOT NULL,
	name CHAR(80) NOT NULL,
	password VARCHAR(90) NOT NULL,
	mail VARCHAR(320) NOT NULL,
	created TIMESTAMP DEFAULT '0000-00-00 00:00:00',
	updated TIMESTAMP DEFAULT now() ON UPDATE now(),
	PRIMARY KEY (user)) engine = innodb;

CREATE TABLE board (
    boardid INT NOT NULL AUTO_INCREMENT,
	name CHAR(128) NOT NULL,
	user CHAR(80) NOT NULL,
	startdate DATETIME,
	created TIMESTAMP DEFAULT '0000-00-00 00:00:00',
	updated TIMESTAMP DEFAULT now() ON UPDATE now(),
	FOREIGN KEY (user) REFERENCES user (user) ON DELETE CASCADE,
	PRIMARY KEY (boardid)) engine = innodb;

CREATE TABLE topic (
	topicid INT NOT NULL AUTO_INCREMENT,
	boardid INT,
	heading CHAR(128),
	description TEXT,
	user CHAR(80) NOT NULL,
	created TIMESTAMP DEFAULT '0000-00-00 00:00:00',
	updated TIMESTAMP DEFAULT now() ON UPDATE now(),
	FOREIGN KEY (boardid) REFERENCES board (boardid) ON DELETE CASCADE,
	PRIMARY KEY (topicid)) engine = innodb;


CREATE TABLE votes (
	voteid INT NOT NULL AUTO_INCREMENT,
	user CHAR(80) NOT NULL,
	topicid INT,
	FOREIGN KEY (user) REFERENCES user (user),
	FOREIGN KEY (topicid) REFERENCES topic (topicid) ON DELETE CASCADE,
	PRIMARY KEY (voteid)) engine = innodb;

