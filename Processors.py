from pickle import FALSE
import pandas as pd
import math
import os
import numpy as np
import streamlit as st

class Round:
  """
    Class for simulating each Round.
  """
  def __init__(self, excel_path, round_name: str, rename_dict=None):
    """
      Constructor of class Round.
    """

    self.data = pd.read_excel(excel_path, engine='openpyxl')

    if rename_dict != None:
      self.rename_columns(rename_dict)

    self.data.drop(columns=['Community', 'Name', 'Serial Number', 'Application Number', 'DOB'], inplace=True)
    self.name = round_name

    self._fix_alphabetical_ranks()
    self.data.sort_values(by='Rank', ignore_index=True, inplace=True)

  def rename_columns(self, rename_dict):
    self.data = self.data.rename(columns=rename_dict)

  def _fix_alphabetical_ranks(self):
    ranks = list(self.data['Rank'].copy())
    new_ranks = []

    for rank in ranks:
      try:
        new_ranks.append(int(rank))
      except ValueError:
        try:
          rank_val = int("".join([x for x in list(str(rank)) if x.isdigit()]))
          if rank_val in new_ranks:
            new_ranks.append(float(rank_val) + (new_ranks.count(rank_val)/10))
          else:
            new_ranks.append(rank_val)
        except:
          new_ranks.append(math.inf)

    self.data['Rank'] = new_ranks

  def filter(self, college_code=None, branch_code=None, community=None):
    if college_code == None and branch_code == None and community == None:
      print('No Filter Applied to RankList Data...')
      return self.data.copy()

    filtered = self.data.copy()

    if college_code:
      filtered = filtered[filtered['College Code'] == college_code]
    if branch_code:
      filtered = filtered[filtered['Branch Code'] == branch_code]
    if community:
      filtered = filtered[filtered['Allotted Community'] == community]

    return filtered


class RankList:
  """
    This class used to store and manipulate RankList data.

    RankList is the combination of data of every round.

    RankList for a given year can be created by concatenating DataFrames of all rounds in that particular year.


    Available methods:

      (i) __init__(rounds : List) -> Reference of RankList object

      (ii) filter(college_code=None : int, branch_code=None : str, community=None : str) -> pd.DataFrame (the Filtered RankList for according to the corresponding filters)

    Properties:
      data : pd.DataFrame

  """

  def __init__(self, rounds):
    """
      Constructor of RankList class.

      Parameters:
        (i) rounds : List (List of <class 'Round'> Objects)

      Return:
        Returns the reference of created RankList Object internally.
    """
    self.data = pd.DataFrame()
    for round in rounds:
      self.data = pd.concat([self.data, round.data.copy()], ignore_index=True)
    self.data.drop_duplicates(subset=['Rank'], keep='last', inplace=True)
    self.data.sort_values(by='Rank', inplace=True, ignore_index=True)

  def filter(self, college_code=None, branch_code=None, community=None):
    """
      Used to filter the RankList based on College Code, Branch Code and Community.

      Not all filters are required to be applied at the same time.


      Parameters:
        (i) college_code : int   =>   College Code of College to be filtered.
        (ii) branch_code : str   =>   Branch Code available for that particular College Code(to be filtered) and of particular Branch Code to be filtered.
        (iii) community : str    =>   Community to be filtered

      Return:
        pd.DataFrame   =>   A filtered DataFrame with applied filters.

    """
    if college_code == None and branch_code == None and community == None:
      print('No Filter Applied to RankList Data...')
      return self.data.copy()

    filtered = self.data.copy()

    if college_code:
      filtered = filtered[filtered['College Code'] == college_code]
    if branch_code:
      filtered = filtered[filtered['Branch Code'] == branch_code]
    if community:
      filtered = filtered[filtered['Allotted Community'] == community]

    return filtered


class SeatMatrix:
  def __init__(self, excel_path: str, rename_dict=None):
    self.data = pd.read_excel(excel_path, engine='openpyxl')

    if rename_dict != None:
      self.data = self.data.rename(columns=rename_dict)

    self._remove_carriage_return('College Name', 'Branch Name')

  @staticmethod
  def cast(df):
    std_columns = ['College Code',
                   'College Name',
                   'Branch Code',
                   'Branch Name',
                   'OC',
                   'BC',
                   'BCM',
                   'MBC',
                   'SC',
                   'SCA',
                   'ST']

    def _checkcols(cols1, cols2):
      for col1 in cols1:
        if col1 not in cols2:
          return False
      return True

    if type(df) == pd.DataFrame:
      if _checkcols(list(df.columns), std_columns):
        df.to_excel('temp.xlsx', index=False)
        result = SeatMatrix('temp.xlsx')
        result.data = result.data[std_columns]
        import os
        os.remove('temp.xlsx')
        result._remove_carriage_return('College Name', 'Branch Name')
        return result
      else:
        print(f'Standard columns:\t{std_columns}\nwere not present in DataFrame object.')
        return None
    else:
      print('The given data was not of type pd.DataFrame( ).')
      return None


  def _remove_carriage_return(self, *columns):
    for column in columns:
      if self.data[column].dtype == object:
        self.data[column] = self.data[column].str.replace('\r', '').replace('\n', '')
      else:
        print(f'Column {column} is not of type object.')

  def __add__(self, adder):
    if type(adder) == SeatMatrix:
      result = self.data.copy()
      for column in list(self.data.columns):
        if column in ['OC', 'BC', 'MBC', 'BCM', 'SC', 'ST', 'SCA']:
          result[column] = self.data[column] + adder.data[column]

      return SeatMatrix.cast(result)
    print('The second object is not of type SeatMatrix')
    return None

  def __sub__(self, adder):
    if type(adder) == SeatMatrix:
      result = self.data.copy()
      for column in list(self.data.columns):
        if column in ['OC', 'BC', 'MBC', 'BCM', 'SC', 'ST', 'SCA']:
          result[column] = self.data[column] - adder.data[column]

      return SeatMatrix.cast(result)
    print('The second object is not of type SeatMatrix')
    return None

  def evaluate_rounds_sm(self, rounds, path=''):
    filled = self - self
    rem = SeatMatrix.cast(self.data.copy())

    os.makedirs(f'./{path}/SeatMatrix/Remaining', exist_ok=True)
    os.makedirs(f'./{path}/SeatMatrix/Filled', exist_ok=True)

    rem.data.to_excel(f'./{path}/SeatMatrix/Remaining/Before Round(s).xlsx', index=False)
    filled.data.to_excel(f'./{path}/SeatMatrix/Filled/Before Round(s).xlsx', index=False)

    for round in rounds:
      round_filled = SeatMatrix.cast(self.data.groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
          lambda group: (
              group.assign(
                  OC=(len(round.filter(community='OC', college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))),
                  BC=(len(round.filter(community='BC', college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))),
                  BCM=(len(round.filter(community='BCM', college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))),
                  MBC=(len(round.filter(community='MBC', college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))),
                  SC=(len(round.filter(community='SC', college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))),
                  SCA=(len(round.filter(community='SCA', college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))),
                  ST=(len(round.filter(community='ST', college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])))
              )
          )
      ).reset_index(drop=True))

      rem -= round_filled
      filled += round_filled

      rem.data.to_excel(f'./{path}/SeatMatrix/Remaining/Remaining After {round.name}.xlsx', index=False)
      filled.data.to_excel(f'./{path}/SeatMatrix/Filled/Filled After {round.name}.xlsx', index=False)

    return None

  def evaluate_rounds_roundwise_collegewise(self, rounds, rank_list, cum=None, high_low_mean=None, by_filled=True, path=''):

    round_names = [round.name for round in rounds]
    if high_low_mean == True:
      temp = [[f'{names}', f'{names} Filled %', f'{names} Lowest Cutoff', f'{names} Highest Cutoff', f'{names} Average Cutoff'] for names in round_names]
    else:
      temp = [[f'{names}', f'{names} Filled %'] for names in round_names]
    round_std = [j for i in temp for j in i]

    round_std = ['College Code', 'College Name'] + round_std + ['Total Available' ,'Total Filled', 'Total % Filled']

    if high_low_mean == True:
      val = self.data.drop(columns=['Branch Name', 'Branch Code', 'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']).groupby(['College Code', 'College Name']).apply(
                lambda group : (group.assign(
                        **{x.name : (len(x.filter(college_code=group['College Code'].iloc[0]))) for x in rounds},
                        Total_Available = self.filter(college_code=group['College Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum(),
                        **{f'{x.name} Filled %' : 0 if (temp := (len(rank_list.filter(college_code=group['College Code'].iloc[0])) if by_filled else self.filter(college_code=group['College Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum())) == 0 else ((len(x.filter(college_code=group['College Code'].iloc[0])) / temp)*100) for x in rounds},
                        TEMP1 = 0,
                        **{f'{x.name} Lowest Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0])) == 0 else temp['Cutoff Mark'].min() for x in rounds},
                        TEMP2 = 0,
                        **{f'{x.name} Highest Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0])) == 0 else temp['Cutoff Mark'].max() for x in rounds},
                        TEMP3 = 0,
                        **{f'{x.name} Average Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0])) == 0 else temp['Cutoff Mark'].mean() for x in rounds}

            ))).drop(columns=['College Code', 'College Name', 'TEMP1', 'TEMP2', 'TEMP3']).reset_index(level=[2], drop=True).reset_index().drop_duplicates().reset_index(drop=True)


    else:
      val = self.data.drop(columns=['Branch Name', 'Branch Code', 'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']).groupby(['College Code', 'College Name']).apply(
          lambda group : (group.assign(
                  **{x.name : (len(x.filter(college_code=group['College Code'].iloc[0]))) for x in rounds},
                  Total_Available = self.filter(college_code=group['College Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum(),
                  **{f'{x.name} Filled %' : 0 if (temp := (len(rank_list.filter(college_code=group['College Code'].iloc[0])) if by_filled else self.filter(college_code=group['College Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum())) == 0 else ((len(x.filter(college_code=group['College Code'].iloc[0])) / temp)*100) for x in rounds},
          ))
      ).drop(columns=['College Code', 'College Name']).reset_index(level=[2], drop=True).reset_index().drop_duplicates().reset_index(drop=True)


    val = val.rename(columns={'Total_Available' : 'Total Available'})

    val['Total Filled'] = val[round_names].sum(axis=1)
    val['Total % Filled'] = (val['Total Filled'] / val['Total Available']) * 100

    val = val[round_std]

    if len(rounds) > 1 and cum == True:
      round_filled_names = [f'{round} Filled %' for round in round_names]
      for ind, round_filled_name in enumerate(round_filled_names[1:]):
        val[round_filled_names[ind + 1]] = val[round_filled_names[ind + 1]] + val[round_filled_names[ind]]
    elif cum == True and len(rounds) == 1:
      print('Cannot Cumulate for One Round...')

    path = f'./{path}'
    os.makedirs(path, exist_ok=True)

    path += '/College-wise'
    os.makedirs(path, exist_ok=True)
    if by_filled:
      if cum:
        val.to_excel(path + '/College-wise Round-wise Filling - By Filled - Cumulative.xlsx', index=False)
      else:
        val.to_excel(path + '/College-wise Round-wise Filling - By Filled - Non-Cumulative.xlsx', index=False)
    else:
      if cum:
        val.to_excel(path + '/College-wise Round-wise Filling - By Total - Cumulative.xlsx', index=False)
      else:
        val.to_excel(path + '/College-wise Round-wise Filling - By Total - Non-Cumulative.xlsx', index=False)

    return val

  def evaluate_rounds_roundwise_collegewise_branchwise(self, rounds, rank_list, cum=None, high_low_mean=None, by_filled=True, path=''):

    round_names = [round.name for round in rounds]
    if high_low_mean == True:
      temp = [[f'{names}', f'{names} Filled %', f'{names} Lowest Cutoff', f'{names} Highest Cutoff', f'{names} Average Cutoff'] for names in round_names]
    else:
      temp = [[f'{names}', f'{names} Filled %'] for names in round_names]
    round_std = [j for i in temp for j in i]

    round_std = ['College Code', 'College Name', 'Branch Code', 'Branch Name'] + round_std + ['Total Available' ,'Total Filled', 'Total % Filled']


    if high_low_mean == True:
      val = self.data.drop(columns=['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']).groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
          lambda group : (group.assign(
                  **{x.name : (len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))) for x in rounds},
                  Total_Available = self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum(),
                  **{f'{x.name} Filled %' : 0 if (temp := (len(rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) if by_filled else self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum())) == 0 else ((len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) / temp)*100) for x in rounds},
                  TEMP1 = 0,
                  **{f'{x.name} Lowest Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) == 0 else temp['Cutoff Mark'].min() for x in rounds},
                  TEMP2 = 0,
                  **{f'{x.name} Highest Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) == 0 else temp['Cutoff Mark'].max() for x in rounds},
                  TEMP3 = 0,
                  **{f'{x.name} Average Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) == 0 else temp['Cutoff Mark'].mean() for x in rounds}
          ))
      ).drop(columns=['College Code', 'College Name', 'Branch Code', 'Branch Name', 'TEMP1', 'TEMP2', 'TEMP3']).reset_index(level=[4], drop=True).reset_index().drop_duplicates().reset_index(drop=True)

    else:
      val = self.data.drop(columns=['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']).groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
          lambda group : (group.assign(
                  **{x.name : (len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0]))) for x in rounds},
                  Total_Available = self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum(),
                  **{f'{x.name} Filled %' : 0 if (temp := (len(rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) if by_filled else self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum())) == 0 else ((len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) / temp)*100) for x in rounds}
          ))
      ).drop(columns=['College Code', 'College Name', 'Branch Code', 'Branch Name']).reset_index(level=[4], drop=True).reset_index().drop_duplicates().reset_index(drop=True)



    val = val.rename(columns={'Total_Available' : 'Total Available'})

    val['Total Filled'] = val[round_names].sum(axis=1)
    val['Total % Filled'] = (val['Total Filled'] / val['Total Available']) * 100

    val = val[round_std]

    if len(rounds) > 1 and cum != None:
      round_filled_names = [f'{round} Filled %' for round in round_names]
      for ind, round_filled_name in enumerate(round_filled_names[1:]):
        val[round_filled_names[ind + 1]] = val[round_filled_names[ind + 1]] + val[round_filled_names[ind]]
    elif cum == True and len(rounds) == 1:
      print('Cannot Cumulate for One Round...')
      return val

    path = f'./{path}'
    os.makedirs(path, exist_ok=True)

    path += '/College-wise Branch-wise'
    os.makedirs(path, exist_ok=True)

    if by_filled:
      if cum:
        val.to_excel(path + '/College-wise Branch-wise Round-wise Filling - By Filled - Cumulative.xlsx', index=False)
      else:
        val.to_excel(path + '/College-wise Branch-wise Round-wise Filling - By Filled - Non-Cumulative.xlsx', index=False)
    else:
      if cum:
        val.to_excel(path + '/College-wise Branch-wise Round-wise Filling - By Total - Cumulative.xlsx', index=False)
      else:
        val.to_excel(path + '/College-wise Branch-wise Round-wise Filling - By Total - Non-Cumulative.xlsx', index=False)

    return val

  def evaluate_rounds_roundwise_collegewise_branchwise_communitywise(self, rounds, rank_list, community, by_filled=True, high_low_mean=False, cum=None, path=''):
    round_names = [round.name for round in rounds]

    communities = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']
    comm_dropped = [com for com in communities if com != community]

    if high_low_mean == True:
      temp = [[f'{names}', f'{names} Filled %', f'{names} Lowest Cutoff', f'{names} Highest Cutoff', f'{names} Average Cutoff'] for names in round_names]
    else:
      temp = [[f'{names}', f'{names} Filled %'] for names in round_names]
    round_std = [j for i in temp for j in i]

    round_std = ['College Code', 'College Name', 'Branch Code', 'Branch Name'] + round_std + ['Total Available' ,'Total Filled', 'Total % Filled']


    if high_low_mean == True:
      val = self.data.drop(columns=comm_dropped).groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
          lambda group : (group.assign(
                  **{x.name : (len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community))) for x in rounds},
                  Total_Available = self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community).tolist()[-1],
                  **{f'{x.name} Filled %' : 0 if (temp := (len(rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community)) if by_filled else self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community).tolist()[-1])) == 0 else ((len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community)) / temp)*100) for x in rounds},
                  TEMP1 = 0,
                  **{f'{x.name} Lowest Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community)) == 0 else temp['Cutoff Mark'].min() for x in rounds},
                  TEMP2 = 0,
                  **{f'{x.name} Highest Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community)) == 0 else temp['Cutoff Mark'].max() for x in rounds},
                  TEMP3 = 0,
                  **{f'{x.name} Average Cutoff' : 0 if len(temp := x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community)) == 0 else temp['Cutoff Mark'].mean() for x in rounds}
          ))
      ).drop(columns=['College Code', 'College Name', 'Branch Code', 'Branch Name', 'TEMP1', 'TEMP2', 'TEMP3', community]).reset_index(level=[4], drop=True).reset_index().drop_duplicates().reset_index(drop=True)

    else:
      val = self.data.drop(columns=comm_dropped).groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
          lambda group : (group.assign(
                  **{x.name : (len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community))) for x in rounds},
                  Total_Available = self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community).tolist()[-1],
                  **{f'{x.name} Filled %' : 0 if (temp := (len(rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community)) if by_filled else self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community).tolist()[-1])) == 0 else ((len(x.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=community)) / temp)*100) for x in rounds}
          ))
      ).drop(columns=['College Code', 'College Name', 'Branch Code', 'Branch Name', community]).reset_index(level=[4], drop=True).reset_index().drop_duplicates().reset_index(drop=True)



    val = val.rename(columns={'Total_Available' : 'Total Available'})

    val['Total Filled'] = val[round_names].sum(axis=1)
    val['Total % Filled'] = (val['Total Filled'] / val['Total Available']) * 100

    val = val[round_std]

    if len(rounds) > 1 and cum != None:
      round_filled_names = [f'{round} Filled %' for round in round_names]
      for ind, round_filled_name in enumerate(round_filled_names[1:]):
        val[round_filled_names[ind + 1]] = val[round_filled_names[ind + 1]] + val[round_filled_names[ind]]
    elif cum == True and len(rounds) == 1:
      print('Cannot Cumulate for One Round...')
      return val

    path = f'./{path}'
    os.makedirs(path, exist_ok=True)

    path += '/College-wise Branch-wise Community-wise'
    os.makedirs(path, exist_ok=True)

    path += f'/{community}'
    os.makedirs(path, exist_ok=True)

    if by_filled:
      if cum:
        val.to_excel(path + '/College-wise Branch-wise Community-wise Round-wise Filling - By Filled - Cumulative.xlsx', index=False)
      else:
        val.to_excel(path + '/College-wise Branch-wise Community-wise Round-wise Filling - By Filled - Non-Cumulative.xlsx', index=False)
    else:
      if cum:
        val.to_excel(path + '/College-wise Branch-wise Community-wise Round-wise Filling - By Total - Cumulative.xlsx', index=False)
      else:
        val.to_excel(path + '/College-wise Branch-wise Community-wise Round-wise Filling - By Total - Non-Cumulative.xlsx', index=False)

    return val


  def evaluate_rounds_communitywise(self, rank_list, path=''):
    val = self.data.drop(columns=['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST', 'Branch Code', 'Branch Name']).groupby(['College Code', 'College Name']).apply(
    lambda group : (group.assign(
        OC = (oc := len(rank_list.filter(college_code=group['College Code'].iloc[0], community='OC'))),
        BC = (bc := len(rank_list.filter(college_code=group['College Code'].iloc[0], community='BC'))),
        BCM = (bcm := len(rank_list.filter(college_code=group['College Code'].iloc[0], community='BCM'))),
        MBC = (mbc := len(rank_list.filter(college_code=group['College Code'].iloc[0], community='MBC'))),
        SC = (sc := len(rank_list.filter(college_code=group['College Code'].iloc[0], community='SC'))),
        SCA = (sca := len(rank_list.filter(college_code=group['College Code'].iloc[0], community='SCA'))),
        ST = (st := len(rank_list.filter(college_code=group['College Code'].iloc[0], community='ST'))),
        Total_Filled = (filled := oc + bc + bcm + mbc + sc + sca + st),
        Total_Available = self.filter(college_code=group['College Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum(),
        OC_Percent = 0 if filled == 0 else (oc/filled) * 100,
        BC_Percent = 0 if filled == 0 else (bc/filled) * 100,
        BCM_Percent = 0 if filled == 0 else (bcm/filled) * 100,
        MBC_Percent = 0 if filled == 0 else (mbc/filled) * 100,
        SC_Percent = 0 if filled == 0 else (sc/filled) * 100,
        SCA_Percent = 0 if filled == 0 else (sca/filled) * 100,
        ST_Percent = 0 if filled == 0 else (st/filled) * 100
    ))
    ).reset_index(level=[2], drop=True).drop(columns=['College Code', 'College Name']).reset_index().drop_duplicates().reset_index(drop=True).rename(columns={
        'Total_Filled' : 'Total Filled',
        'Total_Available' : 'Total Available',
        'OC_Percent' : 'OC Filled %',
        'BC_Percent' : 'BC Filled %',
        'BCM_Percent' : 'BCM Filled %',
        'MBC_Percent' : 'MBC Filled %',
        'SC_Percent' : 'SC Filled %',
        'SCA_Percent' : 'SCA Filled %',
        'ST_Percent' : 'ST Filled %'
    })

    communities = ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']
    temp = [[f'{community}', f'{community} Filled %'] for community in communities]
    std_cols = [j for i in temp for j in i]

    std_cols =  ['College Code', 'College Name'] + std_cols + ['Total Filled', 'Total Available']

    val = val[std_cols]

    os.makedirs(f'./{path}/Community-wise Analysis', exist_ok=True)

    val.to_excel(f'./{path}/Community-wise Analysis/College-wise Community Distribution.xlsx', index=False)

    return val

  def filter(self, college_code=None, branch_code=None, community=None):
    if college_code == None and branch_code == None and community == None:
      print('No Filter Applied to SeatMatrix Data...')
      return self.data.copy()

    filtered = self.data.copy()

    if college_code:
      filtered = filtered[filtered['College Code'] == college_code]
    if branch_code:
      filtered = filtered[filtered['Branch Code'] == branch_code]
    if community in ['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']:
      filtered = filtered[community]

    return filtered

  def run_all_pipeline(self, rounds, rank_list, communities, path):
    self.evaluate_rounds_sm(rounds, path=path)


    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=True, path=path)
    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=True, path=path)


    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=True, path=path)
    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=True, path=path)

    for community in communities:
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=False, by_filled=False, path=path)
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=False, by_filled=True, path=path)
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=True, by_filled=False, path=path)
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=True, by_filled=True, path=path)

    self.evaluate_rounds_communitywise(rank_list, path=path)

  def run_sm_pipeline(self, rounds, path=''):
    self.evaluate_rounds_sm(rounds, path=path)

  def run_collegewise_pipeline(self, rounds, rank_list, path=''):
    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=True, path=path)
    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=True, path=path)

  def run_collegewise_branchwise_pipeline(self, rounds, rank_list, path=''):
    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=False, by_filled=True, path=path)
    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=False, path=path)
    self.evaluate_rounds_roundwise_collegewise_branchwise(rounds, rank_list, high_low_mean=True, cum=True, by_filled=True, path=path)
  
  def run_collegewise_branchwise_communitywise_pipeline(self, rounds, rank_list, path=''):
    
    communities = list(rank_list['Allotted Community'].unique)
    print(type(communities))

    for community in communities:
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=False, by_filled=False, path=path)
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=False, by_filled=True, path=path)
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=True, by_filled=False, path=path)
      self.evaluate_rounds_roundwise_collegewise_branchwise_communitywise(rounds, rank_list, community=community, high_low_mean=True, cum=True, by_filled=True, path=path)

  def run_communitywise_pipeline(self, rank_list, path=''):
    self.evaluate_rounds_communitywise(rank_list, path=path)

  def form1(self, rounds, rank_list):
    by_filled = True
    cum = True

    round_names = [round.name for round in rounds]
    val = self.data.drop(columns=['Branch Name', 'Branch Code', 'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']).groupby(['College Code', 'College Name']).apply(
              lambda group : (group.assign(
                      **{x.name : (len(x.filter(college_code=group['College Code'].iloc[0]))) for x in rounds},
                      Total_Available = self.filter(college_code=group['College Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum(),
                      **{f'{x.name} Filled %' : 0 if (temp := (len(rank_list.filter(college_code=group['College Code'].iloc[0])) if by_filled else self.filter(college_code=group['College Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum().sum())) == 0 else ((len(x.filter(college_code=group['College Code'].iloc[0])) / temp)*100) for x in rounds},
                      TEMP=0,
                      **{f'Opening Rank for {x.name}' : x.filter(college_code=group['College Code'].iloc[0])['Rank'].min() for x in rounds},
                      TEMP1=0,
                      **{f'Closing Rank for {x.name}' : x.filter(college_code=group['College Code'].iloc[0])['Rank'].max() for x in rounds},
                      TEMP2=0,
                      Average_Cutoff = rank_list.filter(college_code=group['College Code'].iloc[0])['Cutoff Mark'].mean()
              ))
          ).drop(columns=['College Code', 'College Name']).reset_index(level=[2], drop=True).reset_index().drop_duplicates().reset_index(drop=True)

    val['Total Filled'] = val[round_names].sum(axis=1)
    val['Remaining Seats'] = val['Total_Available'] - val['Total Filled']
    val['Remaining %'] = (val['Remaining Seats'] / val['Total_Available']) * 100

    for col in val.columns:
      if '_' in col:
        val = val.rename(columns={col : col.replace('_', ' ')})

    if len(rounds) > 1 and cum == True:
      round_filled_names = [f'{names} Filled %' for names in round_names]
      for ind, round_filled_name in enumerate(round_filled_names[1:]):
        val[round_filled_names[ind + 1]] = val[round_filled_names[ind + 1]] + val[round_filled_names[ind]]

      round_open_names = [f'Opening Rank for {name}' for name in round_names]

    elif cum == True and len(rounds) == 1:
      print('Cannot Cumulate for One Round...')

    std_cols = [[name, f'{name} Filled %', f'Opening Rank for {name}', f'Closing Rank for {name}'] for name in round_names]
    new = []

    for x in std_cols:
      for y in x:
        new.append(y)

    new = ['College Code', 'College Name'] + new + ['Total Filled' , 'Remaining Seats', 'Remaining %', 'Total Available', 'Average Cutoff']

    val = val[new]
        
    val = val.fillna(0)

    for col in val.columns:
      if col == 'Average Cutoff':
        pass
      elif '%' not in col and val[col].dtype != object and 'Rank' not in col:
        val[col] = val[col].astype(int)
    

    os.makedirs(f'./{st.session_state.year}', exist_ok=True)
    os.makedirs(f'./{st.session_state.year}/Forms', exist_ok=True)
    val.to_excel(f'./{st.session_state.year}/Forms/Form 1.xlsx', index=False)
  
  def form2(self, rounds, rank_list):
    import numpy as np
    round_names = [round.name for round in rounds]
    cum = True

    val = self.data.groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
        lambda group : group.assign(
            Total_Available=self.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])[['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST']].sum(axis=1),
            **{round.name : len(round.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])) for round in rounds},
            TEMP=0,
            Highest_Cutoff = rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])['Cutoff Mark'].max(),
            Lowest_Cutoff = rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])['Cutoff Mark'].min(),
            Average_Cutoff = rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0])['Cutoff Mark'].mean(),    
        )
    )

    val = val.drop(columns=['College Code', 'College Name', 'Branch Code', 'Branch Name']).reset_index(level=[4], drop=True).reset_index().rename(
        columns={col : col.replace('_', ' ') for col in val.columns if '_' in col}
    )

    for name in round_names:
      val[f'{name} Filled %'] = (val[name] / val['Total Available']) * 100

    for col in val.columns:
      if '%' in col:
        val[col] = val[col].astype(np.float16)

    if len(rounds) > 1 and cum == True:
      round_filled_names = [f'{names}' for names in round_names]
      for ind, round_filled_name in enumerate(round_filled_names[1:]):
        val[round_filled_names[ind + 1]] = val[round_filled_names[ind + 1]] + val[round_filled_names[ind]]

      round_filled_names = [f'{names} Filled %' for names in round_names]
      for ind, round_filled_name in enumerate(round_filled_names[1:]):
        val[round_filled_names[ind + 1]] = val[round_filled_names[ind + 1]] + val[round_filled_names[ind]]

    elif cum == True and len(rounds) == 1:
      print('Cannot Cumulate for One Round...')

    round_cols = [f'{name} Filled %' for name in round_names]
    std_cols = ['College Code', 'College Name', 'Branch Code', 'Branch Name', 'OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST', 'Total Available'] + round_cols + ['Highest Cutoff', 'Lowest Cutoff', 'Average Cutoff']

    val = val[std_cols]
    
    val.to_excel(f'./{st.session_state.year}/Forms/Form 2.xlsx', index=False)

  def form3(self, rounds, rank_list):
    import numpy as np
    val = self.data.melt(id_vars=['College Code', 'College Name', 'Branch Code', 'Branch Name'],
            value_vars=['OC', 'BC', 'BCM', 'MBC', 'SC', 'SCA', 'ST'],
            var_name='Community',
            value_name='Seats Available').drop(columns=['Seats Available'])

    val = val.groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name', 'Community']).apply(lambda group : group.assign(
        Opening_Rank = rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=group['Community'].iloc[0])['Rank'].min(),
        Closing_Rank = rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=group['Community'].iloc[0])['Rank'].max(),
        Opening_Cutoff = rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=group['Community'].iloc[0])['Cutoff Mark'].max(),
        Closing_Cutoff = rank_list.filter(college_code=group['College Code'].iloc[0], branch_code=group['Branch Code'].iloc[0], community=group['Community'].iloc[0])['Cutoff Mark'].min()
    )).drop(
            columns=['College Code', 'College Name', 'Branch Code', 'Branch Name']
          ).reset_index(level=[4], drop=True).reset_index()

    val = val.rename(columns={col : col.replace('_', " ") for col in val.columns})
    val = val[['College Code', 'College Name', 'Branch Code', 'Branch Name', 'Community', 'Opening Rank', 'Opening Cutoff', 'Closing Rank', 'Closing Cutoff']]

    for col in val.columns:
      if 'Rank' in col:
        val[col] = val[col].astype(str)
        val[col] = val[col].str.replace('.0', '')

    val = val.sort_values(by='Community').groupby(['College Code', 'College Name', 'Branch Code', 'Branch Name']).apply(
        lambda x : x.assign(TEMP=0)
    ).reset_index(level=[4], drop=True).drop(columns=['College Code', 'College Name', 'Branch Code', 'Branch Name', 'TEMP']).reset_index()

    val.to_excel(f'./{st.session_state.year}/Forms/Form 3.xlsx', index=False)

def Process(options):
  import time

  rename_dict = {
      'COMMUNI\rTY' : 'Community',
      'AGGR\rMARK' : 'Cutoff Mark',
      'COLLEGE\rCODE' : 'College Code',
      'BRANCH\rCODE' : 'Branch Code',
      'ALLOTTED\rCATEGORY' : 'Allotted Community',
      'RANK' : 'Rank',
      'NAME OF THE CANDIDATE' : 'Name',
      'S NO' : 'Serial Number',
      'APPLN NO' : 'Application Number'
    }

  sm_rename_dict = {
    'COLLEGE\rCODE' : 'College Code',
    'COLLEGE NAME' : 'College Name',
    'BRANCH' : 'Branch Code',
    'BRANCH NAME' : 'Branch Name'
  }

  with st.spinner('Evaluating Selected Options'):
    time.sleep(3)

  with st.status('Simulating Rounds, SeatMatrix and RankList as Objects') as status:
    time.sleep(3)

    if not st.session_state.get('round_objs'):
      status.update(label='Simulating Rounds', state='running')
      rounds = []
      for i in range(st.session_state.rounds):
        rounds.append(Round(f'Inputs/RankList {i+1}.xlsx', f'Round {i+1}', rename_dict=rename_dict))
      st.session_state.round_objs = rounds
      status.update(label='Simulating Rounds Completed...', state='complete')
      time.sleep(2)
    else:
      status.update(label='Loading Cached Rounds', state='running')
      time.sleep(3)
      status.update(label='Loaded Cached Rounds Successfully', state='complete')
      time.sleep(2)


    if not st.session_state.get('seat_matrix'):
      status.update(label='Simulating SeatMatrix', state='running')
      seat_matrix = SeatMatrix('Inputs/SeatMatrix.xlsx', rename_dict=sm_rename_dict)
      st.session_state.seat_matrix = seat_matrix
      status.update(label='Simulating SeatMatrix Completed...', state='complete')
      time.sleep(2)
    else:
      status.update(label='Loading Cached SeatMatrix', state='running')
      time.sleep(3)
      status.update(label='Loaded Cached SeatMatrix Successfully', state='complete')
      time.sleep(2)

    if not st.session_state.get('rank_list'):
      status.update(label='Simulating RankList', state='running')
      rank_list = RankList(rounds=st.session_state.round_objs)
      st.session_state.rank_list = rank_list
      status.update(label='Simulating RankList Completed...', state='complete')
      time.sleep(2)
    else:
      status.update(label='Loading Cached RankList', state='running')
      time.sleep(3)
      status.update(label='Loaded Cached RankList Successfully', state='complete')
      time.sleep(2)

    status.update(label='Simulation Complete', state='complete', expanded=False)

  path = f'{st.session_state.year}'

  with st.spinner('Processing Selected Options'):
    for option in options:
      if option == 'SeatMatrix Round-wise':
        with st.spinner('Processing SeatMatrix Pipeline'):
          st.session_state.seat_matrix.run_sm_pipeline(rounds=st.session_state.round_objs, path=path)
      
      if option == 'College-wise Round-wise':
        with st.spinner('Processing College-wise Pipeline'):
          st.session_state.seat_matrix.run_collegewise_pipeline(rounds=st.session_state.round_objs, rank_list=st.session_state.rank_list, path=path)
      
      if option == 'College-wise Branch-wise Round-wise':
        with st.spinner('Processing College-wise Branch-wise Pipeline'):
          st.session_state.seat_matrix.run_collegewise_branchwise_pipeline(rounds=st.session_state.round_objs, rank_list=st.session_state.rank_list, path=path)

      if option == 'College-wise Branch-wise Community-wise Round-wise':
        with st.spinner('Processing College-wise Branch-wise Community-wise Pipeline'):
          st.session_state.seat_matrix.run_collegewise_branchwise_communitywise_pipeline(rounds=st.session_state.round_objs, rank_list=st.session_state.rank_list, path=path)
      
      if option == 'Community-wise Analysis':
        with st.spinner('Processing Community-wise Analysis Pipeline'):
          st.session_state.seat_matrix.run_communitywise_pipeline(rank_list=st.session_state.rank_list, path=path)

  st.success('Processing Complete for Selected Options...')

def runForms():

  rename_dict = {
      'COMMUNI\rTY' : 'Community',
      'AGGR\rMARK' : 'Cutoff Mark',
      'COLLEGE\rCODE' : 'College Code',
      'BRANCH\rCODE' : 'Branch Code',
      'ALLOTTED\rCATEGORY' : 'Allotted Community',
      'RANK' : 'Rank',
      'NAME OF THE CANDIDATE' : 'Name',
      'S NO' : 'Serial Number',
      'APPLN NO' : 'Application Number'
    }

  sm_rename_dict = {
    'COLLEGE\rCODE' : 'College Code',
    'COLLEGE NAME' : 'College Name',
    'BRANCH' : 'Branch Code',
    'BRANCH NAME' : 'Branch Name'
  }
  import time
  with st.status('Simulating Rounds, SeatMatrix and RankList as Objects') as status:
    time.sleep(3)

    if not st.session_state.get('round_objs'):
      status.update(label='Simulating Rounds', state='running')
      rounds = []
      for i in range(st.session_state.rounds):
        rounds.append(Round(f'Inputs/RankList {i+1}.xlsx', f'Round {i+1}', rename_dict=rename_dict))
      st.session_state.round_objs = rounds
      status.update(label='Simulating Rounds Completed...', state='complete')
      time.sleep(2)
    else:
      status.update(label='Loading Cached Rounds', state='running')
      time.sleep(3)
      status.update(label='Loaded Cached Rounds Successfully', state='complete')
      time.sleep(2)


    if not st.session_state.get('seat_matrix'):
      status.update(label='Simulating SeatMatrix', state='running')
      seat_matrix = SeatMatrix('Inputs/SeatMatrix.xlsx', rename_dict=sm_rename_dict)
      st.session_state.seat_matrix = seat_matrix
      status.update(label='Simulating SeatMatrix Completed...', state='complete')
      time.sleep(2)
    else:
      status.update(label='Loading Cached SeatMatrix', state='running')
      time.sleep(3)
      status.update(label='Loaded Cached SeatMatrix Successfully', state='complete')
      time.sleep(2)

    if not st.session_state.get('rank_list'):
      status.update(label='Simulating RankList', state='running')
      rank_list = RankList(rounds=st.session_state.round_objs)
      st.session_state.rank_list = rank_list
      status.update(label='Simulating RankList Completed...', state='complete')
      time.sleep(2)
    else:
      status.update(label='Loading Cached RankList', state='running')
      time.sleep(3)
      status.update(label='Loaded Cached RankList Successfully', state='complete')
      time.sleep(2)

    status.update(label='Simulation Complete', state='complete', expanded=False)

  with st.spinner('Processing Required Forms'):
    with st.spinner('Processing Form 1'):
      st.session_state.seat_matrix.form1(st.session_state.round_objs, st.session_state.rank_list)
    with st.spinner('Processing Form 2'):
      st.session_state.seat_matrix.form2(st.session_state.round_objs, st.session_state.rank_list)
    with st.spinner('Processing Form 3'):
      st.session_state.seat_matrix.form3(st.session_state.round_objs, st.session_state.rank_list)
  
  st.toast('Completed Processing for Required Forms...')