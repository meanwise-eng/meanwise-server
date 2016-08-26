from common.model_enums import ModelEnum, EnumValue


class NotificationType(ModelEnum):
    FOLLOWED = EnumValue('fol', 'is now following')
    LIKED = EnumValue('lik', 'likes')
    COMMENTED = EnumValue('com', 'commented on')

    @classmethod
    def deletable(cls):
        return [cls.FOLLOWED, cls.LIKED, cls.COMMENTED]
