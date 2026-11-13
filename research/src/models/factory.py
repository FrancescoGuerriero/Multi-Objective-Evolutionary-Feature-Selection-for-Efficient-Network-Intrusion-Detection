from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

def create_model(name,seed):
    if name=='logistic_regression': return LogisticRegression(max_iter=2000,random_state=seed,class_weight='balanced')
    if name=='random_forest': return RandomForestClassifier(n_estimators=300,random_state=seed,class_weight='balanced_subsample',n_jobs=-1)
    if name=='xgboost':
        from xgboost import XGBClassifier
        return XGBClassifier(n_estimators=300,max_depth=6,learning_rate=.05,subsample=.9,colsample_bytree=.9,random_state=seed,n_jobs=-1,eval_metric='logloss')
    raise ValueError(name)
