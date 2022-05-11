"""
Copyright (c) 2022 Cisco and/or its affiliates.

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

import influxdb_client.rest
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient

# Get configuration data.
load_dotenv()
influxdb_host = os.getenv('INFLUX_HOST')
influxdb_port = os.getenv('INFLUX_PORT')
influxdb_dnabucket = os.getenv('INFLUX_DNACBUCKET')
influxdb_sdwanbucket = os.getenv('INFLUX_SDWANBUCKET')
influxdb_token = os.getenv('INFLUX_TOKEN')
influxdb_org = os.getenv('INFLUX_ORG')
grafana_user = os.getenv('GRAFANA_USER')
grafana_password = os.getenv('GRAFANA_PASSWORD')
grafana_host = os.getenv('GRAFANA_HOST')
grafana_port = os.getenv('GRAFANA_PORT')


def influxdb_setup():
    # Connect to influxdb
    print("Connecting to influxdb... " + influxdb_host)
    client = InfluxDBClient(
        url="http://" + influxdb_host + ":" + str(influxdb_port),
        token=influxdb_token)

    # Find the organization id.
    orgs = client.organizations_api().find_organizations()
    org_id = None
    for org in orgs:
        if org.name == influxdb_org:
            org_id = org.id
            break

    # Create the second bucket if it doesn't exist already.
    try:
        client.buckets_api().create_bucket(bucket_name=influxdb_sdwanbucket,
                                           org_id=org_id,
                                           description="")
    except influxdb_client.rest.ApiException as ex:
        # The organization already exists.
        if "bucket with name " + influxdb_sdwanbucket + "already exists" \
                in ex.body:
            pass
    return
