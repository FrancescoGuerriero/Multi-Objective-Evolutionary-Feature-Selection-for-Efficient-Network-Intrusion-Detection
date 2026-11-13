import pandas as pd
import numpy as np
import pytest
from prototype.flow_watch import classify_rows, read_new_records, monitor_compatible_flows

class Fake:
    feature_names_in_ = np.array(["sbytes","service"])
    classes_ = np.array([0,1])
    def predict_proba(self, frame):
        p = np.where(frame.sbytes.astype(float)>10, .9, .1)
        return np.c_[1-p,p]

def test_schema_rejection():
    with pytest.raises(ValueError, match="missing"):
        classify_rows(pd.DataFrame({"sbytes":[1]}), Fake())

def test_scoring():
    r = classify_rows(pd.DataFrame({"sbytes":[2,20],"service":["dns","http"]}),Fake())
    assert r.ids_prediction.tolist() == [0,1]

def test_append_stream(tmp_path,monkeypatch):
    file = tmp_path/"flows.csv"
    file.write_text("sbytes,service\n2,dns\n20,htt",encoding="utf-8")
    first,pos = read_new_records(file,0)
    assert first.service.tolist() == ["dns"]
    with file.open("a") as stream: stream.write("p\n")
    second,pos2 = read_new_records(file,pos)
    assert second.service.tolist() == ["http"]
    assert read_new_records(file,pos2)[0].empty
    monkeypatch.setattr("prototype.flow_watch.load_pipeline",lambda _:Fake())
    got=[]
    count = monitor_compatible_flows(file,"unused.joblib",iterations=2,interval=.001,emit=got.append)
    assert count==2
    assert sorted(x["prediction"] for x in got)==[0,1]
