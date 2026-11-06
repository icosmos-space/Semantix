from semantix.models.project import (
    ROLE_ADMIN,
    ROLE_MEMBER,
    ROLE_OWNER,
    ROLE_VIEWER,
    VALID_ROLES,
)

ROLE_RANK = {
    ROLE_VIEWER: 1,
    ROLE_MEMBER: 2,
    ROLE_ADMIN: 3,
    ROLE_OWNER: 4,
}


def role_at_least(role: str, minimum: str) -> bool:
    if role not in VALID_ROLES or minimum not in VALID_ROLES:
        return False
    return ROLE_RANK[role] >= ROLE_RANK[minimum]
