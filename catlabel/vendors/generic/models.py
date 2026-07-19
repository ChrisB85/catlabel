from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Iterable, Mapping, Optional

from ...protocol.family import ProtocolFamily
from ...protocol.families import get_protocol_definition
from ...protocol.types import ImageEncoding, ImagePipelineConfig
from ...raster import PixelFormat


DATA_DIR = Path(__file__).resolve().parent / "data"
MODELS_PATH = DATA_DIR / "catalog_models.json"
UNSUPPORTED_PATH = DATA_DIR / "catalog_unsupported.json"
PROFILES_PATH = DATA_DIR / "catalog_profiles.json"
PAPER_PRESETS_PATH = DATA_DIR / "catalog_paper_presets.json"
SOURCE_PATH = DATA_DIR / "catalog_source.json"

_NON_GENERIC_FAMILIES = {"niimbot", "phomemo_esc"}
_FAMILY_ALIASES = {
    "tiny": "legacy",
    "tiny_prefixed": "legacy_prefixed",
}
_ENCODING_ALIASES = {
    "tiny_raw": "legacy_raw",
    "tiny_rle": "legacy_rle",
}
_MAC_ADDRESS_RE = re.compile(r"^([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")


def _normalized_name(value: str, *, casefold: bool = False) -> str:
    normalized = re.sub(r"\s+", "", str(value or ""))
    return normalized.casefold() if casefold else normalized


def _normalized_mac(value: str | None) -> str:
    return re.sub(r"[^0-9A-F]", "", str(value or "").upper())


def _catalog_family(value: object) -> ProtocolFamily:
    normalized = _FAMILY_ALIASES.get(str(value or "tiny"), str(value or "tiny"))
    return ProtocolFamily.from_value(normalized)


def _catalog_encoding(value: object) -> ImageEncoding:
    normalized = _ENCODING_ALIASES.get(str(value), str(value))
    return ImageEncoding(normalized)


def _family_default_pipeline(family: ProtocolFamily) -> ImagePipelineConfig:
    return get_protocol_definition(family).behavior.default_image_pipeline


def _pipeline_from_entry(
    entry: Mapping[str, object] | None,
    family: ProtocolFamily,
) -> ImagePipelineConfig:
    if not entry:
        return _family_default_pipeline(family)
    formats = tuple(PixelFormat(str(item)) for item in entry.get("formats", ()) or ())
    encoding_value = entry.get("encoding")
    default = _family_default_pipeline(family)
    return ImagePipelineConfig(
        formats=formats or default.formats,
        encoding=default.encoding if encoding_value is None else _catalog_encoding(encoding_value),
    )


def _middle(tiers: Mapping[str, object] | None, default: int) -> int:
    if not tiers:
        return default
    for key in ("middle", "low", "high"):
        if tiers.get(key) is not None:
            return int(tiers[key])
    return default


def _tier(tiers: Mapping[str, object] | None, key: str, default: int) -> int:
    if not tiers:
        return default
    value = tiers.get(key)
    return default if value is None else int(value)


@dataclass(frozen=True)
class PaperPreset:
    key: str
    label: str
    paper_width_px: int
    render_width_px: int
    left_padding_px: int = 0
    paper_mode: str | None = None
    max_height_px: int | None = None


@dataclass(frozen=True)
class DetectionRule:
    display_name: str
    exact_names: tuple[str, ...] = ()
    prefixes: tuple[str, ...] = ()
    mac_suffixes: tuple[str, ...] = ()

    def match_score(
        self,
        name: str,
        address: str | None,
        *,
        casefold: bool,
    ) -> tuple[int, int, int, int, int] | None:
        candidate = _normalized_name(name, casefold=casefold)
        if not candidate:
            return None

        mac = _normalized_mac(address)
        suffixes = tuple(_normalized_mac(value) for value in self.mac_suffixes)
        if suffixes:
            if not address or not _MAC_ADDRESS_RE.match(str(address).strip()):
                return None
            if not mac or not any(mac.endswith(value) for value in suffixes):
                return None

        best: tuple[int, int, int, int, int] | None = None
        for value in self.exact_names:
            normalized = _normalized_name(value, casefold=casefold)
            if candidate == normalized:
                score = _detection_specificity(value, exact=True, has_mac=bool(suffixes))
                best = max(best or score, score)
        for value in self.prefixes:
            normalized = _normalized_name(value, casefold=casefold)
            if normalized and candidate.startswith(normalized):
                score = _detection_specificity(value, exact=False, has_mac=bool(suffixes))
                best = max(best or score, score)
        return best


def _detection_specificity(
    trigger: str,
    *,
    exact: bool,
    has_mac: bool,
) -> tuple[int, int, int, int, int]:
    normalized = _normalized_name(trigger)
    trigger_length = len(normalized[:-1]) if normalized.endswith(("-", "_")) else len(normalized)
    return (
        trigger_length,
        int(has_mac),
        int(exact),
        len(normalized),
        sum(1 for char in normalized if char.isupper()),
    )


class PrinterModelMatchSource(Enum):
    HEAD_NAME = "head_name"
    MODEL_NO = "model_no"
    ALIAS = "alias"


class PrinterModelAliasKind(Enum):
    HEAD_NAME = "head_name"
    MAC = "mac"


@dataclass(frozen=True)
class PrinterModel:
    model_no: str
    profile_key: str
    head_name: str
    marketing_name: str | None
    detection_rules: tuple[DetectionRule, ...]
    origin_app_packages: tuple[str, ...]
    protocol_family: ProtocolFamily
    protocol_variant: str | None
    image_pipeline: ImagePipelineConfig
    paper_presets: tuple[PaperPreset, ...]
    size: int
    paper_size: int
    print_size: int
    one_length: int
    dev_dpi: int
    img_print_speed: int
    text_print_speed: int
    img_mtu: int
    interval_ms: int
    thin_energy: int
    moderation_energy: int
    deepen_energy: int
    text_energy: int
    has_id: bool
    use_spp: bool
    can_print_label: bool
    label_value: str
    back_paper_num: int
    post_print_feed_count: int
    can_change_mtu: bool = False
    ble_mtu_request: int | None = None
    a4xii: bool = False
    add_mor_pix: bool | None = None
    supported_paper_modes: tuple[str, ...] = ()
    runtime_variant: str | None = None
    runtime_density_profile_key: str | None = None
    runtime_density: Mapping[str, object] | None = None
    profile_density: Mapping[str, object] | None = None
    runtime_capabilities: Mapping[str, object] = field(default_factory=dict)
    testing: bool = False
    testing_note: str | None = None
    vendor: str = "generic"
    media_type: str = "continuous"
    min_density: int | None = None
    default_density: int | None = None
    max_density: int | None = None
    max_speed: int | None = None
    min_energy: int | None = None
    max_energy: int | None = None
    model: int = 0
    paper_num: int = 0

    @property
    def width(self) -> int:
        return self.print_size

    def paper_preset(self, key: str | None = None) -> PaperPreset:
        if not self.paper_presets:
            raise ValueError(f"Printer model {self.model_no!r} has no paper presets")
        if key is None:
            return self.paper_presets[0]
        for preset in self.paper_presets:
            if preset.key == key:
                return preset
        raise ValueError(f"Printer model {self.model_no!r} does not support paper preset {key!r}")


@dataclass(frozen=True)
class PrinterModelMatch:
    model: PrinterModel
    source: PrinterModelMatchSource
    alias_kind: Optional[PrinterModelAliasKind] = None
    protocol_family: ProtocolFamily = ProtocolFamily.LEGACY
    protocol_variant: Optional[str] = None
    image_pipeline: ImagePipelineConfig = field(
        default_factory=lambda: _family_default_pipeline(ProtocolFamily.LEGACY)
    )
    testing: bool = False
    testing_note: Optional[str] = None
    conflict_models: tuple[str, ...] = ()

    @property
    def used_alias(self) -> bool:
        return self.source is PrinterModelMatchSource.ALIAS

    @property
    def has_brand_conflict(self) -> bool:
        return bool(self.conflict_models)


@dataclass(frozen=True)
class _UnsupportedModel:
    model_key: str
    detection_rules: tuple[DetectionRule, ...]


class PrinterModelRegistry:
    _cache: dict[tuple[Path, Path, Path, Path], "PrinterModelRegistry"] = {}

    def __init__(
        self,
        models: Iterable[PrinterModel],
        unsupported: Iterable[_UnsupportedModel],
        deferred: Iterable[_UnsupportedModel] = (),
        *,
        source_metadata: Mapping[str, object],
    ) -> None:
        self._models = tuple(models)
        self._source_unsupported = tuple(unsupported)
        self._deferred = tuple(deferred)
        self.source_metadata = dict(source_metadata)
        self._by_key = {model.model_no: model for model in self._models}

    @classmethod
    def load(
        cls,
        models_path: Path = MODELS_PATH,
        profiles_path: Path = PROFILES_PATH,
        paper_presets_path: Path = PAPER_PRESETS_PATH,
        unsupported_path: Path = UNSUPPORTED_PATH,
    ) -> "PrinterModelRegistry":
        key = tuple(
            path.resolve()
            for path in (models_path, profiles_path, paper_presets_path, unsupported_path)
        )
        cached = cls._cache.get(key)
        if cached is not None:
            return cached

        profiles_raw = json.loads(profiles_path.read_text(encoding="utf-8"))
        presets_raw = json.loads(paper_presets_path.read_text(encoding="utf-8"))
        models_raw = json.loads(models_path.read_text(encoding="utf-8"))
        unsupported_raw = json.loads(unsupported_path.read_text(encoding="utf-8"))
        source_metadata = json.loads(SOURCE_PATH.read_text(encoding="utf-8"))

        profiles = {str(item["profile_key"]): item for item in profiles_raw}
        presets = {
            str(name): cls._parse_paper_preset(str(name), value)
            for name, value in presets_raw.items()
        }

        models: list[PrinterModel] = []
        deferred: list[_UnsupportedModel] = []
        for item in models_raw:
            profile = profiles.get(str(item.get("profile_key", "")))
            if profile is None:
                raise ValueError(
                    f"Catalog model {item.get('model_key')!r} references missing profile "
                    f"{item.get('profile_key')!r}"
                )
            family_name = str((item.get("protocol_override") or {}).get("type") or profile["protocol_default"]["type"])
            if family_name in _NON_GENERIC_FAMILIES:
                deferred.append(cls._unavailable_model(item))
                continue
            try:
                family = _catalog_family(family_name)
                behavior = get_protocol_definition(family).behavior
            except (ValueError, KeyError):
                deferred.append(cls._unavailable_model(item))
                continue
            if not behavior.implemented:
                deferred.append(cls._unavailable_model(item))
                continue
            model = cls._parse_model(item, profile, presets, family)
            models.append(model)

        unsupported = [
            _UnsupportedModel(
                model_key=str(item["model_key"]),
                detection_rules=cls._parse_detection_rules(item),
            )
            for item in unsupported_raw
        ]
        registry = cls(
            models,
            unsupported,
            deferred,
            source_metadata=source_metadata,
        )
        cls._cache[key] = registry
        return registry

    @staticmethod
    def _parse_paper_preset(key: str, raw: Mapping[str, object]) -> PaperPreset:
        return PaperPreset(
            key=key,
            label=str(raw.get("label") or key.replace("_", " ").title()),
            paper_width_px=int(raw["paper_width_px"]),
            render_width_px=int(raw["render_width_px"]),
            left_padding_px=int(raw.get("left_padding_px") or 0),
            paper_mode=None if raw.get("paper_mode") in (None, "") else str(raw["paper_mode"]),
            max_height_px=None if raw.get("max_height_px") in (None, "") else int(raw["max_height_px"]),
        )

    @classmethod
    def _unavailable_model(cls, item: Mapping[str, object]) -> _UnsupportedModel:
        return _UnsupportedModel(
            model_key=str(item["model_key"]),
            detection_rules=cls._parse_detection_rules(item),
        )

    @staticmethod
    def _parse_detection_rules(item: Mapping[str, object]) -> tuple[DetectionRule, ...]:
        rules: list[DetectionRule] = []
        for entry in item.get("detections", ()) or ():
            detection = entry.get("detection") or {}
            display_name = str(entry.get("name") or item.get("model_key") or "")
            exact_names = tuple(str(value) for value in detection.get("exact_names", ()) or ())
            prefixes = tuple(str(value) for value in detection.get("prefixes", ()) or ())
            if not exact_names and not prefixes and display_name:
                exact_names = (display_name,)
            rules.append(
                DetectionRule(
                    display_name=display_name,
                    exact_names=exact_names,
                    prefixes=prefixes,
                    mac_suffixes=tuple(
                        str(value) for value in detection.get("mac_suffixes", ()) or ()
                    ),
                )
            )
        return tuple(rules)

    @classmethod
    def _parse_model(
        cls,
        item: Mapping[str, object],
        profile: Mapping[str, object],
        presets: Mapping[str, PaperPreset],
        family: ProtocolFamily,
    ) -> PrinterModel:
        profile_protocol = profile.get("protocol_default") or {}
        protocol_override = item.get("protocol_override") or {}
        protocol_variant = protocol_override.get("packets_type") or protocol_override.get("variant")
        if protocol_variant is None:
            protocol_variant = profile_protocol.get("packets_type") or profile_protocol.get("variant")

        configured_pipeline = item.get("image_pipeline_override") or profile.get("default_image_pipeline")
        profile_family = _catalog_family(profile_protocol.get("type"))
        if family != profile_family and not item.get("image_pipeline_override"):
            image_pipeline = _family_default_pipeline(family)
        else:
            image_pipeline = _pipeline_from_entry(configured_pipeline, family)

        paper_presets = tuple(
            presets[str(key)]
            for key in profile.get("paper_presets", ()) or ()
            if str(key) in presets
        )
        if not paper_presets:
            raise ValueError(f"Catalog profile {profile['profile_key']!r} has no valid paper preset")
        default_paper = paper_presets[0]

        defaults = profile.get("print_defaults") or {}
        speeds = defaults.get("speed") or {}
        energy = defaults.get("energy") or {}
        image_energy = energy.get("image") or {}
        text_energy = energy.get("text") or {}
        image_speed = int(speeds.get("image") or 0)
        text_speed = int(speeds.get("text") or image_speed)

        runtime_key = item.get("profile_runtime_preset_key")
        runtime_preset = None
        if runtime_key:
            runtime_preset = next(
                (
                    candidate
                    for candidate in profile.get("runtime_presets", ()) or ()
                    if candidate.get("key") == runtime_key
                ),
                None,
            )
            if runtime_preset is None:
                raise ValueError(
                    f"Catalog model {item['model_key']!r} references missing runtime preset "
                    f"{runtime_key!r}"
                )

        rules = cls._parse_detection_rules(item)
        first_name = next((rule.display_name for rule in rules if rule.display_name), str(item["model_key"]))
        supported_modes = tuple(
            dict.fromkeys(
                preset.paper_mode
                for preset in paper_presets
                if preset.paper_mode is not None
            )
        )
        density_defaults = defaults.get("density") or None
        runtime_density = None if runtime_preset is None else runtime_preset.get("density")
        # Runtime presets override profile density in upstream. Keep the
        # effective image tiers separate from the V5G wire-protocol ceiling:
        # these are model-tuned defaults, not hard user-input limits.
        effective_density = runtime_density or density_defaults
        image_density = (
            effective_density.get("image")
            if isinstance(effective_density, Mapping)
            else None
        )
        density_values = (
            [int(value) for value in image_density.values()]
            if isinstance(image_density, Mapping)
            else []
        )
        minimum_density = min(density_values, default=None)
        default_density = (
            _middle(image_density, 0)
            if isinstance(image_density, Mapping)
            else None
        )
        maximum_density = max(density_values, default=None)

        return PrinterModel(
            model_no=str(item["model_key"]),
            profile_key=str(profile["profile_key"]),
            head_name=first_name,
            marketing_name=None if item.get("marketing_name") in (None, "") else str(item["marketing_name"]),
            detection_rules=rules,
            origin_app_packages=tuple(str(value) for value in item.get("origin_app_packages", ()) or ()),
            protocol_family=family,
            protocol_variant=None if protocol_variant in (None, "") else str(protocol_variant),
            image_pipeline=image_pipeline,
            paper_presets=paper_presets,
            size=int(profile.get("size") or 0),
            paper_size=default_paper.paper_width_px,
            print_size=default_paper.render_width_px,
            one_length=int(profile.get("one_length") or 0),
            dev_dpi=int(profile.get("dev_dpi") or 203),
            img_print_speed=image_speed,
            text_print_speed=text_speed,
            img_mtu=int((profile.get("stream") or {}).get("chunk_size") or 128),
            interval_ms=int((profile.get("stream") or {}).get("delay_ms") or 0),
            thin_energy=_tier(image_energy, "low", 0),
            moderation_energy=_middle(image_energy, 0),
            deepen_energy=_tier(image_energy, "high", _middle(image_energy, 0)),
            text_energy=_middle(text_energy, _middle(image_energy, 0)),
            has_id=bool(profile.get("has_id")),
            use_spp=bool(profile.get("use_spp")),
            can_print_label=bool(profile.get("can_print_label")),
            label_value=str(profile.get("label_value") or "0"),
            back_paper_num=int(profile.get("back_paper_num") or 0),
            post_print_feed_count=int(profile.get("post_print_feed_count") or 0),
            can_change_mtu=profile.get("ble_mtu_request") is not None,
            ble_mtu_request=None if profile.get("ble_mtu_request") is None else int(profile["ble_mtu_request"]),
            a4xii=bool(profile.get("a4xii")),
            supported_paper_modes=supported_modes,
            runtime_variant=None if runtime_preset is None else runtime_preset.get("control_algorithm"),
            runtime_density_profile_key=None if runtime_key is None else str(runtime_key),
            runtime_density=runtime_density,
            profile_density=density_defaults,
            runtime_capabilities={} if runtime_preset is None else dict(runtime_preset.get("capabilities") or {}),
            min_density=minimum_density,
            default_density=default_density,
            max_density=maximum_density,
            max_speed=max(image_speed, text_speed, 1),
            min_energy=max(1, _tier(image_energy, "low", 1)),
            max_energy=max(1, _tier(image_energy, "high", _middle(image_energy, 1))),
        )

    @property
    def models(self) -> list[PrinterModel]:
        return list(self._models)

    @property
    def unsupported_model_count(self) -> int:
        return len(self._source_unsupported)

    @property
    def deferred_model_count(self) -> int:
        return len(self._deferred)

    def get(self, model_no: str) -> Optional[PrinterModel]:
        normalized = str(model_no or "").casefold()
        for key, model in self._by_key.items():
            if key.casefold() == normalized:
                return model
        return None

    def get_by_head_name(self, head_name: str) -> Optional[PrinterModel]:
        normalized = _normalized_name(head_name, casefold=True)
        if not normalized:
            return None
        direct = self.get(head_name)
        if direct is not None:
            return direct
        for model in self._models:
            for rule in model.detection_rules:
                if _normalized_name(rule.display_name, casefold=True) == normalized:
                    return model
        return None

    def detect_from_device_name(
        self,
        name: str,
        address: Optional[str] = None,
    ) -> Optional[PrinterModel]:
        match = self.detect_with_origin(name, address)
        return None if match is None else match.model

    def detect_with_origin(
        self,
        name: str,
        address: Optional[str] = None,
    ) -> Optional[PrinterModelMatch]:
        if not _normalized_name(name):
            return None
        for casefold in (False, True):
            supported = self._supported_candidates(name, address, casefold=casefold)
            deferred = self._deferred_candidates(name, address, casefold=casefold)
            unsupported = self._unsupported_candidates(name, address, casefold=casefold)
            if not supported and not deferred and not unsupported:
                continue
            supported.sort(key=lambda item: item[0], reverse=True)
            deferred.sort(key=lambda item: item[0], reverse=True)
            unsupported.sort(key=lambda item: item[0], reverse=True)
            best_supported = supported[0][0] if supported else None
            best_deferred = deferred[0][0] if deferred else None
            best_unsupported = unsupported[0][0] if unsupported else None
            best_catalog_supported = max(
                value
                for value in (best_supported, best_deferred)
                if value is not None
            ) if best_supported is not None or best_deferred is not None else None
            if best_supported is None or (
                best_unsupported is not None
                and best_catalog_supported is not None
                and best_unsupported > best_catalog_supported
            ) or (
                best_deferred is not None and best_deferred >= best_supported
            ):
                return None
            winners = [item for item in supported if item[0] == best_supported]
            unique_models = {item[1].model_no: item[1] for item in winners}
            if len(unique_models) != 1:
                return None
            score, model, rule = winners[0]
            return PrinterModelMatch(
                model=model,
                source=PrinterModelMatchSource.HEAD_NAME,
                alias_kind=(
                    PrinterModelAliasKind.MAC if score[2] else PrinterModelAliasKind.HEAD_NAME
                ),
                protocol_family=model.protocol_family,
                protocol_variant=model.protocol_variant,
                image_pipeline=model.image_pipeline,
                testing=model.testing,
                testing_note=model.testing_note,
            )
        return None

    def _supported_candidates(
        self,
        name: str,
        address: str | None,
        *,
        casefold: bool,
    ) -> list[tuple[tuple[int, int, int, int, int], PrinterModel, DetectionRule]]:
        matches = []
        for model in self._models:
            for rule in model.detection_rules:
                score = rule.match_score(name, address, casefold=casefold)
                if score is not None:
                    matches.append((score, model, rule))
        return matches

    def _unsupported_candidates(
        self,
        name: str,
        address: str | None,
        *,
        casefold: bool,
    ) -> list[tuple[tuple[int, int, int, int, int], _UnsupportedModel, DetectionRule]]:
        matches = []
        for model in self._source_unsupported:
            for rule in model.detection_rules:
                score = rule.match_score(name, address, casefold=casefold)
                if score is not None:
                    matches.append((score, model, rule))
        return matches

    def _deferred_candidates(
        self,
        name: str,
        address: str | None,
        *,
        casefold: bool,
    ) -> list[tuple[tuple[int, int, int, int, int], _UnsupportedModel, DetectionRule]]:
        matches = []
        for model in self._deferred:
            for rule in model.detection_rules:
                score = rule.match_score(name, address, casefold=casefold)
                if score is not None:
                    matches.append((score, model, rule))
        return matches
