from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def main():
    exec_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    png_output = f"/home/fmoy3/git_repo/franklin/bu_et_al_2021/clustered_bdid/img/clustered_bdid-{exec_time}"
    george_csv = pd.read_csv("/home/fmoy3/git_repo/franklin/bu_et_al_2021/bdid_samples/bu_all.csv")
    clustered_csv = pd.read_csv("/home/fmoy3/git_repo/franklin/clustered_bdid_metrics-2022-03-07-15-38-22.csv")
    clustered_csv.rename(columns={'fp_int_id': 'fp', 'cp_level': 'c.cp_level'}, inplace=True)

    # Join the two CSVs
    joined_csv = george_csv.merge(clustered_csv, how='inner', on='fp')
    joined_csv.drop(['c.cp_level'], inplace=True, axis=1)

    # Create ratio dataframes
    cp_r_citing_ratio = joined_csv['cp_r_citing_nonzero_clustered'] / joined_csv['cp_r_citing_pub_nonzero']
    tr_citing_ratio = joined_csv['tr_citing_clustered'] / joined_csv['tr_citing']
    tr_cited_ratio = joined_csv['tr_cited_clustered'] / joined_csv['tr_cited_pub']
    cp_r_cited_ratio = joined_csv['cp_r_cited_nonzero_clustered'] / joined_csv['cp_r_cited_pub_nonzero']

    # Plot the ratios
    # fig = plt.figure()
    # ax = fig.add_subplot(1,1,1)
    # ax.scatter(joined_csv['cp_level'], cp_r_citing_ratio)
    # ax.set_xscale('log')
    # plt.title('Ratio of Intra-Cluster to Intra-Network cp_r_citing_nonzero VS log(cp_level)')
    # plt.ylabel('cp_r_citing_nonzero_clustered / cp_r_citing_pub_nonzero')
    # plt.xlabel('log(cp_level)')
    # plt.savefig(f'{png_output}-0.png')
    # fig.clear()
    # ax = fig.add_subplot(1,1,1)
    # ax.scatter(joined_csv['cp_level'], tr_citing_ratio)
    # ax.set_xscale('log')
    # plt.title('Ratio of Intra-Cluster to Intra-Network tr_citing VS log(cp_level)')
    # plt.ylabel('tr_citing_clustered / tr_citing')
    # plt.xlabel('log(cp_level)')
    # plt.savefig(f'{png_output}-1.png')
    # fig.clear()
    # ax = fig.add_subplot(1,1,1)
    # ax.scatter(joined_csv['cp_level'], tr_cited_ratio)
    # ax.set_xscale('log')
    # plt.title('Ratio of Intra-Cluster to Intra-Network tr_cited VS log(cp_level)')
    # plt.ylabel('tr_cited_clustered / tr_cited')
    # plt.xlabel('log(cp_level)')
    # plt.savefig(f'{png_output}-2.png')
    # fig.clear()
    # ax = fig.add_subplot(1,1,1)
    # ax.scatter(joined_csv['cp_level'], cp_r_cited_ratio)
    # ax.set_xscale('log')
    # plt.title('Ratio of Intra-Cluster to Intra-Network cp_r_cited_nonzero VS log(cp_level)')
    # plt.ylabel('cp_r_cited_nonzero_clustered / cp_r_cited_nonzero')
    # plt.xlabel('log(cp_level)')
    # plt.savefig(f'{png_output}-3.png')
    # fig.clear()

    # Density plots (For some reason plotting them all sequentially doesn't work, Maybe I have to clear?)
    sns.set_style('whitegrid')
    # svm = sns.kdeplot(cp_r_cited_ratio)
    # fig = svm.get_figure()
    # plt.ylim(0, 15)
    # fig.suptitle('Ratio of Intra-Cluster to Intra-Network cp_r_cited_nonzero Density Plot')
    # fig.savefig(f'{png_output}-4.png', dpi=400)
    # svm = sns.kdeplot(tr_cited_ratio)
    # fig = svm.get_figure()
    # plt.ylim(0, 15)
    # fig.suptitle('Ratio of Intra-Cluster to Intra-Network tr_cited Density Plot')
    # fig.savefig(f'{png_output}-5.png', dpi=400)
    # svm = sns.kdeplot(cp_r_citing_ratio)
    # fig = svm.get_figure()
    # plt.ylim(0, 15)
    # fig.suptitle('Ratio of Intra-Cluster to Intra-Network cp_r_citing_nonzero Density Plot')
    # fig.savefig(f'{png_output}-6.png', dpi=400)
    svm = sns.kdeplot(tr_citing_ratio)
    fig = svm.get_figure()
    plt.ylim(0, 15)
    fig.suptitle('Ratio of Intra-Cluster to Intra-Network tr_citing Density Plot')
    fig.savefig(f'{png_output}-7.png', dpi=400)


if __name__ == '__main__':
    main()