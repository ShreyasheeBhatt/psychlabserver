from flask import Flask, flash, redirect, render_template, request, session, abort, jsonify
import os
import datautility as du
import psychlab as pb

app = pb.get_app()


def check_login():
    if 'user_id' in session:
        return 1
    else:
        session.clear()
        return 0


def remove_nonpersistent():
    ret = 0
    rm = []
    for k in session:
        if k not in session['persistent']:
            rm.append(k)
            ret = 1

    for k in rm:
        session.pop(k)

    return ret


# Renders the intro page
@app.route("/")
def index():
    if check_login():
        session.clear()
    return redirect('/PS')


def build_perceptual_sensitivity_study():
    study_id = pb.create_study('Perceptual Sensitivity Study', 'perceptual sensitivity assessment',
                               pb.get_application_by_name('ASSISTments', True))
    # print(study_id)

    tsk_login = pb.create_task('PS_login','login for perceptual sensitivity study','login.html')
    tsk_intro = pb.create_task('PS_intro', 'introduction for perceptual sensitivity study', 'introT1P1.html')
    tsk_task1 = pb.create_task('PS_task1', 'first task for perceptual sensitivity study', 'task1.html')
    tsk_transition = pb.create_task('PS_transition', 'task transition for perceptual sensitivity study',
                                    'transitionPage.html')
    tsk_task2 = pb.create_task('PS_task2', 'second task for perceptual sensitivity study', 'task2.html')
    tsk_final = pb.create_task('PS_final', 'the final page of the study', 'thankyou.html')

    pb.create_study_task_association(study_id, tsk_login)
    pb.create_study_task_association(study_id, tsk_intro)
    pb.create_study_task_association(study_id, tsk_task1)
    pb.create_study_task_association(study_id, tsk_transition)
    pb.create_study_task_association(study_id, tsk_task2)
    pb.create_study_task_association(study_id, tsk_final)

    return study_id


def log_action(user_id, task_id, action_type, entity_name=None, entity_value=None, action_time=None):
    if isinstance(action_type, str):
        action_type_id = pb.get_action_type_by_name(action_type, True)['id']
    else:
        action_type_id = action_type
    return pb.create_action(user_id, action_type_id, task_id, '' if entity_name is None else entity_name,
                            '' if entity_value is None else entity_value, action_time)


@app.route('/_log_user_event')
def log_user_event():

    action_type = 'USER EVENT' if 'type' not in request.args else request.args['type']
    entity_name = 'UNKNOWN' if 'name' not in request.args else request.args['name']
    entity_value = 'UNDEFINED' if 'value' not in request.args else request.args['value']

    log_action(session['user_id'], session['tasks'][session['current_task']]['id'], action_type,
               entity_name, entity_value)

    return jsonify([])


@app.route('/_log_event')
def log_event():

    action_type = 'EVENT' if 'type' not in request.args else request.args['type']
    entity_name = 'UNKNOWN' if 'name' not in request.args else request.args['name']
    entity_value = 'UNDEFINED' if 'value' not in request.args else request.args['value']

    log_action(session['user_id'], session['tasks'][session['current_task']]['id'], action_type,
               entity_name, entity_value)

    return jsonify([])


@app.route('/PS')
def perceptual_sensitivity_study():
    study_id = pb.get_study_by_name('Perceptual Sensitivity Study')
    if study_id is None:
        study_id = build_perceptual_sensitivity_study()
    else:
        study_id = study_id['id']

    if not check_login():
        session['user_id'] = pb.create_user('user')

    session['study_url'] = '/PS'
    session['study_id'] = study_id

    session['persistent'] = list(session.keys())

    # get list of tasks
    session['tasks'] = pb.get_tasks_by_study(session['study_id'])
    for t in session['tasks']:
        print(t)

    session['n_tasks'] = len(session['tasks'])
    session['current_task'] = 0

    # print(request.remote_addr)

    log_action(session['user_id'], session['tasks'][session['current_task']]['id'], 'BEGIN_STUDY')

    return render_template(session['tasks'][session['current_task']]['html_template'])


@app.route('/transition', methods=['POST', 'GET'])
def transition_tasks():
    if not check_login():
        return redirect('/')

    # log anything submitted through a form
    for k in request.form:
        log_action(session['user_id'], session['tasks'][session['current_task']]['id'], 'FORM SUBMISSION',
                   k, request.form[k])

    if session['current_task'] == session['n_tasks']-1:
        # print(session['n_tasks'])
        # print(session['current_task'])
        log_action(session['user_id'], session['tasks'][session['current_task']]['id'], 'COMPLETE_STUDY',
                   session['tasks'][session['current_task'] + 1]['name'])
        remove_nonpersistent()
        return redirect(session['study_url'])
    else:
        log_action(session['user_id'], session['tasks'][session['current_task']]['id'], 'TASK_TRANSITION',
                   session['tasks'][session['current_task']+1]['name'])
        session['current_task'] = session['current_task']+1

    return redirect('/task')


@app.route('/task')
def render_task():
    if not check_login():
        return redirect('/')

    return render_template(session['tasks'][session['current_task']]['html_template'])


if __name__ == "__main__":
    app.run(threaded=True, debug=False, host='0.0.0.0', port='5000')


