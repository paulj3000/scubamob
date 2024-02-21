from rest_framework import serializers

from scuba.system.models import CodebuildJob, CodebuildProject, InvalidCodebuildException


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
            'branch',
        )

    @staticmethod
    def validate_build_status(status):
        for _, item in enumerate(CodebuildJob.BUILD_STATUS_VALUES):
            if item[1] == status:
                return item[0]

        raise InvalidCodebuildException(f"{status} is invalid")

    def save(self, **kwargs):
        validated_data = {**self.validated_data, **kwargs}
        project, _ = CodebuildProject.objects.get_or_create(project=validated_data['project'])

        if validated_data['build_status'] == 0:

            return CodebuildJob.objects.create(
                id=validated_data['build_id'],
                logs=validated_data['logs'],
                project=project,
                branch=validated_data['branch'],
                start_time=validated_data['time'])

        else:
            if validated_data['build_status'] == 1:
                project.last_successful_build = validated_data['time']
                project.save()

            return CodebuildJob.objects.filter(id=validated_data['build_id']) \
                               .update(build_status=validated_data['build_status'],
                                       end_time=validated_data['time'])
