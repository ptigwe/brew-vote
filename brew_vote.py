from flask import Flask, request, render_template, redirect, url_for, session, flash
from database import db_session
import model
import numpy as np
import os

app = Flask(__name__)
app.config['DEBUG'] = True
app.secret_key = os.environ.get('BREW_VOTE_KEY', 'secret_key')
print("Secret Key is {}", app.secret_key)

def get_scoring():
    return {'appearance': 10, 'finish': 20, 'aroma': 10, 'taste': 30, 'drinkability': 30}

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

def get_beer_ratings(beer_id, sess_user=True):
    res = db_session.query(model.Rating).filter(model.Rating.beer_id ==
            beer_id)
    if sess_user:
        comp_id = db_session.query(model.Beer).filter(model.Beer.id ==
                beer_id).first().competition_id
        voter_id = session.get('comp_' + str(comp_id), -1)
        print("Beer ratings sess_id", str(voter_id))
        if voter_id >= 0:
            res = res.filter(model.Rating.rater_id == voter_id)
    return res.all()

def beer_rating_count(beer, sess_user=True):
    ratings = get_beer_ratings(beer.id, sess_user)
    scores = [rating.score() for rating in ratings]
    return np.mean(scores)

@app.context_processor
def beer_rating_func():
    return dict(beer_rating_func=beer_rating_count)

@app.route('/')
def index():
    comps = get_competitions()
    return render_template('index.html', comps=comps)

@app.route('/theme')
def theme():
    return render_template('theme.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        print(list(request.form))
        if request.form['email'] == 'smoked@rye.com':
            session['username'] = request.form['email']
            return redirect(url_for('index'))
    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

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
    beers = sorted(get_comp_beers(comp_id), key=lambda x: beer_rating_count(x, not comp.completed),
            reverse=True)
    print(beers)
    return render_template('view_comp.html', comp=comp, beers=beers)

def add_rating(beers, ratings):
    for beer in beers:
        ap = ratings['appearance_' + str(beer.id)]
        fi = ratings['finish_' + str(beer.id)]
        ar = ratings['aroma_' + str(beer.id)]
        ta = ratings['taste_' + str(beer.id)]
        dr = ratings['drinkability_' + str(beer.id)]
        rating = None
        if 'comp_' + str(beer.competition_id) in session:
            rating = db_session.query(model.Rating).filter(model.Rating.beer_id == beer.id,
                    model.Rating.rater_id == session['comp_' + str(beer.competition_id)]).first()
        if rating is None:
            rating = model.Rating(beer, ap, fi, ar, ta, dr)
            rating.rater_id = session['comp_' + str(beer.competition_id)]
        else:
            rating.update(ap, fi, ar, ta, dr)
        db_session.add(rating)
    db_session.commit()

def rate_to_dict(rating):
    d = dict()
    for name in get_scoring():
        if rating is None:
            d[name] = 0
        else:
            d[name] = rating.__dict__[name]
    return d

@app.route('/comp/rate/<comp_id>', methods=['POST', 'GET'])
def rate_comp(comp_id):
    comp = get_competition(comp_id)

    if comp.completed:
        return redirect(url_for('view_comp', comp_id=comp_id))

    if 'comp_' + comp_id not in session:
        session['comp_' + comp_id] = comp.curr_voters
        comp.curr_voters += 1
        db_session.add(comp)
        db_session.commit()

    flash(" ".join(map(str, ["Voting on competition", comp_id, "with voter id", session['comp_' + comp_id]])))

    names = get_scoring()
    beers = get_comp_beers(comp_id)
    rate_query = db_session.query(model.Rating).filter(model.Rating.rater_id == session['comp_' + comp_id])

    if request.method == 'POST':
        print(list(request.form.keys()))
        add_rating(beers, request.form)
        return redirect(url_for('view_comp', comp_id=comp_id))

    rating = []
    for beer in beers:
        rate = rate_to_dict(rate_query.filter(model.Rating.beer_id == beer.id).first())
        rating.append(rate)

    print(rating)
    return render_template('rate_comp.html', comp=comp, beer_rating=zip(beers,rating), names=names.keys(), limit=names)

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

def get_beer(beer_id):
    return db_session.query(model.Beer).filter(model.Beer.id == beer_id).first()

@app.route('/beer/rate/<beer_id>', methods=['POST', 'GET'])
def rate_beer(beer_id):
    beer = get_beer(beer_id)
    comp = beer.competition
    names = get_scoring()

    if comp.completed:
        return redirect(url_for('view_comp', comp_id=comp_id))

    if 'comp_' + str(comp.id) not in session:
        session['comp_' + str(comp.id)] = comp.curr_voters
        comp.curr_voters += 1
        db_session.add(comp)
        db_session.commit()

    flash(" ".join(map(str, ["Voting on competition", comp.id, "with voter id",
        session['comp_' + str(comp.id)]])))

    if request.method == 'POST':
        add_rating([beer], request.form)
        return redirect(url_for('view_comp', comp_id=beer.competition_id))

    rate_query = db_session.query(model.Rating).filter(model.Rating.rater_id == session['comp_' + str(comp.id)] and model.Rating.beer_id == beer_id)
    rate = rate_to_dict(rate_query.first())

    return render_template('rate_beer.html', beer=beer, comp=beer.competition, names=names.keys(), limit=names, rating=rate)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run()
