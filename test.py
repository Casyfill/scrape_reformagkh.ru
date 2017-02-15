import pandas as pd
from details import flattern_dict,  _parse_detailes

url = 'https://www.reformagkh.ru/myhouse/profile/view/7553712/'

d = _parse_detailes(url)
x = pd.Series(d)
print x