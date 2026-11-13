from abc import ABC,abstractmethod
from dataclasses import dataclass
import numpy as np
@dataclass(frozen=True)
class FeatureSelectionResult:
    algorithm:str; mask:np.ndarray; selected_indices:list[int]; selected_count:int; best_score:float; history:list[float]
class FeatureSelector(ABC):
    @abstractmethod
    def select(self,X,y,*,seed:int)->FeatureSelectionResult: raise NotImplementedError
