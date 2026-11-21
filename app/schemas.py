from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field


class OntologyItem(BaseModel):
    id: str
    label: str


class QuestionsResponse(BaseModel):
    disclaimer: str
    danger_signs: list[OntologyItem]
    symptoms: list[OntologyItem]
    environments: list[OntologyItem]
    seasons: list[OntologyItem]
    onset_timing_available: bool


class ConsultationRequest(BaseModel):
    symptoms: list[Annotated[str, Field(max_length=100)]] = Field(
        default_factory=list, max_length=50
    )
    danger_signs: list[Annotated[str, Field(max_length=100)]] = Field(
        default_factory=list, max_length=50
    )
    symptom_onset_days: dict[
        Annotated[str, Field(max_length=100)], Annotated[int, Field(ge=1)]
    ] = Field(default_factory=dict, max_length=50)
    environment: Annotated[str, Field(max_length=100)] | None = None
    season: Annotated[str, Field(max_length=100)] | None = None


class SymptomEvidence(OntologyItem):
    onset_day: int | None = None
    reported_onset_day: int | None = None


class DiseaseDetails(BaseModel):
    id: str
    label: str
    symptoms: list[SymptomEvidence]
    environments: list[OntologyItem]
    seasons: list[OntologyItem]
    danger_signs: list[OntologyItem]
    self_care: list[OntologyItem]
    medical_referrals: list[OntologyItem]
    avoid: list[OntologyItem]
    references: list[str]


class DiseaseMatch(DiseaseDetails):
    matched_symptom_count: int
    matched_symptoms: list[SymptomEvidence]
    environment_match: bool | None
    season_match: bool | None


class ConsultationResponse(BaseModel):
    emergency: bool
    selected_danger_signs: list[OntologyItem]
    message: str
    matching_method: str
    results: list[DiseaseMatch]


class HealthResponse(BaseModel):
    status: str
    ontology_loaded: bool
    disease_count: int
    message: str
