from django.http import HttpRequest
from django.conf import settings


from geoapi import models as geoapi_models
from geoapi import serializers as geoapi_serializers
from geoapi import responses as geoapi_responses
from geoapi.schemas import schemas
from geoapi import utils

def collections(request: HttpRequest):
    """
    Handler for the /collections endpoint.

    This function contains all the logic behind the collections endpoint.
    """
    # TODO Add links to individual collections inside the collections list

    # The formats that the /collections endpoint accepts. Used for content negotiation.
    accepted_formats = [
        utils.F_JSON, utils.F_HTML, utils.F_GEOJSON
    ]

    # Get the format using the "f" parameter or content negotiation with ACCEPT header.
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    collection_list = geoapi_models.Collection.objects.all()

    base_url, path, query_params = utils.deconstruct_url(request)
    base_url:str = utils.get_base_url()

    # build links
    links = []
    # Landing links
    landing_links = utils.build_landing_links()
    links += landing_links

    # Self link
    self_link_href = f'{base_url}/collections'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # Alternate format links
    for formats in accepted_formats:
        for link_format in formats:
            if "/" not in link_format:
                html_link_href_params = utils.replace_or_create_param(query_params, 'f', link_format)
                html_link_href = f'{base_url}/collections?{html_link_href_params}'
                links.append(
                    schemas.LinkSchema(href=html_link_href, rel="alternate", type=utils.content_type_from_format(link_format), title=f"This document as {link_format.upper()}.")
                )

    serializer = geoapi_serializers.CollectionsSerializer()
    options = {
        "links": links.copy()
    }
    serialized_collections = serializer.serialize(collection_list, **options)
    
    # Response objects
    headers = {}
    
    if f in utils.F_JSON or f in utils.F_GEOJSON:
        #response = json.dumps(resp)
        headers['Content-Type'] = 'application/json; charset=utf-8'
        return geoapi_responses.response_json_200(items_serialized=serialized_collections)

    elif f in utils.F_HTML:
        return geoapi_responses.response_html_200(request, serialized_collections, "collections/collections.html")
    
    else:
        response = "NO SUPPORTED"
        return geoapi_responses.response_bad_request_400(msg=response)

    