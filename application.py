import ast
import json
from random import choice

from quart import Quart, render_template, request, redirect, url_for
from forms import UserName

from model import WriteSong
from utils import data_window, cap_name, set_name, insert_username


# INITIALISATION
# =====================================
application = Quart(__name__)
application.debug = True
application.secret_key = 'Super secret key'


# CONFIGURATION
# =====================================
with open("config.json", "r") as f:
    CONFIG = json.load(f)

WINDOW_SIZE = CONFIG["opts"]["window"]
DATA = {
    "verse_text": data_window(CONFIG["V"]["lyrics_path"], WINDOW_SIZE),
    "chorus_text": data_window(CONFIG["C"]["lyrics_path"], WINDOW_SIZE),
    "rhyme_dict": ast.literal_eval(open(CONFIG["opts"]["dict_path"]).read().strip())
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
