from os import error
from flask import Flask,render_template,request
import controller
app = Flask(__name__)


@app.route('/',methods=['GET','POST'])
def home():
    if request.method == "POST":       
        if request.form.get("pl_link").__contains__("https://www.youtube.com/playlist?list=")==False:
            return render_template("index.html",errorTitle="Invalid playlist link",status="fail",icon="fa fa-warning")
        elif controller.getSpotifyUris(request.form.get("pl_link"),request.form.get("email"),request.form.get("password")) is None:
            print("Empty playlist")
            return render_template("index.html",errorTitle="Empty playlist",status="fail",icon="fa fa-warning")      
        else:
            try:
                controller.main(request.form.get("email"),request.form.get("password"),request.form.get("pl_link"),request.form.get("pl_name"))
                if(controller.read_token()=="Authentication failed"):
                    return render_template("index.html",errorTitle="Authentication failed",status="fail",icon="fa fa-warning")
            finally:
                with open("access_token.txt", "w") as f:
                    f.write("")                    
            return render_template("index.html",errorTitle="Playlist created successfully",status="success",icon="fa fa-check")  
    else:
        return render_template("index.html",error="")
 
if __name__ == '__main__':
    app.run(debug=True)