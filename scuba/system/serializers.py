from rest_framework import serializers

from scuba.system.models import CodebuildJob, InvalidCodebuildException


class CodebuildJobSerializer(serializers.ModelSerializer):
    project = serializers.CharField()
    build_status = serializers.CharField()
    build_id = serializers.CharField()
    time = serializers.DateTimeField()

    class Meta:
        """ define models, fields, etc """
        model = CodebuildJob
        fields = (
            'id',
            'build_id',
            'build_status',
            'project',
            'logs',
            'time',
        )

    @staticmethod
    def validate_build_status(status):
        for _, item in enumerate(CodebuildJob.BUILD_STATUS_VALUES):
            if item[1] == status:
                return item[0]

        raise InvalidCodebuildException(f"{status} is invalid")

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}

        if validated_data['build_status'] == 0:
            return CodebuildJob.objects.create(
                id=validated_data['build_id'],
                logs=validated_data['logs'],
                project=validated_data['project'],
                start_time=validated_data['time'])

        else:
            return CodebuildJob.objects \
                       .filter(id=validated_data['build_id']) \
                       .update(build_status=validated_data['build_status'],
                               end_time=validated_data['time'])
