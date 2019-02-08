from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import datautility as du
 
app = Flask(__name__)
app_args = du.read_paired_data_file(os.path.dirname(os.path.abspath(__file__))+'/config.txt')
app.secret_key = app_args['secret_key']
db = None

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

# Sets the user and uploads them to the database
def set_user(fn,ln):
    db = get_db()
    query = 'INSERT INTO users (first_name, last_name) VALUES (\'{}\', \'{}\') RETURNING id;'.format(fn,ln)
    return du.db_query(db, query)

# Sets the action types and uploads them to the database
def set_actions():
    
    
    
# Renders the intro page
@app.route("/")
def index():
    return render_template('main.html')

# Uploads the data from the login form to the database
@app.route('/login', methods=['POST'])
def create_session():
    print('we are creating a user')
    uid = set_user(request.form['firstname'], request.form['lastname'])
    print(uid)
   # ualias = set_alias(uid)
    return redirect('/')
    
 
if __name__ == "__main__":
    app.run(debug=True)
    

