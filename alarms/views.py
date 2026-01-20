from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import datetime

from .models import Alert, AlertRule
from .services import AlertManager, MonitoringService
from .serializers import AlertSerializer, AlertRuleSerializer


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet dla alarmów"""
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """Lista alarmów"""
        alerts = Alert.objects.select_related(
            'alert_rule',
            'alert_comment',
            'acknowledged_by',
            'closed_by'
        ).all()
        # todo: mozna dodac stronicowanie
        # todo: filtrowanie alarmow
        serializer = self.get_serializer(alerts, many=True)
        return Response({'alerts': serializer.data})

    def create(self, request):
        """Utwórz nowy alarm ręcznie"""
        try:
            rule_id = request.data.get('alert_rule_id')
            triggering_value = request.data.get('triggering_value')
            timestamp_raw = request.data.get('timestamp')
            comment = request.data.get('comment', None)

            if not rule_id or triggering_value is None:
                return Response(
                    {'error': 'Wymagane pola: alert_rule_id, triggering_value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                numeric_value = float(triggering_value)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'triggering_value musi być liczbą'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if timestamp_raw:
                try:
                    parsed_ts = datetime.fromisoformat(timestamp_raw)
                    if timezone.is_naive(parsed_ts):
                        timestamp = timezone.make_aware(parsed_ts)
                    else:
                        timestamp = parsed_ts
                except Exception:
                    return Response(
                        {'error': 'Nieprawidłowy format timestamp, oczekiwany ISO8601'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                timestamp = timezone.now()

            rule = AlertRule.objects.get(id=rule_id)
            alert = MonitoringService.create_alert(
                rule=rule,
                metric_name=rule.target_metric,
                value=numeric_value,
                timestamp=timestamp,
                user=request.user,
            )

            if alert and comment:
                from .models import AlertComment
                alert_comment = AlertComment.objects.create(text=comment)
                alert.alert_comment = alert_comment
                alert.save()

            if alert:
                return Response({'id': alert.id, 'status': 'created'}, status=status.HTTP_201_CREATED)
            return Response(
                {'error': 'Nie można utworzyć alarmu'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except AlertRule.DoesNotExist:
            return Response(
                {'error': 'Reguła nie istnieje'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Błąd podczas tworzenia alarmu: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Potwierdź alarm"""
        alert = self.get_object()
        user = request.user
        comment = request.data.get('comment', None)

        success = AlertManager.acknowledge_alert(alert.id, user.id, comment)

        if success:
            return Response({'status': 'acknowledged'})
        return Response(
            {'error': 'Nie można potwierdzić alarmu'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Zamknij alarm"""
        alert = self.get_object()
        user = request.user
        comment = request.data.get('comment', None)

        success = AlertManager.close_alert(alert.id, user.id, comment)

        if success:
            return Response({'status': 'closed'})
        return Response(
            {'error': 'Nie można zamknąć alarmu'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """Dodaj komentarz do alarmu bez zmiany statusu"""
        alert = self.get_object()
        new_comment = request.data.get('comment', None)

        if not new_comment:
            return Response(
                {'error': 'Komentarz jest wymagany'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from .models import AlertComment

            # Get existing comment text
            existing_text = alert.alert_comment.text if alert.alert_comment else ''

            # Append new comment with separator
            separator = '\n\n---\n\n' if existing_text else ''
            updated_text = existing_text + separator + new_comment

            # Create or update comment
            if alert.alert_comment:
                alert.alert_comment.text = updated_text
                alert.alert_comment.save()
            else:
                alert_comment = AlertComment.objects.create(text=updated_text)
                alert.alert_comment = alert_comment
                alert.save()

            return Response({'status': 'comment_added'})
        except Exception as e:
            return Response(
                {'error': f'Błąd podczas dodawania komentarza: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AlertRuleViewSet(viewsets.ModelViewSet):
    """ViewSet dla reguł alarmów"""
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        """Utwórz nową regułę"""
        rule = AlertManager.create_rule(request.data)

        if rule:
            return Response({'id': rule.id}, status=status.HTTP_201_CREATED)
        return Response(
            {'error': 'Nie można utworzyć reguły'},
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, pk=None):
        """Edytuj regułę"""
        try:
            rule = AlertRule.objects.get(pk=pk)
            for key, value in request.data.items():
                # todo: brakuje walidacji danych
                setattr(rule, key, value)
            rule.save()
            return Response({'status': 'updated'})
        except AlertRule.DoesNotExist:
            return Response(
                {'error': 'Reguła nie istnieje'},
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None):
        """Usuń regułę"""
        try:
            rule = AlertRule.objects.get(pk=pk)
            rule.delete()
            return Response({'status': 'deleted'})
        except AlertRule.DoesNotExist:
            return Response(
                {'error': 'Reguła nie istnieje'},
                status=status.HTTP_404_NOT_FOUND
            )


class DataInspectionViewSet(viewsets.ViewSet):
    """ViewSet do inspectowania danych i sprawdzania reguł"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def check_rules(self, request):
        """
        POST endpoint do analizy danych i sprawdzenia złamania reguł.
        Oczekuje payloadu:
        {
            "metric_name": str,
            "value": float,
            "timestamp": isoformat datetime,
            "details": {
                "sensor_id": int,
                "room": str,
                "status": str
            }
        }
        """
        try:
            metric_name = request.data.get('metric_name')
            value = request.data.get('value')
            timestamp_raw = request.data.get('timestamp')
            details = request.data.get('details') or {}

            # Walidacja wymaganych pól
            if not metric_name or value is None:
                return Response(
                    {'error': 'Wymagane pola: metric_name, value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                numeric_value = float(value)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Pole value musi być liczbą'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # parsowanie timestamp
            if timestamp_raw:
                try:
                    parsed_ts = datetime.fromisoformat(timestamp_raw)
                    if timezone.is_naive(parsed_ts):
                        timestamp = timezone.make_aware(parsed_ts)
                    else:
                        timestamp = parsed_ts
                except Exception:
                    return Response(
                        {'error': 'Nieprawidłowy format timestamp, oczekiwany ISO8601'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                timestamp = timezone.now()

            # Uruchom analizę danych
            MonitoringService.inspect_data(
                metric_name, numeric_value, timestamp, details)

            return Response({
                'status': 'success',
                'message': 'Dane zostały przeanalizowane',
                'metric_name': metric_name,
                'value': numeric_value,
                'timestamp': timestamp,
                'details': details
            })

        except Exception as e:
            return Response(
                {'error': f'Błąd podczas analizy danych: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
