"""test.

# 期間
暗黙の期間 ex. 1000 -> 1000/01/01 ~ 1000/12/31 みたいな
# 月の期間を定義
from dateutil.relativedelta import relativedelta python-dateutil
month_start = year_month.replace(day=1)
month_end = month_start + relativedelta(months=1, days=-1)
明示的期間
    1000/1/1 ~  終わりが不定
    ~ 1111/11/11  始まりが不定
    1000/1/1 ~ 1111/11/11 決まってる



天文学的・歴史的な日付を正確に扱える astropy
    BC AD マイナスの年を扱えるらしい
# period 期間の比較
"""
