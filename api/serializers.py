from rest_framework import serializers

from issues.models import Issue, Tag, Attachment, Comentari, Log
from usuaris.models import Usuari


class UsuariSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username')
    nom = serializers.CharField(source='user.first_name')

    class Meta:
        model = Usuari
        fields = ('id', 'username', 'nom', 'bio', 'avatar')


class IssueSerializer(serializers.ModelSerializer):
    assignacio = UsuariSerializer(read_only=True)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tipus'] = instance.get_tipus_display()
        data['estat'] = instance.get_estat_display()
        data['gravetat'] = instance.get_gravetat_display()
        data['prioritat'] = instance.get_prioritat_display()
        return data

    class Meta:
        model = Issue
        fields = ('id', 'subject', 'tipus', 'estat', 'gravetat', 'prioritat', 'assignacio', 'dataCreacio',
                  'dataLimit', 'bloquejat', 'motiuBloqueig')


class LogSerializer(serializers.ModelSerializer):
    usuari = UsuariSerializer(read_only=True)

    class Meta:
        model = Log
        fields = '__all__'


class UsuariExtendedSerializer(UsuariSerializer):
    observats = IssueSerializer(many=True, read_only=True)
    logs = LogSerializer(many=True, read_only=True)
    token = serializers.CharField(source='user.auth_token', read_only=True)

    class Meta:
        model = Usuari
        fields = ('id', 'username', 'nom', 'bio', 'avatar', 'observats', 'logs', 'token')


class IssueExtendedSerializer(IssueSerializer):
    creador = UsuariSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'
