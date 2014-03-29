-- vim:noet:sw=8

/*
 * Copyright (C) 2010 Jardel Weyrich
 *
 * This file is part of livemgr-webui.
 *
 * livemgr-webui is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * livemgr-webui is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with livemgr-webui. If not, see <http://www.gnu.org/licenses/>.
 *
 * Authors:
 *   Jardel Weyrich <jweyrich@gmail.com>
 */

/*
CREATE DATABASE livemgr;
CREATE USER 'livemgr'@'localhost' IDENTIFIED BY 'livemgr';
GRANT INDEX,ALTER,CREATE,SELECT,INSERT,UPDATE,DELETE ON livemgr.* TO 'livemgr'@'localhost';
*/

CREATE TABLE IF NOT EXISTS acls (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	localim VARCHAR(128) NOT NULL,
	remoteim VARCHAR(128) NOT NULL,
	action TINYINT UNSIGNED NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_acls (localim, remoteim)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS badwords (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	badword VARCHAR(128) NOT NULL,
	isregex TINYINT UNSIGNED NOT NULL DEFAULT 0,
	isenabled TINYINT UNSIGNED NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_badwords (badword)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS settings (
	id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	name VARCHAR(64) NOT NULL,
	value VARCHAR(255) NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_settings (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO settings (name, value) VALUES ('allow_self_reg', '1');
INSERT IGNORE INTO settings (name, value) VALUES ('min_protocol_version', '8');
INSERT IGNORE INTO settings (name, value) VALUES ('max_protocol_version', '18');
INSERT IGNORE INTO settings (name, value) VALUES ('filtered_msg', 'Ouch...');
INSERT IGNORE INTO settings (name, value) VALUES ('default_warning', 'Big Brother is watching you');

CREATE TABLE IF NOT EXISTS usergroups (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	groupname VARCHAR(64) NOT NULL,
	isactive TINYINT UNSIGNED NOT NULL,
	isbuiltin TINYINT UNSIGNED NOT NULL,
	description VARCHAR(512) NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_usergroups (groupname)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO usergroups (groupname, isactive, isbuiltin) VALUES ('guest', 1, 1);

CREATE TABLE IF NOT EXISTS rules (
	id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
	rulename VARCHAR(64) NOT NULL,
	rulevalue VARCHAR(255) NULL,
	description VARCHAR(512) NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_rules (rulename)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT IGNORE INTO rules (id, rulename, description) VALUES (1, 'Conversation history', 'Save instant message conversations');
INSERT IGNORE INTO rules (id, rulename, description) VALUES (2, 'Disclaimer', 'Notify the user that the messages are being monitored');
INSERT IGNORE INTO rules (id, rulename, description) VALUES (3, 'Block file transfers', 'Automatically reject file transfers');
INSERT IGNORE INTO rules (id, rulename) VALUES (4, 'Block unofficial messages');
INSERT IGNORE INTO rules (id, rulename) VALUES (5, 'Block webcam');
INSERT IGNORE INTO rules (id, rulename) VALUES (6, 'Block Remote Assistance');
INSERT IGNORE INTO rules (id, rulename) VALUES (7, 'Block application sharing');
INSERT IGNORE INTO rules (id, rulename) VALUES (8, 'Block custom emoticons');
INSERT IGNORE INTO rules (id, rulename) VALUES (9, 'Block handwriting');
INSERT IGNORE INTO rules (id, rulename) VALUES (10, 'Block nudges');
INSERT IGNORE INTO rules (id, rulename) VALUES (11, 'Block winks');
INSERT IGNORE INTO rules (id, rulename) VALUES (12, 'Block voice clips');
INSERT IGNORE INTO rules (id, rulename) VALUES (13, 'Block encrypted messages');
INSERT IGNORE INTO rules (id, rulename, description) VALUES (14, 'Badword filtering', 'Filter messages based on defined badwords');
INSERT IGNORE INTO rules (id, rulename) VALUES (15, 'Block MSN Games');
INSERT IGNORE INTO rules (id, rulename) VALUES (16, 'Block photo sharing');

CREATE TABLE IF NOT EXISTS grouprules (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	rule_id SMALLINT UNSIGNED NOT NULL,
	group_id INT UNSIGNED NOT NULL,
	PRIMARY KEY (id),
	UNIQUE KEY uk_grouprules (rule_id, group_id),
	FOREIGN KEY (rule_id) REFERENCES rules(id),
	FOREIGN KEY (group_id) REFERENCES usergroups(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS users (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	group_id INT UNSIGNED NOT NULL DEFAULT 1,
	username VARCHAR(128) NOT NULL,
	displayname VARCHAR(130) NOT NULL DEFAULT '',
	psm VARCHAR(130) NOT NULL DEFAULT '',
	status ENUM('NLN', 'BSY', 'IDL', 'AWY', 'BRB', 'PHN', 'LUN', 'HDN', 'FLN') NOT NULL DEFAULT 'FLN',
	lastlogin DATETIME NULL,
	isenabled TINYINT UNSIGNED NOT NULL DEFAULT 1,
	PRIMARY KEY (id),
	UNIQUE KEY uk_users (username),
	FOREIGN KEY (group_id) REFERENCES usergroups(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS buddies (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	user_id INT UNSIGNED NOT NULL,
	username VARCHAR(128) NOT NULL,
	displayname VARCHAR(130) NOT NULL DEFAULT '',
	psm VARCHAR(130) NOT NULL DEFAULT '',
	status ENUM('NLN', 'BSY', 'IDL', 'AWY', 'BRB', 'PHN', 'LUN', 'HDN', 'FLN') NOT NULL DEFAULT 'FLN',
	isblocked TINYINT UNSIGNED NOT NULL DEFAULT 0,
	PRIMARY KEY (id),
	UNIQUE KEY uk_buddies (user_id, username),
	FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS conversations (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	user_id INT UNSIGNED NOT NULL,
	timestamp DATETIME NOT NULL,
	status TINYINT UNSIGNED NOT NULL DEFAULT 1,
	PRIMARY KEY (id),
	FOREIGN KEY (user_id) REFERENCES users(id),
	KEY ix_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS messages (
	id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
	timestamp DATETIME NOT NULL,
	conversation_id INT UNSIGNED NOT NULL,
	clientip INT UNSIGNED NOT NULL,
	inbound TINYINT UNSIGNED NOT NULL,
	type TINYINT UNSIGNED NOT NULL,
	localim VARCHAR(128) NOT NULL,
	remoteim VARCHAR(128) NOT NULL,
	filtered TINYINT UNSIGNED NOT NULL,
	content VARCHAR(2000) NOT NULL,
	PRIMARY KEY (id),
	KEY ix_timestamp (timestamp),
	KEY ix_localim (localim),
	KEY ix_remoteim (remoteim),
	KEY ix_filtered (filtered),
	FULLTEXT KEY ft_messages (content)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

/*
CREATE TABLE IF NOT EXISTS auth_user_profile (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	auth_user_id INT UNSIGNED NOT NULL,
	language varchar(5) DEFAULT 'en',
	debug TINYINT UNSIGNED DEFAULT 0,
	per_page_acls TINYINT UNSIGNED DEFAULT 10,
	per_page_users TINYINT UNSIGNED DEFAULT 10,
	per_page_usergroups TINYINT UNSIGNED DEFAULT 10,
	per_page_conversations TINYINT UNSIGNED DEFAULT 10,
	per_page_badwords TINYINT UNSIGNED DEFAULT 10,
	per_page_buddies TINYINT UNSIGNED DEFAULT 10,
	PRIMARY KEY (id),
	UNIQUE KEY uk_auth_user_profile (auth_user_id),
	FOREIGN KEY (auth_user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
*/

DROP FUNCTION IF EXISTS fn_check_version;
DELIMITER //

CREATE FUNCTION fn_check_version(ver_param INT) RETURNS INT
BEGIN
DECLARE min_version, max_version INT;
SELECT value INTO min_version FROM settings WHERE name='min_protocol_version';
SELECT value INTO max_version FROM settings WHERE name='max_protocol_version';

IF ver_param < min_version OR ver_param > max_version THEN
       RETURN 1;
END IF;

RETURN 0;
END //

DELIMITER ;

DROP PROCEDURE IF EXISTS sp_add_user;
DELIMITER //

CREATE PROCEDURE sp_add_user(IN p_username VARCHAR(128))
BEGIN
DECLARE tmp INT DEFAULT 0;

SELECT value INTO tmp FROM settings WHERE name='allow_self_reg';
IF tmp = 1 THEN
       INSERT IGNORE INTO users(username) VALUES (p_username);
END IF;

END //

DELIMITER ;

/*
CREATE VIEW view_messages AS
SELECT
	m.id AS id,
	m.conversation_id AS conversation_id,
	m.timestamp AS timestamp,
	m.inbound as inbound,
	u.id AS localuser_id,
	m.localim AS localim,
	m.remoteim AS remoteim,
	m.clientip AS clientip,
	m.filtered as filtered,
	m.content AS content,
	c.status AS is_active
FROM messages as m
LEFT OUTER JOIN conversations as c ON c.id = m.conversation_id
LEFT OUTER JOIN users as u ON u.username = m.localim;
*/
