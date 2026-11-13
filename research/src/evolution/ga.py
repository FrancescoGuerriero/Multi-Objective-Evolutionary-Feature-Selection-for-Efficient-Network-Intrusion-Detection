from __future__ import annotations
import random
import numpy as np
from .base import FeatureSelectionResult, FeatureSelector
from .fitness import FeatureSubsetEvaluator

class GAFeatureSelector(FeatureSelector):
    def __init__(self, estimator, X_valid, y_valid, population_size=30, generations=20,
                 crossover_probability=0.8, mutation_probability=0.05,
                 tournament_size=3, feature_penalty=0.02):
        self.estimator=estimator; self.X_valid=X_valid; self.y_valid=y_valid
        self.population_size=population_size; self.generations=generations
        self.crossover_probability=crossover_probability
        self.mutation_probability=mutation_probability
        self.tournament_size=tournament_size; self.feature_penalty=feature_penalty

    def select(self, X, y, *, seed:int) -> FeatureSelectionResult:
        rng=np.random.default_rng(seed); random.seed(seed)
        X=np.asarray(X); n_features=X.shape[1]
        evaluator=FeatureSubsetEvaluator(self.estimator,X,y,self.X_valid,self.y_valid,self.feature_penalty)
        population=rng.integers(0,2,size=(self.population_size,n_features),dtype=np.int8)
        for ind in population:
            if ind.sum()==0: ind[rng.integers(0,n_features)]=1

        cache={}
        def score(ind):
            key=tuple(int(v) for v in ind)
            if key not in cache: cache[key]=evaluator.evaluate(ind)
            return cache[key]
        def tournament():
            ids=rng.integers(0,len(population),size=self.tournament_size)
            return population[max(ids,key=lambda i:score(population[i])[0])].copy()

        history=[]; best=None; best_tuple=(-float('inf'),0.0,0)
        for _ in range(self.generations):
            for ind in population:
                s=score(ind)
                if s[0]>best_tuple[0]: best_tuple=s; best=ind.copy()
            history.append(float(best_tuple[1]))
            new=[]
            while len(new)<self.population_size:
                a,b=tournament(),tournament()
                if rng.random()<self.crossover_probability and n_features>1:
                    point=int(rng.integers(1,n_features)); a[point:],b[point:]=b[point:].copy(),a[point:].copy()
                for child in (a,b):
                    flips=rng.random(n_features)<self.mutation_probability
                    child[flips]=1-child[flips]
                    if child.sum()==0: child[rng.integers(0,n_features)]=1
                    new.append(child)
                    if len(new)>=self.population_size: break
            population=np.asarray(new,dtype=np.int8)
        for ind in population:
            s=score(ind)
            if s[0]>best_tuple[0]: best_tuple=s; best=ind.copy()
        mask=np.asarray(best,dtype=bool)
        return FeatureSelectionResult('GA',mask,np.flatnonzero(mask).tolist(),int(mask.sum()),float(best_tuple[1]),history)
