import asyncio
from typing import List
from fastapi import HTTPException
from PIL import Image

from ..base import BasePrinterClient
from .models import PrinterModelRegistry

from ...protocol._builders import _build_job_from_raster_set
from ...protocol.family import ProtocolFamily
from ...protocol.types import PaperMode
from ...rendering.renderer import image_to_raster
from ...transport.bluetooth import DeviceInfo, SppBackend
from ...transport.bluetooth.types import DeviceTransport
from ...raster import RasterSet

class GenericClient(BasePrinterClient):
    def __init__(self, device, hardware_info, printer_profile, settings):
        super().__init__(device, hardware_info, printer_profile, settings)
        self.backend = SppBackend()
        self.registry = PrinterModelRegistry.load()
        self.model_match = None
        if not getattr(device, "model", None):
            self.model_match = self.registry.detect_with_origin(
                getattr(device, "name", ""),
                getattr(device, "address", None),
            )

        self.model = (
            getattr(device, "model", None)
            or (self.model_match.model if self.model_match else None)
            or self.registry.get(str(hardware_info.get("model_id") or ""))
        )

        if not self.model:
            self.model = self.registry.get("GT01")

    def _effective_protocol_family(self):
        if self.model_match is not None:
            return self.model_match.protocol_family
        value = self.hardware_info.get("protocol_family") or getattr(self.model, "protocol_family", None)
        try:
            return ProtocolFamily.from_value(value)
        except Exception:
            return getattr(self.model, "protocol_family", ProtocolFamily.LEGACY)

    def _effective_protocol_variant(self):
        if self.model_match is not None and self.model_match.protocol_variant:
            return self.model_match.protocol_variant
        return self.hardware_info.get("protocol_variant") or getattr(self.model, "protocol_variant", None)

    def _effective_image_pipeline(self):
        if self.model_match is not None and self.model_match.image_pipeline is not None:
            return self.model_match.image_pipeline
        return self.model.image_pipeline

    async def connect(self) -> bool:
        attempts = []
        prefer_spp = getattr(self.model, "use_spp", False)
        ordered = [DeviceTransport.CLASSIC, DeviceTransport.BLE] if prefer_spp else [DeviceTransport.BLE, DeviceTransport.CLASSIC]

        for transport in ordered:
            attempts.append(
                DeviceInfo(
                    name=getattr(self.device, "name", "Unknown"),
                    address=self.device.address,
                    paired=getattr(self.device, "paired", None),
                    transport=transport,
                    protocol_family=self._effective_protocol_family() if self.model else None,
                )
            )

        if not attempts:
            raise HTTPException(status_code=500, detail="No valid connection endpoints found.")

        self.last_error = None
        for _ in range(3):
            try:
                await self.backend.connect_attempts(attempts)
                return True
            except Exception as exc:
                self.last_error = exc
                await self.backend.disconnect()
                await asyncio.sleep(1.5)

        return False

    async def disconnect(self) -> None:
        await self.backend.disconnect()

    async def print_images(self, images: List[Image.Image], split_mode: bool = False, dither: bool = True) -> None:
        if not self.model:
            raise HTTPException(status_code=500, detail="Unable to resolve printer model.")

        print_width_px = self.hardware_info["width_px"]
        final_images = []

        for img in images:
            if split_mode and img.width > print_width_px:
                for x in range(0, img.width, print_width_px):
                    strip = img.crop((x, 0, min(x + print_width_px, img.width), img.height))
                    if strip.width < print_width_px:
                        padded = Image.new("RGB", (print_width_px, strip.height), "white")
                        padded.paste(strip, (0, 0))
                        strip = padded
                    final_images.append(strip)
            else:
                if img.width != print_width_px:
                    if img.width < print_width_px:
                        padded = Image.new("RGB", (print_width_px, img.height), "white")
                        offset_x = (print_width_px - img.width) // 2
                        padded.paste(img, (offset_x, 0))
                        img = padded
                    else:
                        ratio = print_width_px / float(img.width)
                        new_height = max(1, int(img.height * ratio))
                        img = img.resize((print_width_px, new_height), Image.Resampling.LANCZOS)
                final_images.append(img)

        pipeline_config = self._effective_image_pipeline()
        protocol_family = self._effective_protocol_family()
        protocol_variant = self._effective_protocol_variant()

        hardware_default_speed = int(self.hardware_info.get("default_speed", getattr(self.model, "img_print_speed", 0)) or 0)
        hardware_default_energy = int(self.hardware_info.get("default_energy", getattr(self.model, "moderation_energy", 5000) or 5000) or 5000)
        caps = self.hardware_info.get("capabilities") or {}
        min_allowed_energy = max(1, int(self.hardware_info.get("min_energy", 1) or 1))
        max_allowed_energy = max(min_allowed_energy, int(self.hardware_info.get("max_energy", hardware_default_energy) or hardware_default_energy))
        max_allowed_speed = max(1, int(self.hardware_info.get("max_speed", max(hardware_default_speed, 1)) or max(hardware_default_speed, 1)))

        resolved_speed = self.printer_profile.speed if self.printer_profile and self.printer_profile.speed not in (None, 0) else (self.settings.speed if self.settings.speed > 0 else hardware_default_speed)
        resolved_energy = self.printer_profile.energy if self.printer_profile and self.printer_profile.energy not in (None, 0) else (self.settings.energy if self.settings.energy > 0 else hardware_default_energy)

        use_speed = max(0, min(int(resolved_speed or 0), max_allowed_speed))
        if (caps.get("density") or {}).get("available"):
            density_caps = caps.get("density") or {}
            density_min = int(density_caps.get("min", 0) or 0)
            density_max = int(density_caps.get("max", 5) or 5)
            density_default = int(density_caps.get("default", 1) or 1)
            density_value = self.printer_profile.energy if self.printer_profile and self.printer_profile.energy not in (None, 0) else density_default
            use_density = max(density_min, min(int(density_value or density_default), density_max))
            use_energy = hardware_default_energy
        else:
            use_density = None
            use_energy = max(min_allowed_energy, min(int(resolved_energy or hardware_default_energy), max_allowed_energy))
        use_feed = self.printer_profile.feed_lines if self.printer_profile and self.printer_profile.feed_lines is not None else self.settings.feed_lines

        runtime_controller = None
        if hasattr(self.model, "protocol_family"):
            family_val = protocol_family.value if hasattr(protocol_family, "value") else str(protocol_family)
            
            if family_val == "v5g":
                from ...printing.runtime.v5g import V5GRuntimeController
                runtime_controller = V5GRuntimeController(
                    helper_kind=getattr(self.model, "runtime_variant", None),
                    density_profile_key=getattr(self.model, "runtime_density_profile_key", None),
                    density_profile=None 
                )
            elif family_val == "v5x":
                from ...printing.runtime.v5x import V5XRuntimeController
                runtime_controller = V5XRuntimeController()
            elif family_val == "v5c":
                from ...printing.runtime.v5c import V5CRuntimeController
                runtime_controller = V5CRuntimeController()

        jobs = []
        total_images = len(final_images)
        supported_paper_modes = self.hardware_info.get("supported_paper_modes") or []
        supported_paper_values = {str(item.get("value")) for item in supported_paper_modes if isinstance(item, dict) and item.get("value")}
        paper_mode_value = getattr(self.printer_profile, "paper_mode", None)
        if paper_mode_value and supported_paper_values and paper_mode_value not in supported_paper_values:
            paper_mode_value = None
        if paper_mode_value and not supported_paper_values:
            paper_mode_value = None
        paper_mode = PaperMode(paper_mode_value) if paper_mode_value else None
        total_pages = len(final_images)
        for index, img in enumerate(final_images):
            is_last = index == total_images - 1
            current_feed = use_feed if is_last else 0

            raster = image_to_raster(img, pipeline_config.default_format, dither=dither)
            raster_set = RasterSet.from_single(raster)
            
            job_bytes = _build_job_from_raster_set(
                raster_set=raster_set,
                is_text=False,
                speed=use_speed,
                energy=use_energy,
                density=use_density,
                blackening=use_density if use_density is not None else 3,
                lsb_first=not self.model.a4xii,
                protocol_family=protocol_family,
                protocol_variant=protocol_variant,
                feed_padding=current_feed,
                dev_dpi=self.model.dev_dpi,
                can_print_label=self.model.can_print_label,
                post_print_feed_count=0,
                image_pipeline=pipeline_config,
                paper_mode=paper_mode,
                page_index=index + 1,
                page_count=total_pages,
            )
            jobs.append(job_bytes)

        delay_ms = getattr(self.model, "interval_ms", getattr(self.model, "delay_ms", 4))
        try:
            delay_ms = int(delay_ms or 4)
        except (TypeError, ValueError):
            delay_ms = 4

        try:
            mtu = int(getattr(self.model, "img_mtu", 128) or 128)
        except (TypeError, ValueError):
            mtu = 128
        if mtu <= 0:
            mtu = 128

        for index, job_bytes in enumerate(jobs):
            await self.backend.write(job_bytes, chunk_size=mtu, interval_ms=delay_ms)

            if index < len(jobs) - 1:
                await asyncio.sleep(1.5)
