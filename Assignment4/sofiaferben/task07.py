# -*- coding: utf-8 -*-
"""Task07.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1FH_-DJcfynrnNfTPZqiwd1u4SkhtbGa8

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

# TO DO
ns = Namespace("http://somewhere#")
##1) RDFLib
for s,p,o in g.triples((None, RDFS.subClassOf, ns.LivingThing)):
  print("Subclass of LivingThing:", s)

##2) SPARQL
from rdflib.plugins.sparql import prepareQuery
q1 = prepareQuery('''
SELECT ?sub
WHERE {
  ?sub rdfs:subClassOf ns:LivingThing.
      }
      ''',
      initNs={"rdfs":RDFS, "ns":ns})
# Visualize the results
print("\nSubclass of  LivingThing")
for r in g.query(q1):
  print(r.sub)

"""**TASK 7.2: List all individuals of "Person" with RDFLib and SPARQL (remember the subClasses)**

"""

##1) RDFLib
print("List of all individuals of Person (with subclasses)")
for s,p,o in g.triples((None, RDF.type, ns.Person)):
    print(s)

for s,p,o in g.triples((None, RDFS.subClassOf, ns.Person)):
    for s1,p2,o2 in g.triples((None, RDF.type, s)):
        print(s1)



##2) SPARQL
q2 = prepareQuery('''
  SELECT DISTINCT ?s
  WHERE {
    {?s rdf:type ns:Person}
    UNION
    {
     ?sub rdfs:subClassOf* ns:Person .
     ?s  rdf:type ?sub
    }
  }
  ''',
  initNs = { "ns": ns, "rdf": RDF}
  )

print("\nList of all individuals of Person (with subclasses)")
for r in g.query(q2):
  print(r.s)

"""**TASK 7.3: List all individuals of "Person" or "Animal" and all their properties including their class with RDFLib and SPARQL. You do not need to list the individuals of the subclasses of person**

"""

##1) RDFLib
print("List of invidividuals of Person and their properties:")
for s, p, o in g.triples((None, RDF.type, ns.Person)):
  for sub, pre, obj in g.triples((s, None, None)):
    print(sub, obj)

print("\nList of invidividuals of Animal and their properties:")
for s, p, o in g.triples((None, RDF.type, ns.Animal)):
  for sub, pre, obj in g.triples((s, None, None)):
    print(sub, obj)

##2) SPARQL
q3 = prepareQuery('''
  SELECT DISTINCT ?s ?y
  WHERE {
    {?s  rdf:type ns:Person.
    ?s ?p ?y

    }
    UNION
    {
     ?s rdf:type ns:Animal .
     ?s ?p ?y
    }
  }
  ''',
  initNs = { "ns": ns, "rdf": RDF}
  )

print("\nList of all individuals and properties of Person and Animal ")
for r in g.query(q3):
  print(r.s,r.y)

"""**TASK 7.4:  List the name of the persons who know Rocky**"""

FOAF = Namespace("http://xmlns.com/foaf/0.1/")
VCARD = Namespace("http://www.w3.org/2001/vcard-rdf/3.0/")
from rdflib import XSD

##RDFLib
RockyURI = g.value(subject=None, predicate=VCARD.Given, object=Literal("Rocky"))

knows = g.triples((None, FOAF.knows, RockyURI))
persons = [s for s, p, o in knows if (s, RDF.type, ns.Person) in g]

print("List of persons who know Rocky:")
for person in persons:
    givenName = g.value(subject=person, predicate=VCARD.Given, object=None)
    print(givenName)




##2)SPARQL
q4 = prepareQuery('''
  SELECT  DISTINCT ?Subject ?Given  WHERE {
    ?Subject foaf:knows ?Rocky.
	?Rocky vcard:Given ?RockyName.
	?Subject vcard:Given ?Given.
  ?Subject rdf:type ns:Person.
  }
  ''',
  initNs = { "foaf": FOAF, "vcard": VCARD, "xsd":XSD,"ns":ns}
)

print("Persons who know Rocky:")
for r in g.query(q4, initBindings = {'?RockyName' : Literal('Rocky', datatype=XSD.string)}):
  print(r.Given)

"""**Task 7.5: List the entities who know at least two other entities in the graph**"""

##1) RDFlib
knows = g.triples((None, FOAF.knows, None))
print("Entities who know at least two other entities:")
knows_count = {}
for s, p, o in g.triples((None, FOAF.knows, None)):
    if s not in knows_count:
        knows_count[s] = 1
    else:
        knows_count[s] += 1

for individual, count in knows_count.items():
    if count >= 2:
        print(individual)

##2)SPARQL
q5 = prepareQuery('''
    SELECT DISTINCT ?entity
    WHERE {
  ?entity foaf:knows ?otherperson .
}
  GROUP BY ?entity
  HAVING (COUNT(?otherperson) >= 2)

''', initNs = {"foaf": FOAF}

)
print("\nEntities who know at least two other entities:")
for r in g.query(q5):
    print(r.entity)