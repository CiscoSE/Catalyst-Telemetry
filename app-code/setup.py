"""
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
"""

from influxdb_client import InfluxDBClient
import yaml, time, requests
import dnacentersdk

# get configuration data
config = yaml.safe_load(open("credentials.yaml"))
influxdb_host = config['influxdb_host']
influxdb_port = config['influxdb_port']
influxdb_bucket = config['influxdb_bucket']
influxdb_token = config['influxdb_token']
influxdb_org = config['influxdb_org']
grafana_user = config['grafana_user']
grafana_password = config['grafana_password']
grafana_host = config['grafana_host']
grafana_port = config['grafana_port']


# connect to influxdb and create database
def influxdb_setup():
    time.sleep(5)

    # connect to influxdb
    print("Connecting to influxdb... " + influxdb_host)
    client = InfluxDBClient(
        url="http://" + influxdb_host + ":" + str(influxdb_port),
        token=influxdb_token)

    # Check if buckets already exists, if it works influxdb is working fine.
    client.buckets_api().find_buckets().buckets

    return
