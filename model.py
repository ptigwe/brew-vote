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

    def __init__(self, name=None):
        self.name = name
        self.comp_date = datetime.datetime.utcnow()
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

    def __init__(self, brewer, name, style, comp):
        self.brewer = brewer
        if name == "":
            name = "Beer"
        self.name = name
        self.style = style
        self.competition = comp

class Voting(Base):
    __tablename__ = 'voting'
    id = Column(Integer, primary_key=True)
    beer_id = Column(Integer, ForeignKey('beer.id'))
    beer = relationship(Beer)
    Appearance = Column(Integer)
    Finish = Column(Integer)
    Aroma = Column(Integer)
    Taste = Column(Integer)
    Drinkability = Column(Integer)
