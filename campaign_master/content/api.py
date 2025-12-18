from abc import abstractmethod, ABCMeta
from typing import Self
from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
)

from .settings import GUISettings
from . import planning


settings = GUISettings()
engine = create_engine(
    settings.db_settings.db_scheme, connect_args=settings.db_settings.db_connect_args
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# class ObjectMeta(DeclarativeMeta, ABCMeta):
#     pass


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


# HACK: Create a default ProtoUser with ID 0
# For applications where no ProtoUser, create a default one with ID 0.
with Session() as session:
    Base.metadata.create_all(bind=engine, tables=[ProtoUser.__table__], checkfirst=True)
    if session.query(ProtoUser).filter_by(id=0).first() is None:
        session.add(ProtoUser(id=0))
        session.commit()
    else:
        pass  # Default ProtoUser already exists


# All Objects should mirror the planning.py business logic.
class ObjectID(Base):
    __tablename__ = "object_id"
    __pydantic_model__ = planning.ID
    """
    SQLModel representation of the ID for database storage.
    Inherits from planning.ID.
    """
    proto_user_id: Mapped[int] = mapped_column(
        ForeignKey("proto_user.id"), primary_key=True
    )
    """
    Owner of the ID (ProtoUser).
    0 indicates a global ID.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    """
    The prefix part of the ID. Defined by the object type.
    """
    prefix: Mapped[str] = mapped_column(primary_key=True)
    """
    The numeric part of the ID.
    """
    numeric: Mapped[int] = mapped_column(primary_key=True)
    # """
    # Indicates whether the ID has been released back to the pool.
    # """
    # released: Mapped[bool] = mapped_column(default=False)

    @classmethod
    def generate_id(cls, prefix: str, proto_user_id: int = 0) -> "ObjectID":
        """Generate a new unique ID with the given prefix for the specified user."""
        with Session() as session:
            # query first for released IDs, reuse if available
            # released_id = (
            #     session.query(cls)
            #     .filter_by(prefix=prefix, released=True, proto_user_id=proto_user_id)
            #     .order_by(cls.numeric)
            #     .first()
            # )
            # if released_id:
            #     released_id.released = False
            #     session.flush()
            #     return released_id
            # Otherwise, create a new ID
            max_numeric = (
                session.query(cls)
                .filter_by(prefix=prefix, proto_user_id=proto_user_id)
                .order_by(cls.numeric.desc())
                .first()
            )
            next_numeric = 1 if not max_numeric else max_numeric.numeric + 1
            new_id = cls(
                prefix=prefix,
                numeric=next_numeric,
                proto_user_id=proto_user_id,
            )
            session.add(new_id)
            session.flush()
            return new_id

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

    def to_pydantic(self) -> "planning.ID":
        """Convert to planning.ID."""
        return planning.ID(prefix=self.prefix, numeric=self.numeric)

    def from_pydantic(
        self, id_obj: "planning.ID", proto_user_id: int = 0
    ) -> "ObjectID":
        """Create ObjectID from planning.ID."""
        return ObjectID(
            prefix=id_obj.prefix, numeric=id_obj.numeric, proto_user_id=proto_user_id
        )


class ObjectBase(
    Base,
):
    __tablename__ = "object_base"
    __abstract__ = True

    __pydantic_model__ = planning.Object

    @classmethod
    def _generate_id(cls, proto_user_id: int = 0) -> ObjectID:
        return ObjectID.generate_id(prefix=cls.__pydantic_model__._default_prefix, proto_user_id=proto_user_id)
    """
    SQLModel representation of the base object in the planning system.
    Inherits from planning.Object.
    """
    id: Mapped[int] = mapped_column(ForeignKey("object_id.id"), primary_key=True, default_factory=lambda: ObjectBase._generate_id().id)

    @declared_attr
    def obj_id(cls) -> Mapped[ObjectID]:
        return relationship("ObjectID", backref=cls.__tablename__, uselist=False)

    @abstractmethod
    def to_pydantic(self) -> "PydanticBaseModel":
        pass

    @classmethod
    @abstractmethod
    def from_pydantic(cls, obj) -> "Self":
        pass


class RuleComponent(Base):
    __tablename__ = "rule_component"
    """
    SQLModel representation of a Rule Component in the planning system.
    Inherits from planning.RuleComponent.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column()


class Rule(ObjectBase):
    __tablename__ = "rule"
    __pydantic_model__ = planning.Rule
    """
    SQLModel representation of a Rule in the planning system.
    Inherits from planning.Rule.
    """
    description: Mapped[str] = mapped_column()
    effect: Mapped[str] = mapped_column()
    components: Mapped[list[RuleComponent]] = relationship(
        "RuleComponent", backref="rule"
    )

    def to_pydantic(self) -> "planning.Rule":
        return planning.Rule(
            obj_id=self.obj_id.to_pydantic(),
            description=self.description,
            effect=self.effect,
            components=[comp.value for comp in self.components],
        )

    @classmethod
    def from_pydantic(cls, obj: "planning.Rule") -> "Rule":
        return cls(
            description=obj.description,
            effect=obj.effect,
            components=[RuleComponent(value=comp) for comp in obj.components],
        )


class ObjectiveComponent(Base):
    __tablename__ = "objective_component"
    """
    SQLModel representation of an Objective Component in the planning system.
    Inherits from planning.ObjectiveComponent.
    """
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    value: Mapped[str] = mapped_column()


class ObjectivePrerequisite(Base):
    __tablename__ = "objective_prerequisite"
    """
    Association table for Objective prerequisites.
    """
    objective_id: Mapped[int] = mapped_column(
        ForeignKey("objective.id"), primary_key=True
    )
    prerequisite_id: Mapped[int] = mapped_column(
        ForeignKey("objective.id"), primary_key=True
    )


class Objective(ObjectBase):
    __tablename__ = "objective"
    """
    SQLModel representation of an Objective in the planning system.
    Inherits from planning.Objective.
    """
    description: Mapped[str] = mapped_column()
    components: Mapped[list[ObjectiveComponent]] = relationship(
        "ObjectiveComponent", backref="objective"
    )
    # Not sure about the below, testing required.
    prerequisites: Mapped[list["Objective"]] = relationship(
        "Objective",
        secondary="objective_prerequisite",
        primaryjoin="Objective.id==ObjectivePrerequisite.objective_id",
        secondaryjoin="Objective.id==ObjectivePrerequisite.prerequisite_id",
        backref="dependent_objectives",
    )

    def to_pydantic(self) -> "planning.Objective":
        return planning.Objective(
            obj_id=self.obj_id.to_pydantic(),
            description=self.description,
            components=[comp.value for comp in self.components],
            prerequisites=[
                prereq.obj_id.to_pydantic() for prereq in self.prerequisites
            ],
        )
    
    @classmethod
    def from_pydantic(cls, obj: "planning.Objective") -> "Objective":
        return cls(
            description=obj.description,
            components=[ObjectiveComponent(value=comp) for comp in obj.components],
            # Prerequisites handling may require session management; omitted for brevity.
        )


class Point(ObjectBase):
    __tablename__ = "point"
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


class Segment(ObjectBase):
    __tablename__ = "segment"
    """
    SQLModel representation of a Segment in the planning system.
    Inherits from planning.Segment.
    """
    title: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    # Point data
    start_id: Mapped[int] = mapped_column(ForeignKey("point.id"))
    start: Mapped[Point] = relationship(
        "Point", foreign_keys="[Segment.start_id]", backref="segment_starts"
    )
    end_id: Mapped[int] = mapped_column(ForeignKey("point.id"))
    end: Mapped[Point] = relationship(
        "Point", foreign_keys="[Segment.end_id]", backref="segment_ends"
    )


class Arc(ObjectBase):
    __tablename__ = "arc"
    """
    SQLModel representation of an Arc in the planning system.
    Inherits from planning.Arc.
    """
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    segments: Mapped[list[Segment]] = relationship("Segment", backref="arc")


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
    """
    SQLModel representation of an Item in the planning system.
    Inherits from planning.Item.
    """
    name: Mapped[str] = mapped_column()
    type_: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()

    _properties: Mapped[list[ItemProperty]] = relationship(
        "ItemProperty", backref="item"
    )

    @property  # Heh, different type of property
    def properties(self) -> dict[str, str]:
        return {prop.key: prop.value for prop in self._properties}

    @properties.setter
    def properties(self, props: dict[str, str]):
        self._properties = [ItemProperty(key=k, value=v) for k, v in props.items()]


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
    """
    SQLModel representation of a Character in the planning system.
    Inherits from planning.Character.
    """
    name: Mapped[str] = mapped_column()
    role: Mapped[str] = mapped_column()
    backstory: Mapped[str] = mapped_column()

    _attributes: Mapped[list[CharacterAttribute]] = relationship(
        "CharacterAttribute", backref="character"
    )

    @property
    def attributes(self) -> dict[str, int]:
        return {attr.key: attr.value for attr in self._attributes}

    @attributes.setter
    def attributes(self, attrs: dict[str, int]):
        self._attributes = [
            CharacterAttribute(key=k, value=v) for k, v in attrs.items()
        ]

    _skills: Mapped[list[CharacterSkill]] = relationship(
        "CharacterSkill", backref="character"
    )

    @property
    def skills(self) -> dict[str, int]:
        return {skill.key: skill.value for skill in self._skills}

    @skills.setter
    def skills(self, skills: dict[str, int]):
        self._skills = [CharacterSkill(key=k, value=v) for k, v in skills.items()]

    storylines: Mapped[list[Arc]] = relationship(
        "Arc", secondary="character_storylines", backref="characters"
    )
    inventory: Mapped[list[Item]] = relationship(
        "Item", secondary="character_inventory", backref="owners"
    )


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


class Location(ObjectBase):
    __tablename__ = "location"
    """
    SQLModel representation of a Location in the planning system.
    Inherits from planning.Location.
    """
    name: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    coords: Mapped[LocationCoord | None] = relationship(
        "LocationCoord", uselist=False, backref="location"
    )
    neighboring_locations: Mapped[list["Location"]] = relationship(
        "Location",
        secondary="location_neighbors",
        primaryjoin="Location.id==LocationNeighbor.location_id",
        secondaryjoin="Location.id==LocationNeighbor.neighbor_id",
        backref="neighbors",
    )


class CampaignPlan(ObjectBase):
    __tablename__ = "campaign_plan"
    """
    SQLModel representation of a Campaign Plan in the planning system.
    Inherits from planning.CampaignPlan.
    """
    title: Mapped[str] = mapped_column()
    version: Mapped[str] = mapped_column()
    setting: Mapped[str] = mapped_column()
    summary: Mapped[str] = mapped_column()
    # These relationships may be unnecessary, depending on how we load the full plan.
    storypoints: Mapped[list[Arc]] = relationship("Arc", backref="campaign_plan")
    characters: Mapped[list[Character]] = relationship(
        "Character", backref="campaign_plan"
    )
    locations: Mapped[list[Location]] = relationship(
        "Location", backref="campaign_plan"
    )
    items: Mapped[list[Item]] = relationship("Item", backref="campaign_plan")
