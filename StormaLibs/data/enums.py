import enum


__all__ = ("Types", )


class Types(enum.StrEnum):
    not_perms = "not_perm"           # insufficient rights
    not_perm_user = "not_perm_user"  # user has no rights
    is_bot = "is_bot"                # Is member not bot
    RE = "RE"                        # Response ERROR
    idtgag = "idtgag"                # insufficient data to generate a graph
    not_owner = "not_owner"          # user is not the owner of the guild
    not_activity = "not_activity"    # server offline
    DM_NOT_GUILD = "dm_not_guild"
