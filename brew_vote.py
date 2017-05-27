from flask import Flask, request, render_template, redirect, url_for, session
from database import db_session
import model

app = Flask(__name__)
app.config['DEBUG'] = True

def get_scoring():
    return {'Appearance': 10, 'Finish': 20, 'Aroma': 10, 'Taste': 30, 'Drinkability': 30}

def get_beers(comp_id, names):
    return [dict(zip(['id'] + list(names.keys()), [i + 1] + [0] * len(names))) for i in range(5)]

def get_competitions():
    comps = db_session.query(model.Competition).all()
    for i in comps:
        print(i.id)
    return comps

def get_competition(comp_id):
    return db_session.query(model.Competition).filter(model.Competition.id == comp_id).first()

def get_comp_beers(comp_id):
    return db_session.query(model.Beer).filter(model.Beer.competition_id == comp_id).all()

def generate_competition(name, beers):
    comp = model.Competition(name)
    comp.completed = False
    db_session.add(comp)
    for i in range(beers):
        b = model.Beer()
        b.competition = comp
        db_session.add(b)
    db_session.commit()
    return comp

@app.route('/')
def index():
    comps = get_competitions()
    return render_template('index.html', comps=comps)

@app.route('/theme')
def theme():
    return render_template('theme.html')

@app.route('/login')
def login():
    return render_template('signin.html')

@app.route('/comp/new', methods=['GET','POST'])
def new_comp():
    if request.method == 'POST':
        name = request.form['name']
        beers = request.form['beers']
        comp = generate_competition(name, int(beers))
        return redirect(url_for('view_comp', comp_id=comp.id))
    return render_template('new_comp.html')

@app.route('/comp/end/<comp_id>')
def end_comp(comp_id):
    comp = get_competition(comp_id)
    comp.completed = True
    db_session.add(comp)
    db_session.commit()
    return redirect(url_for('view_comp', comp_id=comp_id))

@app.route('/comp/view/<comp_id>')
def view_comp(comp_id):
    comp = get_competition(comp_id)
    beers = get_comp_beers(comp_id)
    return render_template('view_comp.html', comp=comp, beers=beers)

@app.route('/comp/rate/<comp_id>')
def rate_comp(comp_id):
    names = get_scoring()
    beers = get_comp_beers(comp_id)
    return render_template('comp.html', comp_id=comp_id, beers=beers, names=names.keys(), limit=names)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
