import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from database import Base

class Competition(Base):
    __tablename__ = 'competition'
    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    completed = Column(Boolean, default=False)
    comp_date = Column(DateTime, default=datetime.datetime.utcnow)
    curr_voters = Column(Integer, default=0)

    def __init__(self, name=None):
        self.name = name
        self.comp_date = datetime.datetime.utcnow()
        self.curr_voters = 0
        if name is None or name == '':
            self.name = self.name_from_date(self.comp_date)

    def name_from_date(self, date):
        return date.strftime("%B-%Y")

class Beer(Base):
    __tablename__ = 'beer'
    id = Column(Integer, primary_key=True)
    brewer = Column(String(120))
    name = Column(String(120))
    style = Column(String(120))
    competition_id = Column(Integer, ForeignKey('competition.id'))
    competition = relationship(Competition)

    def __init__(self, name, brewer, style, comp):
        self.brewer = brewer
        if name == "":
            name = "Beer"
        self.name = name
        self.style = style
        self.competition = comp

class Rating(Base):
    __tablename__ = 'voting'
    id = Column(Integer, primary_key=True)
    beer_id = Column(Integer, ForeignKey('beer.id'))
    rater_id = Column(Integer)
    beer = relationship(Beer)
    appearance = Column(Integer)
    finish = Column(Integer)
    aroma = Column(Integer)
    taste = Column(Integer)
    drinkability = Column(Integer)

    def __init__(self, beer, ap, fi, ar, ta, dr):
        self.beer = beer
        self.appearance = ap
        self.finish = fi
        self.aroma = ar
        self.taste = ta
        self.drinkability = dr

    def score(self):
        return (self.appearance + self.finish + self.aroma + self.taste 
            + self.drinkability)

    def __repr__(self):
        return str(self.beer.id) + "->" + str(self.score())
