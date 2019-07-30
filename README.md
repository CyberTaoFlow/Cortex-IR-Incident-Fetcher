# Cortex-IR-Incident-Fetcher
The program helps fetched incidents from Palo Alto Networks Cortex XDR IR and index to ElasticSearch for report.

Currently, Cortex Incident Response does not support forward incidents via syslog. The only way to get incident is to fetch by API call. 
The script will
1. Fetch incidents from Cortex
2. Formated it (modify and add some fields) in a standard json.
3. Send it to ElasticSearch

On ElasticSearch, you just need to create index based on formated data sent by the script. It will be able to search and visualize Cortex data on dashboard.

Have fun.
