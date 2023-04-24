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


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = '__all__'


class ComentariSerializer(serializers.ModelSerializer):
    autor = UsuariSerializer(read_only=True)
    autor_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuari.objects.all(),
        write_only=True,
        source='autor'
    )
    issue_id = serializers.PrimaryKeyRelatedField(
        queryset=Issue.objects.all(),
        write_only=True,
        source='issue'
    )

    class Meta:
        model = Comentari
        fields = ('id', 'text', 'autor', 'autor_id', 'data', 'issue_id')


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
    creador_id = serializers.PrimaryKeyRelatedField(
        queryset=Usuari.objects.all(),
        write_only=True,
        source='creador'
    )
    observadors = UsuariSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    comentaris = ComentariSerializer(many=True, read_only=True)
    logs = LogSerializer(many=True, read_only=True)

    class Meta:
        model = Issue
        fields = '__all__'
