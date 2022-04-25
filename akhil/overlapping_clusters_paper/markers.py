import csv
import pandas as pd
import psycopg2 as pg


def main():
  conn = pg.connect(
      database='ernieplus',
  )
  cursor = conn.cursor()


  query = 'select * from aj_markers'
  sql_query = pd.read_sql_query(query, conn)
  df = pd.DataFrame(sql_query)
  df.to_csv(r'~/spring_2022_research/akhil/overlapping_clusters_paper/markers.csv', index = False)

  if conn:
    cursor.close()
    conn.close()


if __name__ == '__main__':
  main()
