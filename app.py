from flask import Flask, render_template_string
import os

app = Flask(__name__)

@app.route('/')
def run_script():
    os.system("python3 webhook_submitter.py")
    return render_template_string("<h2>Script executed. Check terminal for results.</h2>")

if __name__ == '__main__':
    app.run(debug=True)
