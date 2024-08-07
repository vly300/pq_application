CREATE TABLE IF NOT EXISTS team_members(
    team_id INTEGER,
    users_id INTEGER,
    FOREIGN KEY (team_id) REFERENCES Teams(team_id),
    FOREIGN KEY (users_id) REFERENCES Users(users_id),
    PRIMARY KEY (team_id, users_id)
);

