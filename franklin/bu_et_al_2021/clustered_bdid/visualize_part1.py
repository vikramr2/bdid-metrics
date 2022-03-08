from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd


def main():
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    csv_out = f"clustered_bdid-{exec_time}.csv"
    png_output = f"clustered_bdid-{exec_time}"
    in_csv = pd.read_csv("fmoy3_clustered_bdid-2022-02-26-20-10-48.csv")
    sample_csv = pd.read_csv("/srv/local/shared/external/dbid/franklins_sample.csv")

    # Average everything by cluster_id
    avg_csv = in_csv.drop(['fp_int_id'], axis=1)
    avg_csv = in_csv.groupby(['fp_cluster_id']).mean()

    # avg_csv.to_csv(csv_out)

    # Join avg_csv with each cluster's cluster size
    sample_csv = sample_csv.drop(['V1', 'gp'], axis=1)
    sample_csv.rename(columns={'V2': 'fp_cluster_id', 'N': 'cluster_size'}, inplace=True)
    avg_csv = avg_csv.merge(sample_csv, on='fp_cluster_id', how='inner')

    # Visualize all averages
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.scatter(avg_csv['cluster_size'], avg_csv['num_citing_edges_from_same_cluster'], figure=fig)
    ax.set_xscale('log')
    plt.ylabel('Average citing edges from same cluster')
    plt.xlabel('log(Cluster Size)')
    plt.savefig(f'{png_output}-0.png')
    fig.clear()
    ax = fig.add_subplot(1,1,1)
    ax.scatter(avg_csv['cluster_size'], avg_csv['num_citing_nodes_from_same_cluster'], figure=fig)
    ax.set_xscale('log')
    plt.ylabel('Average citing nodes from same cluster')
    plt.xlabel('log(Cluster Size)')
    plt.savefig(f'{png_output}-1.png')
    fig.clear()
    ax = fig.add_subplot(1,1,1)
    ax.scatter(avg_csv['cluster_size'], avg_csv['num_cited_nodes_from_same_cluster'], figure=fig)
    ax.set_xscale('log')
    plt.ylabel('Average cited nodes from same cluster')
    plt.xlabel('log(Cluster Size)')
    plt.savefig(f'{png_output}-2.png')
    fig.clear()
    ax = fig.add_subplot(1,1,1)
    ax.scatter(avg_csv['cluster_size'], avg_csv['tr_citing_both_from_same_cluster'], figure=fig)
    ax.set_xscale('log')
    plt.ylabel('Average tr_citing from same cluster')
    plt.xlabel('log(Cluster Size)')
    plt.savefig(f'{png_output}-3.png')
    fig.clear()
    ax = fig.add_subplot(1,1,1)
    ax.scatter(avg_csv['cluster_size'], avg_csv['tr_cited_both_from_same_cluster'], figure=fig)
    ax.set_xscale('log')
    plt.ylabel('Average tr_cited from same cluster')
    plt.xlabel('log(Cluster Size)')
    plt.savefig(f'{png_output}-4.png')
    fig.clear()
    ax = fig.add_subplot(1,1,1)
    ax.scatter(avg_csv['cluster_size'], avg_csv['cp_citing_nonzero_from_same_cluster'], figure=fig)
    ax.set_xscale('log')
    plt.ylabel('Average cp_citing_nonzero from same cluster')
    plt.xlabel('log(Cluster Size)')
    plt.savefig(f'{png_output}-5.png')
    fig.clear()
    ax = fig.add_subplot(1,1,1)
    ax.scatter(avg_csv['cluster_size'], avg_csv['cp_cited_nonzero_from_same_cluster'], figure=fig)
    ax.set_xscale('log')
    plt.ylabel('Average cp_cited_nonzero from same cluster')
    plt.xlabel('log(Cluster Size)')
    plt.savefig(f'{png_output}-6.png')
    fig.clear()


if __name__ == '__main__':
    main()