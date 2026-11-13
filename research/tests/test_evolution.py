import numpy as np
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from research.src.evolution.ga import GAFeatureSelector
from research.src.evolution.bpso import BPSOFeatureSelector

def _data():
 X,y=make_classification(n_samples=120,n_features=8,n_informative=4,n_redundant=2,random_state=7)
 return train_test_split(X,y,test_size=.25,random_state=42,stratify=y)

def test_ga_selects_features():
 Xtr,Xv,ytr,yv=_data(); m=LogisticRegression(max_iter=500)
 r=GAFeatureSelector(m,Xv,yv,population_size=6,generations=2).select(Xtr,ytr,seed=42)
 assert 1<=r.selected_count<=Xtr.shape[1]
 assert 0<=r.best_score<=1

def test_bpso_selects_features():
 Xtr,Xv,ytr,yv=_data(); m=LogisticRegression(max_iter=500)
 r=BPSOFeatureSelector(m,Xv,yv,particles=6,iterations=2).select(Xtr,ytr,seed=42)
 assert 1<=r.selected_count<=Xtr.shape[1]
 assert 0<=r.best_score<=1
