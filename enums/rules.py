from enum import Enum
from enums.roles import Role, VoteEnum


class VoteRules:

    rules = {
        'Mason' : "PROMOTE_TO_SILVER",
        'SilverMason' : "PROMOTE_TO_GOLDEN",
        'GoldMason' : "PROMOTE_TO_ARCHITECT"
    }

class PromoteRules:

    rules = {
        "PROMOTE_TO_SILVER" : Role.SILVER_MASON,
        "PROMOTE_TO_GOLDEN" : Role.GOLD_MASON,
        "PROMOTE_TO_ARCHITECT" : Role.ARCHITECT
    }

    new_rules = {
        "PROMOTE_TO_SILVER" : [Role.SILVER_MASON.value],
        "PROMOTE_TO_GOLDEN" : [Role.GOLD_MASON.value],
        "PROMOTE_TO_ARCHITECT" : [
                                Role.MASON.value,
                                Role.SILVER_MASON.value,
                                Role.GOLD_MASON.value
        ],
        "BAN_USER" : [
                                Role.MASON.value,
                                Role.SILVER_MASON.value,
                                Role.GOLD_MASON.value
        ]
    }