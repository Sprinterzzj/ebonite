import contextlib
import os
import tempfile
import typing

import xgboost

from ebonite.core.analyzer.base import TypeHookMixin
from ebonite.core.analyzer.model import ModelHook
from ebonite.core.objects import ModelWrapper
from ebonite.core.objects.artifacts import Blobs, LocalFileBlob
from ebonite.core.objects.wrapper import FilesContextManager


class XGBoostModelWrapper(ModelWrapper):
    """
    :class:`~.ModelWrapper` implementation for XGBoost models
    """
    model_path = 'model.xgb'

    @contextlib.contextmanager
    @ModelWrapper.with_model
    def _dump(self) -> FilesContextManager:
        model: xgboost.Booster = self.model
        with tempfile.TemporaryDirectory(prefix='ebonite_xgboost_dump') as f:
            path = os.path.join(f, self.model_path)
            model.save_model(path)
            yield Blobs({self.model_path: LocalFileBlob(path)})

    def _load(self, path):
        self.model = xgboost.Booster()
        self.model.load_model(os.path.join(path, self.model_path))

    def _exposed_methods_mapping(self) -> typing.Dict[str, str]:
        return {
            'predict': '_predict'
        }

    @ModelWrapper.with_model
    def _predict(self, data):
        if not isinstance(data, xgboost.DMatrix):
            data = xgboost.DMatrix(data)
        return self.model.predict(data)


class XGBoostModelHook(ModelHook, TypeHookMixin):
    """
    :class:`.ModelHook` implementation for `xgboost.Booster` objects
    """
    valid_types = [xgboost.Booster]

    def process(self, obj, **kwargs) -> ModelWrapper:
        return XGBoostModelWrapper().bind_model(obj, **kwargs)
