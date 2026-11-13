import argparse,json,time
from pathlib import Path
import numpy as np
from sklearn.pipeline import Pipeline
from research.src.utils.seed import set_global_seed
from research.src.utils.data import load_csv_dataset,make_train_valid_test_split
from research.src.models.preprocessing import build_preprocessor
from research.src.models.factory import create_model
from research.src.models.metrics import classification_metrics
SEEDS=[42,101,202,303,404]

def run_once(csv,target,model,seed):
    set_global_seed(seed); X,y=load_csv_dataset(csv,target); s=make_train_valid_test_split(X,y,seed)
    pipe=Pipeline([('prep',build_preprocessor(s.X_train)),('model',create_model(model,seed))])
    t=time.perf_counter(); pipe.fit(s.X_train,s.y_train); train=time.perf_counter()-t
    t=time.perf_counter(); pred=pipe.predict(s.X_test); infer=time.perf_counter()-t
    return {'seed':seed,'model':model,'n_raw_features':X.shape[1],'training_seconds':train,'inference_seconds':infer,'inference_ms_per_sample':infer/max(len(s.X_test),1)*1000,**classification_metrics(s.y_test,pred)}

def summarise(runs):
    out={}
    for k in ['accuracy','balanced_accuracy','macro_precision','macro_recall','macro_f1','training_seconds','inference_ms_per_sample']:
        a=np.array([r[k] for r in runs],float); out[k]={'mean':float(a.mean()),'std':float(a.std(ddof=1)) if len(a)>1 else 0.0}
    return out

def main():
    p=argparse.ArgumentParser(); p.add_argument('--csv',required=True); p.add_argument('--target',default='label'); p.add_argument('--model',choices=['logistic_regression','random_forest','xgboost'],default='random_forest'); p.add_argument('--seeds',nargs='*',type=int,default=SEEDS); p.add_argument('--output',default='results/baseline_results.json'); a=p.parse_args()
    runs=[run_once(a.csv,a.target,a.model,s) for s in a.seeds]; payload={'experiment':'baseline_full_features','runs':runs,'summary':summarise(runs)}
    o=Path(a.output); o.parent.mkdir(parents=True,exist_ok=True); o.write_text(json.dumps(payload,indent=2),encoding='utf-8'); print(json.dumps(payload['summary'],indent=2))
if __name__=='__main__': main()
