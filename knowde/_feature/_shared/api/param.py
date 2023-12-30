from pydantic import BaseModel

from knowde._feature._shared.repo.base import LBase


class ApiParam(BaseModel, frozen=True):
    def set_attr(self, lb: LBase) -> None:
        for k, v in self.model_fields:
            setattr(lb, k, v)

    # def make_req(self) -> None:
    #     for k, v in self.model_fields.items():
    #         create_function()
