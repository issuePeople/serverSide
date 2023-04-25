from rest_framework import serializers
from django.contrib.auth.models import User
from issues.models import Issue, Tag, Attachment, Comentari, Log
from usuaris.models import Usuari


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False)
    first_name = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'first_name')


class UsuariSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', required=False)
    nom = serializers.CharField(source='user.first_name', required=False)

    def update(self, instance, validated_data):
        # La part corresponent a usuari.user, la actualitzem amb UserSerializer
        data_user = validated_data.get('user', None)
        if data_user:
            user_serializer = UserSerializer(instance=instance.user, data=data_user)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()
            validated_data.pop('user')

        # La resta de camps, els actualitzem amb el propi serializer (són camps d'Usuari)
        return super().update(instance, validated_data)

    class Meta:
        model = Usuari
        fields = ('id', 'username', 'nom', 'bio', 'avatar')


class IssueSerializer(serializers.ModelSerializer):
    subject = serializers.CharField(required=False)
    assignacio = UsuariSerializer(read_only=True)
    assignacio_id = serializers.PrimaryKeyRelatedField(
        allow_null=True,
        queryset=Usuari.objects.all(),
        write_only=True,
        required=False,
        source='assignacio'
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['tipus'] = instance.get_tipus_display()
        data['estat'] = instance.get_estat_display()
        data['gravetat'] = instance.get_gravetat_display()
        data['prioritat'] = instance.get_prioritat_display()
        return data

    class Meta:
        model = Issue
        fields = ('id', 'subject', 'tipus', 'estat', 'gravetat', 'prioritat', 'assignacio', 'assignacio_id',
                  'dataCreacio', 'dataLimit', 'bloquejat', 'motiuBloqueig')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class AttachmentSerializer(serializers.ModelSerializer):
    issue_id = serializers.PrimaryKeyRelatedField(
        queryset=Issue.objects.all(),
        write_only=True,
        source='issue'
    )

    class Meta:
        model = Attachment
        fields = ('id', 'data', 'document', 'issue_id')


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
        fields = ('usuari', 'data', 'tipus', 'valor_previ', 'valor_nou')


class LogExtendedSerializer(LogSerializer):
    issue = IssueSerializer(read_only=True)

    class Meta:
        model = Log
        fields = ('issue', 'usuari', 'data', 'tipus', 'valor_previ', 'valor_nou')


class UsuariExtendedSerializer(UsuariSerializer):
    observats = IssueSerializer(many=True, read_only=True)
    logs = LogExtendedSerializer(many=True, read_only=True)
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
