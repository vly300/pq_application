CREATE TABLE IF NOT EXISTS deleted_questions(
	question_id INTEGER NOT NULL,
	reference_id TEXT NOT NULL,
	FOREIGN KEY (question_id) REFERENCES Questions(question_id)
);