from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import create_app
from app.ontology import DEFAULT_ONTOLOGY_PATH, OntologyData


class OntologyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.ontology = OntologyData(DEFAULT_ONTOLOGY_PATH)

    def test_loads_diseases_symptoms_and_exposure_options(self) -> None:
        self.assertEqual(len(self.ontology.diseases), 21)
        self.assertIn("DemamTinggi", self.ontology.symptoms)
        self.assertEqual(len(self.ontology.environments), 5)
        self.assertEqual(len(self.ontology.seasons), 2)

    def test_manifestation_timing_is_attached_to_symptom_evidence(self) -> None:
        dengue_symptoms = self.ontology.symptoms_by_disease["Dengue"]
        self.assertEqual(dengue_symptoms["DemamTinggi"], 1)


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(create_app(DEFAULT_ONTOLOGY_PATH))

    def test_health_and_questions_are_available(self) -> None:
        health = self.client.get("/api/health")
        questions = self.client.get("/api/questions")

        self.assertEqual(health.status_code, 200)
        self.assertTrue(health.json()["ontology_loaded"])
        self.assertEqual(health.json()["disease_count"], 21)
        self.assertEqual(questions.status_code, 200)
        self.assertIn("DemamTinggi", [item["id"] for item in questions.json()["symptoms"]])
        self.assertIn("KejangDanKelumpuhanOtot", [
            item["id"] for item in questions.json()["danger_signs"]
        ])
        self.assertEqual(self.client.get("/api/symptoms").status_code, 200)

    def test_consultation_ranks_diseases_by_matching_symptom_count(self) -> None:
        response = self.client.post(
            "/api/consultations",
            json={
                "symptoms": ["DemamTinggi", "NyeriSendi"],
                "symptom_onset_days": {"DemamTinggi": 2},
            },
        )

        self.assertEqual(response.status_code, 200)
        result = response.json()["results"][0]
        self.assertEqual(result["id"], "Dengue")
        self.assertEqual(result["matched_symptom_count"], 2)
        self.assertEqual(
            next(item["onset_day"] for item in result["matched_symptoms"] if item["id"] == "DemamTinggi"),
            1,
        )
        self.assertEqual(
            next(
                item["reported_onset_day"]
                for item in result["matched_symptoms"]
                if item["id"] == "DemamTinggi"
            ),
            2,
        )
        self.assertIn("tidak memengaruhi urutan", response.json()["matching_method"])

    def test_danger_sign_triggers_urgent_message_without_symptoms(self) -> None:
        response = self.client.post(
            "/api/consultations",
            json={"danger_signs": ["KejangDanKelumpuhanOtot"]},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["emergency"])
        self.assertIn("Segera cari pertolongan medis", response.json()["message"])
        self.assertEqual(response.json()["results"], [])

    def test_no_symptom_match_is_reported_without_inventing_results(self) -> None:
        response = self.client.post("/api/consultations", json={"symptoms": []})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["results"], [])
        self.assertIn("konsultasikan dengan tenaga kesehatan", response.json()["message"])

    def test_onset_day_must_belong_to_a_selected_symptom(self) -> None:
        response = self.client.post(
            "/api/consultations",
            json={
                "symptoms": [],
                "symptom_onset_days": {"DemamTinggi": 2},
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_onset_day_must_be_a_positive_integer(self) -> None:
        response = self.client.post(
            "/api/consultations",
            json={
                "symptoms": ["DemamTinggi"],
                "symptom_onset_days": {"DemamTinggi": 0},
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_unknown_ids_are_rejected(self) -> None:
        response = self.client.post(
            "/api/consultations",
            json={"symptoms": ["GejalaRekaan"]},
        )

        self.assertEqual(response.status_code, 422)

    def test_unknown_disease_returns_not_found(self) -> None:
        response = self.client.get("/api/diseases/PenyakitRekaan")

        self.assertEqual(response.status_code, 404)

    def test_invalid_ontology_reports_degraded_health_and_service_unavailable(self) -> None:
        with self.assertLogs("app.main", level="ERROR"):
            client = TestClient(create_app("ontologi-tidak-ada.owx"))

        self.assertEqual(client.get("/api/health").json()["status"], "degraded")
        self.assertEqual(client.get("/api/questions").status_code, 503)

    def test_frontend_is_served(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Tanya Tropis", response.text)


if __name__ == "__main__":
    unittest.main()
