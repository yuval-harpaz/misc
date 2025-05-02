import json
import pickle
import requests
import pandas as pd
import os

url2= 'https://www.nadlan.gov.il/Nadlan.REST/Main/GetAssestAndDeals' 
headers = {
'Accept': 'application/json, text/plain, */*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.9',
'Connection': 'keep-alive',
'Content-Length': '782',
'Content-Type': 'application/json;charset=UTF-8',
'Cookie': 'p_hosting=!VIRm9NuJsOb0I+5p0vuartGE7rkM2nG02UUNxx62/mx3I8sRodXWyxRh7ibEOz8xDcfaduhP3OFg4yM=; _ga=GA1.3.980327007.1693941992; _gid=GA1.3.184240161.1693941992; _ga_RWF2PL4D3L=GS1.3.1693941992.1.0.1693941992.0.0.0',
'Host': 'www.nadlan.gov.il',
'Origin': 'https://www.nadlan.gov.il',
'Referer': 'https://www.nadlan.gov.il/?search=%D7%A8%D7%9E%D7%AA%20%D7%94%D7%A9%D7%A8%D7%95%D7%9F',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-origin',
'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
'sec-ch-ua': '"Not.A/Brand";v="99", "Google Chrome";v="115", "Chromium";v="115"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': '"macOS"'
}
payload = """{
  "MoreAssestsType": 0,
  "FillterRoomNum": 0,
  "GridDisplayType": 0,
  "ResultLable": "רמת השרון",
  "ResultType": 1,
  "ObjectID": "2650",
  "ObjectIDType": "text",
  "ObjectKey": "UNIQ_ID",
  "DescLayerID": "SETL_MID_POINT",
  "Alert": null,
  "X": 184204.68832654,
  "Y": 671580.2353939,
  "Gush": "",
  "Parcel": "",
  "showLotParcel": false,
  "showLotAddress": false,
  "OriginalSearchString": "רמת השרון",
  "MutipuleResults": false,
  "ResultsOptions": null,
  "CurrentLavel": 2,
  "Navs": [
    {
      "text": "מחוז תל אביב - יפו",
      "url": null,
      "order": 1
    }
  ],
  "QueryMapParams": {
    "QueryToRun": null,
    "QueryObjectID": "2650",
    "QueryObjectType": "number",
    "QueryObjectKey": "SETL_CODE",
    "QueryDescLayerID": "KSHTANN_SETL_AREA",
    "SpacialWhereClause": null
  },
  "isHistorical": false,
  "PageNo": PAGE_NUMBER,
  "OrderByFilled": "DEALDATETIME",
  "OrderByDescending": true,
  "Distance": 0
}"""

all_df = pd.DataFrame()
for i in range(0,30):
    print(i)
    try:
        npayload=payload.replace('PAGE_NUMBER', str(i))
        npayload2 = npayload.encode()
        response = requests.request("POST", url2, headers=headers, data=npayload2)
        page_results = json.loads(response.text)['AllResults']
        all_df = pd.concat([all_df, pd.DataFrame(page_results)], axis=0)
    except:
        print("error")
