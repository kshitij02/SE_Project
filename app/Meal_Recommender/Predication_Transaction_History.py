import pandas as pd
from itertools import combinations


def convert_into_list(input_str):
    return sorted(input_str.replace("'","").replace("[","").replace(" ","").replace("]","").split(","))
def every_object(list_of_list):
    for i in range(len(list_of_list)):
        list_of_list[i]=','.join(convert_into_list(list_of_list[i]))
    return list_of_list

#input string products sepearted by ',' output is dictinary 
def combination_creator(input,df):
    input=input.split(',')
    output = sum([list(map(list, combinations(input, i))) for i in range(len(input) + 1)], [])
    output=output[1:]
    out={}
    for item in output:
        item.sort()
        item=",".join(item)
        li=finding_consequents(item,df)
        for x in li:
            for y in x.split(','):
                if y in out:
                    out[y]+=1
                else:
                    out[y]=1
    return out
def finding_consequents(value,df):
    return df.loc[df['antecedents']==value]['consequents'].tolist()
def sorted_results(mydict):
    list_output=[]
    print(mydict)
    for key, value in sorted(mydict.items(), key=lambda item: item[1]):
        list_output.append(key)
#         print(key)
    return list_output[::-1]

def reterving_results_form_transaction_history(value,Absolute_Trained_Model_Path):
    df = pd.read_csv(Absolute_Trained_Model_Path + '/Associative_Rules_Data/Transaction_History_Predications.csv')
    output=combination_creator(value,df)
    return sorted_results(output)


# Unit Test
# reterving_results_form_transaction_history('coffee,flour,veal,winered,winewhite')
# reterving_results_form_transaction_history('')

