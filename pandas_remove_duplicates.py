import pandas as pd

# Read the Excel file into a DataFrame
df = pd.read_excel('linux.is.cmdb.xlsx')

# Specify the column from which you want to remove duplicates
column_name = 'Instance Id'
df_no_duplicates = df.drop_duplicates(subset=column_name)

# Save the DataFrame without duplicates to a new Excel file
df_no_duplicates.to_excel('linux.cmdb.no.dup.xlsx', index=False)