from extract_qsr_customers import get_qsr_data
from compute_metrics import compute_metrics
from plot_results import plot_dictionaries
from utils import retention_since_given_period
from pprint import pprint
import os



if __name__ == "__main__":
    acquisition_start_date = '2024-01-15'
    acquisition_end_date = '2024-01-31'
    retention_start_date = acquisition_end_date
    retention_end_date = '2024-09-01'
    store_names = ["KFC", "Domino''s Pizza", "Pizza Hut", "MAX Premium Burgers", "Burger King", "Subway by AMIC Energy", "Burger King®", "Telepizza"]
    qsr_customers, not_qsr_customers, mc_donalds = get_qsr_data(acquisition_start_date, acquisition_end_date, store_names, update=False)
    mc_donalds.name = 'McDonalds'
    qsr_customers.name = 'QSR w/o McDo'
    not_qsr_customers.name = 'Not QSR'
    customers_dfs = [mc_donalds, qsr_customers, not_qsr_customers]

    # # retention cohort
    # customer_cohort_names = ['McDonalds', 'QSR w/o McDo', 'Not QSR']
    # retention_df = retention_since_given_period(retention_start_date, retention_end_date, customers_dfs, customer_cohort_names)
    # print(retention_df.to_string())

    # # save dataframe
    # output_dir = 'data/retention'
    # os.makedirs(output_dir, exist_ok=True)
    # retention_df.to_csv(os.path.join(output_dir, 'retention_df.csv'), index=True)


    # report
    metrics_dict = compute_metrics(customers_dfs)
    plot_dictionaries(metrics_dict)
    pprint(metrics_dict)

