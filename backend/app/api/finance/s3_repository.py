import json
import re
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app import settings


class S3YieldRepository:
    """S3-backed repository for year-based JSON data files."""

    def __init__(
        self,
        user_email: str,
        bucket: str = settings.S3_BUCKET,
    ) -> None:
        self.bucket = bucket
        self.prefix = user_email
        self._s3 = boto3.client("s3")

    # ── private ──────────────────────────────────────────────────────────────

    def _key(self, year: int) -> str:
        """Construct the S3 object key for the given year."""
        return f"{self.prefix}/{year}.json"

    # ── public ───────────────────────────────────────────────────────────────

    def list_years(self) -> list[int]:
        """Return a sorted list of years that have a corresponding data file."""
        paginator = self._s3.get_paginator("list_objects_v2")
        years: list[int] = []

        for page in paginator.paginate(Bucket=self.bucket, Prefix=f"{self.prefix}/"):
            for obj in page.get("Contents", []):
                name = obj["Key"].split("/")[-1].removesuffix(".json")
                if re.fullmatch(r"\d{4}", name):
                    years.append(int(name))
        return sorted(years)

    def read_year(self, year: int) -> dict[str, Any]:
        """Read and return the data for the given year."""
        try:
            obj = self._s3.get_object(Bucket=self.bucket, Key=self._key(year))
            return json.loads(obj["Body"].read())  # type: ignore[no-any-return]
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return {"dividends": {}, "yields": {}}
            raise

    def write_year(self, year: int, data: dict[str, Any]) -> None:
        """Write the data for the given year."""
        self._s3.put_object(
            Bucket=self.bucket,
            Key=self._key(year),
            Body=json.dumps(data, indent=2),
            ContentType="application/json",
        )

    def delete_all_data(self) -> None:
        """Delete all S3 objects for this user.

        This is a destructive, irreversible operation used when a user
        permanently deletes their account.
        """
        paginator = self._s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=f"{self.prefix}/"):
            keys = [{"Key": obj["Key"]} for obj in page.get("Contents", [])]
            if keys:
                self._s3.delete_objects(Bucket=self.bucket, Delete={"Objects": keys})

    def delete_entry(self, year: int, section: str, key: str) -> bool:
        """Remove a single entry from a section of the given year's data."""
        data = self.read_year(year)
        if key not in data.get(section, {}):
            return False
        del data[section][key]
        self.write_year(year, data)
        return True

    def read_settings(self) -> dict[str, Any]:
        """Read and return user settings (goals, steuerfreibetrag)."""
        settings_key = f"{self.prefix}/settings.json"
        try:
            obj = self._s3.get_object(Bucket=self.bucket, Key=settings_key)
            return json.loads(obj["Body"].read())  # type: ignore[no-any-return]
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                return {}
            raise

    def write_settings(self, data: dict[str, Any]) -> None:
        """Persist user settings to settings.json in S3."""
        settings_key = f"{self.prefix}/settings.json"
        self._s3.put_object(
            Bucket=self.bucket,
            Key=settings_key,
            Body=json.dumps(data, indent=2),
            ContentType="application/json",
        )
