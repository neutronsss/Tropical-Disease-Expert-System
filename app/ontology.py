from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

OWL_NS = "http://www.w3.org/2002/07/owl#"
NS = {"owl": OWL_NS}
DEFAULT_ONTOLOGY_PATH = (
    Path(__file__).resolve().parent.parent / "Project_Advanced_SROIQ_1_8_2.owx"
)


class OntologyLoadError(ValueError):
    """Raised when the OWL/XML document cannot provide the expected data."""


def _local_id(element: ET.Element) -> str:
    iri = element.attrib.get("IRI", "")
    if "#" in iri:
        return iri.rsplit("#", 1)[1]
    return iri.rsplit("/", 1)[-1]


def display_label(identifier: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", " ", identifier.replace("_", " "))


class OntologyData:
    def __init__(self, path: Path | str = DEFAULT_ONTOLOGY_PATH) -> None:
        self.path = Path(path)
        try:
            root = ET.parse(self.path).getroot()
        except (OSError, ET.ParseError) as exc:
            raise OntologyLoadError("Ontologi tidak dapat dibaca sebagai OWL/XML.") from exc

        if root.tag != f"{{{OWL_NS}}}Ontology":
            raise OntologyLoadError("Format ontologi bukan OWL/XML yang didukung.")

        self.class_members: dict[str, set[str]] = defaultdict(set)
        self.object_relations: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self.onset_days: dict[str, int] = {}
        self.references: dict[str, list[str]] = defaultdict(list)

        for assertion in root.findall("owl:ClassAssertion", NS):
            class_element, individual_element = list(assertion)
            self.class_members[_local_id(class_element)].add(_local_id(individual_element))

        for assertion in root.findall("owl:ObjectPropertyAssertion", NS):
            property_element, subject_element, object_element = list(assertion)
            self.object_relations[_local_id(property_element)].append(
                (_local_id(subject_element), _local_id(object_element))
            )

        for assertion in root.findall("owl:DataPropertyAssertion", NS):
            property_element, subject_element, literal_element = list(assertion)
            if _local_id(property_element) != "mulaiDirasakanHariKe":
                continue
            try:
                self.onset_days[_local_id(subject_element)] = int(literal_element.text or "")
            except ValueError as exc:
                raise OntologyLoadError(
                    "Nilai mulaiDirasakanHariKe pada ontologi harus berupa bilangan bulat."
                ) from exc

        for assertion in root.findall("owl:AnnotationAssertion", NS):
            property_element, subject_element, value_element = list(assertion)
            if _local_id(property_element) == "sumberRujukan":
                source = (value_element.text or "").strip()
                if source:
                    self.references[_local_id(subject_element)].append(source)

        self.diseases = set()
        for class_name, members in self.class_members.items():
            if class_name.startswith("Penyakit"):
                self.diseases.update(members)

        self.symptoms_by_disease: dict[str, dict[str, int | None]] = defaultdict(dict)
        disease_by_manifestation = dict(self.object_relations["menghubungkanPenyakit"])
        for manifestation, symptom in self.object_relations["melibatkanGejala"]:
            disease = disease_by_manifestation.get(manifestation)
            if disease in self.diseases:
                self.symptoms_by_disease[disease][symptom] = self.onset_days.get(manifestation)

        self.symptoms = {
            symptom
            for disease_symptoms in self.symptoms_by_disease.values()
            for symptom in disease_symptoms
        }
        self.danger_signs = self.class_members.get("TandaBahaya", set())
        self.environments = self.class_members.get("Lingkungan", set())
        self.seasons = self.class_members.get("Musim", set())
        self._disease_relations = {
            property_name: self._group_by_disease(property_name)
            for property_name in (
                "disebabkan",
                "punyaKontakLingkungan",
                "umumTerjadiPadaMusim",
                "memilikiTandaBahaya",
                "memilikiPenanganan",
                "memilikiPenangananMandiri",
                "memilikiRujukanMedis",
                "pantanganMandiri",
            )
        }

        if not self.diseases or not self.symptoms:
            raise OntologyLoadError(
                "Ontologi tidak memiliki data penyakit dan manifestasi gejala yang diperlukan."
            )

    def _group_by_disease(self, property_name: str) -> dict[str, list[str]]:
        grouped: dict[str, list[str]] = defaultdict(list)
        for subject, value in self.object_relations[property_name]:
            if subject in self.diseases:
                grouped[subject].append(value)
        return grouped

    def relations_for(self, property_name: str, disease: str) -> list[str]:
        return self._disease_relations.get(property_name, {}).get(disease, [])
