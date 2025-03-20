import pandas as pd
import json
import threading
def row2json(df,i):
    json_data={}
    for j in range(7):
        key=df.iloc[0,j]
        value=[df.iloc[i,j]]
        json_data[key]=value
    if type(json_data["Date"][0])==str:
        json_data["Date"][0]=json_data["Date"][0].split(" ")[0]
    else:
        json_data["Date"][0]="1900-01-01"
    json_data["Brand"][0]="nan"
    json_data["AST"]=[]
    for j in range(7,35):
        key=df.iloc[0,j]
        value=[df.iloc[i,j]]
        json_data["AST"].append({key:value})
    json_data["SPI"]=[]
    for j in range(35,55):
        if df.iloc[i,j]=="1":
            json_data["SPI"].append(df.iloc[0,j])
    json_data["AMR"]=[]
    for j in range(55,154):
        if df.iloc[i,j]=="1":
            json_data["AMR"].append(df.iloc[0,j])
    json_data["plasmid"]=[]
    for j in range(154,175):
        if df.iloc[i,j]=="1":
            json_data["plasmid"].append(df.iloc[0,j])
    return json_data

lock=threading.Lock()
def job(df,i,json_datas):
    json_data=row2json(df,i)
    lock.acquire()
    json_datas.append(json_data)
    lock.release()


def excel2jsons(xlsx_file):
    df=pd.read_excel(xlsx_file,dtype=str)
    json_datas=[]
    threads=[]
    for i in range(1,df.shape[0]):
    # for i in range(1,501):
    # for i in range(501,1000):
        t=threading.Thread(target=job,args=(df,i,json_datas))
        t.start()
    for t in threads:
        t.join()
    return json_datas

def main():
    df=pd.read_excel("Salmonella.xlsx",dtype=str)
    json_data=row2json(df,1)
    with open("Salmonella.json","w") as f:
        json.dump(json_data,f)
    json_datas=excel2jsons("Salmonella.xlsx")
    # print(len(json_datas))

if __name__=="__main__":
    main()