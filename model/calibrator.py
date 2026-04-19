"""Wrapper de calibracao isotonica para XGBoost — importavel para compatibilidade de pickle."""
import numpy as np


class _CalibratedXGB:
    """Wrapper que aplica calibracao isotonica sobre o XGBoost."""
    def __init__(self, base, calibrator, threshold=0.5):
        self.base = base
        self.calibrator = calibrator
        self.threshold = threshold
        self.classes_ = getattr(base, "classes_", np.array([0, 1]))

    def predict_proba(self, X):
        raw = self.base.predict_proba(X)[:, 1]
        cal = self.calibrator.predict(raw)
        return np.column_stack([1 - cal, cal])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= self.threshold).astype(int)
