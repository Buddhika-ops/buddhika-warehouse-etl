import pandas as pd
import random
import numpy as np
from faker import Faker

faker = Faker()





  #  ------------------------------------------------------------------------------------------------------------------------
                # employee data generate by this code and save as csv file. you can run this code once to generate the data.
                #  after that you can comment out the code to avoid regenerating the data every time you run the script.
  # ------------------------------------------------------------------------------------------------------------------------
# def employees():
#     data = []

#     departments = [
#         'Inside Sales',
#         'Field Sales',
#         'Enterprise Sales',
#         'SMB Sales',
#         'Channel Sales',
#         'Customer Success & Renewals'
#     ]
#     MIN_WORKING_AGE = 18
#     salary_bands = {
#         'Inside Sales':                (35000, 75000),
#         'SMB Sales':                   (38000, 80000),
#         'Customer Success & Renewals': (42000, 85000),
#         'Channel Sales':               (50000, 100000),
#         'Field Sales':                 (55000, 120000),
#         'Enterprise Sales':            (65000, 150000),
#     }
    
#     for i in range(500):
#         department = random.choice(departments)
#         if random.random() < 0.02:
#             department = None
    
#         age = random.randint(22, 60)
#         if random.random() < 0.03:
#             age = None
    
#         if age is not None:
#             max_experience = max(0, age - MIN_WORKING_AGE)
#             years_of_experience = random.randint(0, min(max_experience, 30))
#         else:
#             years_of_experience = random.randint(0, 30)
    
#         # Realistic salary: base band per department + experience-based scaling + noise
#         if department is not None and department in salary_bands:
#             low, high = salary_bands[department]
#         else:
#             # fallback band if department is missing
#             low, high = (35000, 120000)
    
#         # Experience pushes salary up toward the top of the band (capped at 30 yrs)
#         experience_factor = min(years_of_experience / 30, 1.0)
#         base_salary = low + (high - low) * experience_factor
    
#         # Add realistic noise (+/- 10%) so it's not a perfectly clean formula
#         noise = random.uniform(-0.10, 0.10)
#         salary = base_salary * (1 + noise)
    
#         # Round to nearest 500 to mimic real-world pay bands
#         salary = round(salary / 500) * 500
    
#         if random.random() < 0.05:
#             salary = None
    
#         data.append([
#             i + 1,
#             faker.name(),
#             department,
#             age,
#             years_of_experience,
#             salary,
#             faker.city()
#         ])
    
#     df = pd.DataFrame(
#         data,
#         columns=['employee_id', 'name', 'department', 'age',
#                 'years_of_experience', 'salary', 'city']
#     )
    
#     df.to_csv('data/employee_data.csv', index=False)
#     print("employees created")
    


#  #  ------------------------------------------------------------------------------------------------------------------------
                # sales data generate by this code and save as csv file. you can run this code once to generate the data. 
                # after that you can comment out the code to avoid regenerating the data every time you run the script.
#  #  ------------------------------------------------------------------------------------------------------------------------




  # load employees and filter to Sales department only

def sales():
    sales_data = []
 
    # Product catalog: product -> unit price
    product_catalog = {
        "Laptop": 220000,
        "Desktop PC": 350000,
        "Mouse": 25000,
        "Keyboard": 30000,
        "Monitor": 150000,
        "Phone": 225000,
        "Tablet": 450000,
        "Printer": 180000,
        "Webcam": 60000,
        "Headset": 9000,
        "Docking Station": 15000,
        "External SSD": 11000,
        "Router": 13000,
        "Server Rack Unit": 45000,
        "Network Switch": 60000,
        "Software License (Annual)": 30000,
        "Support & Maintenance Plan": 50000,
        "Extended Warranty": 15000,
    }
 
    # Which products each department is allowed to sell
    department_products = {
        # Big-ticket, bulk/infrastructure deals
        "Enterprise Sales": [
            "Server Rack Unit", "Network Switch", "Desktop PC", "Laptop",
            "Monitor", "Software License (Annual)", "Support & Maintenance Plan"
        ],
        # On-site sales of full hardware range
        "Field Sales": [
            "Laptop", "Desktop PC", "Monitor", "Printer", "Router",
            "Network Switch", "Docking Station"
        ],
        # Smaller bundles, standard small-business kit
        "SMB Sales": [
            "Laptop", "Desktop PC", "Mouse", "Keyboard", "Monitor",
            "Printer", "Router", "Webcam"
        ],
        # Phone/remote sales of simple, easy-to-ship items
        "Inside Sales": [
            "Mouse", "Keyboard", "Webcam", "Headset", "External SSD",
            "Docking Station", "Tablet", "Phone"
        ],
        # Reseller/partner driven, mixed catalog
        "Channel Sales": [
            "Laptop", "Phone", "Tablet", "Monitor", "Printer",
            "External SSD", "Router"
        ],
        # Renewals/upsells - service & warranty focused, not hardware
        "Customer Success & Renewals": [
            "Software License (Annual)", "Support & Maintenance Plan",
            "Extended Warranty"
        ],
    }
 
    # load employees and keep their department so we can match product to department
    employees_df = pd.read_csv("data/employee_data.csv")  # adjust path to your actual employee data
    employees_df = employees_df.dropna(subset=["employee_id", "department"])
    employees_df = employees_df[employees_df["department"].isin(department_products.keys())]
 
    # employee_id -> department lookup
    emp_to_dept = dict(zip(employees_df["employee_id"], employees_df["department"]))
    employee_ids = list(emp_to_dept.keys())
 
    for i in range(1000000):
        employee_id = random.choice(employee_ids)
        department = emp_to_dept[employee_id]
 
        # pick a product that this department actually sells
        product = random.choice(department_products[department])
        unit_price = product_catalog[product]
 
        quantity = random.randint(1, 10)
        amount = quantity * unit_price
 
        # null-out product occasionally (after computing amount, so amount stays valid)
        if random.random() < 0.02:
            product = None
 
        # null-out amount occasionally, independent of product
        if random.random() < 0.04:
            amount = None
 
        sales_data.append([
            i + 1,
            employee_id,
            product,
            quantity,
            amount,
            faker.date_between(start_date="-10y", end_date="today")
        ])
 
    df = pd.DataFrame(
        sales_data,
        columns=["sale_id", "employee_id", "product","quantity", "amount", "date"]
    )
    df.to_csv("data/sales.csv", index=False)
    print("sales created")




#  #  ------------------------------------------------------------------------------------------------------------------------
                # attendance data generate by this code and save as csv file. you can run this code once to generate the data.
                #  after that you can comment out the code to avoid regenerating the data every time you run the script.
#  #  ------------------------------------------------------------------------------------------------------------------------

# def attendance():
#     employees_df = pd.read_csv("data/employee_data.csv")
#     employee_ids = employees_df["employee_id"].dropna().astype(int).tolist()
 
#     # Build the list of weekdays (Mon-Fri) over the last year — attendance only
#     # makes sense on actual working days, not weekends.
#     end_date = pd.Timestamp.today().normalize()
#     start_date = end_date - pd.DateOffset(years=1)
#     all_days = pd.date_range(start_date, end_date, freq="D")
#     workdays = [d for d in all_days if d.weekday() < 5]  # Mon=0 ... Fri=4
 
#     attendance_data = []
 
#     for employee_id in employee_ids:
#         # Each employee has their own slight "tendency" - some are consistently
#         # punctual/full-day, some run a bit short on average. Adds realistic
#         # person-to-person variation instead of every row being independent.
#         personal_avg = np.random.normal(loc=8.0, scale=0.4)
 
#         for day in workdays:
#             # Absence: ~4% chance employee didn't log hours that day (sick, leave, etc.)
#             if random.random() < 0.04:
#                 hours = None
#             else:
#                 # Most days cluster tightly around a normal ~8hr workday,
#                 # with occasional early leave / overtime as natural variation.
#                 hours = np.random.normal(loc=personal_avg, scale=1.0)
#                 hours = round(max(0, min(hours, 12)), 1)  # clip to a sane 0-12hr range
 
#                 # Small chance of a half-day (planned leave, appointment, etc.)
#                 if random.random() < 0.03:
#                     hours = round(hours / 2, 1)
 
#             attendance_data.append([
#                 employee_id,
#                 day.date(),
#                 hours
#             ])
 
#     df = pd.DataFrame(attendance_data, columns=[
#         "employee_id", "date", "attendance_hours"
#     ])
#     df.to_csv("data/attendance.csv", index=False)
#     print("Attendance created")