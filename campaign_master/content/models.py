from typing import Self

from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column, relationship

from ..util import get_basic_logger
from . import planning

logger = get_basic_logger(__name__)

# Base = declarative_base(metaclass=ObjectMeta)
Base = declarative_base()


class ProtoUser(Base):
    __tablename__ = "proto_user"
    """
    SQLModel representation of a user in the system.
    """
    id: Mapped[int] = mapped_column(primary_key=True)
    # Serves no real purpose for GUI, but useful for Web API.
    #  Links collections of objects to a user.


# All Objects should mirror the planning.py business logic.
class ObjectID(Base):
    __tablename__ = "object_id"
    __pydantic_model__ = planning.ID
    """
    SQLModel representation of the ID for database storage.
    Inherits from planning.ID.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """
    The prefix part of the ID. Defined by the object type.
    """
    proto_user_id: Mapped[int] = mapped_column(ForeignKey("proto_user.id"), index=True)
    """
    Owner of the ID (ProtoUser).
    0 indicates a global ID.
    """
    prefix: Mapped[str] = mapped_column(index=True)
    """
    The numeric part of the ID.
    """
    numeric: Mapped[int] = mapped_column(index=True)
    # """
    # Indicates whether the ID has been released back to the pool.
    # """
    # released: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return self.to_pydantic().__repr__()

    # NOTE: Moving DB manipulation logic to api.py for better separation of concerns.

    # @classmethod
    # def release_id(cls, id_obj: "planning.ID"):
    #     """
    #     Release the given ID back to the pool.
    #     NOTE: This should only be called when an object is deleted.
    #     """
    #     with Session() as session:
    #         db_id = (
    #             session.query(cls)
    #             .filter_by(
    #                 prefix=id_obj.prefix,
    #                 numeric=id_obj.numeric,
    #             )
    #             .first()
    #         )
    #         if db_id:
    #             db_id.released = True
    #             session.flush()

    def to_pydantic(self, session: Session | None = None) -> "planning.ID":
        """Convert to planning.ID."""
        # session parameter accepted for consistency, but not used
        return planning.ID(prefix=self.prefix, numeric=self.numeric)

    @classmethod
    def from_pydantic(
        cls,
        id_obj: "planning.ID",
        proto_user_id: int = 0,
        session: Session | None = None,
    ) -> "Self":
        """
        Create ObjectID from planning.ID.
        Checks if the ID already exists; if not, creates a new one.

        Note: This method does NOT commit. Caller is responsible for commit.
        """

        # Query to see if it exists
        def perform(session):
            from . import api as content_api

            existing = content_api._retrieve_id(
                prefix=id_obj.prefix,
                numeric=id_obj.numeric,
                proto_user_id=proto_user_id,
                session=session,
            )
            if not existing:
                logger.debug("No existing ID found, creating new ObjectID for %s", id_obj)
                return content_api._generate_id(
                    prefix=id_obj.prefix,
                    proto_user_id=proto_user_id,
                    session=session,
                    auto_commit=False,
                )
            else:
                logger.debug("Existing ID found: %s", existing)
            return existing

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)


class ObjectBase(
    Base,
):
    __tablename__ = "object_base"
    __abstract__ = True

    __pydantic_model__ = planning.Object

    # @classmethod
    # def _generate_id(cls, proto_user_id: int = 0) -> ObjectID:
    #     from .api import generate_id
    #     logger.debug(f"Generating ID for {cls.__name__} with prefix {cls.__pydantic_model__._default_prefix} and proto_user_id {proto_user_id}.")
    #     return cls.from_pydantic(
    #         cls.__pydantic_model__.model_validate({
    #             "obj_id": generate_id(
    #                 prefix=cls.__pydantic_model__._default_prefix,
    #                 proto_user_id=proto_user_id,
    #             )
    #         })
    #     )

    """
    SQLModel representation of the base object in the planning system.
    Inherits from planning.Object.
    """
    id: Mapped[int] = mapped_column(
        ForeignKey("object_id.id"),
        primary_key=True,
    )

    # def __init__(self, **kwargs):
    #     if 'id' not in kwargs:
    #         kwargs['id'] = self._generate_id().id
    #     super().__init__(**kwargs)

    # @declared_attr
    # def obj_id(cls) -> Mapped[ObjectID]:
    #     return relationship(
    #         "ObjectID", backref=cls.__tablename__, uselist=False, foreign_keys=[cls.id]
    #     )
    def obj_id(self, session: Session):
        obj_id = session.execute(select(ObjectID).where(ObjectID.id == self.id)).scalars().first()
        if not obj_id:
            raise ValueError(
                f"ObjectID with id {self.id} not found in DB. This is likely an orphaned object, or one created improperly."
            )
        return obj_id

    def to_pydantic(self, session: Session) -> "planning.Object":
        obj = planning.Object.model_validate(
            {
                "obj_id": self.obj_id(session=session).to_pydantic(),
                **self.__pydantic_model__.model_validate(self).model_dump(),
            }
        )
        logger.debug("Converted to pydantic: %s %s", obj, type(obj))
        return obj

    @classmethod
    def from_pydantic(
        cls,
        obj: "planning.Object",
        proto_user_id: int = 0,
        session: Session | None = None,
    ) -> "Self":
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            return cls(
                obj_id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session),
            )

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(obj_id={self.id})>"


class RuleComponent(Base):
    __tablename__ = "rule_component"
    """
    SQLModel representation of a Rule Component in the planning system.
    Inherits from planning.RuleComponent.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column()
    rule_id: Mapped[int] = mapped_column(ForeignKey("rule.id"))


class Rule(ObjectBase):
    __tablename__ = "rule"
    __pydantic_model__ = planning.Rule
    """
    SQLModel representation of a Rule in the planning system.
    """
    description: Mapped[str] = mapped_column()
    effect: Mapped[str] = mapped_column()
    components: Mapped[list[RuleComponent]] = relationship(
        "RuleComponent", backref="rule", cascade="all, delete-orphan"
    )

    def to_pydantic(self, session: Session) -> "planning.Rule":
        obj_id = self.obj_id(session=session).to_pydantic()
        logger.debug("Rule obj_id retrieved: %s", obj_id)
        obj = planning.Rule(
            obj_id=obj_id,  # type: ignore[arg-type]  # added in Object constructor
            description=self.description,
            effect=self.effect,
            components=[comp.value for comp in self.components],
        )
        # logger.debug("Converted to pydantic: %s %s", obj, type(obj))
        return obj

    @classmethod
    def from_pydantic(cls, obj: "planning.Rule", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        # check for existing
        # First get the ObjectID
        def perform(session: Session) -> "Self":
            from . import api as content_api

            # First find existing ID
            # logger.debug("Retrieving ID for Rule... (%s)", obj.obj_id)

            obj_id_db = content_api._retrieve_id(
                prefix=obj.obj_id.prefix,
                numeric=obj.obj_id.numeric,
                proto_user_id=proto_user_id,
                session=session,
            )
            if not obj_id_db:
                # FIXME: This should not happen due to pydantic validation, log warning
                # logger.warning("No ID found for Rule: %s", obj.obj_id)
                # obj_id_db = content_api._generate_id(
                #     prefix=obj.obj_id.prefix, proto_user_id=proto_user_id, session=session, auto_commit=False
                # )
                raise ValueError(f"No ID found for Rule: {obj.obj_id}")
            # else:
            #     logger.debug("Found existing ID for Rule: %s", obj_id_db)
            # Now check for existing Rule with this ID
            existing = session.execute(select(cls).where(cls.id == obj_id_db.id)).scalars().first()
            # logger.debug("Existing Rule found: %s", existing)
            if existing:
                return existing
            # logger.debug("Creating new Rule from pydantic using ObjectID: %s", obj)
            db_obj = cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                description=obj.description,
                effect=obj.effect,
                components=[RuleComponent(value=comp) for comp in obj.components],
            )
            # logger.debug("Created Rule in DB: %s", db_obj)
            # logger.debug("w/ obj_id: %s", db_obj.obj_id(session=session))
            result = session.execute(select(ObjectID).where(ObjectID.id == db_obj.id))
            # logger.debug("Retrieved ObjectID: %s", result.scalars().first())
            return db_obj

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Rule", session: Session) -> None:
        """Update this Rule's fields from a Pydantic Rule model."""
        self.description = obj.description
        self.effect = obj.effect
        # Clear existing components before setting new ones (to avoid orphan constraint errors)
        for comp in self.components:
            session.delete(comp)
        self.components = [RuleComponent(value=comp) for comp in obj.components]


class ObjectiveComponent(Base):
    __tablename__ = "objective_component"
    """
    SQLModel representation of an Objective Component in the planning system.
    Inherits from planning.ObjectiveComponent.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    objective_id: Mapped[int] = mapped_column(ForeignKey("objective.id"))
    value: Mapped[str] = mapped_column()


class ObjectivePrerequisite(Base):
    __tablename__ = "objective_prerequisite"
    """
    Association table for Objective prerequisites.
    """
    objective_id: Mapped[int] = mapped_column(ForeignKey("objective.id"), primary_key=True)
    prerequisite_id: Mapped[int] = mapped_column(ForeignKey("objective.id"), primary_key=True)


class Objective(ObjectBase):
    __tablename__ = "objective"
    __pydantic_model__ = planning.Objective
    """
    SQLModel representation of an Objective in the planning system.
    Inherits from planning.Objective.
    """
    description: Mapped[str] = mapped_column()
    components: Mapped[list[ObjectiveComponent]] = relationship(
        "ObjectiveComponent", backref="objective", cascade="all, delete-orphan"
    )
    # Not sure about the below, testing required.
    prerequisites: Mapped[list["Objective"]] = relationship(
        "Objective",
        secondary="objective_prerequisite",
        primaryjoin="Objective.id==ObjectivePrerequisite.objective_id",
        secondaryjoin="Objective.id==ObjectivePrerequisite.prerequisite_id",
        backref="dependent_objectives",
    )

    def to_pydantic(self, session: Session) -> "planning.Objective":
        return planning.Objective(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type] # added in Object constructor
            description=self.description,
            components=[comp.value for comp in self.components],
            prerequisites=[prereq.obj_id(session=session).to_pydantic() for prereq in self.prerequisites],
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Objective", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            objective = cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                description=obj.description,
                components=[ObjectiveComponent(value=comp) for comp in obj.components],
            )
            session.add(objective)
            session.flush()  # Ensure objective has an ID for relationships

            # Handle prerequisites (list of Objective IDs - self-referential)
            for prereq_id in obj.prerequisites:
                prereq_obj_id = ObjectID.from_pydantic(prereq_id, proto_user_id=proto_user_id, session=session)
                prereq = session.execute(select(cls).where(cls.id == prereq_obj_id.id)).scalars().first()
                if prereq:
                    objective.prerequisites.append(prereq)

            return objective

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Objective", session: Session) -> None:
        """Update this Objective's fields from a Pydantic Objective model."""
        self.description = obj.description
        # Clear existing components before setting new ones (to avoid orphan constraint errors)
        for comp in self.components:
            session.delete(comp)
        self.components = [ObjectiveComponent(value=comp) for comp in obj.components]

        # Update prerequisites relationship
        self.prerequisites.clear()
        for prereq_id in obj.prerequisites:
            prereq_obj_id = ObjectID.from_pydantic(prereq_id, proto_user_id=0, session=session)
            prereq = session.execute(select(Objective).where(Objective.id == prereq_obj_id.id)).scalars().first()
            if prereq:
                self.prerequisites.append(prereq)


class Point(ObjectBase):
    __tablename__ = "point"
    __pydantic_model__ = planning.Point
    """
    SQLModel representation of a Point in the planning system.
    Inherits from planning.Point.
    """
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    objective_id: Mapped[int | None] = mapped_column(ForeignKey("objective.id"))
    objective: Mapped[Objective | None] = relationship(
        "Objective", foreign_keys="[Point.objective_id]", backref="points"
    )

    def to_pydantic(self, session: Session) -> "planning.Point":
        return planning.Point(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            name=self.name,
            description=self.description,
            objective=(self.objective.obj_id(session=session).to_pydantic() if self.objective else None),
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Point", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            # Check for existing
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id
                        == ObjectID.from_pydantic(
                            obj.obj_id,
                            proto_user_id=proto_user_id,
                            session=session,
                        ).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            # Get the objective_id if an objective is specified
            objective_obj_id = None
            if obj.objective:
                objective_obj_id = ObjectID.from_pydantic(obj.objective, proto_user_id=proto_user_id, session=session)

            return cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                name=obj.name,
                description=obj.description,
                objective_id=objective_obj_id.id if objective_obj_id else None,
            )

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Point", session: Session) -> None:
        """Update this Point's fields from a Pydantic Point model."""
        self.name = obj.name
        self.description = obj.description

        if obj.objective:
            # Find the objective by ID
            obj_id = ObjectID.from_pydantic(obj.objective, proto_user_id=0, session=session)
            self.objective_id = obj_id.id
        else:
            self.objective_id = None


class Segment(ObjectBase):
    __tablename__ = "segment"
    __pydantic_model__ = planning.Segment
    """
    SQLModel representation of a Segment in the planning system.
    Inherits from planning.Segment.
    """
    arc_id: Mapped[int | None] = mapped_column(ForeignKey("arc.id"), nullable=True)
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    # Point data
    start_id: Mapped[int | None] = mapped_column(ForeignKey("point.id"), nullable=True)
    start: Mapped[Point | None] = relationship("Point", foreign_keys="[Segment.start_id]", backref="segment_starts")
    end_id: Mapped[int | None] = mapped_column(ForeignKey("point.id"), nullable=True)
    end: Mapped[Point | None] = relationship("Point", foreign_keys="[Segment.end_id]", backref="segment_ends")

    def to_pydantic(self, session: Session) -> "planning.Segment":
        return planning.Segment(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            name=self.name,
            description=self.description,
            start=(
                self.start.obj_id(session=session).to_pydantic() if self.start else planning.ID(prefix="P", numeric=0)
            ),
            end=(self.end.obj_id(session=session).to_pydantic() if self.end else planning.ID(prefix="P", numeric=0)),
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Segment", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            # Try to find the start and end points in the database
            start_obj_id = ObjectID.from_pydantic(obj.start, proto_user_id=proto_user_id, session=session)
            end_obj_id = ObjectID.from_pydantic(obj.end, proto_user_id=proto_user_id, session=session)

            return cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                name=obj.name,
                description=obj.description,
                start_id=start_obj_id.id if start_obj_id.numeric != 0 else None,
                end_id=end_obj_id.id if end_obj_id.numeric != 0 else None,
            )

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Segment", session: Session) -> None:
        """Update this Segment's fields from a Pydantic Segment model."""
        self.name = obj.name
        self.description = obj.description
        # Update start point reference
        if obj.start:
            start_obj_id = ObjectID.from_pydantic(obj.start, proto_user_id=0, session=session)
            self.start_id = start_obj_id.id if start_obj_id.numeric != 0 else None
        else:
            self.start_id = None
        # Update end point reference
        if obj.end:
            end_obj_id = ObjectID.from_pydantic(obj.end, proto_user_id=0, session=session)
            self.end_id = end_obj_id.id if end_obj_id.numeric != 0 else None
        else:
            self.end_id = None


class Arc(ObjectBase):
    __tablename__ = "arc"
    __pydantic_model__ = planning.Arc
    """
    SQLModel representation of an Arc in the planning system.
    Inherits from planning.Arc.
    """
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    segments: Mapped[list[Segment]] = relationship("Segment", backref="arc")

    def to_pydantic(self, session: Session) -> "planning.Arc":
        return planning.Arc(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            name=self.name,
            description=self.description,
            segments=[seg.to_pydantic(session=session) for seg in self.segments],
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Arc", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            return cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                name=obj.name,
                description=obj.description,
                segments=[
                    Segment.from_pydantic(seg, proto_user_id=proto_user_id, session=session) for seg in obj.segments
                ],
            )

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Arc", session: Session) -> None:
        """Update this Arc's fields from a Pydantic Arc model."""
        self.name = obj.name
        self.description = obj.description
        # Note: Updating segments is complex as they are related objects
        # For simplicity, we only update scalar fields here


class ArcToCampaign(Base):
    __tablename__ = "campaign_arc"
    """
    Association table for CampaignPlan and their Arcs (Storylines).
    """
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign_plan.id"), primary_key=True)
    arc_id: Mapped[int] = mapped_column(ForeignKey("arc.id"), primary_key=True)


class PointToCampaign(Base):
    __tablename__ = "campaign_point"
    """
    Association table for CampaignPlan and their Points (Storypoints).
    """
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign_plan.id"), primary_key=True)
    point_id: Mapped[int] = mapped_column(ForeignKey("point.id"), primary_key=True)


class ItemProperty(Base):
    __tablename__ = "item_properties"
    """
    SQLModel representation of Item properties as key-value pairs.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
    key: Mapped[str] = mapped_column()
    value: Mapped[str] = mapped_column()


class Item(ObjectBase):
    __tablename__ = "item"
    __pydantic_model__ = planning.Item
    """
    SQLModel representation of an Item in the planning system.
    Inherits from planning.Item.
    """
    name: Mapped[str] = mapped_column()
    type_: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    _properties: Mapped[list[ItemProperty]] = relationship(
        "ItemProperty", backref="item", cascade="all, delete-orphan"
    )

    @property  # Heh, different type of property
    def properties(self) -> dict[str, str]:
        return {prop.key: prop.value for prop in self._properties}

    @properties.setter
    def properties(self, props: dict[str, str]):
        self._properties = [ItemProperty(key=k, value=v) for k, v in props.items()]

    def to_pydantic(self, session: Session) -> "planning.Item":
        return planning.Item(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            name=self.name,
            type_=self.type_,
            description=self.description,
            properties=self.properties,
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Item", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            return cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                name=obj.name,
                type_=obj.type_,
                description=obj.description,
                properties=obj.properties,
            )

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Item", session: Session) -> None:
        """Update this Item's fields from a Pydantic Item model."""
        self.name = obj.name
        self.type_ = obj.type_
        self.description = obj.description
        # Clear existing properties before setting new ones (to avoid orphan constraint errors)
        for prop in self._properties:
            session.delete(prop)
        self._properties = [ItemProperty(key=k, value=v) for k, v in obj.properties.items()]


class CampaignItem(Base):
    __tablename__ = "campaign_item"
    """
    Association table for CampaignPlan and their Items.
    """
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign_plan.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), primary_key=True)


class StorylineToCharacter(Base):
    __tablename__ = "character_storylines"
    """
    Association table for Characters and their Storylines (Arcs).
    """
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), primary_key=True)
    arc_id: Mapped[int] = mapped_column(ForeignKey("arc.id"), primary_key=True)


class CharacterInventory(Base):
    __tablename__ = "character_inventory"
    """
    Association table for Characters and their Items (Inventory).
    """
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"), primary_key=True)


class CharacterAttribute(Base):
    __tablename__ = "character_attributes"
    """
    SQLModel representation of Character attributes as key-value pairs.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"))
    key: Mapped[str] = mapped_column()
    value: Mapped[int] = mapped_column()


class CharacterSkill(Base):
    __tablename__ = "character_skills"
    """
    SQLModel representation of Character skills as key-value pairs.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"))
    key: Mapped[str] = mapped_column()
    value: Mapped[int] = mapped_column()


class Character(ObjectBase):
    __tablename__ = "character"
    __pydantic_model__ = planning.Character
    """
    SQLModel representation of a Character in the planning system.
    Inherits from planning.Character.
    """
    name: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column()
    backstory: Mapped[str] = mapped_column()

    _attributes: Mapped[list[CharacterAttribute]] = relationship(
        "CharacterAttribute", backref="character", cascade="all, delete-orphan"
    )

    @property
    def attributes(self) -> dict[str, int]:
        return {attr.key: attr.value for attr in self._attributes}

    @attributes.setter
    def attributes(self, attrs: dict[str, int]):
        self._attributes = [CharacterAttribute(key=k, value=v) for k, v in attrs.items()]

    _skills: Mapped[list[CharacterSkill]] = relationship(
        "CharacterSkill", backref="character", cascade="all, delete-orphan"
    )

    @property
    def skills(self) -> dict[str, int]:
        return {skill.key: skill.value for skill in self._skills}

    @skills.setter
    def skills(self, skills: dict[str, int]):
        self._skills = [CharacterSkill(key=k, value=v) for k, v in skills.items()]

    storylines: Mapped[list[Arc]] = relationship("Arc", secondary="character_storylines", backref="characters")
    inventory: Mapped[list[Item]] = relationship("Item", secondary="character_inventory", backref="owners")

    def to_pydantic(self, session: Session) -> "planning.Character":
        return planning.Character(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            name=self.name,
            role=self.role,
            backstory=self.backstory,
            attributes=self.attributes,
            skills=self.skills,
            inventory=[item.obj_id(session=session).to_pydantic() for item in self.inventory],
            storylines=[arc.obj_id(session=session).to_pydantic() for arc in self.storylines],
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Character", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            character = cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                name=obj.name,
                role=obj.role,
                backstory=obj.backstory,
                attributes=obj.attributes,
                skills=obj.skills,
            )
            session.add(character)
            session.flush()  # Ensure character has an ID for relationships

            # Handle inventory (list of Item IDs)
            for item_id in obj.inventory:
                item_obj_id = ObjectID.from_pydantic(item_id, proto_user_id=proto_user_id, session=session)
                item = session.execute(select(Item).where(Item.id == item_obj_id.id)).scalars().first()
                if item:
                    character.inventory.append(item)

            # Handle storylines (list of Arc IDs)
            for arc_id in obj.storylines:
                arc_obj_id = ObjectID.from_pydantic(arc_id, proto_user_id=proto_user_id, session=session)
                arc = session.execute(select(Arc).where(Arc.id == arc_obj_id.id)).scalars().first()
                if arc:
                    character.storylines.append(arc)

            return character

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Character", session: Session) -> None:
        """Update this Character's fields from a Pydantic Character model."""
        self.name = obj.name
        self.role = obj.role
        self.backstory = obj.backstory
        # Clear existing attributes before setting new ones (to avoid orphan constraint errors)
        for attr in self._attributes:
            session.delete(attr)
        self._attributes = [CharacterAttribute(key=k, value=v) for k, v in obj.attributes.items()]
        # Clear existing skills before setting new ones
        for skill in self._skills:
            session.delete(skill)
        self._skills = [CharacterSkill(key=k, value=v) for k, v in obj.skills.items()]

        # Update inventory relationship
        self.inventory.clear()
        for item_id in obj.inventory:
            item_obj_id = ObjectID.from_pydantic(item_id, proto_user_id=0, session=session)
            item = session.execute(select(Item).where(Item.id == item_obj_id.id)).scalars().first()
            if item:
                self.inventory.append(item)

        # Update storylines relationship
        self.storylines.clear()
        for arc_id in obj.storylines:
            arc_obj_id = ObjectID.from_pydantic(arc_id, proto_user_id=0, session=session)
            arc = session.execute(select(Arc).where(Arc.id == arc_obj_id.id)).scalars().first()
            if arc:
                self.storylines.append(arc)


class CharacterToCampaign(Base):
    __tablename__ = "campaign_character"
    """
    Association table for CampaignPlan and their Characters.
    """
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign_plan.id"), primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), primary_key=True)


class LocationCoord(Base):
    __tablename__ = "location_coords"
    """
    SQLModel representation of Location coordinates.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"))
    latitude: Mapped[float] = mapped_column()
    longitude: Mapped[float] = mapped_column()
    altitude: Mapped[float | None] = mapped_column()

    def to_pydantic(self, session: Session | None = None) -> tuple[float, float] | tuple[float, float, float]:
        """Convert to Pydantic tuple representation."""
        if self.altitude is not None:
            return (self.latitude, self.longitude, self.altitude)
        return (self.latitude, self.longitude)

    @classmethod
    def from_pydantic(
        cls,
        coords: tuple[float, float] | tuple[float, float, float],
        proto_user_id: int = 0,
        session: Session | None = None,
    ) -> "LocationCoord":
        """Create LocationCoord from tuple."""
        return cls(
            latitude=coords[0],
            longitude=coords[1],
            altitude=coords[2] if len(coords) > 2 else None,
        )


class LocationNeighbor(Base):
    __tablename__ = "location_neighbors"
    """
    Association table for neighboring Locations.
    """
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), primary_key=True)
    neighbor_id: Mapped[int] = mapped_column(ForeignKey("location.id"), primary_key=True)


class Location(ObjectBase):
    __tablename__ = "location"
    __pydantic_model__ = planning.Location
    """
    SQL model representation of a Location in the planning system.
    Inherits from planning.Location.
    """
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    coords: Mapped[LocationCoord | None] = relationship("LocationCoord", uselist=False, backref="location")
    neighboring_locations: Mapped[list["Location"]] = relationship(
        "Location",
        secondary="location_neighbors",
        primaryjoin="Location.id==LocationNeighbor.location_id",
        secondaryjoin="Location.id==LocationNeighbor.neighbor_id",
        backref="neighbors",
    )

    def to_pydantic(self, session: Session) -> "planning.Location":
        return planning.Location(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            name=self.name,
            description=self.description,
            coords=self.coords.to_pydantic(session=session) if self.coords else None,
            neighboring_locations=[loc.obj_id(session=session).to_pydantic() for loc in self.neighboring_locations],
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Location", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            location = cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                name=obj.name,
                description=obj.description,
                coords=(
                    LocationCoord.from_pydantic(obj.coords, proto_user_id=proto_user_id, session=session)
                    if obj.coords
                    else None
                ),
            )
            session.add(location)
            session.flush()  # Ensure location has an ID for relationships

            # Handle neighboring_locations (list of Location IDs)
            for neighbor_id in obj.neighboring_locations:
                neighbor_obj_id = ObjectID.from_pydantic(neighbor_id, proto_user_id=proto_user_id, session=session)
                neighbor = session.execute(select(cls).where(cls.id == neighbor_obj_id.id)).scalars().first()
                if neighbor:
                    location.neighboring_locations.append(neighbor)

            return location

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.Location", session: Session) -> None:
        """Update this Location's fields from a Pydantic Location model."""
        self.name = obj.name
        self.description = obj.description
        # Update coords if provided
        if obj.coords:
            if self.coords:
                # Update existing coords
                self.coords.latitude = obj.coords[0]
                self.coords.longitude = obj.coords[1]
                self.coords.altitude = obj.coords[2] if len(obj.coords) > 2 else None
            else:
                # Create new coords
                self.coords = LocationCoord(
                    latitude=obj.coords[0],
                    longitude=obj.coords[1],
                    altitude=obj.coords[2] if len(obj.coords) > 2 else None,
                )
        else:
            self.coords = None

        # Update neighboring_locations relationship
        self.neighboring_locations.clear()
        for neighbor_id in obj.neighboring_locations:
            neighbor_obj_id = ObjectID.from_pydantic(neighbor_id, proto_user_id=0, session=session)
            neighbor = session.execute(select(Location).where(Location.id == neighbor_obj_id.id)).scalars().first()
            if neighbor:
                self.neighboring_locations.append(neighbor)


class CampaignLocation(Base):
    __tablename__ = "campaign_location"
    """
    Association table for CampaignPlan and their Locations.
    """
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign_plan.id"), primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("location.id"), primary_key=True)


class CampaignRule(Base):
    __tablename__ = "campaign_rule"
    """
    Association table for CampaignPlan and their Rules.
    """
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign_plan.id"), primary_key=True)
    rule_id: Mapped[int] = mapped_column(ForeignKey("rule.id"), primary_key=True)


class CampaignObjective(Base):
    __tablename__ = "campaign_objective"
    """
    Association table for CampaignPlan and their Objectives.
    """
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaign_plan.id"), primary_key=True)
    objective_id: Mapped[int] = mapped_column(ForeignKey("objective.id"), primary_key=True)


class CampaignPlan(ObjectBase):
    __tablename__ = "campaign_plan"
    __pydantic_model__ = planning.CampaignPlan
    """
    SQLModel representation of a Campaign Plan in the planning system.
    Inherits from planning.CampaignPlan.
    """
    title: Mapped[str] = mapped_column()
    version: Mapped[str] = mapped_column()
    setting: Mapped[str] = mapped_column()
    summary: Mapped[str] = mapped_column()
    # These relationships may be unnecessary, depending on how we load the full plan.
    storypoints: Mapped[list[Point]] = relationship("Point", secondary="campaign_point", backref="campaign_plan_points")
    storyline: Mapped[list[Arc]] = relationship("Arc", secondary="campaign_arc", backref="campaign_plan_arcs")
    characters: Mapped[list[Character]] = relationship(
        "Character", secondary="campaign_character", backref="campaign_plan"
    )
    locations: Mapped[list[Location]] = relationship("Location", secondary="campaign_location", backref="campaign_plan")
    items: Mapped[list[Item]] = relationship("Item", secondary="campaign_item", backref="campaign_plan")
    rules: Mapped[list[Rule]] = relationship("Rule", secondary="campaign_rule", backref="campaign_plan")
    objectives: Mapped[list[Objective]] = relationship(
        "Objective", secondary="campaign_objective", backref="campaign_plan"
    )

    def to_pydantic(self, session: Session) -> "planning.CampaignPlan":
        return planning.CampaignPlan(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            title=self.title,
            version=self.version,
            setting=self.setting,
            summary=self.summary,
            storypoints=[pt.to_pydantic(session=session) for pt in self.storypoints],
            storyline=[arc.to_pydantic(session=session) for arc in self.storyline],
            characters=[char.to_pydantic(session=session) for char in self.characters],
            locations=[loc.to_pydantic(session=session) for loc in self.locations],
            items=[item.to_pydantic(session=session) for item in self.items],
            rules=[rule.to_pydantic(session=session) for rule in self.rules],
            objectives=[obj.to_pydantic(session=session) for obj in self.objectives],
        )

    def update_from_pydantic(self, obj: "planning.CampaignPlan", session: Session) -> None:
        """Update this CampaignPlan's fields from a Pydantic CampaignPlan model."""
        # Update scalar fields
        self.title = obj.title
        self.version = obj.version
        self.setting = obj.setting
        self.summary = obj.summary

        # Update relationships - clear and repopulate
        # Get proto_user_id from the ObjectID
        proto_user_id = self.obj_id(session=session).proto_user_id

        # Clear existing relationships
        self.storypoints.clear()
        self.storyline.clear()
        self.characters.clear()
        self.locations.clear()
        self.items.clear()
        self.rules.clear()
        self.objectives.clear()

        # Repopulate storypoints
        for point in obj.storypoints:
            point_obj = Point.from_pydantic(point, proto_user_id, session=session)
            self.storypoints.append(point_obj)

        # Repopulate storyline
        for arc in obj.storyline:
            arc_obj = Arc.from_pydantic(arc, proto_user_id, session=session)
            self.storyline.append(arc_obj)

        # Repopulate characters
        for char in obj.characters:
            char_obj = Character.from_pydantic(char, proto_user_id, session=session)
            self.characters.append(char_obj)

        # Repopulate locations
        for loc in obj.locations:
            loc_obj = Location.from_pydantic(loc, proto_user_id, session=session)
            self.locations.append(loc_obj)

        # Repopulate items
        for item in obj.items:
            item_obj = Item.from_pydantic(item, proto_user_id, session=session)
            self.items.append(item_obj)

        # Repopulate rules
        for rule in obj.rules:
            rule_obj = Rule.from_pydantic(rule, proto_user_id, session=session)
            self.rules.append(rule_obj)

        # Repopulate objectives
        for objective in obj.objectives:
            obj_db = Objective.from_pydantic(objective, proto_user_id, session=session)
            self.objectives.append(obj_db)

    @classmethod
    def from_pydantic(cls, obj: "planning.CampaignPlan", proto_user_id: int = 0, session: Session | None = None) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            campaign_plan = cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                title=obj.title,
                version=obj.version,
                setting=obj.setting,
                summary=obj.summary,
            )
            # Populate storypoints relationship
            for point in obj.storypoints:
                point_obj = Point.from_pydantic(point, proto_user_id, session=session)
                campaign_plan.storypoints.append(point_obj)
            # Populate storyline relationship
            for arc in obj.storyline:
                arc_obj = Arc.from_pydantic(arc, proto_user_id, session=session)
                campaign_plan.storyline.append(arc_obj)
            # Populate characters relationship
            for char in obj.characters:
                char_obj = Character.from_pydantic(char, proto_user_id, session=session)
                campaign_plan.characters.append(char_obj)
            # Populate locations relationship
            for loc in obj.locations:
                loc_obj = Location.from_pydantic(loc, proto_user_id, session=session)
                campaign_plan.locations.append(loc_obj)
            # Populate items relationship
            for item in obj.items:
                item_obj = Item.from_pydantic(item, proto_user_id, session=session)
                campaign_plan.items.append(item_obj)
            # Populate rules relationship
            for rule in obj.rules:
                rule_obj = Rule.from_pydantic(rule, proto_user_id, session=session)
                campaign_plan.rules.append(rule_obj)
            # Populate objectives relationship
            for objective in obj.objectives:
                obj_db = Objective.from_pydantic(objective, proto_user_id, session=session)
                campaign_plan.objectives.append(obj_db)
            return campaign_plan

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)


class AgentConfig(ObjectBase):
    __tablename__ = "agent_config"
    __pydantic_model__ = planning.AgentConfig
    """
    SQLAlchemy model for AI agent configuration.
    Stores settings for AI completion providers.
    """
    name: Mapped[str] = mapped_column(default="")
    provider_type: Mapped[str] = mapped_column(default="")
    api_key: Mapped[str] = mapped_column(default="")
    base_url: Mapped[str] = mapped_column(default="")
    model: Mapped[str] = mapped_column(default="")
    max_tokens: Mapped[int] = mapped_column(default=500)
    temperature: Mapped[float] = mapped_column(default=0.7)
    is_default: Mapped[bool] = mapped_column(default=False)
    is_enabled: Mapped[bool] = mapped_column(default=True)
    system_prompt: Mapped[str] = mapped_column(default="")

    def to_pydantic(self, session: Session) -> "planning.AgentConfig":
        return planning.AgentConfig(
            obj_id=self.obj_id(session=session).to_pydantic(),  # type: ignore[arg-type]  # added in Object constructor
            name=self.name,
            provider_type=self.provider_type,
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            is_default=self.is_default,
            is_enabled=self.is_enabled,
            system_prompt=self.system_prompt,
        )

    @classmethod
    def from_pydantic(
        cls,
        obj: "planning.AgentConfig",
        proto_user_id: int = 0,
        session: Session | None = None,
    ) -> "Self":  # type: ignore[override]
        """Create from pydantic. Does NOT commit - caller handles that."""

        def perform(session: Session) -> "Self":
            existing = (
                session.execute(
                    select(cls).where(
                        cls.id == ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id
                    )
                )
                .scalars()
                .first()
            )
            if existing:
                return existing
            return cls(
                id=ObjectID.from_pydantic(obj.obj_id, proto_user_id=proto_user_id, session=session).id,
                name=obj.name,
                provider_type=obj.provider_type,
                api_key=obj.api_key,
                base_url=obj.base_url,
                model=obj.model,
                max_tokens=obj.max_tokens,
                temperature=obj.temperature,
                is_default=obj.is_default,
                is_enabled=obj.is_enabled,
                system_prompt=obj.system_prompt,
            )

        if session is None:
            from .database import SessionLocal

            with SessionLocal() as session:
                try:
                    return perform(session)
                except Exception as e:
                    session.rollback()
                    raise
        return perform(session)

    def update_from_pydantic(self, obj: "planning.AgentConfig", session: Session) -> None:
        """Update this AgentConfig's fields from a Pydantic model."""
        self.name = obj.name
        self.provider_type = obj.provider_type
        self.api_key = obj.api_key
        self.base_url = obj.base_url
        self.model = obj.model
        self.max_tokens = obj.max_tokens
        self.temperature = obj.temperature
        self.is_default = obj.is_default
        self.is_enabled = obj.is_enabled
        self.system_prompt = obj.system_prompt


PydanticToSQLModel: dict[type[planning.Object] | type[planning.ID], type[ObjectBase] | type[ObjectID]] = {
    planning.ID: ObjectID,
    planning.Object: ObjectBase,
    planning.Rule: Rule,
    planning.Objective: Objective,
    planning.Point: Point,
    planning.Segment: Segment,
    planning.Arc: Arc,
    planning.Item: Item,
    planning.Character: Character,
    planning.Location: Location,
    planning.CampaignPlan: CampaignPlan,
    planning.AgentConfig: AgentConfig,
}
