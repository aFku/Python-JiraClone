from rest_framework import serializers

from .models import Sprint
from .services.sprint_status_management import SprintStatusManager, InvalidSprintStatusTransition


class SprintsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['id', 'name', 'start_date', 'close_date', 'project', 'status']


class SprintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['name', 'project']


class SprintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['name', 'status']

    def to_internal_value(self, data):
        error = {
            "errors": {}
        }
        for key in data.keys():
            if key not in self.fields:
                error["errors"][key] = ["This field is not allowed."]
        if error["errors"]:
            raise serializers.ValidationError(error)
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        to_status = validated_data.pop('status', None)
        if to_status:
            try:
                SprintStatusManager.change_status(to_status, instance)
            except InvalidSprintStatusTransition as e:
                raise serializers.ValidationError({
                    "errors": {
                        "status": str(e)
                    }
                })
        validated_data["status"] = to_status
        return super().update(instance, validated_data)