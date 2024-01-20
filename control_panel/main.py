from flask import Flask, render_template, request, session, jsonify,url_for
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = "1234"

# Path to the config.json file
config_path = 'static/config.json'
@app.route("/getC")
def getc():
    with open(config_path, "r") as f:
        data = json.load(f)
    
    # Reset specific keys to 0 using update_config_custom
    update_config_custom(start=0, stop=0, terminate=0, changes=0)
    
    return jsonify(data)

def update_config_custom(start=None, stop=None, terminate=None, getfile1=None, getfile2=None, changes=None):
    # Load current configuration from the JSON file
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Update the specified values
    if start is not None:
        config['start'] = start
    if stop is not None:
        config['stop'] = stop
    if terminate is not None:
        config['terminate'] = terminate
    if getfile1 is not None:
        config['getfile1'] = getfile1
    if getfile2 is not None:
        config['getfile2'] = getfile2
    if changes is not None:
        config['changes'] = changes

    # Write the updated configuration back to the JSON file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)


@app.route("/start")
def start():
    update_config_custom(start=1)
    return {"status":200},200


@app.route("/stop")
def stop():
    update_config_custom(stop=1)
    return {"status":200},200

@app.route("/terminate")
def terminate():
    update_config_custom(terminate=1)
    return {"status":200},200


@app.route("/logged/<data>")
def logged(data):
    with open("static/logs.txt","a") as f:
        f.writelines("\n"+data)
    return "done",200

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file provided', 400

    file = request.files['file']

    if file.filename == '':
        return 'No selected file', 400

    # Specify the folder where you want to save the uploaded files
    upload_folder = 'static/uploads'
    file_path = f'{upload_folder}/{file.filename}'

    file.save(file_path)

    # Generate the URL for the uploaded file
    file_url = url_for('static', filename=f'uploads/{file.filename}', _external=True)
    update_config_custom(getfile1=file_url,changes=1)

    return f'File uploaded successfully. URL: {file_url}'

@app.route("/logs", methods=["GET"])
def logs():
    with open("static/logs.txt","r") as f:
        data=f.readlines()

    # Create the JSON response
    response = jsonify(data)

    return response

@app.route('/execution', methods=['POST'])
def exe():
    try:
        json_data = request.get_json()

        with open("static/settings.json", "w") as f:
            json.dump(json_data, f)
        file_url = url_for('static', filename=f'settings.json', _external=True)
        update_config_custom(getfile2=file_url,changes=1)

        return jsonify({"message": "Changes saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/pingData/<data>")
def pingdata(data):
    if data in ["0", "1"]:
        timestamp = datetime.now().timestamp()
        with open("static/online.txt", "w") as f:
            f.write(f"{data}:{timestamp}")
        return "", 200
    else:
        return "", 400


@app.route("/checkOnline")
def check():
    offline_threshold = 5  # 5 seconds threshold for considering as offline

    try:
        with open("static/online.txt", "r") as f:
            content = f.read().strip().split(":")
        
        if len(content) == 2:
            data, timestamp_str = content
            timestamp = float(timestamp_str)
            current_time = datetime.now().timestamp()

            if current_time - timestamp > offline_threshold:
                with open("static/online.txt", "w") as f:
                    f.write("0")
                return jsonify({"status": "offline"})
            else:
                return "1"
        else:
            return jsonify({"status": "offline"})
    except Exception as e:
        print(f"Error checking online status: {e}")
        return jsonify({"status": "offline"})
    return "1"
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == 'project100' and password == '123456':
        session["authen"] = True
        return "", 200
    else:
        return "", 400

@app.route('/dash')
def dashboard():
    if "authen" in session:
        return render_template("dash.html")
    else:
        return render_template("login.html")

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, use_debugger=False)
