from rattle.utils.enums import enum


@enum
class Level:
    IN_TESTS = 10
    IN_PRODUCTION = 20
    WARN_LATER = 30
    ERROR_NOW = 40
