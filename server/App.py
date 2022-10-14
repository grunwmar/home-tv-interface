import os
import subprocess
from flask import render_template
from flask import Flask
from flask import request
import markdown
from datetime import datetime
import shlex

# path to file where notes are stored [todo: config]
TEXTFILE=os.path.join(os.environ['HOME'],'desk_notes.log')

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
)

# helper functions to mark console output
def colorize(string, fg=2, bg=0, sty=1):
    return f"\033[{sty};3{fg};4{bg}m{string}\033[0m"

def _print(*args, fg=2, bg=0, sty=1, **kwargs):
    _args = [colorize(arg) for arg in args]
    print(*_args, **kwargs)

executed_processes = list()


# index
@app.route('/')
def main():
    return render_template('main.html')


# acces to notepad
@app.route('/page/desk')
def desk():
    address="192.168.100.76"
    port="5000"

    try:
        with open(TEXTFILE, 'r') as f:
            text = f.read()
    except Exception as e:
        with open(TEXTFILE, 'w') as f:
            f.write('')
        with open(TEXTFILE, 'r') as f:
            text = f.read()
    return render_template('textfield.html', address=address, port=port, content=text)


# access to notepad content processed by markdnown
@app.route('/page/desk/md')
def desk_md():
    try:
        with open(TEXTFILE, 'r') as f:
            text = f.read()
    except Exception as e:
        with open(TEXTFILE, 'w') as f:
            f.write('')
        with open(TEXTFILE, 'r') as f:
            text = f.read()
    html = markdown.markdown(text)
    return render_template('markdown.html', content=html)


# get content of notepad file
@app.route('/action/messages/view')
def view_messages():
    try:
        with open(TEXTFILE, 'r') as f:
            text = f.read()
    except Exception as e:
        with open(TEXTFILE, 'w') as f:
            f.write('')
        with open(TEXTFILE, 'r') as f:
            text = f.read()
    html = text
    return render_template('view_md.html', messages=html)


# action method - accept text to write to notepad
@app.route('/action/messages/accept', methods=['POST'])
def accept_message():
    data = request.form.get('message')
    _print(data)
    text = str(data)
    _print(text, fg=4)
    with open(TEXTFILE,'w') as contents:
        contents.write(text)
    return render_template('back.html', back="/page/desk")


# interface to turn off or reboot pc
@app.route('/page/turnoff', methods=['POST','GET'])
def page_turn_off():
    data = request.form.get('confirm')
    _print(data)
    if data == "turnoff":
        os.system('poweroff')
        _print(data, 'Turning off')
    elif data == "reboot":
        os.system('reboot')
    return render_template('turnoff.html')


# action method - turn off or reboot pc
@app.route('/action/turnoff', methods=['POST','GET'])
def action_turn_off():
    data = request.form.get('confirm')
    _print(data)
    if data == "turnoff":
        os.system('poweroff')
        _print(data, 'Turning off')
    elif data == "reboot":
        os.system('reboot')
    return f"Turning off ({data})"


# interface for managing shell commands
@app.route('/page/command')
def programs():
    _print(executed_processes)
    return render_template('prog_exc.html', processes=executed_processes)


# action method - accept and execute command
@app.route('/action/command/run', methods=['POST','GET'])
@app.route('/action/command/run::<xdgopen>', methods=['POST','GET'])
def exec(xdgopen=None):
    global executed_processes
    cmd = request.form.get('cmd')
    cmd_split = shlex.split(cmd)
    _print("RUN:", cmd, "<<<")

    if xdgopen == "xdg-open":
        _print("xdg-open*")
        cmd_split = ["xdg-open"] + cmd_split
        _print(cmd_split)

        cmd = " ".join(cmd_split)
    try:
        proc = subprocess.Popen(cmd_split)
        _print(proc.pid, fg=1)
        executed_processes += [(None, cmd, "...", proc.pid)]
    except Exception as exc:
        executed_processes += [(None, cmd, exc, None)]
    return render_template('back.html', back="/page/command")


# action method - kill process identified by it PID
@app.route('/action/command/terminate:<pid>')
def terminate_process(pid):
    pid = int(pid)
    _print(executed_processes, fg=3)
    for i, proc in enumerate(executed_processes):
        if proc[3] == pid:
            _print(f'killing {pid}...', fg=3)
            os.system(f'kill -9 {pid}')
            del executed_processes[i]
    return render_template('back.html', back="/page/command")


# TODO: config
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
