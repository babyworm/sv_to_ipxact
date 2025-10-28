from lxml import etree

class IpxactConverter:
    def __init__(self, input_file):
        self.input_file = input_file
        self.tree = etree.parse(input_file)
        self.root = self.tree.getroot()
        self.namespace = None
        # Extract namespace from the root tag, e.g., {http://...}component
        if '}' in self.root.tag:
            self.namespace = self.root.tag.split('}')[0][1:]
        else:
            # Fallback for documents that might not have a namespace on the root
            for uri in self.root.nsmap.values():
                if 'SPIRIT/1685-2009' in uri or 'IPXACT/1685' in uri:
                    self.namespace = uri
                    break

    def get_version(self):
        if self.namespace:
            if '1685-2009' in self.namespace:
                return '2009'
            elif '1685-2014' in self.namespace:
                return '2014'
            elif '1685-2022' in self.namespace:
                return '2021'
        return None

    def convert(self, target_version):
        current_version = self.get_version()
        if current_version is None:
            raise ValueError("Unsupported or unknown IP-XACT version.")

        if current_version == target_version:
            return self.tree

        self._transform_namespaces(current_version, target_version)

        return self.tree

    def _transform_namespaces(self, current_version, target_version):
        version_map = {
            '2009': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009',
            '2014': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2014',
            '2021': 'http://www.accellera.org/XMLSchema/IPXACT/1685-2022',
        }

        target_namespace = version_map.get(target_version)
        if not target_namespace:
            raise ValueError(f"Unknown target version: {target_version}")

        # Update the namespace prefixes
        new_nsmap = {k: v.replace(self.namespace, target_namespace) for k, v in self.root.nsmap.items()}

        # Create a new root element with the correct namespace
        new_root = etree.Element(self.root.tag.replace(self.namespace, target_namespace), nsmap=new_nsmap)
        new_root[:] = self.root[:]
        for attr, value in self.root.attrib.items():
            new_root.set(attr, value)

        self.root = new_root
        self.tree = etree.ElementTree(new_root)

        # Determine the old and new prefixes
        old_prefix = None
        new_prefix = None
        for prefix, uri in new_nsmap.items():
            if uri == target_namespace:
                new_prefix = prefix
            if self.root.nsmap.get(prefix) == self.namespace:
                old_prefix = prefix

        if old_prefix and new_prefix and old_prefix != new_prefix:
            # Update all elements in the tree
            for element in self.root.xpath('//*'):
                if isinstance(element.tag, str) and element.tag.startswith(f"{{{self.namespace}}}"):
                    element.tag = element.tag.replace(f"{{{self.namespace}}}", f"{{{target_namespace}}}")

                for attr_name in list(element.attrib.keys()):
                    if attr_name.startswith(f"{{{self.namespace}}}"):
                        new_attr_name = attr_name.replace(f"{{{self.namespace}}}", f"{{{target_namespace}}}")
                        element.attrib[new_attr_name] = element.attrib.pop(attr_name)
        else: # if no prefix or prefix is the same, just update namespace
             for element in self.root.xpath('//*'):
                if isinstance(element.tag, str) and self.namespace in element.tag:
                    element.tag = element.tag.replace(self.namespace, target_namespace)


        self.namespace = target_namespace

    def validate(self, version):
        schema_path = f"libs/ipxact_schemas/{version}/component.xsd"
        try:
            xmlschema_doc = etree.parse(schema_path)
            xmlschema = etree.XMLSchema(xmlschema_doc)
            xmlschema.assertValid(self.tree)
            print("Validation successful!")
            return True
        except etree.DocumentInvalid as e:
            print("Validation error:")
            for error in xmlschema.error_log:
                print(f"  Line {error.line}: {error.message}")
            return False
        except FileNotFoundError:
            print(f"Schema file not found for version {version}")
            return False

    def save(self, output_file):
        self.tree.write(output_file, pretty_print=True, xml_declaration=True, encoding='UTF-8')
