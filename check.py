
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "this is the home page"

if __name__ == "__main__":
    app.run(debug=True)



"""
for i in range(10):
    line = ser.readline()
    if line:
        lines.append(line)
        lines.append(datetime.now())
final_string = '\n'.join(lines)
"""