from dataclasses import dataclass, field


@dataclass(slots=True)
class Entity:
    entity_id: str
    canonical_name: str
    entity_type: str
    aliases: list[str] = field(default_factory=list)
    attributes: dict = field(default_factory=dict)
