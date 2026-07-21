from dataclasses import dataclass
from typing import Literal


HubKind = Literal["start", "end", "normal"]


class InvalidConfig(Exception):
    pass


@dataclass
class MapData:
    name: str
    x: int
    y: int
    kind: HubKind  # start / end / normal
    zone: str = "normal"
    color: str = "none"
    max_drones: int = 1


@dataclass
class Connection:
    from_hub: str
    to_hub: str
    max_link_cap: int = 1


def parse_metadata(text: str, line_no: int) -> dict[str, str]:
    """Parses Metadata from maps.txt file"""
    metadata: dict[str, str] = {}

    if not text:
        return metadata

    for item in text.split():
        if "=" not in item:
            raise InvalidConfig(f"Line {line_no}: invalid metadata '{item}'")

        key, value = item.split("=", 1)

        if key in metadata:
            raise InvalidConfig(
                f"Line {line_no}:"
                f"duplicate metadata key '{key}'")

        metadata[key] = value

    return metadata


def parse_file(filename: str) -> tuple[int, dict[str,
                                                 MapData], list[Connection]]:
    """Parses main file data and checks for errors"""
    nb_drones: int | None = None
    hubs: dict = {}
    connections: list[Connection] = []
    seen_connections: set[tuple[str, str]] = set()

    start_count = 0
    end_count = 0

    allowed_zones: set[str] = {"normal", "blocked", "restricted", "priority"}

    with open(filename, "r") as file:
        for line_no, raw_line in enumerate(file, start=1):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("nb_drones:"):
                if nb_drones is not None:
                    raise InvalidConfig(f"Line {line_no}: duplicate nb_drones")

                try:
                    nb_drones = int(line.split(":", 1)[1].strip())
                except InvalidConfig:
                    raise InvalidConfig(
                        f"Line {line_no}:"
                        "invalid nb_drones format")

                if nb_drones <= 0:
                    raise InvalidConfig(
                        f"Line {line_no}:"
                        "nb_drones must be positive")

                continue

            # enforces nb_drone must be first
            if nb_drones is None:
                raise InvalidConfig(
                    f"Line {line_no}:"
                    "nb_drones must be defined first")

            if line.startswith("connection:"):
                content = line[len("connection:"):].strip()
                metadata = ""

                if "[" in content:
                    content, metadata = content.split("[", 1)
                    metadata = metadata.rstrip("]")

                try:
                    hub1, hub2 = content.strip().split("-")
                except Exception:
                    raise InvalidConfig(
                        f"Line {line_no}:"
                        "invalid connection format")

                hub1 = hub1.strip()
                hub2 = hub2.strip()

                # check hubs exist
                if hub1 not in hubs or hub2 not in hubs:
                    raise InvalidConfig(
                        f"Line {line_no}: connection uses undefined hub"
                    )

                # undirected duplicate check
                edge = (hub1, hub2) if hub1 < hub2 else (hub2, hub1)
                if edge in seen_connections:
                    raise InvalidConfig(
                        f"Line {line_no}: duplicate connection {hub1}-{hub2}"
                    )
                seen_connections.add(edge)

                meta = parse_metadata(metadata, line_no)

                cap = int(meta.get("max_link_capacity", 1))
                if cap <= 0:
                    raise InvalidConfig(
                        f"Line {line_no}: max_link_capacity must be positive"
                    )

                connections.append(
                    Connection(
                        from_hub=hub1,
                        to_hub=hub2,
                        max_link_cap=cap
                    )
                )
                continue

            kind: HubKind | None = None

            if line.startswith("start_hub:"):
                kind = "start"
                content = line[len("start_hub:"):].strip()
                start_count += 1

            elif line.startswith("end_hub:"):
                kind = "end"
                content = line[len("end_hub:"):].strip()
                end_count += 1

            elif line.startswith("hub:"):
                kind = "normal"
                content = line[len("hub:"):].strip()

            else:
                raise InvalidConfig(f"Line {line_no}: unknown line type")

            # matadata parsing
            metadata = ""
            if "[" in content:
                content, metadata = content.split("[", 1)
                metadata = metadata.rstrip("]")

            parts = content.split()

            if len(parts) != 3:
                raise InvalidConfig(f"Line {line_no}: invalid hub format")

            name = parts[0]
            x = int(parts[1])
            y = int(parts[2])

            # name rules: no spaces, no dashes
            if "-" in name or " " in name:
                raise InvalidConfig(
                    f"Line {line_no}: invalid hub name '{name}'"
                )

            # uniqueness
            if name in hubs:
                raise InvalidConfig(
                    f"Line {line_no}: duplicate hub name '{name}'"
                )

            meta = parse_metadata(metadata, line_no)

            zone = meta.get("zone", "normal")
            if zone not in allowed_zones:
                raise InvalidConfig(
                    f"Line {line_no}: invalid zone type '{zone}'"
                )

            max_drones = int(meta.get("max_drones", 1))
            if max_drones <= 0:
                raise InvalidConfig(
                    f"Line {line_no}: max_drones must be positive"
                )

            hubs[name] = MapData(
                name=name,
                x=x,
                y=y,
                kind=kind,
                zone=zone,
                color=meta.get("color", "none"),
                max_drones=max_drones
            )

    if start_count != 1:
        raise InvalidConfig("Must contain exactly one start_hub")

    if end_count != 1:
        raise InvalidConfig("Must contain exactly one end_hub")

    if nb_drones is None:
        raise InvalidConfig("Missing nb_drones")

    return nb_drones, hubs, connections
