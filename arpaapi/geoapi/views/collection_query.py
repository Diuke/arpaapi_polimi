from django.http import HttpRequest

from geoapi import utils
from geoapi import models as geoapi_models
from geoapi import responses
from geoapi import serializers as geoapi_serializers
from geoapi.schemas import schemas as geoapi_schemas

"""
query parameters:
f = Format. Example: "json" or "geojson"
limit = Max number of elements. Used for pagination
offset = Initial element. Used for pagination
bbox = For filtering in a bounding box. Example: 10.010,45.312,10.048,45.719
datetime = Datetime range for filtering by datetime. It can be a closed interval (2023-01-01/2023-02-28), or open interval (2023-01-01/.. or ../2023-02-28)
"param" = It is a dynamic parameter for filtering according to the properties of the collection. 
"""

#GLOBAL CONSTANTS
LIMIT_DEFAULT = 100
MAX_ELEMENTS = 1000000

def collection_query(request: HttpRequest, collectionId: str, query: str):
    model_name = collectionId
    collection = geoapi_models.Collection.objects.get(model_name=model_name)
    collection_model = geoapi_models.get_model(collection)
    base_url, path, query_params = utils.deconstruct_url(request)

    # Format of the response
    # Default format is GeoJSON
    accepted_formats = [
        utils.F_GEOJSON, utils.F_HTML, utils.F_JSON
    ]
    f = utils.get_format(request=request, accepted_formats=accepted_formats)

    links = []
    # Self link
    self_link_href = f'{base_url}collections/{collection.model_name}/items'
    if query_params:
        self_link_href += f'?{query_params}'
    links.append(
        geoapi_schemas.LinkSchema(href=self_link_href, rel="self", type=utils.content_type_from_format(f), title="This document")
    )

    # Parent collection link
    parent_collection_link = f'{base_url}collections/{collection.model_name}'
    links.append(
        geoapi_schemas.LinkSchema(href=parent_collection_link, rel="collection", type=utils.content_type_from_format(f), title=f"{collection.description}")
    )

    # alternate format links
    for link_format in accepted_formats:
        html_link_href_params = utils.replace_or_create_param(query_params, 'f', link_format)
        html_link_href = f'{base_url}collections/{collection.model_name}/items/?{html_link_href_params}'
        links.append(
            geoapi_schemas.LinkSchema(href=html_link_href, rel="alternate", type=utils.content_type_from_format(link_format), title=f"Items as {link_format.upper()}.")
        )

    if query == geoapi_schemas.POSITION:
        return responses.response_bad_request_400("Position query not yet supported")  
    
    elif query == geoapi_schemas.RADIUS:   
        return responses.response_bad_request_400("Radius query not yet supported")

    elif query == geoapi_schemas.AREA: 
        return responses.response_bad_request_400("Area query not yet supported")
    
    elif query == geoapi_schemas.CUBE: 
        return responses.response_bad_request_400("Cube query not yet supported")
    
    elif query == geoapi_schemas.TRAJECTORY: 
        return responses.response_bad_request_400("Trajectory query not yet supported")
    
    elif query == geoapi_schemas.CORRIDOR: 
        return responses.response_bad_request_400("Corridor query not yet supported")
    
    elif query == geoapi_schemas.ITEMS: 
        # Perform query for all elements
        # if collection.api_type == geoapi_models.Collection.API_Types.EDR:
        #     display_fields = [ 'id' ] + collection.display_fields.split(',')
        #     display_fields = [ f'A.{field}' for field in display_fields ]
        #     items = f"SELECT {', '.join(display_fields)}, st_AsGeoJSON(B.location, {6}) AS geojson FROM geoapi_{collection.model_name} as A, geoapi_airqualitysensor as B LIMIT 10"

        #     items = collection_model.objects.raw(
        #         raw
        #     )
        #     for i in range(10):
        #         print(items[i])
        # else:
        # TODO raw queries for improving geojson speed from the database
        items = collection_model.objects.all()

        # Query parameters
        # Common accepted parameters of this request
        accepted_parameters = [
            'bbox', 'datetime', 'skipGeometry', 'limit', 'offset', 'f'
        ]
        # Collection-specific accepted query parameters:
        filter_fields = collection.filter_fields.split(",")
        accepted_parameters += [ field for field in filter_fields ]

        django_filters = ["", "__lte", "__lt", "__gte", "__gt", "__ne", "__in"]
        for field in filter_fields: 
            for d_filter in django_filters:
                accepted_parameters.append((field + d_filter))

        # Return 400 if there is an "unknown" parameter in the request
        for key, value in request.GET.items():
            if key not in accepted_parameters:
                return responses.response_bad_request_400(f"Unknown Parameter: {key}")

        bbox = request.GET.get('bbox', None)
        datetime_param = request.GET.get('datetime', None)
        skip_geometry = request.GET.get('skipGeometry', None)
        if skip_geometry is not None:
            skip_geometry = True if skip_geometry == "true" else False

        # Limit parameter, if not an integer, return error
        try:
            limit = int(request.GET.get('limit', LIMIT_DEFAULT)) #100 elements by default
        except:
            return responses.response_bad_request_400("Error in limit parameter")
        
        # Offset parameter, if not an integer, return error
        try:
            offset = int(request.GET.get('offset', 0))
        except:
            return responses.response_bad_request_400("Error in offset parameter")

        filtering_params = {}
        for field in filter_fields:
            # Iterate the different filters that django supports
            # This supports the usage of other operators as != (__ne), > (__gt), >= (__gte), < (__lt), <= (__lte)
            for d_filter in django_filters:
                filter_name = (field + d_filter)
                filtering_param_value = request.GET.get(filter_name, None)
                
                if filtering_param_value is not None:
                    filtering_params[filter_name] = filtering_param_value

                    # If it is an array filter - input must be comma-separated
                    if d_filter == "__in":
                        filtering_params[filter_name] = filtering_params[filter_name].strip().split(",")

                    #validate boolean fields
                    if filtering_params[filter_name] == 'true': filtering_params[filter_name] = True
                    if filtering_params[filter_name] == 'false': filtering_params[filter_name] = False

        #filters
        # bbox filter
        if bbox is not None:
            bbox = bbox.split(",")
            #validate bbox
            if not (isinstance(bbox, list) and (len(bbox) == 4 or len(bbox) == 6)):
                return responses.response_bad_request_400("malformed bbox parameter")
            try:
                bbox = [ float(el) for el in bbox ]
            except Exception as ex:
                return responses.response_bad_request_400("malformed bbox parameter")
            
            items = utils.filter_bbox(items, bbox, collection)

        # datetime filter
        datetime_field = collection.datetime_field
        if datetime_param is not None:
            # if the collection has a datetime field to filter
            if datetime_field is not None:
                start_date, end_date = utils.process_datetime_interval(datetime_param)
                items = utils.filter_datetime(items, start_date, end_date, datetime_field)

        # model fields filters
        # Iterate the filtering parameters already calculated before. This supports basic filtering operators
        for field in filtering_params.keys():
            if filtering_params[field] is not None:
                items = utils.filter(items, field, filtering_params[field])

        # Maximum 100.000 elements in request
        items_count = items.count()
        if limit > MAX_ELEMENTS and items_count > MAX_ELEMENTS:
            print("too many elements")
            return responses.response_bad_request_400("Too many elements")
        if limit == -1: # Max number
            limit = MAX_ELEMENTS
        
        # pagination
        if limit is None:
            if collection.api_type == geoapi_models.Collection.API_Types.EDR:
                return responses.response_bad_request_400("Limit must be set!")

        items, retrieved_elements, full_count = utils.paginate(items, limit, offset)

        # Create pagination links if the result has pages
        if limit + offset <= full_count:
            # next page link
            next_limit = limit
            next_offset = limit + offset
            next_params = query_params
            next_params = utils.replace_or_create_param(next_params, 'limit', str(next_limit))
            next_params = utils.replace_or_create_param(next_params, 'offset', str(next_offset))
            next_link_href = f'{base_url}{path}?{next_params}'
            next_link = geoapi_schemas.LinkSchema(
                href=next_link_href, rel='next', type=utils.content_type_from_format(f), title="Next page"
            )
            links.append(next_link)

        if offset - limit >= 0:
            # previous page link
            prev_limit = limit
            prev_offset = offset - limit
            prev_params = query_params
            prev_params = utils.replace_or_create_param(prev_params, 'limit', str(prev_limit))
            prev_params = utils.replace_or_create_param(prev_params, 'offset', str(prev_offset))
            prev_link_href = f'{base_url}{path}?{prev_params}'
            prev_link = geoapi_schemas.LinkSchema(
                href=prev_link_href, rel='prev', type=utils.content_type_from_format(f), title="Previous page"
            )
            links.append(prev_link)


        # format (f) parameter
        # Last part and return
        if f == 'geojson':
            fields = collection.display_fields.split(",")
            geometry_field = None if skip_geometry else collection.geometry_field

            # Select the serializer depending on the API type.
            #   For EDR collections, use the EDR GeoJSON serializer, for normal Features
            #   use the FeaturesGeoJSON serializer.
            if collection.api_type == geoapi_models.Collection.API_Types.EDR:
                serializer = geoapi_serializers.EDRGeoJSONSerializer()
            else:
                serializer = geoapi_serializers.FeaturesGeoJSONSerializer()
            options = {
                "number_matched": full_count, 
                "number_returned": retrieved_elements, 
                "links": links,
                "geometry_field": geometry_field, 
                "fields": fields
            }
            items_serialized = serializer.serialize(items, **options)
            return responses.response_geojson_200(items_serialized)

        elif f == utils.F_JSON:
            fields = collection.display_fields.split(",")
            serializer = geoapi_serializers.SimpleJsonSerializer()
            items_serialized = serializer.serialize(items, fields=fields)
            return responses.response_json_200(items_serialized)

        elif f == utils.F_CSV:
            #TODO Add support for CSV format
            return responses.response_bad_request_400("Format CSV not yet supported")
        
        elif f == utils.F_HTML:
            fields = collection.display_fields.split(",")
            serializer = geoapi_serializers.SimpleJsonSerializer()
            items_serialized = serializer.serialize(items, fields=fields)

            if retrieved_elements > 100: 
                return responses.response_bad_request_400("Request too large for HTML representation - Max 100 elements")
            return responses.response_html_200(request, items_serialized, "collections/items.html")
        
        else:
            return responses.response_bad_request_400(f"Format {f} not yet supported")

    elif query == geoapi_schemas.LOCATIONS: 
        # Query parameters
        location_id = request.GET.get('locationId', None)
        datetime_param = request.GET.get('datetime', None)
        parameter_name = request.GET.get('parameter-name', None)
        skip_geometry = request.GET.get('skipGeometry', None)
        if skip_geometry is not None:
            skip_geometry = True if skip_geometry == "true" else False
        crs = request.GET.get('crs', None)
        limit = request.GET.get('limit', LIMIT_DEFAULT ) #100 elements by default
        offset = request.GET.get('offset', 0)
        f = request.GET.get('f', 'json')

        if location_id is None:
            #TODO return a list of available locaions - that is the list of sensors available
            return responses.response_geojson_200([])
        
        else: 
            items = collection_model.objects.all()
            location_id = int(location_id)
            location_filter_field = collection.locations_field
            items = utils.filter(items, location_filter_field, location_id)

        # pagination
        if limit is None:
            return responses.response_bad_request_400("Limit must be set!")

        items, retrieved_elements, full_count = utils.paginate(items, limit, offset)

        if retrieved_elements >= 100000:
            return responses.response_bad_request_400("Too many elements")
        
        # build links
        links = []

        # Format and response
        if f == 'geojson':
            fields = collection.display_fields.split(",")
            geometry_field = None if skip_geometry else collection.geometry_field
            serializer = geoapi_serializers.EDRGeoJSONSerializer()
            options = {
                "number_matched": full_count, 
                "number_returned": retrieved_elements, 
                "geometry_field": geometry_field, 
                "fields": fields,
                "links": links
            }
            items_serialized = serializer.serialize(items, **options)
            return responses.response_geojson_200(items_serialized)

        elif f == 'json':
            fields = collection.display_fields.split(",")
            serializer = geoapi_serializers.SimpleJsonSerializer()
            items_serialized = serializer.serialize(items, fields=fields)
            return responses.response_json_200(items_serialized)

        elif f == 'csv':
            #TODO Add support for CSV format
            return responses.response_bad_request_400("Format CSV not yet supported")
        
        elif f == 'html':
            #TODO Add render for HTML format
            return responses.response_bad_request_400("Format HTML not yet supported")
        
        else:
            return responses.response_bad_request_400(f"Format {f} not yet supported")

    elif query == geoapi_schemas.INSTANCES: 
        return responses.response_bad_request_400("Instances query not yet supported")
            
    else:
        return responses.response_bad_request_400("Query not supported")

def create_pagination_links():
    return []