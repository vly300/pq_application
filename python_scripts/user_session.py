'''
This script creates the user_session class, and allows for
the tracking of the current user's role, id and team.
Knowing the role is crucial, since if the user is role 'user' or 'admin'
will determine what functionalities they have access to. Knowing
their team and id allows for the application to use these to populate other
fields also.
'''


class user_session:
    def __init__(self):
        self.user_id = None
        self.user_role = None
        self.user_team = None

    def set_user(self, user_id, user_role, user_team):
        self.user_id = user_id
        self.user_role = user_role
        self.user_team = user_team

    def clear_user(self):
        self.user_id = None
        self.user_role = None
        self.user_team = None


current_session = user_session()
