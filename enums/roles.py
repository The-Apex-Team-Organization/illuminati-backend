import enum


class Role(enum.Enum):
    GOLD_MASON = 'GoldMason'
    SILVER_MASON = 'SilverMason'
    MASON = 'Mason'
    ARCHITECT = "Architect"


class VoteEnum(enum.Enum):
    PROMOTE_TO_SILVER = 'PROMOTE_TO_SILVER'
    PROMOTE_TO_GOLDEN = 'PROMOTE_TO_GOLDEN'
    PROMOTE_TO_ARCHITECT = 'PROMOTE_TO_ARCHITECT'