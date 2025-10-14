from dataclasses import dataclass, field # for easy data storage
import typing as t # for type hints

@dataclass # simple class to hold egram data
class EgramData: # ECG data structure
    time: t.List[float] = field(default_factory=list) # time points
    atrial: t.List[float] = field(default_factory=list) # atrial signal
    ventricular: t.List[float] = field(default_factory=list) # ventricular signal
    sampling_rate: float = 100.0 # Hz Placeholder for now
    timestamp: str = "" # when data was recorded

    def clear(self):
        self.time.clear()
        self.atrial.clear()
        self.ventricular.clear()
        self.timestamp = ""
    
