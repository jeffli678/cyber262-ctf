#encoding: utf-8
import hashlib
import os

def make_token(name):
    salt = 'cyber262'
    hash = hashlib.sha1(name + salt).hexdigest()
    return hash[:8]

def delete_submissions():
    os.system('rm ./submissions/*.zip')

team_names = open('team-names.txt').read().splitlines()
team_info = open('team-info.txt', 'w')
team_info.write('#id, current_problem, token, team_name\n')

for name in team_names:
    output = '0, ' +  make_token(name) + ', ' + name + '\n'
    team_info.write(output)
team_info.close()
print('team info created')

res = raw_input('Delete exsisting submissions? ')
if res == 'Y':
    res = raw_input('Are you sure? ')
    if res == 'Y':
        delete_submissions()

