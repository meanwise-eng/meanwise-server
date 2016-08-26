"""
    Base class for creating model choice enums
"""
from six import with_metaclass


class EnumValue(object):
    """
        Class to be used to specify values on an enum. This opens up possibilities of some further abstraction
        and extensibility.
        However the reason that makes this class mandatory is the need to maintain the order in which the enum
        values have been defined on their class. Django uses this approach as well.
        python 3 has capabilities that allow ordering without needing a field class such as this one
    """
    counter = 0

    def __init__(self, value, verboseName):
        self.value = value
        self.verboseName = verboseName
        EnumValue.counter += 1
        self.counter = EnumValue.counter

    def modelFieldChoice(self):
        return (self.value, self.verboseName)

    def __lt__(self, other):
        return self.counter < other.counter


class ModelEnumMeta(type):
    """
        Meta class for enum classes to be used for model choices.
    """
    def __init__(cls, name, bases, attrs):
        # Get all the all caps class variables (enum values)
        enumValues = {}  # will contain attribName : (value, verboseName)
        for attr in attrs:
            if attr.isupper():
                enumValue = attrs[attr]
                if not isinstance(enumValue, EnumValue):
                    raise ValueError("Error in %s.%s Enum values are expected to be instances of the EnumValue class" %
                            (cls.__name__, attr))
                enumValue.name = attr
                enumValues[attr] = enumValue
                setattr(cls, attr, enumValue.value)

        cls._enumValues = enumValues


class ModelEnum(with_metaclass(ModelEnumMeta, object)):
    """
        Base class for creating enums to use for choices in models
        Usage:
            class TestChoices(ModelEnum):
                CHOICE1 = EnumValue(value1, "verbose name 1")
                CHOICE2 = EnumValue(value2, "verbose name 2")
                CHOICE3 = EnumValue(value3, "verbose name 3")

        TestChoices.CHOICE1 == value1 # True
        TestChoices.choices()
            returns [(value1, "verbose name 1"), (value2, "verbose name 2"), (value3, "verbose name 3")]
        TestChoices.choices() can be used directly for field.choices.

        The choice fields on the enum class must be named with all caps to be picked up as choices.
    """
    @classmethod
    def choices(cls):
        return [enumValue.modelFieldChoice() for enumValue in sorted(cls._enumValues.values())]

    @classmethod
    def verboseName(cls, value):
        matches = [enumVal for enumVal in cls._enumValues.values() if enumVal.value == value]
        if len(matches) != 1:
            raise ValueError("Invalid value provided for enum %s: %s" % (cls.__name__, value))
        return matches[0].verboseName

    @classmethod
    def validateValue(cls, value):
        matches = [enumVal for enumVal in cls._enumValues.values() if enumVal.value == value]
        if len(matches) != 1:
            raise ValueError("Invalid value provided for enum %s: %s" % (cls.__name__, value))
