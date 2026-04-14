"""Settings Pydantic schemas."""

from pydantic import BaseModel


class DesignSettings(BaseModel):
    """Saved glass design config (flexible dict)."""
    settings: dict


class SaveSettingsRequest(BaseModel):
    course_name: str
    settings: dict


class SettingsListItem(BaseModel):
    filename: str
    course_name: str
    saved_at: str
