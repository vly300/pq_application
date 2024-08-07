CREATE TABLE IF NOT EXISTS Users(
	users_id INTEGER PRIMARY KEY AUTOINCREMENT,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	team_name INTEGER NOT NULL,
	work_email TEXT NOT NULL,
	password TEXT NOT NULL,
	role TEXT NOT NULL CHECK(role IN('admin','user'))
);