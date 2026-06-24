 # missing_emp_id = df['employee_id'].isnull().sum()
    # print(missing_emp_id) #0

    # missing_emp_id = df['name'].isnull().sum()
    # print(missing_emp_id) #0

    # missing_emp_id = df['department'].isnull().sum()
    # print(missing_emp_id) #9

    # missing_emp_id = df['age'].isnull().sum()
    # print(missing_emp_id) #12

    # missing_emp_id = df['years_of_experience'].isnull().sum()
    # print(missing_emp_id) #0

    # missing_emp_id = df['salary'].isnull().sum()
    # print(missing_emp_id) #31

    # missing_emp_id = df['city'].isnull().sum()
    # print(missing_emp_id) #0

 # >> dublicate name found 
    # duplicate = df_cleand[df_cleand.duplicated(subset= ['name'] , keep= False)]
    # print(duplicate) #1







# >>check sales without employees and flag it
   #  invalid_mask = ~silver_sales_df["employee_id"].isin(silver_employee_df["employee_id"])

 # >> priduct name missing
   #  print (silver_sales_df['product'].isnull().sum())

# >> amount missings 
   #  print(silver_sales_df["amount"].isnull().sum() )

# >>check missing dates
   #  print(silver_sales_df['date'].isnull().sum())