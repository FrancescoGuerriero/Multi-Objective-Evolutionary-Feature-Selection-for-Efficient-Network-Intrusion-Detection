from __future__ import annotations
import numpy as np
from .base import FeatureSelectionResult, FeatureSelector
from .fitness import FeatureSubsetEvaluator

class BPSOFeatureSelector(FeatureSelector):
    def __init__(self, estimator, X_valid, y_valid, particles=30, iterations=20,
                 inertia=0.7, cognitive=1.5, social=1.5, feature_penalty=0.02):
        self.estimator=estimator; self.X_valid=X_valid; self.y_valid=y_valid
        self.particles=particles; self.iterations=iterations; self.inertia=inertia
        self.cognitive=cognitive; self.social=social; self.feature_penalty=feature_penalty

    @staticmethod
    def _sigmoid(v):
        v=np.clip(v,-30,30)
        return 1.0/(1.0+np.exp(-v))

    def select(self, X, y, *, seed:int) -> FeatureSelectionResult:
        rng=np.random.default_rng(seed); X=np.asarray(X); n_features=X.shape[1]
        evaluator=FeatureSubsetEvaluator(self.estimator,X,y,self.X_valid,self.y_valid,self.feature_penalty)
        position=rng.integers(0,2,size=(self.particles,n_features),dtype=np.int8)
        for p in position:
            if p.sum()==0: p[rng.integers(0,n_features)]=1
        velocity=rng.normal(0,1,size=(self.particles,n_features))
        pbest=position.copy(); pbest_score=np.full(self.particles,-np.inf); pbest_f1=np.zeros(self.particles)
        gbest=position[0].copy(); gbest_scalar=-np.inf; gbest_f1=0.0
        history=[]
        cache={}
        def evaluate(mask):
            k=tuple(int(v) for v in mask)
            if k not in cache: cache[k]=evaluator.evaluate(mask)
            return cache[k]
        for _ in range(self.iterations):
            for i in range(self.particles):
                scalar,f1,_=evaluate(position[i])
                if scalar>pbest_score[i]:
                    pbest_score[i]=scalar; pbest_f1[i]=f1; pbest[i]=position[i].copy()
                if scalar>gbest_scalar:
                    gbest_scalar=scalar; gbest_f1=f1; gbest=position[i].copy()
            history.append(float(gbest_f1))
            r1=rng.random((self.particles,n_features)); r2=rng.random((self.particles,n_features))
            velocity=(self.inertia*velocity + self.cognitive*r1*(pbest-position) + self.social*r2*(gbest-position))
            probability=self._sigmoid(velocity)
            position=(rng.random((self.particles,n_features))<probability).astype(np.int8)
            for p in position:
                if p.sum()==0: p[rng.integers(0,n_features)]=1
        mask=np.asarray(gbest,dtype=bool)
        return FeatureSelectionResult('BPSO',mask,np.flatnonzero(mask).tolist(),int(mask.sum()),float(gbest_f1),history)
