import xml.etree.ElementTree as ET

OWL_NS = "http://www.w3.org/2002/07/owl#"
ET.register_namespace("", OWL_NS)

INPUT_FILE = "Project_Reified.owx"
OUTPUT_FILE = "Project_Reified_LOD.owx"

wikidata_mapping = {
    "Dengue": "http://www.wikidata.org/entity/Q152436",
    "BuruliUlcer": "http://www.wikidata.org/entity/Q1017366",
    "ChagasDisease": "http://www.wikidata.org/entity/Q309489",
    "Dracunculiasis": "http://www.wikidata.org/entity/Q843232",
    "Echinococcosis": "http://www.wikidata.org/entity/Q319227",
    "FoodborneTrematodiases": "http://www.wikidata.org/entity/Q1437175",
    "HumanAfricanTrypanosomiasis": "http://www.wikidata.org/entity/Q310037",
    "Leishmaniasis": "http://www.wikidata.org/entity/Q206583",
    "Leprosy": "http://www.wikidata.org/entity/Q129143",
    "LymphaticFilariasis": "http://www.wikidata.org/entity/Q839180",
    "Mycetoma": "http://www.wikidata.org/entity/Q1956555",
    "Noma": "http://www.wikidata.org/entity/Q1135767",
    "Onchocerciasis": "http://www.wikidata.org/entity/Q605809",
    "Rabies": "http://www.wikidata.org/entity/Q42278",
    "Scabies": "http://www.wikidata.org/entity/Q192135",
    "Schistosomiasis": "http://www.wikidata.org/entity/Q212623",
    "SnakebiteEnvenoming": "http://www.wikidata.org/entity/Q131448",
    "SoilTransmittedHelminthiases": "http://www.wikidata.org/entity/Q7554904",
    "Taeniasis": "http://www.wikidata.org/entity/Q7674252",
    "Trachoma": "http://www.wikidata.org/entity/Q216390",
    "Yaws": "http://www.wikidata.org/entity/Q645474"
}

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

for penyakit, uri_wikidata in wikidata_mapping.items():
    aa = ET.SubElement(root, f"{{{OWL_NS}}}AnnotationAssertion")
    ET.SubElement(aa, f"{{{OWL_NS}}}AnnotationProperty", abbreviatedIRI="owl:sameAs")
    
    # Subject (Individu Penyakit lokal)
    subj = ET.SubElement(aa, f"{{{OWL_NS}}}IRI")
    subj.text = f"#{penyakit}"
    
    # Target (URI Wikidata)
    target = ET.SubElement(aa, f"{{{OWL_NS}}}IRI")
    target.text = uri_wikidata

tree.write(OUTPUT_FILE, xml_declaration=True, encoding="utf-8")
print(f"Selesai! File LOD tersimpan sebagai: {OUTPUT_FILE}")