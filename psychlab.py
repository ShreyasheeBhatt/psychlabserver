from flask import Flask
import datautility as du
import os

app = Flask(__name__)
app_args = du.read_paired_data_file(os.path.dirname(os.path.abspath(__file__))+'/config.txt')
app.secret_key = app_args['secret_key']
db = None


def get_app():
    global app
    return app


# Connects to the database
def connect_db():
    db = du.db_connect(app_args['db_name'], app_args['username'], app_args['password'],
                       host=app_args['host'], port=app_args['port'])
    return db


# Gets the database being used
def get_db():
    global db
    if db is None:
        db = connect_db()
    return db


def get_by_id(table, id):
    db = get_db()
    query = 'SELECT * FROM {} WHERE id = {};'.format(table, id)
    row, col = du.db_query(db, query, return_column_names=True)

    if len(row) == 0:
        return None

    res = dict()
    for c in range(len(col)):
        res[col[c]] = row[0][c]

    return res


def get_first_by_column(table, column, value):
    db = get_db()
    if isinstance(value, str):
        value = '\'{}\''.format(value)
    query = 'SELECT * FROM {} WHERE {} = {};'.format(table, column, value)
    row, col = du.db_query(db, query, return_column_names=True)

    if len(row) == 0:
        return None

    res = dict()
    for c in range(len(col)):
        res[col[c]] = row[0][c]

    return res


def get_all_by_column(table, column, value):
    db = get_db()
    if isinstance(value, str):
        value = '\'{}\''.format(value)
    query = 'SELECT * FROM {} WHERE {} = {};'.format(table, column, value)
    row, col = du.db_query(db, query, return_column_names=True)

    if len(row) == 0:
        return None

    res = dict()
    for c in range(len(col)):
        res[col[c]] = []
        for r in range(len(row)):
            res[col[c]].append(row[r][c])

    return res


# Sets the user and uploads them to the database
def create_user(fn, ln=None):
    db = get_db()
    query = 'INSERT INTO users (first_name, last_name) ' \
            'VALUES (\'{}\', {}) RETURNING id;'.format(fn,'NULL' if ln is None else '\'{}\''.format(ln))
    return du.db_query(db, query)[0][0]


def get_user(id):
    return get_by_id('users',id)


def create_action_type(name, description=None):
    db = get_db()
    query = 'INSERT INTO action_types (name, description) ' \
            'VALUES (\'{}\',{}) RETURNING id;'.format(name,
                                                      'NULL' if description is None else '\'{}\''.format(description))
    return du.db_query(db, query)[0][0]


def get_action_type(id):
    return get_by_id('action_types', id)


def get_action_type_by_name(name, create=False):
    if create:
        ret = get_first_by_column('action_types', 'name', name)
        if ret is None:
            return get_by_id('action_types',create_action_type(name))
        return ret
    return get_first_by_column('action_types', 'name', name)


def create_action(user_id, action_type_id, task_id, entity_name, entity_value, action_time=None):
    db = get_db()
    query = 'INSERT INTO actions (user_id, action_type_id, action_time, task_id, entity_name, entity_value) ' \
            'VALUES ({}, {}, {}, {}, \'{}\', \'{}\') ' \
            'RETURNING id;'.format(user_id, action_type_id,
                                   'now()' if action_time is None else 'timestamp with time zone \'{}\''.format(
                                       action_time),
                                   task_id, entity_name, entity_value)
    return du.db_query(db, query)[0][0]


def get_action(id):
    return get_by_id('actions', id)


def create_application(name):
    db = get_db()
    query = 'INSERT INTO applications (name) VALUES (\'{}\') RETURNING id;'.format(name)
    return du.db_query(db, query)[0][0]


def get_application(id):
    return get_by_id('applications', id)


def get_application_by_name(name, create=False):
    if create:
        ret = get_first_by_column('applications', 'name', name)
        if ret is None:
            return create_application(name)
        return ret
    return get_first_by_column('applications', 'name', name)


def create_study(name, description=None, application_id=None):
    db = get_db()
    query = 'INSERT INTO studies (name, description, application_id) ' \
            'VALUES (\'{}\',{},{}) ' \
            'RETURNING id;'.format(name, 'NULL' if description is None else '\'{}\''.format(description),
                                   'NULL' if application_id is None else application_id)
    return du.db_query(db, query)[0][0]


def get_study(id):
    return get_by_id('studies', id)


def get_study_by_name(name):
    return get_first_by_column('studies', 'name', name)


def create_task(name, description=None, html_template=None):
    db = get_db()
    query = 'INSERT INTO tasks (name, description, html_template) ' \
            'VALUES (\'{}\',{},{}) ' \
            'RETURNING id;'.format(name, 'NULL' if description is None else '\'{}\''.format(description),
                                   'NULL' if html_template is None else '\'{}\''.format(html_template))
    return du.db_query(db, query)[0][0]


def get_task(id):
    return get_by_id('tasks', id)


def get_task_by_name(name):
    return get_first_by_column('tasks', 'name', name)


def create_study_task_association(study_id, task_id):
    db = get_db()
    query = 'INSERT INTO study_task_associations (study_id, task_id) VALUES ({},{}) RETURNING id;'.format(study_id,
                                                                                                          task_id)
    return du.db_query(db, query)[0][0]


def get_tasks_by_study(study_id):
    res = get_all_by_column('study_task_associations','study_id',study_id)
    if res is None:
        return None

    tasks = []
    for i in res['task_id']:
        tasks.append(get_task(i))

    return tasks


def create_user_alias(user_id, application_id, alias):
    db = get_db()
    query = 'INSERT INTO user_aliases (user_id, application_id, alias) ' \
            'VALUES ({}, {}, \'{}\') RETURNING id;'.format(user_id, application_id, alias)
    return du.db_query(db, query)[0][0]


def get_user_alias(user_id, application_id):
    res = get_first_by_column('user_aliases', '(user_id, application_id)', '({},{})'.format(user_id, application_id))
    return None if res is None else res['alias']


def get_user_alias_by_id(id):
    return get_by_id('user_aliases', id)
