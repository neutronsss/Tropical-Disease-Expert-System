from __future__ import annotations

from typing import TypedDict

from app.ontology import OntologyData, display_label


class ConsultationAnswers(TypedDict):
    symptoms: list[str]
    danger_signs: list[str]
    symptom_onset_days: dict[str, int]
    environment: str | None
    season: str | None


def item(identifier: str) -> dict[str, str]:
    return {"id": identifier, "label": display_label(identifier)}


def build_questions(ontology: OntologyData) -> dict[str, object]:
    return {
        "disclaimer": (
            "Informasi awal saja; hasil bukan diagnosis dan tidak menggantikan tenaga kesehatan."
        ),
        "danger_signs": [item(value) for value in sorted(ontology.danger_signs)],
        "symptoms": [item(value) for value in sorted(ontology.symptoms)],
        "environments": [item(value) for value in sorted(ontology.environments)],
        "seasons": [item(value) for value in sorted(ontology.seasons)],
        "onset_timing_available": bool(ontology.onset_days),
    }


def disease_details(ontology: OntologyData, disease: str) -> dict[str, object]:
    symptom_evidence = [
        {
            **item(symptom),
            "onset_day": onset_day,
        }
        for symptom, onset_day in sorted(ontology.symptoms_by_disease.get(disease, {}).items())
    ]
    return {
        "id": disease,
        "label": display_label(disease),
        "symptoms": symptom_evidence,
        "environments": [
            item(value)
            for value in ontology.relations_for("punyaKontakLingkungan", disease)
        ],
        "seasons": [
            item(value)
            for value in ontology.relations_for("umumTerjadiPadaMusim", disease)
        ],
        "danger_signs": [
            item(value)
            for value in ontology.relations_for("memilikiTandaBahaya", disease)
        ],
        "self_care": [
            item(value)
            for value in (
                ontology.relations_for("memilikiPenangananMandiri", disease)
                + ontology.relations_for("memilikiPenanganan", disease)
            )
        ],
        "medical_referrals": [
            item(value)
            for value in ontology.relations_for("memilikiRujukanMedis", disease)
        ],
        "avoid": [
            item(value)
            for value in ontology.relations_for("pantanganMandiri", disease)
        ],
        "references": ontology.references.get(disease, []),
    }


def consult(ontology: OntologyData, answers: ConsultationAnswers) -> dict[str, object]:
    symptoms = set(answers["symptoms"])
    danger_signs = set(answers["danger_signs"])
    symptom_onset_days = answers["symptom_onset_days"]
    environment = answers["environment"]
    season = answers["season"]

    emergency = bool(danger_signs)
    if not symptoms:
        message = (
            "Tanda bahaya dipilih. Segera cari pertolongan medis."
            if emergency
            else "Belum ada kecocokan yang dapat ditampilkan tanpa gejala terpilih. "
            "Jika Anda khawatir atau kondisi berlanjut, konsultasikan dengan tenaga kesehatan."
        )
        return {
            "emergency": emergency,
            "selected_danger_signs": [item(value) for value in sorted(danger_signs)],
            "message": message,
            "matching_method": (
                "Hasil diurutkan berdasarkan jumlah gejala terpilih yang tercatat untuk "
                "penyakit; faktor paparan hanya membantu mengurutkan jika cocok. "
                "Hari mulai gejala yang diisi hanya ditampilkan sebagai konteks."
            ),
            "results": [],
        }

    results: list[dict[str, object]] = []
    for disease in ontology.diseases:
        disease_symptoms = ontology.symptoms_by_disease.get(disease, {})
        matched_symptoms = symptoms.intersection(disease_symptoms)
        if not matched_symptoms:
            continue

        details = disease_details(ontology, disease)
        matching_environment = (
            environment is not None
            and environment
            in {
                relation[1]
                for relation in ontology.object_relations["punyaKontakLingkungan"]
                if relation[0] == disease
            }
        )
        matching_season = (
            season is not None
            and season
            in {
                relation[1]
                for relation in ontology.object_relations["umumTerjadiPadaMusim"]
                if relation[0] == disease
            }
        )
        results.append(
            {
                **details,
                "matched_symptom_count": len(matched_symptoms),
                "matched_symptoms": [
                    {
                        **evidence,
                        "reported_onset_day": symptom_onset_days.get(evidence["id"]),
                    }
                    for evidence in details["symptoms"]
                    if evidence["id"] in matched_symptoms
                ],
                "environment_match": matching_environment if environment else None,
                "season_match": matching_season if season else None,
            }
        )

    results.sort(
        key=lambda result: (
            -int(result["matched_symptom_count"]),
            -int(result["environment_match"] is True),
            -int(result["season_match"] is True),
            str(result["id"]),
        )
    )
    message = (
        "Tanda bahaya dipilih. Segera cari pertolongan medis."
        if emergency
        else (
            "Kecocokan berikut hanya berdasarkan relasi yang tercatat dalam ontologi; "
            "ini bukan diagnosis."
            if results
            else "Tidak ditemukan kecocokan gejala dalam ontologi. Konsultasikan kondisi "
            "Anda dengan tenaga kesehatan."
        )
    )
    return {
        "emergency": emergency,
        "selected_danger_signs": [item(value) for value in sorted(danger_signs)],
        "message": message,
        "matching_method": (
            "Diurutkan dari jumlah gejala terpilih yang tercatat per penyakit; "
            "jika jumlah sama, kecocokan lingkungan lalu musim menjadi pemecah seri. "
            "Hari mulai gejala yang diisi hanya ditampilkan sebagai konteks dan tidak "
            "memengaruhi urutan. Tidak ada probabilitas atau skor akurasi medis."
        ),
        "results": results,
    }
