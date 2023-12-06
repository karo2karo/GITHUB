#!/usr/bin/env python3

import pandas as pd

excel_2 = 'linux.cmdb.no.dup.xlsx'
excel_3 = 'exOmni_katello02.xlsx'

df2 = pd.read_excel(excel_2)
df3 = pd.read_excel(excel_3)

merged_df = df2[~df2['Host Name'].isin(df3['Column1'])]

# Save the merged DataFrame to 'output.xlsx'
merged_df.to_excel('output19.xlsx', index=False)