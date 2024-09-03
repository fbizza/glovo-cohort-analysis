from extract_qsr_customers import get_qsr_data
from compute_metrics import compute_metrics
from plot_results import plot_dictionaries
from utils import retention_since_given_period
import os



if __name__ == "__main__":
    acquisition_start_date = '2024-01-01'
    acquisition_end_date = '2024-01-31'
    retention_start_date = acquisition_end_date
    retention_end_date = '2024-09-01'
    store_names = ["McDonald''s", "KFC", "Domino''s Pizza", "Pizza Hut", "MAX Premium Burgers", "Burger King", "Subway by AMIC Energy", "Burger King®"]
    qsr_customers, not_qsr_customers = get_qsr_data(acquisition_start_date, acquisition_end_date, store_names, update=True)
    qsr_customers.name = 'qsr_customers'
    not_qsr_customers.name = 'not_qsr_customers'
    customers_dfs = [qsr_customers, not_qsr_customers]

    # retention cohort
    customer_cohort_names = ['QSR', 'NOT_QSR']
    retention_df = retention_since_given_period(retention_start_date, retention_end_date, customers_dfs, customer_cohort_names)
    print(retention_df)

    # save dataframe
    output_dir = 'data/retention'
    os.makedirs(output_dir, exist_ok=True)
    retention_df.to_csv(os.path.join(output_dir, 'retention_df.csv'), index=True)


    # report
    metrics_dict = compute_metrics(customers_dfs)
    plot_dictionaries(metrics_dict)
