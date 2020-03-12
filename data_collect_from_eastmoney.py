import requests
import time, os
import execjs
import h5py
import pandas as pd
import numpy as np

# 获取所有基金的基本信息
def getAllFunds(outpath):
    url = 'http://fund.eastmoney.com/js/fundcode_search.js'
    content = requests.get(url)
    jsContent = execjs.compile(content.text)
    rawData = jsContent.eval('r')
    allCode = []
    allCName = []
    allName = []
    allType= []
    for code in rawData:
        allCode.append(code[0])
        allCName.append(code[2])
        allName.append(code[4])
        allType.append(code[3])
    data = pd.DataFrame()
    data['code'] = allCode
    data['CName'] = allCName
    data['Name'] = allName
    data['Type'] = allType
    data.to_csv(outpath+'allfund.csv',index=None)
    return

# 获取原始数据js文件
def getAllJs(path):
    if not os.path.exists(path+'jsfile'):
        os.makedirs(path+'jsfile/')
    data = pd.read_csv(path+'allfund.csv', dtype=object)
    codes = data['code'].values.tolist()
    js_flag = []
    for c in range(len(codes)):
        code = codes[c]
        if not os.path.exists(path+'jsfile/'+str(code)+'.js'):
            url = 'http://fund.eastmoney.com/pingzhongdata/' + code
            url = url + '.js?v=' + time.strftime("%Y%m%d%H%M%S", time.localtime())
            try:
                content = requests.get(url)
                if content.status_code == 200:
                    with open(path+'jsfile/'+str(code)+'.js', 'w') as f:
                        f.write(content.text)
                    js_flag.append(1)
                    time.sleep(0.5)
                else:
                    print(code)
                    js_flag.append(0)
            except:
                print(code)
                js_flag.append(0)
                time.sleep(0.5)
        else:
            js_flag.append(1)
        if c % 100 == 0:
            print('已完成:' + str(c) + '  未完成:' + str(len(codes) - c))
    data['available'] = js_flag
    data.to_csv(outpath + 'allfund.csv', index=None)

# 从原始js文件获取单只基金的数据
def getInf(path, code):
    if not os.path.exists(path+'jsfile/'+str(code)+'.js'):
        print(path+'jsfile/'+str(code)+'.js 不存在！')
        return
    f = open(path+'jsfile/'+str(code)+'.js', 'r') # encoding='utf-8'
    jsContent = execjs.compile(f.readline())
    inf = {
        'name':jsContent.eval('fS_name'),
        'code':jsContent.eval('fS_code'),
        'sourceRate' : jsContent.eval('fund_sourceRate'),#原费率
        'fund_Rate' : jsContent.eval('fund_Rate'),  # 现费率
        'fund_minsg' : jsContent.eval('fund_minsg'),  # 最小申购金额
        'stockCodes' : str(jsContent.eval('stockCodes')),  # 基金持仓股票代码
        'zqCodes' : str(jsContent.eval('zqCodes')),  # 基金持仓债券代码
        'stockCodesNew' : str(jsContent.eval('stockCodesNew ')), # 基金持仓股票代码(新市场号)
        'zqCodesNew' : str(jsContent.eval('zqCodesNew ')),  # 基金持仓债券代码（新市场号）
        'syl_1n' : jsContent.eval('syl_1n'),  # 近一年收益率
        'syl_6y' : jsContent.eval('syl_6y'),  # 近6月收益率
        'syl_3y' : jsContent.eval('syl_3y'),  # 近三月收益率
        'syl_1y' : jsContent.eval('syl_1y'), # 近一月收益率
        'Data_fundSharesPositions' : str(jsContent.eval('Data_fundSharesPositions ')), # 股票仓位测算图
    }

    # 累计净值走势 存入hd5
    Data_ACWorthTrend = jsContent.eval('Data_ACWorthTrend')
    datainf ={
        'Data_netWorthTrend':str(jsContent.eval('Data_netWorthTrend')), #单位净值走势 equityReturn-净值回报 unitMoney-每份派送金
        'Data_grandTotal':str(jsContent.eval('Data_grandTotal')), # 累计收益率走势
        'Data_rateInSimilarType':str(jsContent.eval('Data_rateInSimilarType')) # 同类排名走势
    }

    return inf

if __name__ == '__main__':
    # getAllFunds('E:/FundResearch/')
    getAllJs('E:/FundResearch/')
    # inf = getInf('E:/FundResearch/','000001')
    # print(inf)
