from typing import Tuple

import pandas as pd
import numpy as np


class Predictions:
    def __init__(self, indices: list, values: list):
        try:
            # Convert to a number when possible, since they're
            # more comparable e.g. 1 == 1.0, etc.
            values_series = pd.Series(values, dtype=np.float)
        except ValueError:
            # Fall back to a string
            values_series = pd.Series(values, dtype=np.str)

        self.data = pd.DataFrame(
            # Indices should always be parseable to a float
            {"indices": pd.Series(indices, dtype=np.float), "values": values_series}
        )

    @staticmethod
    def find_common(
        preds_a: "Predictions", preds_b: "Predictions"
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Get the predictions from preds_a and preds_b that are
        for the same rows in their parent pipeline's dataset.
        Returns the common prediction values aligned by dataset
        row index. So `common.values_a[i]` is a prediction for
        the same dataset row as `common.values_b[i]`.
        """
        common = pd.merge(
            preds_a.data, preds_b.data, on="indices", suffixes=("_a", "_b")
        )
        return common.values_a, common.values_b
