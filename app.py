from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500))
    type = db.Column(db.String(50))
    status = db.Column(db.String(10), default="new")


@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/add_task_ajax', methods=['POST'])
def add_task_ajax():
    title = request.form.get('title')
    description = request.form.get('description')
    task_type = request.form.get('type')

    if title and task_type:
        new_task = Task(title=title, description=description, type=task_type)
        db.session.add(new_task)
        db.session.commit()
        return jsonify({'success': True, 'task_id': new_task.id, 'title': new_task.title, 'description': new_task.description, 'type': new_task.type})
    return jsonify({'success': False, 'error': 'Title or type is missing'})

@app.route('/edit/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get(task_id)
    if request.method == 'POST':
        task.title = request.form.get('title')
        task.description = request.form.get('description')
        task.type = request.form.get('type')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit.html', task=task)

@app.route('/mark_task_as_done/<int:task_id>')
def mark_task_as_done(task_id):
    task = Task.query.get(task_id)
    if task:
        task.status = "done"
        db.session.commit()
        return redirect(url_for('index'))
    return jsonify({'success': False, 'error': 'Task not found'})

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for('index'))

@app.template_filter('enumerate')
def jinja2_enumerate(iterable, start=1):
    return enumerate(iterable, start)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
