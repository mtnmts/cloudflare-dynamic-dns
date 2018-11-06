#/usr/bin/env python2

import yaml
import sys
import json
import requests

## config.yaml
## zone_id: abcdefgh16
## api_key: abcdefgh16 
## api_email: john@gmail.com

class CloudflareAPI(object):
    REQUIRED_CONFIG_KEYS = ['zone_id', 'api_email', 'api_key']
    BASE_URL = "https://api.cloudflare.com/client/v4/"
    def __init__(self,config_path):
        self._config = yaml.load(open(config_path,'rb'))
        assert all(map(lambda x: x in CloudflareAPI.REQUIRED_CONFIG_KEYS, self._config))

    def get_dns_records(self):
        request_url = CloudflareAPI.BASE_URL + 'zones/' + self._config['zone_id']  + '/dns_records'
        args = { "type" : "A" }
        results = json.loads(requests.get(request_url, json=args, headers=self.headers).text)
        return self._ok(results)

    def _ok(self,result):
        if not len(result['errors']) == 0:
            raise Exception("Error encountered in API Request: " + str(result['errors']))
        return result['result']
    
    def get_dns_record(self, partial_name):
        for dns_record in self.get_dns_records():
            if partial_name in dns_record['name']:
                return dns_record
        raise exception("Failed to find DNS Record partial match:" + partial_name)

    def update_dns_record(self, partial_name, ip):
        record = self.get_dns_record(partial_name)
        request_url = CloudflareAPI.BASE_URL + 'zones/' + record['zone_id'] + '/dns_records/' + record['id']
        args = { "type" : record['type'] ,"name" : record['name'], 'content' : ip}
        result = json.loads(requests.put(request_url, json=args, headers=self.headers).text)
        return self._ok(result)

    @property
    def headers(self):
        return { "X-Auth-Email" : self._config['api_email'],
                 "X-Auth-Key"   : self._config['api_key'],
                 "Content-Type" : "application/json", }

def main(config, record_name, ip):
    capi = CloudflareAPI(config)
    capi.update_dns_record(record_name,ip)

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print sys.argv[0] + " <Configuration> <Record Name> <IP>"
        sys.exit(-1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
