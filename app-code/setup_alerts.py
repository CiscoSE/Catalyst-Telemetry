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


import yaml, requests
from datetime import datetime


# get configuration data
config = yaml.safe_load(open("credentials.yaml"))
grafana_user = config['grafana_user']
grafana_password = config['grafana_password']
grafana_notificationchannel = config['grafana_notificationchannel']
grafana_dashboard_uid = config['grafana_dashboard_uid']
grafana_host = config['grafana_host']
grafana_port = config['grafana_port']
grafana_alert_for = config['grafana_alert_for']
grafana_alert_frequency = config['grafana_alert_frequency']
grafana_alertcondition_aggregation = config['grafana_alertcondition_aggregation']
grafana_alertcondition_time1 = config['grafana_alertcondition_time1']
grafana_alertcondition_time2 = config['grafana_alertcondition_time2']


# collect thresholds for different transceivers using Ansible
total_info = []
def alert_thresholds():

    print('ALERT THRESHOLDS UPDATE')
    print('- collecting transceiver information and thresholds')

    playbook_on_start_referencetime = datetime.utcnow()
    s = ansible_runner.run(private_data_dir='/usr/src/app', playbook='playbook-show_int_transceiver_details.yaml')

    if s.status == 'successful':
        print('- transceiver information and thresholds collected successfully')

    for event in s.events:

        # the event labeled "playbook_on_start" includes references to the most recent playbook execution
        if event['event'] == "playbook_on_start":
            created_string = event['created']
            created = datetime.strptime(created_string, '%Y-%m-%dT%H:%M:%S.%f')
            if created > playbook_on_start_referencetime:
                playbook_uuid_filter = event['event_data']['playbook_uuid']

        # the event labeled "runner_on_ok" includes the output of the commands run in the playbook 'playbook-show_int_transceiver_details.yaml'
        if event['event'] == "runner_on_ok":
            playbook_uuid = event['event_data']['playbook_uuid']
            if playbook_uuid == playbook_uuid_filter:
                host = event['event_data']['host']

                # output of "show interface transceiver details" cmd
                int_list = []
                details_cmd_line_output = event['event_data']['res']['stdout_lines'][0]
                for details_line in details_cmd_line_output[9:]:
                    x = ' '.join(details_line.split()).split(" ")
                    if x == ['']:
                        break
                    int_list.append(x[0])

                # output of "show interface transceiver properties" cmd
                properties_cmd_line_output = event['event_data']['res']['stdout_lines'][1]
                properties = []
                for properties_line in properties_cmd_line_output:
                    if properties_line != '':
                        key_value_list = properties_line.split(': ')
                        if key_value_list[0] == 'Name ':  # interface name
                            info = {
                                'name': key_value_list[1],
                                'media_type': ''
                            }
                        elif key_value_list[0] == 'Media Type':
                            info['media_type'] = key_value_list[1]
                            if info['name'] in int_list:
                                properties.append(info)

                # bring information together in list total_info
                for property in properties:
                    exists = False
                    for media_type in total_info:
                        if property['media_type'] == media_type['media_type']:
                            exists = True
                            exists_host = False
                            for item in media_type['interfaces']:
                                if item['host'] == host:
                                    exists_host = True
                                    item['interfaces'].append(property['name'])
                                    break
                            if exists_host == False:
                                add = {
                                    'host': host,
                                    'interfaces': [property['name']]
                                }
                                media_type['interfaces'].append(add)
                            break
                    if exists == False:
                        info_per_media_type = {}
                        info_per_media_type['media_type'] = property['media_type']
                        info_per_media_type['interfaces'] = []
                        info = {
                            'host': host,
                            'interfaces': [property['name']]
                        }
                        info_per_media_type['interfaces'].append(info)
                        thresholds = {
                            'temperature_thresholds': {},
                            'voltage_thresholds': {},
                            'current_thresholds': {},
                            'transmitPower_thresholds': {},
                            'receivePower_thresholds': {}
                        }
                        info_per_media_type.update(thresholds)
                        i = 0
                        for details_line in details_cmd_line_output[4:]:
                            x = ' '.join(details_line.split()).split(" ")
                            if x[0] == '---------':
                                i += 1
                            if i == 1 and x[0] == property['name']:  # Temperature
                                info_per_media_type['temperature_thresholds']['high_alarm'] = x[2]
                                # info_per_media_type['temperature_thresholds']['high_warn'] = x[3]
                                # info_per_media_type['temperature_thresholds']['low_warn'] = x[4]
                                info_per_media_type['temperature_thresholds']['low_alarm'] = x[5]
                            elif i == 2 and x[0] == property['name']:  # Voltage
                                info_per_media_type['voltage_thresholds']['high_alarm'] = x[2]
                                # info_per_media_type['voltage_thresholds']['high_warn'] = x[3]
                                # info_per_media_type['voltage_thresholds']['low_warn'] = x[4]
                                info_per_media_type['voltage_thresholds']['low_alarm'] = x[5]
                            elif i == 3 and x[0] == property['name']:  # Current
                                info_per_media_type['current_thresholds']['high_alarm'] = x[2]
                                # info_per_media_type['current_thresholds']['high_warn'] = x[3]
                                # info_per_media_type['current_thresholds']['low_warn'] = x[4]
                                info_per_media_type['current_thresholds']['low_alarm'] = x[5]
                            elif i == 4 and x[0] == property['name']:  # Transmit
                                info_per_media_type['transmitPower_thresholds']['high_alarm'] = x[2]
                                # info_per_media_type['transmitPower_thresholds']['high_warn'] = x[3]
                                # info_per_media_type['transmitPower_thresholds']['low_warn'] = x[4]
                                info_per_media_type['transmitPower_thresholds']['low_alarm'] = x[5]
                            elif i == 5 and x[0] == property['name']:  # Receive
                                info_per_media_type['receivePower_thresholds']['high_alarm'] = x[2]
                                # info_per_media_type['receivePower_thresholds']['high_warn'] = x[3]
                                # info_per_media_type['receivePower_thresholds']['low_warn'] = x[4]
                                info_per_media_type['receivePower_thresholds']['low_alarm'] = x[5]
                        total_info.append(info_per_media_type)

    print('- transceiver information and thresholds processed succesfully')

    # update collected information in grafana
    sync_grafana()

    # create list to return to main.py, to provide tagging info in influxdb and grafana
    tagging_info = []
    for item in total_info:
        tag = {
            'media_type': item['media_type'],
            'interfaces': item['interfaces']
        }
        tagging_info.append(tag)

    print('ALERT THRESHOLDS UPDATE COMPLETE')

    return tagging_info


# update threshold information in grafana as queries and matching alerts
def sync_grafana():
    grafana_base_url = 'http://' + grafana_host + ':' + str(grafana_port) + '/api/'
    grafana_headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # get dashboard
    dashboard_json_request = requests.get(grafana_base_url + 'dashboards/uid/' + grafana_dashboard_uid, headers=grafana_headers, auth=(grafana_user, grafana_password))
    dashboard_json = dashboard_json_request.json()['dashboard']

    print('- updating queries and alerts in Grafana with transceiver information and threshold')

    # create new query and alert per media_type in total_info list
    update = False
    for media_type_info in total_info:

        media_type = media_type_info['media_type']

        # go into each panel/graph to add query and alert for that media score_category
        for panel in dashboard_json['panels']:
            name = panel['title']
            refId = panel['targets'][0]['select'][0][0]['params'][0]
            refId_mediatype = refId + '_' + media_type

            # query josn
            query = {
                "alias": "",
                "groupBy": [
                    {
                        "params": [
                            "host"
                        ],
                        "score_category": "tag"
                    },
                    {
                        "params": [
                            "interface"
                        ],
                        "score_category": "tag"
                    },
                    {
                        "params": [
                            "media_type"
                        ],
                        "score_category": "tag"
                    }
                ],
                "hide": True,
                "measurement": "dom_statistics",
                "orderByTime": "ASC",
                "policy": "default",
                "rawQuery": False,
                "refId": "",
                "resultFormat": "time_series",
                "select": [
                    [
                        {
                            "params": [
                                ""
                            ],
                            "score_category": "field"
                        }
                    ]
                ],
                "tags": [
                    {
                        "key": "media_type",
                        "operator": "=",
                        "value": media_type
                    }
                ]
            }

            # alert jsons
            alert = {
                "alertRuleTags": {},
                "conditions": [],
                "executionErrorState": "alerting",
                "for": grafana_alert_for,
                "frequency": grafana_alert_frequency,
                "handler": 1,
                "name": "",
                "noDataState": "no_data",
                "notifications": [
                    {
                        "uid": grafana_notificationchannel
                    }
                ]
            }
            alert_condition = {
                "evaluator": {
                    "params": ["", ""],
                    "score_category": "outside_range"
                },
                "operator": {
                    "score_category": ""
                },
                "query": {
                    "params": [
                        "",
                        grafana_alertcondition_time1,
                        grafana_alertcondition_time2
                    ]
                },
                "reducer": {
                    "params": [],
                    "score_category": grafana_alertcondition_aggregation
                },
                "score_category": "query"
            }

            # query customization, if it does not exist yet
            target_exists = False
            for target in panel['targets']:
                if target['refId'] == refId_mediatype:
                    target_exists = True
                    break
            if target_exists == False:
                query['refId'] = refId_mediatype
                query['select'][0][0]['params'][0] = refId
                update = True
                panel['targets'].append(query)

            # get threshold identifier to get right alert values
            if panel['title'] == 'Optical Rx Power (in dBm)':
                threshold_identifier = 'receivePower_thresholds'
            elif panel['title'] == 'Optical Tx Power (in dBm)':
                threshold_identifier = 'transmitPower_thresholds'
            elif panel['title'] == 'Temperature (in Celsius)':
                threshold_identifier = 'temperature_thresholds'
            elif panel['title'] == 'Voltage (in Volts)':
                threshold_identifier = 'voltage_thresholds'
            elif panel['title'] == 'Current (in mA)':
                threshold_identifier = 'current_thresholds'

            # alert customization, if it does not exist yet
            low_alarm = float(media_type_info[threshold_identifier]['low_alarm'])
            high_alarm = float(media_type_info[threshold_identifier]['high_alarm'])
            if 'alert' not in panel.keys():
                alert['name'] = name
                alert_condition['query']['params'][0] = refId_mediatype
                alert_condition['evaluator']['params'][0] = low_alarm
                alert_condition['evaluator']['params'][1] = high_alarm
                alert_condition['operator']['score_category'] = 'and'
                alert['conditions'].append(alert_condition)
                update = True
                panel['alert'] = alert
            else:
                condition_exists = False
                for condition in panel['alert']['conditions']:
                    if condition['query']['params'][0] == refId_mediatype:
                        condition_exists = True
                        break
                if condition_exists == False:
                    alert_condition['query']['params'][0] = refId_mediatype
                    alert_condition['evaluator']['params'][0] = low_alarm
                    alert_condition['evaluator']['params'][1] = high_alarm
                    alert_condition['operator']['score_category'] = 'or'
                    update = True
                    panel['alert']['conditions'].append(alert_condition)

    # update dashboard in grafana if changes were made
    if update == True:
        payload = {
            'dashboard': dashboard_json
        }
        dashboard_json_request = requests.post(grafana_base_url + 'dashboards/db', json=payload, headers=grafana_headers, auth=(grafana_user, grafana_password))

        if dashboard_json_request.status_code == 200:
            print('- queries and alerts successfully updated in Grafana')
        else:
            print('Something went wrong while updating transceiver information in Grafana: ' + str(dashboard_json_request.json()))
    else:
        print('- queries and alerts already up to date in Grafana')

    return