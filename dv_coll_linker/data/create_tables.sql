CREATE TABLE IF NOT EXISTS collections
( id INTEGER UNIQUE, 
alias TEXT NOT NULL PRIMARY KEY, 
name TEXT);

CREATE TABLE IF NOT EXISTS children
( parent_id INTEGER,
parent_alias TEXT,
child_id INTEGER,
child_alias TEXT,
FOREIGN KEY (parent_alias) REFERENCES collections(alias),
FOREIGN KEY (child_alias) REFERENCES collections(alias),
UNIQUE (parent_id, parent_alias, child_id, child_alias));

CREATE TABLE IF NOT EXISTS studies
( pid TEXT PRIMARY KEY,
dv_alias TEXT,
title TEXT,
created_time TEXT,
updated_time TEXT,
FOREIGN KEY (dv_alias) REFERENCES collections(alias));

CREATE TABLE IF NOT EXISTS links
( pid TEXT,
parent TEXT,
child TEXT,
FOREIGN KEY (pid) REFERENCES studies(pid) ON DELETE CASCADE,
FOREIGN KEY (parent) REFERENCES collections(alias)
FOREIGN KEY (child) REFERENCES collections(alias));

CREATE TABLE IF NOT EXISTS status
( last_check TEXT PRIMARY KEY,
last_count INT);

CREATE TABLE IF NOT EXISTS raw_data
( last_check TEXT,
search_json TEXT,
FOREIGN KEY (last_check) REFERENCES status(last_check));
