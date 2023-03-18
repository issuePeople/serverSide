from django.db import models
from django.utils.translation import gettext_lazy as _

from usuaris.models import Usuari


class Issue(models.Model):
    # Tipus possibles
    BUG = 'B'
    PREG = 'P'
    MIL = 'M'
    TTIPUS = (
        (BUG, _('Bug')),
        (PREG, _('Pregunta')),
        (MIL, _('Millora'))
    )

    # Estats possibles
    NOVA = 'N'
    DOING = 'D'
    TEST = 'T'
    CLOSED = 'C'
    INFO = 'I'
    REBUTJADA = 'R'
    PROP = 'P'
    TESTATS = (
        (NOVA, _('Nova')),
        (DOING, _('En curs')),
        (TEST, _('Llesta per testejar')),
        (CLOSED, _('Tancada')),
        (INFO, _('Necessita informació')),
        (REBUTJADA, _('Rebutjada')),
        (PROP, _('Proposada'))
    )

    # Gravetats possibles
    DESITJ = 'D'
    MENOR = 'M'
    NORMAL = 'N'
    IMP = 'I'
    CRITIC = 'C'
    TGRAVETAT = (
        (DESITJ, _('Desitjada')),
        (MENOR, _('Menor')),
        (NORMAL, _('Normal')),
        (IMP, _('Important')),
        (CRITIC, _('Crítica'))
    )

    # Prioritats possibles
    BAIXA = 'B'
    MITJA = 'M'
    ALTA = 'A'
    TPRIORITAT = (
        (BAIXA, _('Baixa')),
        (MITJA, _('Normal')),
        (ALTA, _('Alta'))
    )

    id = models.AutoField(primary_key=True, verbose_name=_('Identificador'))
    subject = models.CharField(max_length=500, null=False, blank=False, verbose_name=_('Assumpte'))
    descripcio = models.CharField(max_length=524288, null=True, blank=True, verbose_name=_('Descripció'))
    tipus = models.CharField(choices=TTIPUS, default=BUG, max_length=5, verbose_name=_('Tipus'))
    estat = models.CharField(choices=TESTATS, default=NOVA, max_length=5, verbose_name=_('Estat'))
    gravetat = models.CharField(choices=TGRAVETAT, default=NORMAL, max_length=5, verbose_name=_('Gravetat'))
    prioritat = models.CharField(choices=TPRIORITAT, default=MITJA, max_length=5, verbose_name=_('Prioritat'))
    creador = models.ForeignKey(Usuari, related_name='creats', on_delete=models.DO_NOTHING, verbose_name=_('Creador'))
    assignacio = models.ForeignKey(Usuari, related_name='assignats', null=True, on_delete=models.DO_NOTHING, verbose_name=_('Assignada a'))
    dataCreacio = models.DateField(auto_now_add=True, verbose_name=_('Data creació'))
    dataModificacio = models.DateField(auto_now=True, verbose_name=_('Última modificació'))
    dataLimit = models.DateField(null=True, verbose_name=_('Data límit'))

