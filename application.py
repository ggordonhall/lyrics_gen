#!/Users/gabrielgordon-hall/.local/share/virtualenvs/lyrics_gen-ETPm8Ymq/bin/python3.7
import ast
import json
from random import choice

from quart import Quart, render_template, request, redirect, url_for
from forms import UserName

from model import WriteSong
from utils import cap_name, set_name, insert_username


# ELASTIC BEANSTALK INITIALISATION
# =====================================
application = Quart(__name__)
application.debug = True
application.secret_key = 'Super secret key'


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
async def login():
    form = UserName()
    if form.validate_on_submit():
        r_form = await request.form
        name = r_form['artistName']
        return redirect(url_for('result', name=name))
    return await render_template('homepage.html', form=form)


@application.route('/result')
async def result():
    username = cap_name(request.args['name'])
    structure = choice(CONFIG["opts"]["structs"])
    lyrics_str = insert_username(
        WriteSong(CONFIG, structure, DATA).get_song(), username)
    song_name = set_name(lyrics_str)
    lyrics = lyrics_str.split('\n')
    return await render_template('resultpage.html', username=username, lyrics=lyrics, song_name=song_name)


if __name__ == '__main__':
    application.run()
