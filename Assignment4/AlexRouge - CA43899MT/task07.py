# -*- coding: utf-8 -*-
"""Task07.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eS7bihOCI7PBV-u5OucIKaK8KYzwgBq8

**Task 07: Querying RDF(s)**
"""

!pip install rdflib
github_storage = "https://raw.githubusercontent.com/FacultadInformatica-LinkedData/Curso2023-2024/master/Assignment4/course_materials"

"""First let's read the RDF file"""

from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS
g = Graph()
g.namespace_manager.bind('ns', Namespace("http://somewhere#"), override=False)
g.namespace_manager.bind('vcard', Namespace("http://www.w3.org/2001/vcard-rdf/3.0#"), override=False)
g.parse(github_storage+"/rdf/example6.rdf", format="xml")

"""**TASK 7.1: List all subclasses of "LivingThing" with RDFLib and SPARQL**"""

from rdflib.plugins.sparql import prepareQuery

ns = Namespace("http://somewhere#")

q1 = prepareQuery('''
  SELECT ?Subclass WHERE {
    ?Subclass rdfs:subClassOf/rdfs:subClassOf* ns:LivingThing.
  }
  ''',
  initNs = { "rdfs":RDFS, "ns":ns}
)
# Visualize the results
print("SPARQL")
for r in g.query(q1):
  print(r.Subclass)

  def find_subclasses(subclass, subclasses=set()):
    for s, p, o in g.triples((None, RDFS.subClassOf, subclass)):
        if s not in subclasses:
            subclasses.add(s)
            find_subclasses(s, subclasses)
    return subclasses

# RDFLib - find all subclasses of ns.LivingThing
rdfLib_subclasses = find_subclasses(ns.LivingThing)
print("RDFLib")
for subclass in rdfLib_subclasses:
    print(subclass)

"""**TASK 7.2: List all individuals of "Person" with RDFLib and SPARQL (remember the subClasses)**

"""

def find_individuals_and_subclasses(target_class, individuals=set(), seen_classes=set()):
    if target_class in seen_classes:
        return individuals

    seen_classes.add(target_class)

    # Add direct instances of the target class
    for s, p, o in g.triples((None, RDF.type, target_class)):
        individuals.add(s)

    # Recursively process each subclass
    for s, p, o in g.triples((None, RDFS.subClassOf, target_class)):
        find_individuals_and_subclasses(s, individuals, seen_classes)

    return individuals

individuals_rdflib = find_individuals_and_subclasses(ns.Person)
print("RDFLib results:")
for i in individuals_rdflib:
    print(i)

# SPARQL
q1 = prepareQuery('''
    SELECT ?i
    WHERE {
        ?i rdf:type/rdfs:subClassOf* ns:Person.
    }
    ''',
    initNs={"rdfs": RDFS, "ns": ns}
)
print("SPARQL results:")
for r in g.query(q1):
    print(r.i)

"""**TASK 7.3: List all individuals of "Person" or "Animal" and all their properties including their class with RDFLib and SPARQL. You do not need to list the individuals of the subclasses of person**

"""

q1 = prepareQuery('''
  SELECT ?individual ?property ?value WHERE {
    {
      ?individual rdf:type ns:Person.
      ?individual ?property ?value.
    } UNION {
      ?individual rdf:type ns:Animal.
      ?individual ?property ?value.
    }
}
  ''',
  initNs = { "rdf":RDF, "ns":ns, "rdfs":RDFS}
)
# Visualize the results
print("RDFLib")
for s, p, o in g.triples((None, RDF.type, ns.Person)):
  for a, b, c in g.triples((s, None, None)):
    print(a,b,c)

for s, p, o in g.triples((None, RDF.type, ns.Animal)):
  for a, b, c in g.triples((s, None, None)):
    print(a,b,c)

print("SPARQL")
for r in g.query(q1):
  print(r)

"""**TASK 7.4:  List the name of the persons who know Rocky**"""

# Define a SPARQL query to retrieve the names of persons who know Rocky

ns = Namespace("http://somewhere#")
vcard = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
foaf = Namespace("http://xmlns.com/foaf/0.1/")


q2 = prepareQuery('''
  SELECT ?name
    WHERE {
    ?person foaf:knows <http://somewhere#RockySmith> .
    ?person vcard:FN ?name .
    }
  ''',
  initNs={"rdf": RDF, "ns": ns, "rdfs": RDFS, "vcard":vcard}
)

# Execute the query and print the results
print("Persons who know Rocky - SPARQL:")
for row in g.query(q2):
    print(row.name)


# Function to find all persons who know a specific individual
def find_persons_who_know(target_individual):
    persons_who_know = []
    # Querying for all subjects who know the target individual
    for person in g.subjects(predicate=foaf.knows, object=ns.RockySmith):
        persons_who_know.append(person)
    return persons_who_know

# Retrieve the names of persons who know Rocky
persons_who_know_rocky = find_persons_who_know(ns.RockySmith)

print("Persons who know Rocky - RDFLib:")
for person in persons_who_know_rocky:
    name = g.value(subject=person, predicate=vcard.FN)
    if name:
        print(name)

"""**Task 7.5: List the entities who know at least two other entities in the graph**"""

foaf = Namespace("http://xmlns.com/foaf/0.1/")


q2 = prepareQuery('''
  SELECT DISTINCT ?entity
    WHERE {
      ?entity foaf:knows ?other1 .
      ?entity foaf:knows ?other2 .
      FILTER(?other1 != ?other2) .
    }
  ''',
  initNs={"rdf": RDF, "ns": ns, "rdfs": RDFS, "foaf": foaf}
)

# Execute the query and print the results
print("Persons who know at least two entities- SPARQL:")
for row in g.query(q2):
  print(row)


  # Function to find entities who know at least two different entities
def find_entities_knowing_others():
    entities = set()
    for entity in g.subjects(predicate=foaf.knows):
        known_entities = set(g.objects(subject=entity, predicate=foaf.knows))
        if len(known_entities) >= 2:
            entities.add(entity)
    return entities

# Execute the function and print the results
entities_knowing_others = find_entities_knowing_others()

print("Entities who know at least two other entities- RDFLib:")
for entity in entities_knowing_others:
    print(entity)