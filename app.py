import os
import spotipy
import uuid
from flask_session import Session
from flask import Flask,render_template,request,redirect,session,url_for
import controller

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
Session(app)

caches_folder = './.spotify_caches/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')

@app.route('/')
def index():
    if not session.get('uuid'):
        # Step 1. Visitor is unknown, give random ID
        session['uuid'] = str(uuid.uuid4())

    auth_manager = spotipy.oauth2.SpotifyOAuth(scope='user-read-currently-playing playlist-modify-private user-library-read playlist-modify-public',
            client_id="12fe8879174845bf94e9de513fe889c7",
            client_secret="15ffde4f252e482488d723204e91a21c",
            redirect_uri='http://127.0.0.1:5000/',
            cache_path=session_cache_path(),show_dialog=True
    )
    if request.args.get("code"):
        # Step 3. Being redirected from Spotify auth page
        auth_manager.get_access_token(request.args.get("code"))
        return redirect('/')

    if not auth_manager.get_cached_token():
        # Step 2. Display sign in link when no token
        auth_url = auth_manager.get_authorize_url()
        return f'<h2><a href="{auth_url}">Sign in</a></h2>'

    # Step 4. Signed in, display data
    spotify = spotipy.Spotify(auth_manager=auth_manager)
    return redirect("/home")


@app.route('/home',methods=['GET','POST'])
def home():
    if request.method == "POST":       
        if request.form.get("pl_link").__contains__("https://www.youtube.com/playlist?list=")==False:
            return render_template("index.html",errorTitle="Invalid playlist link",status="fail",icon="fa fa-warning")
        elif controller.getSpotifyUris(request.form.get("pl_link")) is None:
            print("Empty playlist")
            return render_template("index.html",errorTitle="Empty playlist",status="fail",icon="fa fa-warning")      
        else:
            controller.main(request.form.get("pl_link"),request.form.get("pl_name"))                  
            return render_template("index.html",errorTitle="Playlist created successfully",status="success",icon="fa fa-check")  
    else:
        return render_template("index.html",errorTitle="")
 
if __name__ == '__main__':
    app.run(debug=True)