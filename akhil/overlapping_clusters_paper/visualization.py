import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import statistics


def scatterplot_analysis(information, x_col, x_scale, y_col, y_scale, hue_val, output_file_path):
  df = pd.DataFrame.from_dict(information)
  
  plt.figure()
  ax = sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_val)
  #ax.invert_xaxis()
  ax.set_xscale(x_scale)
  ax.set_yscale(y_scale)
  plt.savefig(output_file_path)


def histogram_analysis(frequency_list, output_file_path, min_k_core, inclusion_criterion):
  plt.figure()
  print(min(frequency_list), max(frequency_list), statistics.median(frequency_list))
  ax = sns.displot(frequency_list, kde=False, bins=100)
  ax.set_xscale('log')
  ax.set_yscale('log')
  plt.xlabel('Num Clusters Placed Into')
  plt.ylabel('Frequency')
  plt.savefig(str(min_k_core) + '_' + str(inclusion_criterion) + '_'  + output_file_path)

