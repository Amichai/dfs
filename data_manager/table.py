import tabulate

class Table:
  def __init__(self, columns):
    self.rows = []
    self.columns = columns

  def add_row(self, dict):
    self.rows.append(dict)

  def print(self, sort_key):
    rows_to_print = []
    for row in self.rows:
      current_row = []
      for column in self.columns:
        if column in row:
          val = row[column]
          if isinstance(val, float):
            current_row.append(round(val, 2))
          else:
            current_row.append(val)
        else:
          current_row.append('')
      rows_to_print.append(current_row)


    # __import__('pdb').set_trace()
    sort_idx = self.columns.index(sort_key)


    rows_to_print_sorted = sorted(rows_to_print, key=lambda a: a[sort_idx], reverse=True)

    print(tabulate.tabulate(rows_to_print_sorted, self.columns))