CREATE TABLE IF NOT EXISTS Questions(
	question_id INTEGER PRIMARY KEY AUTOINCREMENT,
	reference_id TEXT NOT NULL,
	date_submitted TEXT NOT NULL,
	question TEXT NOT NULL,
	answer TEXT,
	allocated_status TEXT NOT NULL DEFAULT "unallocated",
	team_id INTEGER,
	advised_action TEXT,
	additional_comments TEXT,
	phs_relevant TEXT NOT NULL DEFAULT "TBD",
	is_updated INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY (team_id) REFERENCES Teams(team_id)
);