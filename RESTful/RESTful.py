from flask import Flask

from flask import abort, jsonify, make_response, \
				  request, url_for

from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
	if username == 'phoenix':
		return 'hainuer'
	return None

@auth.error_handler
def unauthorized():
	# return make_response(jsonify({'error': 'Unauthorized access'}), 401)
	return make_response(jsonify({'error': 'Unauthorized access'}), 403)

app = Flask(__name__)

# Datas
tasks = [
	{
		'id': 1,
		'title': u'Buy iPad',
		'description': u'iPad Air 2',
		'done': False
	},
	{
		'id': 2,
		'title': u'Learn Openstack',
		'description': u'Need to find a good OpenStack tutorial on the web',
		'done': False
	}
]

def make_public_task(task):
	new_task = {}
	for field in task:
		if field == 'id':
			new_task['uri'] = url_for('get_task', task_id=task['id'], _external=True)
		else:
			new_task[field] = task[field]
	return new_task

@app.route('/')
def index():
	return '<p align="center"><a href="/todo/api/v1.0/tasks">Todo API</a></p>'

@app.route('/todo/api/v1.0/tasks', methods=['GET'])
def get_tasks():
	# return jsonify({'tasks': tasks})
	return jsonify({'tasks': list(map(make_public_task, tasks))})

@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['GET'])
@auth.login_required
def get_task(task_id):
	# filter->list
	task = list(filter(lambda t: t['id'] == int(task_id), tasks))
	if len(task) == 0:
		abort(404)
	return jsonify({'task': task[0]})

@app.route('/todo/api/v1.0/tasks', methods=['POST'])
@auth.login_required
def create_task():
	if not request.json or not 'title' in request.json:
		abort(400)
	task = {
		'id': tasks[-1]['id'] + 1,
		'title': request.json['title'],
		'description': request.json.get('description', ""),
		'done': False
	}
	tasks.append(task)
	return jsonify({'task': task}), 201


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['PUT'])
@auth.login_required
def update_task(task_id):
	task = list(filter(lambda t: t['id'] == task_id, tasks))
	if len(task) == 0:
		abort(404)
	if not request.json:
		abort(400)
	if 'title' in request.json and type(request.json['title']) != unicode:
		abort(400)
	if 'description' in request.json and type(request.json['description']) is not unicode:
		abort(400)
	if 'done' in request.json and type(request.json['done']) is not bool:
		abort(400)
	task[0]['title'] = request.json.get('title', task[0]['title'])
	task[0]['description'] = request.json.get('description', task[0]['description'])
	task[0]['done'] = request.json.get('done', task[0]['done'])
	return jsonify({'task': task[0]})


@app.route('/todo/api/v1.0/tasks/<int:task_id>', methods=['DELETE'])
@auth.login_required
def delete_task(task_id):
	task = filter(lambda t: t['id'] == task_id, tasks)
	if len(task) == 0:
		abort(404)
	tasks.remove(task[0])
	return jsonify({'result': True})

@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not found.'}), 404)

if __name__ == '__main__':
	app.run(debug=True)


