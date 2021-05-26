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

import os
from influxdb_client import InfluxDBClient
import time
from dotenv import load_dotenv

# Get configuration data.
load_dotenv()
influxdb_host = os.getenv('INFLUX_HOST')
influxdb_port = os.getenv('INFLUX_PORT')
influxdb_bucket = os.getenv('INFLUX_BUCKET')
influxdb_token = os.getenv('INFLUX_TOKEN')
influxdb_org = os.getenv('INFLUX_ORG')
grafana_user = os.getenv('GRAFANA_USER')
grafana_password = os.getenv('GRAFANA_PASSWORD')
grafana_host = os.getenv('GRAFANA_HOST')
grafana_port = os.getenv('GRAFANA_PORT')


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
