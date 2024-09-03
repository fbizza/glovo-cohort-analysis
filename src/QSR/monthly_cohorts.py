from utils import retention_of_given_month, generate_completed_months
from extract_qsr_customers import get_qsr_data
import pandas as pd

def retention_since_given_period(start_date, end_date, list_of_customers_df, customer_cohort_names):
    months = generate_completed_months(start_date, end_date)
    print("Generating retention evolution for the following months: ", months)
    retentions = []
    for customer_cohort in list_of_customers_df:
        retention_list = []
        previous_month_customers = customer_cohort
        n_of_customers = customer_cohort.shape[0]
        for month in months:
            retained_customers, percentage = retention_of_given_month(previous_month_customers, n_of_customers, month)
            retention_list.append(percentage)
            previous_month_customers = retained_customers
        retentions.append(retention_list)

    df = pd.DataFrame(retentions, columns=months, index=customer_cohort_names)

    return df


# Example usage
start_date = '2024-03-01'
end_date = '2024-06-01'
qsr_customers, not_qsr_customers = get_qsr_data('2024-01-01', '2024-01-31', ["McDonald''s"], update=False)
list_of_customers_df = [qsr_customers, not_qsr_customers]
customer_cohort_names = ['QSR', 'NOT_QSR']
retention_df = retention_since_given_period(start_date, end_date, list_of_customers_df, customer_cohort_names)
print(retention_df)