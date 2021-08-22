#!/usr/bin/env python3

_dict = {
  'PegelOnline': {
    'endpoint':       'https://www.pegelonline.wsv.de/webservices/rest-api/v2/stations.json',
    'responseType':   'PGO',
    'subtitle':       'der Wasserstraßen- und Schiffahrtsverwaltung des Bundes',
    'title':          'PEGELONLINE Gewässerkundliches Informationssystem'
  },
  'UKFloodMonitoring': {
    'endpoint':       'https://environment.data.gov.uk/flood-monitoring/id/floods',
    'responseType':   'UKF',
    'subtitle':       'Department for Environment Food & Rural Affairs',
    'title':          'Flood Monitoring'
  },
  'UKFloodMonitoringForecast': {
    'endpoint':       'https://environment.data.gov.uk/flood-monitoring/id/3dayforecast',
    'responseType':   'UKF',
    'subtitle':       'Department for Environment Food & Rural Affairs',
    'title':          'Flood Monitoring: 3 Day Forecast'
  }
}

_docs = {
  'OpenFEMA':                           'https://www.fema.gov/about/openfema/api',
  'PegelAlarm':                         'https://pegelalarm.com/api_and_data.php',
  'PegelOnline':                        'https://www.pegelonline.wsv.de/webservice/dokuRestapi',
  'PredictHQ':                          'https://docs.predicthq.com/api/introduction/',
  'UKFloodMonitoring':                  'https://environment.data.gov.uk/flood-monitoring/doc'
}
