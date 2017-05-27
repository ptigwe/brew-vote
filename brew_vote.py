from flask import Flask, request, render_template
app = Flask(__name__)
app.config['DEBUG'] = True

def get_scoring():
    return {'Appearance': 10, 'Finish': 20, 'Aroma': 10, 'Taste': 30, 'Drinkability': 30}

def get_beers(comp_id, names):
    return [dict(zip(['id'] + list(names.keys()), [i + 1] + [0] * len(names))) for i in range(5)]

@app.route('/')
def index():
    return render_template('layout.html')

@app.route('/theme')
def theme():
    return render_template('theme.html')

@app.route('/login')
def login():
    return render_template('signin.html')

@app.route('/rate/<comp_id>')
def rate(comp_id):
    names = get_scoring()
    beers = get_beers(comp_id, names)
    return render_template('comp.html', comp_id=comp_id, beers=beers, names=names.keys(), limit=names)

if __name__ == '__main__':
    app.run()
