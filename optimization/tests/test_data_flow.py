import json
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client, override_settings
from django.utils import timezone

from alarms.models import AlertRule, RuleOperator, Alert, AlertPriority


SQLITE_TEST_DB = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}


@override_settings(DATABASES=SQLITE_TEST_DB)
class DataFlowIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create an alert rule that will trigger on metric "temperature"
        self.rule = AlertRule.objects.create(
            name='High Temperature',
            target_metric='temperature',
            operator=RuleOperator.GREATER_THAN,
            threshold_max=50.0,
            priority=AlertPriority.CRITICAL,
            duration_seconds=0,
        )

    @patch('alarms.services.requests.get')
    @override_settings(BASE_URL='http://testserver')
    def test_acquisition_to_alarms_creates_alert_and_calls_optimization(self, mock_get):
        # Mock optimization emergency-mode endpoint call
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'OK'
        mock_get.return_value = mock_response

        payload = {
            'metric_name': 'temperature',
            'value': 60.0,
            'timestamp': timezone.now().isoformat(),
            'details': {
                'sensor_id': 1,
                'room': '101',
                'status': 'OK'
            }
        }

        # Send measurement to alarms inspection endpoint (simulating acquisition -> alarms)
        resp = self.client.post(
            '/api/data-inspection/check_rules/',
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        # Verify alert created
        alerts = Alert.objects.filter(alert_rule=self.rule)
        self.assertEqual(alerts.count(), 1)
        alert = alerts.first()
        self.assertEqual(alert.priority, AlertPriority.CRITICAL)
        self.assertEqual(alert.triggering_value, 60.0)

        # Verify that emergency-mode was called with GET (alarms -> optimization)
        self.assertTrue(mock_get.called)
        called_args, called_kwargs = mock_get.call_args
        # Note: endpoint spelling in code
        self.assertIn('/api/optimization/alarm/', called_args[0])
        params = called_kwargs.get('params', {})
        # Basic payload fields forwarded
        self.assertEqual(params.get('id'), alert.id)
        self.assertEqual(params.get('priority'), AlertPriority.CRITICAL)
        self.assertEqual(float(params.get('triggering_value')), 60.0)
        self.assertEqual(params.get('rule_name'), 'High Temperature')
        self.assertEqual(params.get('rule_metric'), 'temperature')

    @patch('optimization.integration.clients.SimulationClient.publish_command')
    def test_optimization_webhook_receives_alert_and_dispatches_command(self, mock_publish):
        # Compose external alarm payload like alarms would send
        now = timezone.now()
        external_payload = {
            'id': 123,
            'status': 'NEW',
            'priority': 'CRITICAL',
            'triggering_value': 99.9,
            'timestamp_generated': now.isoformat(),
            'rule_name': 'High Temperature',
            'rule_metric': 'temperature',
        }

        resp = self.client.post(
            '/api/optimization/alarm/',
            data=json.dumps(external_payload),
            content_type='application/json'
        )
        self.assertEqual(resp.status_code, 200)

        # OptimizationController should dispatch shutdown command to Simulation
        self.assertTrue(mock_publish.called)
        called_args, called_kwargs = mock_publish.call_args
        device_id = called_args[0]
        command_map = called_args[1]
        # controller routes CRITICAL to device ID=1 (demo)
        self.assertEqual(device_id, 1)
        self.assertEqual(command_map.get('status'), 'OFF')
        self.assertEqual(command_map.get('reason'), 'EXTERNAL_ALARM_CRITICAL')
        self.assertIn('Metric: temperature', command_map.get('details', ''))
