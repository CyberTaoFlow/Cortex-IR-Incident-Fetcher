import requests
import datetime
import time
import json

def test_standard_authentication(api_key_id, api_key):
    headers = {
        "x-xdr-auth-id": str(api_key_id),
        "Authorization": api_key
    }
    parameters = {}
    #Input API URI of your Cortex instance here
    res = requests.post(url="https://us-central1-xdr-cloudfunction-eu.cloudfunctions.net/cf-xxxxx/api_keys/validate/",
                        headers=headers,
                        json=parameters)
    return res

def convert_time(epoch):
    s = int(epoch) / 1000.0
    return(datetime.datetime.fromtimestamp(s).strftime('%Y-%m-%dT%H:%M:%S'))


def convert_epoch():
    t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    p = '%Y-%m-%d %H:%M:%S'
    epoch = int(time.mktime(time.strptime(t, p)))
    return(epoch*1000)


def index_to_elastic(j):
    headers = {
        "Content-Type": "application/json"
    }
    dic = json.loads(j)
    #Input IP of your elasticsearch here. Localhost will work when running the script on ELK server
    url = "http://localhost:9200/xdr-ir-incident/_doc/"
    res = requests.post(url=url, headers=headers, json=dic)
    return(res.text)


def index_to_elastic_stats(j):
    headers = {
        "Content-Type": "application/json"
    }
    dic = json.loads(j)
    url = "http://localhost:9200/xdr-ir-status/_doc/"
    res = requests.post(url=url, headers=headers, json=dic)
    return(res.text)


def fetch_incident(api_key_id, api_key):
    headers = {
        "x-xdr-auth-id": str(api_key_id),
        "Authorization": api_key
    }
    parameters = {'request_data': {
        'filters': [{'field': 'creation_time', 'operator': 'gte',
                     'value': convert_epoch()}],
        'search_from': 0,
        'search_to': 5,
        'sort': {'field': 'creation_time', 'keyword': 'desc'},
    }
    }

    res = requests.post(
        url="https://us-central1-xdr-cloudfunction-eu.cloudfunctions.net/cf-1928255847/public_api/v1/incidents/get_incidents/",
        headers=headers,
        json=parameters)
    return(res.text)


def get_incident(api_key_id, api_key):
    fullresponse = fetch_incident(api_key_id, api_key)
    fullresponse2 = fetch_incident(api_key_id, api_key)

    #Write total number of incident to Elastic Search index xdr-ir-status
    with open('xdrstatistic.json','w') as f:
        statistic = fullresponse[10:fullresponse.find(', \"incidents\"')] + ', "@timestamp": '+'\"'+datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S')+'\"}'
        f.write(statistic)
        print(index_to_elastic_stats(statistic))

    i = 0
    #Pre-parse json response from Cortex XDR
    fullresponse = fullresponse.replace('{','')
    fullresponse = fullresponse.replace('}', '')
    fullresponse = fullresponse.replace('[', '')
    fullresponse = fullresponse.replace(']', '')
    full = fullresponse.split()
    #Count number of incident_id
    count = 0
    for i in range(0, len(full)):
        if '\"incident_id\":' ==  full[i]:
            count += 1
    #Write each fetched incident to Elastic Search index xdr-ir-incident
    for i in range(0,count-1):
        with open('xdrincident'+str(i)+'.json','w') as f:
            incident = '{'+fullresponse2[fullresponse2.find('\"incident_id\"'):fullresponse2.find('\"}')]+'\"}'
            #print(incident)
            time = incident[incident.find('\"creation_time\":')+17:incident.find(', \"modification_time\"')]
            goodtime = convert_time(time)
            #Add @timestamp field to each incident
            formated_incident = incident.replace(time,'\"'+goodtime+'\"')
            formated_incident2 = formated_incident.replace('}',', "@timestamp": '+'\"'+goodtime+'\"}')
            formated_incident3 = formated_incident2.replace('\'','')
            formated_incident4 = formated_incident3.replace('null','\"NA\"')
            print(formated_incident4)
            #Check list of incident ID fetched
            incident_id = incident[incident.find('{\"incident_id\": ')+17:incident.find(', \"creation_time\":')-1]
            #if incident_id not in incident_id_list:
            incident_id_list.append(incident_id)
            f.write(formated_incident4)
                #f.write(fullresponse2)
            print(index_to_elastic(formated_incident4))
                #crop each incident from full json to let the loop goes on
            fullresponse2 = fullresponse2[fullresponse2.find('\"incident_id\"')+len(incident):-1]

    #return statistic



def get_detail_incident(api_key_id, api_key, incident_id):
    headers = {
        "x-xdr-auth-id": str(api_key_id),
        "Authorization": api_key
    }
    parameters = {
				"request_data": {
				"incident_id": str(incident_id),
				"alerts_limit": 5
				}
			    }

    res = requests.post(url="https://us-central1-xdr-cloudfunction-eu.cloudfunctions.net/cf-1928255847/public_api/v1/incidents/get_incident_extra_data/",
                        headers=headers,
                        json=parameters)
    return res.text

#Set up connection to XDR
#Input API_ID and Key here. The information can be get on Cortex XDR IR Setting portal.
api_id = "X"
key = "XXXX"
#print(test_standard_authentication(api_id,key))


#Execution
while True:
    get_incident(api_id,key)
    incident_id_list = []
    #print(get_detail_incident(api_id,key,306))
    #print(convert_epoch())
    time.sleep(60.0 - (time.time() % 60.0))
