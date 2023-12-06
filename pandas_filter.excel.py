#!/usr/bin/env python3

import pandas as pd

excel_1 = 'CMDB_custom_Tanium_2.xlsx'
excel_2 = 'LinuxInternal_katello01.xlsx'
excel_3 = 'exOmni_katello02.xlsx'

df1 = pd.read_excel(excel_1)
df2 = pd.read_excel(excel_2)
df3 = pd.read_excel(excel_3)

filtered_df_1 = df1.loc[(df1['Unnamed: 2'].isin(df2['Column1']))]
filtered_df_2 = df1.loc[(df1['Unnamed: 2'].isin(df3['Column1']))]

header = pd.read_excel(excel_1, nrows=1)
combined_df = pd.concat([header, filtered_df_1, filtered_df_2])

combined_df.to_excel('CMDB_custom_Tanium_2 - Copy2.xlsx', index=False)
