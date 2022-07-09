import xml.etree.ElementTree as ET
import xmltodict


xml_example = """<employees>
    <person ID="1234567">
        <name>
            <first>Valerii</first>
            <last>Martell</last>
        </name>
        <address>
            <city>Kyiv</city>
            <district>Solomynskiy</district>
        </address>
    </person>

    <person ID="7654321">
        <name>
            <first>Ivan</first>
            <last>Petrov</last>
        </name>
        <address>
            <city>Kyiv</city>
            <district>Pechersk</district>
        </address>
    </person>
</employees>"""


def parse_by_xml():
    root = ET.fromstring(xml_example)

    print("type(root):", type(root))

    first_person = root.find("person")
    all_persons = root.findall("person")

    print("first_person ID: ", first_person.get("ID"))
    print("all persons: ", all_persons)
    print("first_person first name", first_person.find("name").find("first").text)


def parse_by_xmltodict():
    parsed = xmltodict.parse(xml_example)
    print(parsed)

    first_person = parsed["employees"]["person"][0]
    all_persons = parsed["employees"]["person"]

    print("first_person ID: ", first_person["@ID"])
    print("all persons: ", all_persons)
    print("first_person first name", first_person["name"]["first"])


parse_by_xmltodict()
