#!flask/bin/python
import ast
import json
from random import choice

from model import WriteSong
from utils import cap_name, set_name, insert_username

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for

from application import application
from application import UserName

# ELASTIC BEANSTALK INITIALISATION
# =====================================
application = Flask(__name__)
application.debug = True
application.secret_key = ''


# CONFIGURATION
# =====================================
with open("config.json", "r") as f:
    CONFIG = json.load(f)

DATA = {
    "verse_text": open(CONFIG["V"]["lyrics_path"]).read().strip(),
    "chorus_text": open(CONFIG["C"]["lyrics_path"]).read().strip(),
    "verse_dict": ast.literal_eval(open(CONFIG["V"]["dict_path"]).read().strip()),
    "chorus_dict": ast.literal_eval(
        open(CONFIG["C"]["dict_path"]).read().strip()
    ),
}

# ROUTES
# =====================================


@application.route('/', methods=['POST', 'GET'])
def login():
    form = UserName()
    if form.validate_on_submit():
        name = request.form['artistName']
        return redirect(url_for('result', name=name))
    return render_template('homepage.html', form=form)


@application.route('/result')
def result():
    username = cap_name(request.args['name'])
    structure = choice(CONFIG["opts"]["structs"])
    lyrics_str = insert_username(
        WriteSong(CONFIG, structure, DATA).get_song(), username)
    song_name = set_name(lyrics_str)
    lyrics = lyrics_str.split('\n')
    return render_template('resultpage.html', username=username, lyrics=lyrics, song_name=song_name)


if __name__ == '__main__':
    application.run()
