from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.ontology import DEFAULT_ONTOLOGY_PATH, OntologyData, OntologyLoadError
from app.schemas import (
    ConsultationRequest,
    ConsultationResponse,
    DiseaseDetails,
    HealthResponse,
    OntologyItem,
    QuestionsResponse,
)
from app.services import build_questions, consult, disease_details

logger = logging.getLogger(__name__)
STATIC_DIR = Path(__file__).resolve().parent / "static"


def create_app(ontology_path: Path | str | None = None) -> FastAPI:
    app = FastAPI(
        title="Tanya Jawab Penyakit Tropis",
        description="Informasi awal berdasarkan relasi di dalam ontologi OWL/XML.",
        version="1.0.0",
    )
    selected_path = ontology_path or os.environ.get(
        "ONTOLOGY_PATH", str(DEFAULT_ONTOLOGY_PATH)
    )
    ontology: OntologyData | None = None
    load_error: str | None = None

    try:
        ontology = OntologyData(selected_path)
    except OntologyLoadError:
        logger.exception("Ontologi tidak dapat dimuat.")
        load_error = "Basis pengetahuan tidak dapat dimuat; periksa konfigurasi dan log layanan."

    def require_ontology() -> OntologyData:
        if ontology is None:
            raise HTTPException(
                status_code=503,
                detail=load_error or "Basis pengetahuan tidak tersedia.",
            )
        return ontology

    @app.get("/api/health", response_model=HealthResponse)
    def health() -> dict[str, Any]:
        return {
            "status": "ok" if ontology is not None else "degraded",
            "ontology_loaded": ontology is not None,
            "disease_count": len(ontology.diseases) if ontology is not None else 0,
            "message": (
                "Basis pengetahuan siap digunakan."
                if ontology is not None
                else load_error
            ),
        }

    @app.get("/api/questions", response_model=QuestionsResponse)
    def questions() -> dict[str, object]:
        return build_questions(require_ontology())

    @app.get("/api/symptoms", response_model=list[OntologyItem])
    def symptoms() -> list[dict[str, str]]:
        return build_questions(require_ontology())["symptoms"]

    @app.post("/api/consultations", response_model=ConsultationResponse)
    def consultations(request: ConsultationRequest) -> dict[str, object]:
        data = require_ontology()
        unknown_symptoms = set(request.symptoms) - data.symptoms
        unknown_danger_signs = set(request.danger_signs) - data.danger_signs
        unknown_onset_symptoms = set(request.symptom_onset_days) - set(request.symptoms)
        if unknown_symptoms or unknown_danger_signs or unknown_onset_symptoms:
            unknown_ids = sorted(
                unknown_symptoms | unknown_danger_signs | unknown_onset_symptoms
            )
            raise HTTPException(
                status_code=422,
                detail=(
                    "ID gejala/tanda bahaya tidak dikenal, atau hari mulai diisi untuk "
                    f"gejala yang tidak dipilih: {', '.join(unknown_ids)}"
                ),
            )
        if request.environment is not None and request.environment not in data.environments:
            raise HTTPException(status_code=422, detail="ID lingkungan tidak dikenal.")
        if request.season is not None and request.season not in data.seasons:
            raise HTTPException(status_code=422, detail="ID musim tidak dikenal.")

        return consult(
            data,
            {
                "symptoms": request.symptoms,
                "danger_signs": request.danger_signs,
                "symptom_onset_days": request.symptom_onset_days,
                "environment": request.environment,
                "season": request.season,
            },
        )

    @app.get("/api/diseases/{disease_id}", response_model=DiseaseDetails)
    def disease(disease_id: str) -> dict[str, object]:
        data = require_ontology()
        if disease_id not in data.diseases:
            raise HTTPException(status_code=404, detail="Penyakit tidak ditemukan dalam ontologi.")
        return disease_details(data, disease_id)

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(STATIC_DIR / "index.html")

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    return app


app = create_app()
