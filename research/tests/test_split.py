import pandas as pd
from research.src.utils.data import make_train_valid_test_split
def test_split():
 X=pd.DataFrame({'a':range(100)}); y=pd.Series([0,1]*50); s=make_train_valid_test_split(X,y,42); assert len(s.X_train)+len(s.X_valid)+len(s.X_test)==100
