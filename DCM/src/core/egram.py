from dataclasses import dataclass, field
import typing as t

@dataclass
class EgramData:
    time: t.List[float] = field(default_factory=list)
    atrial: t.List[float] = field(default_factory=list)
    ventricular: t.List[float] = field(default_factory=list)
    sampling_rate: float = 100.0 # Hz Placeholder for now
    timestamp: str = ""
    
