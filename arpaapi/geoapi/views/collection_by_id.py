import json
import datetime
from django.shortcuts import HttpResponse
from django.http import HttpRequest
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.apps import apps

from geoapi import models as geoapi_models
from geoapi import utils


#GET for a single collection.
#POST for adding data to a collection - both bulk and single.
def collection_by_id(request: HttpRequest, collectionId: str):

    if request.method == "GET":
        model_name = collectionId
        coll = geoapi_models.Collections.objects.filter(model_name=model_name).first()

        #Collection schema: https://schemas.opengis.net/ogcapi/features/part1/1.0/openapi/schemas/collection.yaml
        resp = {
            "id": coll.model_name,
            "title": coll.title,
            "description": coll.description,
            "links": [],
            "extent": {},
            "itemType": "feature",
            "crs": ["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]
        }
        
        # Response objects
        response = None
        headers = {}

        # Query parameters
        f = request.GET.get('f', 'json')
        
        if f == 'json':
            response = json.dumps(resp)
            headers['Content-Type'] = 'application/json; charset=utf-8'
        else:
            response = "NO SUPPORTED"
            headers['Content-Type'] = 'text/html; charset=utf-8'

        return HttpResponse(response, headers=headers, status=200)

    elif request.method == "POST":
        body:dict = json.loads(request.body)
        bulk_upload = body.get('bulk', False)
        # structure: {'bulk': boolean, items: []}

        if bulk_upload:
            #bulk upload
            items = body.get("items")
        else:
            #single insert
            items = body.get("items")

        """
        if 'latitude' in body and 'longitude' in body:
            body['location'] = Point(x=body['longitude'], y=body['latitude'])

        if 'date_start' in body:
            # expect dd/mm/yyyy or null
            if body['date_start'] is not None:
                date_start_parts = str(body['date_start']).split("/")
                body['date_start'] = datetime.date(
                    int(date_start_parts[2].lstrip('0')), 
                    int(date_start_parts[1].lstrip('0')), 
                    int(date_start_parts[0].lstrip('0'))
            )
        if 'date_stop' in body:
            # expect dd/mm/yyyy or null
            if body['date_stop'] is not None:
                date_stop_parts = str(body['date_stop']).split("/")
                body['date_stop'] = datetime.date(
                    int(date_stop_parts[2].lstrip('0')), 
                    int(date_stop_parts[1].lstrip('0')), 
                    int(date_stop_parts[0].lstrip('0'))
            )
        """
            
        model_name = collectionId
        collection_model = apps.get_model('geoapi', model_name=model_name)
        try:
            new_items = collection_model.objects.bulk_create([collection_model(**item) for item in items ], ignore_conflicts=True)
        except Exception as ex:
            print(ex)
            return HttpResponse("Duplicated", status=500)
        
        return HttpResponse(new_items, status=200)