"""VK API Client.

Provides async interface to VK API for uploading photos and posting to wall.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential_jitter


class VKClient:
    """Async client for VK API."""

    def __init__(
        self,
        access_token: str,
        group_id: str,
        album_id: Optional[str] = None,
        api_version: str = "5.199",
        base_url: str = "https://api.vk.com/method",
    ):
        self._access_token = access_token
        self._group_id = group_id
        self._album_id = album_id
        self._api_version = api_version
        self._base_url = base_url
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_params(self) -> Dict[str, str]:
        """Get common request parameters."""
        return {
            "access_token": self._access_token,
            "v": self._api_version,
        }

    async def _call(self, method: str, **params) -> Dict[str, Any]:
        """Call VK API method."""
        url = f"{self._base_url}/{method}"
        all_params = {**self._get_params(), **params}

        response = await self.client.post(url, data=all_params)
        response.raise_for_status()

        data = response.json()
        if "error" in data:
            raise RuntimeError(
                f"VK API error: {data['error'].get('error_msg')}")

        return data.get("response", {})

    async def get_wall_upload_server(self) -> Dict[str, Any]:
        """Get upload server URL for wall photos."""
        return await self._call(
            "photos.getWallUploadServer",
            group_id=self._group_id,
        )

    async def upload_photo(self, upload_url: str,
                           photo_path: str) -> Dict[str, Any]:
        """Upload photo to VK upload server."""
        with open(photo_path, "rb") as f:
            files = {"photo": f}
            async with httpx.AsyncClient() as client:
                response = await client.post(upload_url, files=files)
                response.raise_for_status()
                return response.json()

    async def save_wall_photo(
        self,
        server: int,
        photo: str,
        hash: str,
    ) -> Dict[str, Any]:
        """Save uploaded photo to wall."""
        return await self._call(
            "photos.saveWallPhoto",
            group_id=self._group_id,
            server=server,
            photo=photo,
            hash=hash,
        )

    async def wall_post(
        self,
        message: str,
        attachments: Optional[str] = None,
        from_group: bool = True,
    ) -> Dict[str, Any]:
        """Post to wall.

        Args:
            message: Post text
            attachments: Comma-separated attachments (photo{owner_id}_{id})
            from_group: Post as group (True) or user (False)

        Returns:
            Post info with post_id
        """
        params = {
            "owner_id": f"-{self._group_id}",
            "from_group": 1 if from_group else 0,
            "message": message,
        }
        if attachments:
            params["attachments"] = attachments

        return await self._call("wall.post", **params)

    async def post_with_photo(
        self,
        message: str,
        photo_url: str,
    ) -> Dict[str, Any]:
        """Download photo, upload to VK, and post to wall."""
        # Download photo
        async with httpx.AsyncClient() as client:
            response = await client.get(photo_url)
            response.raise_for_status()
            photo_data = response.content

        # Save to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(photo_data)
            temp_path = f.name

        try:
            # Get upload server
            upload_server = await self.get_wall_upload_server()
            upload_url = upload_server.get("upload_url")

            # Upload photo
            upload_result = await self.upload_photo(upload_url, temp_path)

            # Save photo
            saved = await self.save_wall_photo(
                server=upload_result["server"],
                photo=upload_result["photo"],
                hash=upload_result["hash"],
            )

            # Create attachment string
            photo_info = saved[0]
            attachment = f"photo{photo_info['owner_id']}_{photo_info['id']}"

            # Post to wall
            return await self.wall_post(message=message, attachments=attachment)

        finally:
            # Clean up temp file
            import os
            try:
                os.unlink(temp_path)
            except OSError:
                pass


class MockVKClient:
    """Mock VK client for testing."""

    def __init__(self, *args, **kwargs):
        self.posts = []
        self.uploaded_photos = []

    async def close(self) -> None:
        pass

    async def get_wall_upload_server(self) -> Dict[str, Any]:
        return {"upload_url": "https://mock.vk.com/upload"}

    async def upload_photo(self, upload_url: str,
                           photo_path: str) -> Dict[str, Any]:
        self.uploaded_photos.append(photo_path)
        return {"server": 1, "photo": "mock_photo", "hash": "mock_hash"}

    async def save_wall_photo(
        self,
        server: int,
        photo: str,
        hash: str,
    ) -> Dict[str, Any]:
        return [{"owner_id": -12345, "id": 67890}]

    async def wall_post(
        self,
        message: str,
        attachments: Optional[str] = None,
        from_group: bool = True,
    ) -> Dict[str, Any]:
        self.posts.append({
            "message": message,
            "attachments": attachments,
        })
        return {"post_id": len(self.posts)}

    async def post_with_photo(
        self,
        message: str,
        photo_url: str,
    ) -> Dict[str, Any]:
        self.posts.append({
            "message": message,
            "photo_url": photo_url,
        })
        return {"post_id": len(self.posts)}
