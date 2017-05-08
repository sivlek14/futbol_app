# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from decorators import cache_per_user_function, get_data

from django.shortcuts import render

import datetime

@cache_per_user_function(ttl=5)
def index(request,**kwargs):
	response = {"datetime": kwargs['datetime'] ,"completed_in": "%s segundos"  %str(datetime.datetime.now() - kwargs['datetime']),"c": {"d": "e"},"a": "b"}
	return response

@cache_per_user_function(ttl=5)
@get_data()
def futbol(request, events=None, **kwargs):
	now = datetime.datetime.now()
	games = []
	for ch in events.iter("partido"):
		if ch.find("estado").text is not None and ch.find("estado").text == "Finalizado":
			fecha = ch.attrib['fecha']
			hora = ch.attrib['hora']
			datetime_object = datetime.datetime.strptime(fecha+" "+hora, '%Y%m%d %H:%M:%S')
			for x in ch:
				if x.tag == "visitante":
					visitante = x.attrib['nc']
				if x.tag == "local":
					local = x.attrib['nc']
			if (int(ch.find("goleslocal").text) > int(ch.find("golesvisitante").text)):
				ganador = local
			elif(int(ch.find("golesvisitante").text) > int(ch.find("goleslocal").text)):
				ganador = visitante
			elif(int(ch.find("golesvisitante").text) == int(ch.find("goleslocal").text)):
				ganador = "Empate"
			games.append({
				"partido": local+" - "+visitante,
				"ganador": ganador,
				"resultado" : ch.find("goleslocal").text+" - "+ ch.find("golesvisitante").text,
				"fecha": datetime_object.strftime('%H:%M %d-%m-%Y')
			})
	
	response = {
		"datetime":	kwargs['datetime'],
		"completed_in":	"%s segundos"  %str(now - kwargs['datetime']),
		"partidos":games
	}
	return response
