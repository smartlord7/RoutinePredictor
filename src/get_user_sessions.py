import os
import pandas as pd
from src.db_setup import db_setup


"""
Used to get all the sessions from all users, and store them in a file.
Only adds sessions that we have data for!
"""

PATH_DATA = '../data/'
EXTENSION_TEXT = '.txt'
PATH_USER_SESSIONS = PATH_DATA + 'user_sessions_number' + EXTENSION_TEXT

# Database connection configurations
db_config, db_uri, conn = db_setup()

session_file_name = 'user_sessions_number.txt'
cursor = conn.cursor()

sessions = pd.read_sql_query('SELECT * FROM session', db_uri)

# Dict of user:[session list]
users = sessions['user_id'].unique()  # All user ids
user_session_dict = {}

if not os.path.exists(session_file_name):
    # File does not exist, create it

    session_file = open(session_file_name, 'w')

    print(f'There are {len(users)} users.')

    # Get user that has the most session_ids locations
    for index, user in enumerate(users):
        print(f'{index} - User {user}')

        user_sessions = sessions.loc[sessions['user_id'] == user]['session_id'].unique()

        # Create SQL string to get all sessions location for a user, to avoid multiple queries
        sql_string = 'SELECT * FROM gslocation WHERE '
        for i, session_id in enumerate(user_sessions):
            if i == len(user_sessions) - 1:
                sql_string += f'session_id = {session_id}'
            else:
                sql_string += f'session_id = {session_id} OR '

        # All sessions with all locations for this user
        all_session_locations = pd.read_sql_query(sql_string, db_uri)

        # Filter each session
        for session_id in user_sessions:
            # Filter the data for this specific session
            session_locations = all_session_locations.loc[all_session_locations['session_id'] == session_id]

            # Check if we have the location data of this session
            if not session_locations.empty:
                # Check if list exists, and create it if needed
                if user_session_dict.get(user) is None:
                    user_session_dict[user] = [session_locations['session_id'].values[0]]
                else:
                    user_session_dict[user].append(session_locations['session_id'].values[0])

        # Write to file if this user has location for any session
        if user_session_dict.get(user) is not None:
            # Store list in file
            l = user_session_dict.get(user)
            session_file.write(f'{user},')
            for i in range(len(l)):
                if i == (len(l) - 1):
                    session_file.write(f'{l[i]}\n')
                else:
                    session_file.write(f'{l[i]},')

else:
    # File exists, read it
    session_file = open(session_file_name, 'r')
    for line in session_file.readlines():
        split = line.strip().split(',')
        user = int(split[0])
        user_sessions = list(map(int, split[1:]))
        user_session_dict[user] = user_sessions

session_file.close()

users = user_session_dict

"""
for user, s in users.items():
    print(f'User {user} has {len(s)} sessions.')
"""

# Get user with most amount of sessions
ordered_users = sorted(users, key=lambda x: len(users.get(x)), reverse=True)[0:5]

print('The 5 users with the most sessions are: ')
for user in ordered_users:
    print(f'User {user} with {len(users[user])} sessions.')
