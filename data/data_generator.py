# import pandas as pd
# import random
# from faker import Faker

# faker = Faker()





  #  ------------------------------------------------------------------------------------------------------------------------
                # employee data generate by this code and save as csv file. you can run this code once to generate the data.
                #  after that you can comment out the code to avoid regenerating the data every time you run the script.
  # ------------------------------------------------------------------------------------------------------------------------

# data = []

# departments = ['HR', 'Finance', 'Engineering', 'Marketing', 'Sales']

# for i in range (500):
#     salary = random.randint(30, 150)*1000
#     if random.random() < 0.05:   
#         salary = None

#     age = random.randint(22, 60)
#     if random.random() < 0.03:   
#         age = None

#     department = random.choice(departments)
#     if random.random() < 0.02:   
#         department = None
#     data.append([
#         i + 1,
#         faker.name(),
#         department,
#         age,
#         random.randint(0,30),
#         salary,
#         faker.city()
#     ])
# df = pd.DataFrame(
#     data, 
#     columns=['employee_id', 'name', 'department', 'age',
#               'years_of_experience', 'salary', 'city'])
# df.to_csv('data/employee_data.csv',index=False)
# print("emloyees created")




#  #  ------------------------------------------------------------------------------------------------------------------------
                # sales data generate by this code and save as csv file. you can run this code once to generate the data. 
                # after that you can comment out the code to avoid regenerating the data every time you run the script.
#  #  ------------------------------------------------------------------------------------------------------------------------

# sales_data = []     

# products = ["Laptop", "Mouse", "Keyboard", "Monitor", "Phone", "Tablet"]

# for i in range(1000000):
#     amount = random.randint(10, 3000)

#     if random.random() < 0.04:
#         amount = None

#     product = random.choice(products)

#     if random.random() < 0.02:
#         product = None

#     sales_data.append([
#         i + 1,
#         random.randint(1,500),
#         product,
#         amount,
#         faker.date_between(start_date = "-10y",end_date = "today")

#     ])

# df = pd.DataFrame(sales_data, columns=["sale_id", "employee_id", "product", "amount", "date"])
# df.to_csv("data/sales.csv",index=False)
# print("sales created")




#  #  ------------------------------------------------------------------------------------------------------------------------
                # attendance data generate by this code and save as csv file. you can run this code once to generate the data.
                #  after that you can comment out the code to avoid regenerating the data every time you run the script.
#  #  ------------------------------------------------------------------------------------------------------------------------

# attendance = []

# for i in range(150000):
#     hours = random.randint(4, 10)

#     if random.random() < 0.06:
#         hours = None

#     attendance.append([
#         random.randint(1, 500),
#         faker.date_between(start_date="-1y", end_date="today"),
#         hours
#     ])

# df = pd.DataFrame(attendance, columns=[
#     "employee_id", "date", "attendance_hours"
# ])

# df.to_csv("data/attendance.csv", index=False)
s
# print("Attendance created")