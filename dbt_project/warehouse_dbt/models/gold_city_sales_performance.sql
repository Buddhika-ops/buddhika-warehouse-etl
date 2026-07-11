

SELECT 
    e.city,

    SUM(s.amount) AS total_sales_amount,

    COUNT(DISTINCT(s.employee_id)) AS num_employees,

    ROUND(
        SUM(s.amount)/ COUNT(DISTINCT(s.employee_id))
    ) AS avg_sales_per_employee,

    SUM(s.quantity) AS total_quantity_sold,

    COUNT(DISTINCT(s.sale_id)) as total_transactions,

FROM {{source('silver','silver_sales')}} AS s
LEFT JOIN {{source('silver','silver_employees')}} as e
ON s.employee_id = e.employee_id
GROUP BY e.city

