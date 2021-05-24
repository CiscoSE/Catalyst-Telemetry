'''
Copyright (c) 2021 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
'''

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from datetime import datetime
import yaml, time
from setup import influxdb_setup
import dnacentersdk

# get configuration data
config = yaml.safe_load(open("credentials.yaml"))
influxdb_host = config['influxdb_host']
influxdb_port = config['influxdb_port']
influxdb_bucket = config['influxdb_bucket']
influxdb_token = config['influxdb_token']
influxdb_org = config['influxdb_org']
collector_interval = int(config['collector_interval'])
transceiver_update_interval = int(config['transceiver_update_interval'])
dnacenter_sandbox_url = config['dnacenter_sandbox_url']
dnacenter_sandbox_user = config['dnacenter_sandbox_user']
dnacenter_sandbox_password = config['dnacenter_sandbox_password']
dnacenter_live_url = config['dnacenter_live_url']
dnacenter_live_user = config['dnacenter_live_user']
dnacenter_live_password = config['dnacenter_live_password']

# Setup influxdb
influxdb_setup()
client = InfluxDBClient(
    url="http://" + influxdb_host + ":" + str(influxdb_port),
    token=influxdb_token)

# Setup DNA Center Sandbox
dnacenter_sandbox = dnacentersdk.DNACenterAPI(
    base_url=dnacenter_sandbox_url,
    username=dnacenter_sandbox_user,
    password=dnacenter_sandbox_password)

# Setup DNA Center Sandbox
dnacenter_live = dnacentersdk.DNACenterAPI(
    base_url=dnacenter_live_url,
    username=dnacenter_live_user,
    password=dnacenter_live_password,
    verify=False)

while True:
    write_api = client.write_api(write_options=SYNCHRONOUS)

    # Client health
    print('\nPrinting client health...')
    response = dnacenter_live.clients.get_overall_client_health().response
    for score in response[0]['scoreDetail']:
        score_category = score['scoreCategory']['value']
        score_client_count = score['clientCount']
        score_value = score['scoreValue']
        print('Type: {0}, Count: {1}, Score: {2}'.format(
            score_category,
            score_client_count,
            score_value))

        # Save to influxdb
        data = "client_health_general,score_category=" + score_category + \
               " score_value=" + str(score_value)
        write_api.write(influxdb_bucket, influxdb_org, data)
        data = "client_health_general,score_category=" + score_category + \
               " client_count=" + str(score_client_count)
        write_api.write(influxdb_bucket, influxdb_org, data)
        try:
            for category in score['scoreList']:
                category_type = category['scoreCategory']['value']
                client_count = category['clientCount']
                print('\tType: {0}, Count: {1}'.format(
                    category_type,
                    client_count))

                data = "client_health_detailed,score_category=" + \
                       score_category + ",type=" + category_type + \
                       " client_count=" + str(client_count)
                write_api.write(influxdb_bucket, influxdb_org, data)
        except:
            pass

    devices = dnacenter_sandbox.devices. \
        get_device_list(family="Switches and Hubs").response
    for device in devices:
        device_details = \
            dnacenter_sandbox.devices. \
                get_device_detail(identifier="uuid",
                                  search_by=device.id).response
        cpu = device_details.cpu
        overall_health = device_details.overallHealth
        device_name = device.nwDeviceName

        data = "cpu,host=" + device.id + ",device_name=" + device.hostname + \
               " cpu_used=" + str(cpu)
        write_api.write(influxdb_bucket, influxdb_org, data)
        data = "overall_health,host=" + device.id + ",device_name=" + \
               device.hostname + " overall_health=" + str(overall_health)
        write_api.write(influxdb_bucket, influxdb_org, data)

    # pause the script for x seconds, represents the polling interval
    time.sleep(collector_interval)
