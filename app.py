from os import error
from flask import Flask,render_template,request,redirect,session,url_for
import controller
app = Flask(__name__)
app.secret_key = 'sASDafsdfj'
app.config['SESSION_COOKIE_NAME'] = 'spotify-login-session'


@app.route('/')
def login():
    sp_oauth = controller.create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()
    print(auth_url)
    return redirect(auth_url)

@app.route('/redirect')
def redirectPage():
    sp_oauth = controller.create_spotify_oauth()
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)
    session['token_info'] = token_info
    return redirect(url_for('home', _external=True))

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