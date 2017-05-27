from flask import Flask, request, render_template, redirect, url_for, session
from database import db_session
import model
import numpy as np

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

def generate_competition(name):
    comp = model.Competition(name)
    comp.completed = False
    db_session.add(comp)
    db_session.commit()
    return comp

def get_beer_ratings(beer_id):
    return db_session.query(model.Rating).filter(model.Rating.beer_id ==
            beer_id).all()

@app.template_filter('beer_rating_count')
def beer_rating_count(beer):
    ratings = get_beer_ratings(beer.id)
    scores = [rating.score() for rating in ratings]
    return np.mean(scores)

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
        comp = generate_competition(name)
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
    beers = sorted(get_comp_beers(comp_id), key=lambda x: beer_rating_count(x),
            reverse=True)
    return render_template('view_comp.html', comp=comp, beers=beers)

def add_rating(beers, ratings):
    for beer in beers:
        ap = ratings['Appearance_' + str(beer.id)]
        fi = ratings['Finish_' + str(beer.id)]
        ar = ratings['Aroma_' + str(beer.id)]
        ta = ratings['Taste_' + str(beer.id)]
        dr = ratings['Drinkability_' + str(beer.id)]
        rating = model.Rating(beer, ap, fi, ar, ta, dr)
        db_session.add(rating)
    db_session.commit()

@app.route('/comp/rate/<comp_id>', methods=['POST', 'GET'])
def rate_comp(comp_id):
    comp = get_competition(comp_id)
    names = get_scoring()
    beers = get_comp_beers(comp_id)
    if request.method == 'POST':
        print(list(request.form.keys()))
        add_rating(beers, request.form)
        return redirect(url_for('view_comp', comp_id=comp_id))
    return render_template('comp.html', comp=comp, beers=beers, names=names.keys(), limit=names)

def create_beer(name, brewer, style, comp):
    beer = model.Beer(name, brewer, style, comp)
    db_session.add(beer)
    db_session.commit()

@app.route('/beer/add/<comp_id>', methods=['POST','GET'])
def new_beer(comp_id):
    comp = get_competition(comp_id)
    if request.method == 'POST':
        name = request.form['name']
        brewer = request.form['brewer']
        style = request.form['style']
        create_beer(name, brewer, style, comp)
    return render_template('add_beer.html', comp=comp)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
