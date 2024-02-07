import pandas as pd

# pick your files
excel_1 = 'linux.cmdb.no.dup.xlsx'
excel_2 = 'output.xlsx'

# read your files
df1 = pd.read_excel(excel_1)
df2 = pd.read_excel(excel_2)

# pick rows from column Asset Name from df1 that CONTAINS STRING in Column1 from df2.
rows_to_remove = df1[df1['Asset Name'].str.contains('|'.join(df2['Column1']), case=False, na=False)]

# remove identified rows from df1
df1 = df1.drop(rows_to_remove.index)

# save the output to a new file
df1.to_excel('output_file2.xlsx', index=False)