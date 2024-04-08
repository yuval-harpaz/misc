import pandas as pd
import os
if os.path.isdir('/home/innereye/misc/'):
    os.chdir('/home/innereye/misc/')
url = 'https://themadad.com/allpolls/'
df = pd.read_html(url)
df[0].to_csv('data/themadad.csv', index=False)
# df[1].to_csv('1.csv', index=False)


