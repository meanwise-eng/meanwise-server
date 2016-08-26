from common.model_enums import EnumValue, ModelEnum


class EventType(ModelEnum):
    ACADEMIC = EnumValue('ac', 'Academic')
    ACHIEVEMENT = EnumValue('ah', 'Achievement')
    EVENT = EnumValue('ev', 'Event')
    PROJECT = EnumValue('pj', 'Project')
    PROFESSIONAL = EnumValue('pf', 'Professional')
    OTHER = EnumValue('ot', 'Other')
