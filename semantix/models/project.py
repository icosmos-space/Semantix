from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from semantix.models.base import Base, TimestampMixin, uuid_pk

ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_MEMBER = "member"
ROLE_VIEWER = "viewer"
VALID_ROLES = {ROLE_OWNER, ROLE_ADMIN, ROLE_MEMBER, ROLE_VIEWER}


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = uuid_pk()
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)

    memberships = relationship(
        "Membership",
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Membership(Base, TimestampMixin):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("user_id", "project_id", name="uq_membership_user_project"),)

    id: Mapped[str] = uuid_pk()
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    project_id: Mapped[str] = mapped_column(String(36), ForeignKey("projects.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False, default=ROLE_MEMBER)

    user = relationship("User", back_populates="memberships")
    project = relationship("Project", back_populates="memberships")
