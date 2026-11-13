from __future__ import annotations
import numpy as np
from sklearn.base import clone
from sklearn.metrics import f1_score

class FeatureSubsetEvaluator:
    """Evaluate binary feature masks on a fixed validation set.

    score = macro-F1 - feature_penalty * selected_fraction
    The final multi-objective phase will separate these objectives instead of
    collapsing them into a single scalar.
    """
    def __init__(self, estimator, X_train, y_train, X_valid, y_valid, feature_penalty: float = 0.02):
        self.estimator=estimator
        self.X_train=np.asarray(X_train)
        self.y_train=np.asarray(y_train)
        self.X_valid=np.asarray(X_valid)
        self.y_valid=np.asarray(y_valid)
        self.feature_penalty=float(feature_penalty)
        self.n_features=self.X_train.shape[1]

    def evaluate(self, mask) -> tuple[float,float,int]:
        mask=np.asarray(mask,dtype=bool)
        count=int(mask.sum())
        if count==0:
            return -1.0, 0.0, 0
        model=clone(self.estimator)
        model.fit(self.X_train[:,mask],self.y_train)
        pred=model.predict(self.X_valid[:,mask])
        f1=float(f1_score(self.y_valid,pred,average='macro',zero_division=0))
        selected_fraction=count/self.n_features
        scalar=f1-self.feature_penalty*selected_fraction
        return float(scalar), f1, count
