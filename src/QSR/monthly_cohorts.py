from utils import retention_since_given_period
from extract_qsr_customers import get_qsr_data


# Example usage
start_date = '2024-03-01'
end_date = '2024-06-01'
qsr_customers, not_qsr_customers = get_qsr_data('2024-01-01', '2024-01-31', ["McDonald''s"], update=False)
list_of_customers_df = [qsr_customers, not_qsr_customers]
customer_cohort_names = ['QSR', 'NOT_QSR']
retention_df = retention_since_given_period(start_date, end_date, list_of_customers_df, customer_cohort_names)
print(retention_df)