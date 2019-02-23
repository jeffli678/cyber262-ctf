import os
import itertools
import json
import datetime
from bottle import route, run, template, static_file, post, request, auth_basic
import logging
import shutil

teams = {}
max_problem = 0

def read_team_info(info_path = 'team-info.txt'):
    f = open(info_path).read().splitlines()
    for line in f:
        if line.startswith('#'):
            continue
        solved_problem, token, team_name = line.split(',')
        solved_problem = int(solved_problem)
        token = token.strip()
        team_name = team_name.strip()
        teams[token] = [solved_problem, team_name]

def print_team_info():
    for team in teams:
        print(team, teams[team])

def check_progress(token):
    
    team_name = None
    solved_problem = None

    if not token in teams:
        output = 'no such team'
    else:
        solved_problem = teams[token][0]
        team_name = teams[token][1]
        if solved_problem >= max_problem:
            output = 'Congrats %s! You have solved all problems' % team_name
        else:
            output = 'Hello %s, You have solved %d problems, and you should be working on the No. %d problem. ' \
                            % (team_name, solved_problem, solved_problem + 1)

    print(output)
    return (output, team_name, solved_problem)

def check(user, pw):
    # Check user/pw here and return True/False
    return user == 'cyber262' and pw == 'cyber262-admin'

def init_system():
    global max_problem
    max_problem = count_challenges()
    print('there are %d challenges' % max_problem)
    read_team_info()
    print_team_info()

@route('')
@route('/')
@route('/index.html')
def show_index():
    return static_file('index.html', root = './html')

@post('/status')
def check_status():
    token = request.forms.get('token')
    output, _, _ = check_progress(token)
    return output

@route('/admin')
@auth_basic(check)
def show_admin():
    return static_file('admin.html', root = './html') 

@route('/reload-system')
@auth_basic(check)
def reload_system():
    init_system()
    return 'system reloaded'


@route('/collect-submissions')
@auth_basic(check)
def collect_submissions():

    curr_time = datetime.datetime.now()
    curr_time_str = curr_time.strftime('%Y%m%d-%H-%M-%S')

    root_path = './snapshots'
    zip_name = 'submissions-snapshot-%s' % curr_time_str
    zip_path = os.path.join(root_path, zip_name)
    
    shutil.make_archive(zip_path, 'zip', 'submissions')

    zip_name_with_suffix = zip_name + '.zip'

    return static_file(zip_name_with_suffix, root = root_path, \
                        download = zip_name_with_suffix)

@post('/download')
def down_latest():
    token = request.forms.get('token')
    if not token in teams:
        output = 'no such team'
        return output

    output, team_name, solved_problem = check_progress(token)
    if solved_problem >= max_problem:
        output = 'Congrats %s! You have solved all problems!' % team_name
        return output

    file_name = 'c%d.zip' % (solved_problem + 1)
    root_path = './challenges'
    if not os.path.exists(os.path.join(root_path, file_name)):
        output = 'File %s does not exist. This is a server bug. Please contact your TA. Thanks!' % file_name
        return output

    return static_file(file_name, root = root_path, download = file_name)
        

@post('/upload')
def upload():
    token = request.forms.get('token')
    if not token in teams:
        output = 'no such team'
        return output

    output, team_name, solved_problem = check_progress(token)
    if solved_problem >= max_problem:
        output = 'Hi %s, you have solved all problems and can no longer submit' % team_name
        return output
    
    upload = request.POST['upload']
    _, ext = os.path.splitext(upload.filename)
    if not ext.lower() == '.zip':
        output = 'You can only submit zip files. Please create a zip archive and try again.'
        return output

    idx = int(request.forms.get('idx'))
    if idx != solved_problem + 1:
        output = 'You wish to submit problem %d. But I belive you should be working on problem %d. Please check again.' % (idx, solved_problem + 1)
        return output

    curr_time = datetime.datetime.now()
    curr_time_str = curr_time.strftime('%Y%m%d-%H-%M-%S')

    file_save_name = '%s-%d-%s.zip' % (token, idx, curr_time_str)
    root_path = './submissions'
    full_save_path = os.path.join(root_path, file_save_name)
    print(full_save_path)

    if os.path.exists(full_save_path):
        output = 'File %s already exists. This is a server bug. Most likely your submission fails. Please contact your TA. Thanks!' % file_save_name
        return output

    # actually save the file
    try:
        upload.save(full_save_path)
    except:
        output = 'Fail to save your uploaded file. This is a server bug. Most likely your submission fails. Please contact your TA. Thanks!'
        return output

    # update the team info
    teams[token][0] += 1
    try:
        update_team_info()
    except:
        output = 'Fail to update your information. This is a server bug. Most likely your submission fails. Please contact your TA. Thanks!'
        return output

    output = 'Congrats! Your submission is uploaded. Please proceed to the next problem.'
    return output

def token_from_name(team_name):
    for token in teams:
        if teams[token][1] == team_name:
            return token
    return ''

def sort_and_print(section_teams, section):
    output = 'Section %d</br>' % section
    sorted_teams = sorted(section_teams, key = section_teams.get, reverse = True)
    for token in sorted_teams:
        output += (token + '\t' + str(section_teams[token]) + '</br>' )
    output += '<br>'
    return output

@route('/ctf-status')
@auth_basic(check)
def ctf_status():

    output = ''
    for section in [1, 2]:
        section_teams = {}
        if not os.path.exists(('team-names-%d.txt' % section)):
            continue

        team_names = open('team-names-%d.txt' % section).read().splitlines()
        for team_name in team_names:
            team_name = team_name.strip()
            if team_name.startswith('test_team'):
                continue
            token = token_from_name(team_name)
            if token == '':
                print('%s not found' % team_name)
                continue
            section_teams[token] = teams[token][0]

        output += sort_and_print(section_teams, section)
    
    return output

def update_team_info():

    shutil.copyfile('team-info.txt', 'team-info-backup.txt')
    
    f = open('team-info.txt', 'w')
    for team in teams:
        output = str(teams[team][0]) + ', ' + team + ', ' + teams[team][1] + '\n'
        f.write(output)

    f.close()
    os.remove('team-info-backup.txt')


def count_challenges():
    count = 0
    for file in os.listdir('./challenges'):
        if file.endswith('.zip'):
            count += 1
    return count

def main():
    init_system()
    run(host='localhost', port = 26200)


if __name__ == '__main__':
    main()
