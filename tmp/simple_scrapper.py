from lxml import html
import requests

for veh in range(10001,10010):
	# Fixing the url
	url = "http://www.ecovehiculos.gob.mx/ecoetiquetado.php?vehiculo_id=" + str(veh)
	url = requests.get(url)
	# Obtaining the text
	tree = html.fromstring(url.text)
	# XPath queries
	rend_ajustado_xpath_query = "/html/body/table/tr[4]/td/table/tr/td[2]/table[2]/tr[1]/td[1]/b/table/tr[10]/td[2]/table/tr/td[1]"
	result = tree.xpath(rend_ajustado_xpath_query)
	print 'Vehicle: ' + str(veh) + ': ' + result[0].text.strip()