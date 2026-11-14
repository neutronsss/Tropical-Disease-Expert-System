import xml.etree.ElementTree as ET

OWL_NS = "http://www.w3.org/2002/07/owl#"
ET.register_namespace("", OWL_NS)

INPUT_FILE = "Project.owx"
OUTPUT_FILE = "Project_Reified.owx"

data_penyakit = [
    {
        "penyakit": "Dengue",
        "disebabkan": "Virus",
        "musim": "Hujan",
        "lingkungan": "GenanganAir",
        "gejala": [("DemamTinggi", 1), ("NyeriSendi", 3)],
        "penanganan": ["SegeraMencariPertolonganPro", "KonsumsiParasetamol"]
    },
    {
        "penyakit": "BuruliUlcer",
        "disebabkan": "Bakteri",
        "musim": "Hujan",
        "lingkungan": "GenanganAir",
        "gejala": [("LukaBorok", 7)],
        "penanganan": ["JagaKebersihanLuka", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "ChagasDisease",
        "disebabkan": "Parasit",
        "musim": "Kemarau",
        "lingkungan": "WilayahHutan",
        "gejala": [("DemamTinggi", 2), ("NyeriPerut", 5)],
        "penanganan": ["SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Dracunculiasis",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "SanitasiBuruk",
        "gejala": [("GatalKulit", 1), ("LukaBorok", 4)],
        "penanganan": ["JagaKebersihanLuka", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Echinococcosis",
        "disebabkan": "Parasit",
        "musim": "Kemarau",
        "lingkungan": "DekatPeternakan",
        "gejala": [("NyeriPerut", 14)],
        "penanganan": ["SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "FoodborneTrematodiases",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "SanitasiBuruk",
        "gejala": [("NyeriPerut", 2), ("Diare", 3)],
        "penanganan": ["MemasakSampaiBenarMatang", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "HumanAfricanTrypanosomiasis",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "WilayahHutan",
        "gejala": [("DemamTinggi", 3), ("PembengkakanKelenjar", 7)],
        "penanganan": ["SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Leishmaniasis",
        "disebabkan": "Parasit",
        "musim": "Kemarau",
        "lingkungan": "WilayahHutan",
        "gejala": [("LukaBorok", 10), ("DemamTinggi", 3)],
        "penanganan": ["JagaKebersihanLuka", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Leprosy",
        "disebabkan": "Bakteri",
        "musim": "Kemarau",
        "lingkungan": "PadatPenduduk",
        "gejala": [("RuamKulit", 14), ("GatalKulit", 7)],
        "penanganan": ["JagaKebersihanLuka", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "LymphaticFilariasis",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "GenanganAir",
        "gejala": [("PembengkakanKelenjar", 5)],
        "penanganan": ["BanyakIstirahat", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Mycetoma",
        "disebabkan": "Jamur",
        "musim": "Kemarau",
        "lingkungan": "WilayahHutan",
        "gejala": [("LukaBorok", 14)],
        "penanganan": ["JagaKebersihanLuka", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Noma",
        "disebabkan": "Bakteri",
        "musim": "Hujan",
        "lingkungan": "SanitasiBuruk",
        "gejala": [("LukaBorok", 3)],
        "penanganan": ["JagaKebersihanLuka", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Onchocerciasis",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "WilayahHutan",
        "gejala": [("GatalKulit", 2), ("GangguanPenglihatan", 30)],
        "penanganan": ["SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Rabies",
        "disebabkan": "Virus",
        "musim": "Kemarau",
        "lingkungan": "DekatPeternakan",
        "gejala": [("DemamTinggi", 3)],
        "penanganan": ["JagaKebersihanLuka", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Scabies",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "PadatPenduduk",
        "gejala": [("GatalKulit", 1), ("RuamKulit", 3)],
        "penanganan": ["CuciPakaianDenganAirPanas", "HindariMenggarukLuka"]
    },
    {
        "penyakit": "Schistosomiasis",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "GenanganAir",
        "gejala": [("NyeriPerut", 4), ("Diare", 5)],
        "penanganan": ["SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "SnakebiteEnvenoming",
        "disebabkan": "Serangga",
        "musim": "Hujan",
        "lingkungan": "WilayahHutan",
        "gejala": [("GatalKulit", 1)],
        "penanganan": ["PosisikanGigitanLebihRendahDariJantung", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "SoilTransmittedHelminthiases",
        "disebabkan": "Parasit",
        "musim": "Hujan",
        "lingkungan": "SanitasiBuruk",
        "gejala": [("NyeriPerut", 3), ("Diare", 4)],
        "penanganan": ["MandiBersih", "MenjagaKebersihanTangan"]
    },
    {
        "penyakit": "Taeniasis",
        "disebabkan": "Parasit",
        "musim": "Kemarau",
        "lingkungan": "DekatPeternakan",
        "gejala": [("NyeriPerut", 7)],
        "penanganan": ["MemasakSampaiBenarMatang"]
    },
    {
        "penyakit": "Trachoma",
        "disebabkan": "Bakteri",
        "musim": "Kemarau",
        "lingkungan": "SanitasiBuruk",
        "gejala": [("GangguanPenglihatan", 5)],
        "penanganan": ["MenjagaKebersihanTangan", "SegeraMencariPertolonganPro"]
    },
    {
        "penyakit": "Yaws",
        "disebabkan": "Bakteri",
        "musim": "Hujan",
        "lingkungan": "SanitasiBuruk",
        "gejala": [("RuamKulit", 3), ("LukaBorok", 7)],
        "penanganan": ["JagaKebersihanLuka", "MandiBersih"]
    }
]

tree = ET.parse(INPUT_FILE)
root = tree.getroot()

# 1. Deklarasi Kelas dan Properties Baru untuk Reifikasi
def add_declaration(root, tag_type, name):
    dec = ET.SubElement(root, f"{{{OWL_NS}}}Declaration")
    ET.SubElement(dec, f"{{{OWL_NS}}}{tag_type}", IRI=f"#{name}")

add_declaration(root, "Class", "ManifestasiGejala")
add_declaration(root, "ObjectProperty", "menghubungkanPenyakit")
add_declaration(root, "ObjectProperty", "melibatkanGejala")

def add_object_assertion(root, prop, subject, obj):
    opa = ET.SubElement(root, f"{{{OWL_NS}}}ObjectPropertyAssertion")
    ET.SubElement(opa, f"{{{OWL_NS}}}ObjectProperty", IRI=f"#{prop}")
    ET.SubElement(opa, f"{{{OWL_NS}}}NamedIndividual", IRI=f"#{subject}")
    ET.SubElement(opa, f"{{{OWL_NS}}}NamedIndividual", IRI=f"#{obj}")

def add_data_assertion(root, prop, subject, val):
    dpa = ET.SubElement(root, f"{{{OWL_NS}}}DataPropertyAssertion")
    ET.SubElement(dpa, f"{{{OWL_NS}}}DataProperty", IRI=f"#{prop}")
    ET.SubElement(dpa, f"{{{OWL_NS}}}NamedIndividual", IRI=f"#{subject}")
    lit = ET.SubElement(dpa, f"{{{OWL_NS}}}Literal", datatypeIRI="http://www.w3.org/2001/XMLSchema#integer")
    lit.text = str(val)

for item in data_penyakit:
    p = item["penyakit"]
    
    if item["disebabkan"]:
        add_object_assertion(root, "disebabkan", p, item["disebabkan"])
    if item["musim"]:
        add_object_assertion(root, "umumTerjadiPadaMusim", p, item["musim"])
    if item["lingkungan"]:
        add_object_assertion(root, "punyaKontakLingkungan", p, item["lingkungan"])
        
    for gejala_ind, hari in item["gejala"]:
        manifest_id = f"{p}_{gejala_ind}"
        
        # Deklarasi individu reifikasi
        add_declaration(root, "NamedIndividual", manifest_id)
        
        ca = ET.SubElement(root, f"{{{OWL_NS}}}ClassAssertion")
        ET.SubElement(ca, f"{{{OWL_NS}}}Class", IRI="#ManifestasiGejala")
        ET.SubElement(ca, f"{{{OWL_NS}}}NamedIndividual", IRI=f"#{manifest_id}")
        
        # Hubungkan ke penyakit dan gejala asli
        add_object_assertion(root, "menghubungkanPenyakit", manifest_id, p)
        add_object_assertion(root, "melibatkanGejala", manifest_id, gejala_ind)
        
        # Pasang data property hari ke individu reifikasi
        add_data_assertion(root, "mulaiDirasakanHariKe", manifest_id, hari)
            
    for pen in item["penanganan"]:
        add_object_assertion(root, "memilikiPenanganan", p, pen)

tree.write(OUTPUT_FILE, xml_declaration=True, encoding="utf-8")
print(f"File reifikasi tersimpan sebagai: {OUTPUT_FILE}")