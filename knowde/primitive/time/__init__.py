"""時系列.

時間の表現
    EDTF
    和暦
    期間の表現どうするか
        EDTF で 1950/2000 みたいに表現できるが分かりにくい気がする
        yyyy ~ yyyy
            がいい
        前者と後者をEDTFとして結合すればいい


"""


from typing import Self

from pydantic import BaseModel


class KnTime(BaseModel):
    """時刻."""

    val: str

    @classmethod
    def parse(cls, line: str) -> Self:
        """From string to time."""
        return cls(val=line)
