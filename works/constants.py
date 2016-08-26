from django.utils.translation import ugettext_lazy as _

from common.model_enums import EnumValue, ModelEnum


class WorkItemType(ModelEnum):
    IMAGE = EnumValue('img', 'Image')
    YOUTUBE = EnumValue('you', 'Youtube')
    VIMEO = EnumValue('vim', 'Vimeo')
    SOUNDCLOUD = EnumValue('scl', 'Sound Cloud')
    SPOTIFY = EnumValue('spo', 'Spotify')
    GIST = EnumValue('gis', 'Gist')
    JSFIDDLE = EnumValue('jsf', 'JSFiddle')


class WorkState(ModelEnum):
    DRAFT = EnumValue('df', 'Draft')
    PUBLISHED = EnumValue('pb', 'Published')
    DELETED = EnumValue('dl', 'Deleted')

WORK_NOT_FOUND = _('Work not found')
WORKITEM_NOT_FOUND = _('Work item not found')
