#encoding: utf-8
import hashlib
import os

def make_token(name):
    salt = 'cyber262'
    hash = hashlib.sha1(name + salt).hexdigest()
    return hash[:8]

def delete_submissions():
    os.system('rm ./submissions/*.zip')

team_names = []
if os.path.exists('team-names-1.txt'):
    team_names = open('team-names-1.txt').read().splitlines()
    team_names = [name.strip() for name in team_names]

if os.path.exists('team-names-2.txt'):
    team_names.extend( open('team-names-2.txt').read().splitlines())
    team_names = [name.strip() for name in team_names]

if not len(team_names):
    print('no teams found')

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

