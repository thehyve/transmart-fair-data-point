'''
* Copyright (c) 2017 The Hyve B.V.
* This code is licensed under the GNU General Public License,
* version 3.
* Author: Ruslan Forostianov
'''

import rdflib
from rdflib import Graph, Literal, BNode, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, FOAF
from datetime import datetime
from transmart_api import TransmartApi

class TransmartFairMetadata(object):

	DCT = Namespace('http://purl.org/dc/terms/')
	DCAT = Namespace('http://www.w3.org/ns/dcat#')
	R3D = Namespace('http://www.re3data.org/schema/3-0#')
	FDP = Namespace('http://rdf.biosemantics.org/ontologies/fdp-o#')
	DATACITE = Namespace('http://purl.org/spar/datacite/')

	LANG = Namespace('http://id.loc.gov/vocabulary/iso639-1/')

	ORGANIZATION = URIRef('http://thehyve.nl')
	ORGANIZATION_NAME = 'The Hyve'

	def __init__(self):
		self.transmart_api = TransmartApi(
			host = 'http://transmart-pro-dev.thehyve.net',
			user = 'admin',
			password = 'changeme')

	def _triples_to_graph(self, triples):
		g = rdflib.Graph()
		for triple in triples:
			g.add(triple)
		g.bind("rdf", RDF)
		g.bind("rdfs", RDFS)
		g.bind("foaf", FOAF)
		g.bind("dct", self.DCT)
		g.bind("dcat", self.DCAT)
		g.bind("r3d", self.R3D)
		g.bind("fdp", self.FDP)
		g.bind("datacite", self.DATACITE)
		return g

	def repository(self):
		repository = URIRef('')
		metaId = 'repository-metadata-id'
		metaIdUri = URIRef('/' + metaId)
		repositoryId = 'repository-id'
		repositoryIdUri = URIRef('/' + repositoryId)
		gpl3 = URIRef('https://www.gnu.org/licenses/gpl-3.0.en.html')
		return self._triples_to_graph([
			(repository, self.DCT.title, Literal('TranSMART')),
			(repository, self.FDP.metadataIssued, Literal(datetime(2017, 2, 17))),
			(repository, self.DCT.hasVersion, Literal(1)),
			(repository, self.DCT.description, Literal('This is the development instance of tranSMART FAIR Datapoint.', lang = 'en')),
			(repository, self.DCT.publisher, self.ORGANIZATION),
			(repository, self.DCT.language, self.LANG.en),
			(repository, self.DCT.language, self.LANG.nl),
			(repository, self.DCT.license, gpl3),
			(repository, self.DCT.rights, gpl3),
			(repository, self.R3D.dataCatalog, URIRef('/studies')),
			(repository, self.FDP.metadataIdentifier, Literal(metaId)),
			(repository, self.R3D.repositoryIdentifier, repositoryIdUri),
			(metaIdUri, RDF.type, self.DATACITE.ResourceIdentifier),
			(metaIdUri, self.DCT.identifier, Literal(metaId)),
			(repositoryIdUri, RDF.type, self.DATACITE.ResourceIdentifier),
			(repositoryIdUri, self.DCT.identifier, Literal(repositoryId))
		])

	def catalog(self):
		catalog = URIRef('')
		metaId = 'studies-catalog-metadata-id'
		metaIdUri = URIRef('/' + metaId)
		triples = [
			(catalog, RDF.type, self.DCAT.Catalog),
			(catalog, self.DCT.title, Literal('Studies', lang = 'en')),
			(catalog, self.DCT.hasVersion, Literal(1)),
			(catalog, self.DCT.publisher, self.ORGANIZATION),
			(catalog, self.DCAT.themeTaxonomy, URIRef('https://www.wikidata.org/wiki/Q30612')),
			(catalog, self.FDP.metadataIdentifier, Literal(metaId)),
			(catalog, self.FDP.metadataIssued, Literal(datetime(2017, 2, 17))),
			(self.ORGANIZATION, RDF.type, FOAF.Organization),
			(self.ORGANIZATION, FOAF.name, Literal(self.ORGANIZATION_NAME)),
			(metaIdUri, RDF.type, Literal(self.DATACITE.ResourceIdentifier)),
			(metaIdUri, self.DCT.identifier, Literal(metaId))
		]
		studies_result = self.transmart_api.get_studies()
		if 'studies' in studies_result:
			for study in studies_result['studies']:
				triples.append((catalog, self.DCAT.dataset, URIRef('/studies/' + study['id'])))

		return self._triples_to_graph(triples)

	def dataset(self, study_id):
		study = self.transmart_api.get_studies(study_id)
		dataset = URIRef('')
		metaId = study['id'] + '-dataset-metadata-id'
		metaIdUri = URIRef('/' + metaId)

		triples = [
			(dataset, RDF.type, self.DCAT.Dataset),
			(dataset, self.DCT.hasVersion, Literal(1)),
			(dataset, self.DCT.publisher, self.ORGANIZATION),
			(dataset, self.DCAT.distribution, URIRef('/studies/' + study['id'] + '/observations')),
			(dataset, RDFS.label, Literal(study['id'])),
			(dataset, self.FDP.metadataIdentifier, Literal(metaId)),
			(dataset, self.FDP.metadataIssued, Literal(datetime.now())),
			(metaIdUri, RDF.type, self.DATACITE.ResourceIdentifier),
			(metaIdUri, self.DCT.identifier, Literal(metaId))
		]

		if 'metadata' in study['ontologyTerm']:
			metadata = study['ontologyTerm']['metadata']
			if 'Title' in metadata:
				triples.append((dataset, self.DCT.title, Literal(metadata['Title'])))
			if 'Has Version' in metadata:
				triples.append((dataset, self.DCT.hasVersion, Literal(metadata['Has Version'])))
			if 'License' in metadata:
				triples.append((dataset, self.DCT.license, URIRef(metadata['License'])))
			if 'theme' in metadata:
				triples.append((dataset, self.DCAT.theme, Literal(metadata['theme'])))
			if 'Publisher' in metadata:
				publisherUri = URIRef(metadata['Publisher'])
				triples.append((dataset, self.DCT.publisher, publisherUri))
				triples.append((publisherUri, RDF.type, FOAF.Organization))
				if 'name' in metadata:
					triples.append((publisherUri, FOAF.name, Literal(metadata['name'])))

		return self._triples_to_graph(triples)

	def distribution(self, study_id):
		study = self.transmart_api.get_studies(study_id)
		metaId = study['id'] + '-distribution-metadata-id'
		metaIdUri = URIRef('/' + metaId)
		distribution = URIRef('')

		return self._triples_to_graph([
			(distribution, RDF.type, self.DCAT.Distribution),
			(distribution, self.DCT.title, Literal(study_id + ' JSON')),
			(distribution, self.DCT.hasVersion, Literal(1)),
			(distribution, self.FDP.metadataIdentifier, Literal(metaId)),
			(distribution, self.FDP.metadataIssued, Literal(datetime(2017, 2, 17))),
			(distribution, self.DCAT.mediaType, Literal('application/json')),
			(distribution, self.DCAT.downloadURL, URIRef('/studies/' + study['id'] + '/observations')),
			(metaIdUri, RDF.type, self.DATACITE.ResourceIdentifier),
			(metaIdUri, self.DCT.identifier, Literal(metaId))
		])