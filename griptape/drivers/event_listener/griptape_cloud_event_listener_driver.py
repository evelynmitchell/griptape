from __future__ import annotations

import os
from urllib.parse import urljoin

import requests
from attrs import Factory, define, field

from griptape.drivers.event_listener.base_event_listener_driver import BaseEventListenerDriver


@define
class GriptapeCloudEventListenerDriver(BaseEventListenerDriver):
    """Driver for publishing events to Griptape Cloud.

    Attributes:
        base_url: The base URL of Griptape Cloud. Defaults to the GT_CLOUD_BASE_URL environment variable.
        api_key: The API key to authenticate with Griptape Cloud.
        headers: The headers to use when making requests to Griptape Cloud. Defaults to include the Authorization header.
        structure_run_id: The ID of the Structure Run to publish events to. Defaults to the GT_CLOUD_STRUCTURE_RUN_ID environment variable.
    """

    base_url: str = field(
        default=Factory(lambda: os.getenv("GT_CLOUD_BASE_URL", "https://cloud.griptape.ai")),
        kw_only=True,
    )
    api_key: str = field(kw_only=True)
    headers: dict = field(
        default=Factory(lambda self: {"Authorization": f"Bearer {self.api_key}"}, takes_self=True),
        kw_only=True,
    )
    structure_run_id: str = field(default=Factory(lambda: os.getenv("GT_CLOUD_STRUCTURE_RUN_ID")), kw_only=True)

    @structure_run_id.validator  # pyright: ignore[reportAttributeAccessIssue]
    def validate_run_id(self, _, structure_run_id: str):
        if structure_run_id is None:
            raise ValueError(
                "structure_run_id must be set either in the constructor or as an environment variable (GT_CLOUD_STRUCTURE_RUN_ID).",
            )

    def try_publish_event_payload(self, event_payload: dict) -> None:
        url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{self.structure_run_id}/events")

        response = requests.post(url=url, json=event_payload, headers=self.headers)
        response.raise_for_status()

    def try_publish_event_payload_batch(self, event_payload_batch: list[dict]) -> None:
        url = urljoin(self.base_url.strip("/"), f"/api/structure-runs/{self.structure_run_id}/events")

        response = requests.post(url=url, json=event_payload_batch, headers=self.headers)
        response.raise_for_status()
