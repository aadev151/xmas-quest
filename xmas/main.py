import flask
import os
import random
import pyqrcode
import png
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/new')
def new_room():
    last_number_file = open('last_number.txt', 'r')
    last_number = int(last_number_file.read())
    last_number_file.close()

    number = str(last_number + 1)

    return flask.render_template('new_room.html', number=number)


@app.route('/new/processing...', methods=["POST"])
def creating_new_room():
    last_number_file = open('last_number.txt', 'r')
    last_number = int(last_number_file.read())
    last_number_file.close()

    number = str(last_number + 1)

    last_number_file = open('last_number.txt', 'w')
    last_number_file.write(number)
    last_number_file.close()

    os.mkdir('rooms/' + number)
    os.mkdir('rooms/' + number + '/questions')
    os.mkdir('rooms/' + number + '/users')
    open('rooms/' + number + '/users.txt', 'w').close()

    url = 'https://xmas.aadev151.repl.co/join/' + number
    qr = pyqrcode.create(url)
    qr.png('static/' + number + '.png', scale=6)

    questions = []
    if flask.request.form.get('sayTo2020'):
        questions.append('What would you say to 2020?')
    if flask.request.form.get('funniestStory'):
        questions.append('Tell us your funniest story')

    random.shuffle(questions)

    for q in range(len(questions)):
        os.mkdir('rooms/' + number + '/questions/' + str(q + 1))
        open('rooms/' + number + '/questions/' + str(q + 1) + '/answers.txt', 'w').close()
        index_file = open('rooms/' + number + '/questions/' + str(q + 1) + '/index.txt', 'w')
        index_file.write(questions[q])
        index_file.close()

    return flask.redirect('/room/' + number + '/admin')


@app.route('/join')
def join_room():
    return flask.render_template('join_room.html')


@app.route('/join/processing...', methods=["POST"])
def joining_room():
    number = flask.request.form['number']
    return flask.redirect('/join/' + number)


@app.route('/join/<room>')
def jcr(room):
    return flask.redirect('/join/' + room + '/')


@app.route('/join/<room>/')
def join_certain_room(room):
    return flask.render_template('join_certain_room.html', room=room)


@app.route('/join/<room>/processing...', methods=["POST"])
def joining_certain_room(room):
    name = flask.request.form['name']

    # TODO: проверка имени

    users_file = open('rooms/' + room + '/users.txt', 'a+')
    users_file.write(name + '\n')

    return flask.redirect('/room/' + room + '/' + name)


@app.route('/room/<room>/admin', methods=["POST"])
def admin(room):
    return flask.redirect('/room/' + room + '/admin/')


@app.route('/room/<room>/admin/')
def room_admin(room):
    users = []
    users_file = open('rooms/' + room + '/users.txt', 'r')
    for line in users_file:
        users.append(line[:-1])
    users_file.close()

    url = 'https://xmas.aadev151.repl.co/join/' + room

    return flask.render_template('admin.html', room=room, users=users, url=url)


@app.route('/room/<room>/admin/question/<question>', methods=["GET", "POST"])
def cqa(room, question):
    return flask.redirect('/room/' + room + '/admin/question/' + question + '/')


@app.route('/room/<room>/admin/question/<question>/')
def certain_question_admin(room, question):

    if question == '1':
        users = []
        users_file = open('rooms/' + room + '/users.txt', 'r')
        for line in users_file:
            users.append(line[:-1])
        users_file.close()

        for user in users:
            user_file = open('rooms/' + room + '/users/' + user + '.txt', 'w')
            user_file.write('0')
            user_file.close()

    if not os.path.isdir('rooms/' + room + '/questions/' + question):
        medal_img = Image.open('static/medal.png')
        font = ImageFont.truetype('font.ttf', 70)
        winner_name = ''

        users = []
        users_file = open('rooms/' + room + '/users.txt', 'r')
        for line in users_file:
            users.append(line[:-1])
        users_file.close()

        maximum = 0

        for user in users:
            user_file = open('rooms/' + room + '/users/' + user + '.txt', 'r')
            current = int(user_file.read())
            user_file.close()

            if current > maximum:
                maximum = current
                winner_name = user

        img_editable = ImageDraw.Draw(medal_img)

        img_editable.text((110, 207), winner_name, (0, 0, 0), font=font)

        filename = 'medal' + room + '.png'

        medal_img.save('static/' + filename)

        winner_file = open('rooms/' + room + '/winner.txt', 'w')
        winner_file.write(winner_name)
        winner_file.close()

        return flask.render_template('results.html', room=room, img=flask.url_for('static', filename=filename), winner=winner_name)

    index_file = open('rooms/' + room + '/questions/' + question + '/index.txt', 'r')
    question_index = index_file.read()
    index_file.close()

    answers_file = open('rooms/' + room + '/questions/' + question + '/answers.txt')
    answers = []
    for line in answers_file:
        answers.append(line[:-1].split('|'))
    answers_file.close()

    return flask.render_template('admin_room.html', question=question, index=question_index, answers=answers)


@app.route('/room/<room>/admin/question/<question>/processing...', methods=["POST"])
def best_answer(room, question):
    best_user = flask.request.form['best']

    best_user_score = open('rooms/' + room + '/users/' + best_user + '.txt', 'r')
    cur_score = best_user_score.read()
    best_user_score.close()

    best_user_score = open('rooms/' + room + '/users/' + best_user + '.txt', 'w')
    best_user_score.write(str(int(cur_score) + 1))
    best_user_score.close()

    return flask.redirect('/room/' + room + '/admin/question/' + str(int(question) + 1))


@app.route('/room/<room>/<name>')
def cuser(room, name):
    return flask.redirect('/room/' + room + '/' + name + '/')


@app.route('/room/<room>/<name>/')
def certain_user(room, name):
    return flask.render_template('room.html', room=room, name=name)


@app.route('/room/<room>/<name>/question/<question>', methods=["GET", "POST"])
def cq(room, name, question):
    return flask.redirect('/room/' + room + '/' + name + '/question/' + question + '/')


@app.route('/room/<room>/<name>/question/<question>/')
def certain_question(room, name, question):
    index_file = open('rooms/' + room + '/questions/' + question + '/index.txt', 'r')
    question_index = index_file.read()
    index_file.close()

    if question_index == 'What would you say to 2020?':
        return flask.render_template('sayTo2020.html', name=name, question=question)

    if question_index == 'Tell us your funniest story':
        return flask.render_template('funniestStory.html', question=question)


@app.route('/room/<room>/<name>/question/<question>/waiting...')
def waiting_for_others(room, name, question):
    return flask.render_template('waiting.html')


@app.route('/room/<room>/<name>/question/<question>/next', methods=["GET", "POST"])
def redirecting(room, name, question):
    next_question = str(int(question) + 1)

    if os.path.isdir('rooms/' + room + '/questions/' + next_question):
        return flask.redirect('/room/' + room + '/' + name + '/question/' + next_question)

    winner_file = open('rooms/' + room + '/winner.txt', 'r')
    winner_name = winner_file.read()
    winner_file.close()

    filename = 'medal' + room + '.png'

    if name == winner_name:
        return flask.render_template('winner.html', name=name, img=flask.url_for('static', filename=filename))
    else:
        return flask.render_template('loser.html', name=name, winner=winner_name)


@app.route('/room/<room>/<name>/question/<question>/processing...', methods=["POST"])
def answer_to_question(room, name, question):
    answer_file = open('rooms/' + room + '/questions/' + question + '/answers.txt', 'a+')
    answer_file.write(name + '|' + flask.request.form['answer'] + '\n')
    answer_file.close()

    return flask.redirect('/room/' + room + '/' + name + '/question/' + question + '/waiting...')


app.run(host='0.0.0.0', port=8080)
