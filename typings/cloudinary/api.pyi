"""
This type stub file was generated by pyright.
"""

def ping(**options):  # -> Response:
    ...
def usage(**options):  # -> Response:
    """Get account usage details.

    Get a report on the status of your Cloudinary account usage details, including storage, credits, bandwidth,
    requests, number of resources, and add-on usage. Note that numbers are updated periodically.

    See: `Get account usage details
    <https://cloudinary.com/documentation/admin_api#get_account_usage_details>`_

    :param options:     Additional options
    :type options:      dict, optional
    :return:            Detailed usage information
    :rtype:             Response
    """
    ...

def config(**options):  # -> Response:
    """
    Get account config details.

    :param options:     Additional options.
    :type options:      dict, optional
    :return:            Detailed config information.
    :rtype:             Response
    """
    ...

def resource_types(**options):  # -> Response:
    ...
def resources(**options):  # -> Response:
    ...
def resources_by_tag(tag, **options):  # -> Response:
    ...
def resources_by_moderation(kind, status, **options):  # -> Response:
    ...
def resources_by_ids(public_ids, **options):  # -> Response:
    ...
def resources_by_asset_folder(asset_folder, **options):  # -> Response:
    """
    Returns the details of the resources (assets) under a specified asset_folder.

    :param asset_folder:    The Asset Folder of the asset
    :type asset_folder:     string
    :param options:     Additional options
    :type options:      dict, optional
    :return:            Resources (assets) of a specific asset_folder
    :rtype:             Response
    """
    ...

def resources_by_asset_ids(asset_ids, **options):  # -> Response:
    """Retrieves the resources (assets) indicated in the asset IDs.
    This method does not return deleted assets even if they have been backed up.

    See: `Get resources by context API reference
    <https://cloudinary.com/documentation/admin_api#get_resources>`_

    :param asset_ids:   The requested asset IDs.
    :type asset_ids:    list[str]
    :param options:     Additional options
    :type options:      dict, optional
    :return:            Resources (assets) as indicated in the asset IDs
    :rtype:             Response
    """
    ...

def resources_by_context(key, value=..., **options):  # -> Response:
    """Retrieves resources (assets) with a specified context key.
    This method does not return deleted assets even if they have been backed up.

    See: `Get resources by context API reference
    <https://cloudinary.com/documentation/admin_api#get_resources_by_context>`_

    :param key:         Only assets with this context key are returned
    :type key:          str
    :param value:       Only assets with this value for the context key are returned
    :type value:        str, optional
    :param options:     Additional options
    :type options:      dict, optional
    :return:            Resources (assets) with a specified context key
    :rtype:             Response
    """
    ...

def visual_search(image_url=..., image_asset_id=..., text=..., image_file=..., **options):  # -> Response:
    """
    Find images based on their visual content.

    :param image_url:       The URL of an image.
    :type image_url:        str
    :param image_asset_id:  The asset_id of an image in your account.
    :type image_asset_id:   str
    :param text:            A textual description, e.g., "cat"
    :type text:             str
    :param image_file:      The image file.
    :type image_file:       str|callable|Path|bytes
    :param options:         Additional options
    :type options:          dict, optional
    :return:                Resources (assets) that were found
    :rtype:                 Response
    """
    ...

def resource(public_id, **options):  # -> Response:
    ...
def resource_by_asset_id(asset_id, **options):  # -> Response:
    """
    Returns the details of the specified asset and all its derived assets by asset id.

    :param asset_id:    The Asset ID of the asset
    :type asset_id:     string
    :param options:     Additional options
    :type options:      dict, optional
    :return:            Resource (asset) of a specific asset_id
    :rtype:             Response
    """
    ...

def update(public_id, **options):  # -> Response:
    ...
def delete_resources(public_ids, **options):  # -> Response:
    ...
def delete_resources_by_prefix(prefix, **options):  # -> Response:
    ...
def delete_all_resources(**options):  # -> Response:
    ...
def delete_resources_by_tag(tag, **options):  # -> Response:
    ...
def delete_derived_resources(derived_resource_ids, **options):  # -> Response:
    ...
def delete_derived_by_transformation(public_ids, transformations, resource_type=..., type=..., invalidate=..., **options):  # -> Response:
    """Delete derived resources of public ids, identified by transformations

    :param public_ids: the base resources
    :type public_ids: list of str
    :param transformations: the transformation of derived resources, optionally including the format
    :type transformations: list of (dict or str)
    :param type: The upload type
    :type type: str
    :param resource_type: The type of the resource: defaults to "image"
    :type resource_type: str
    :param invalidate: (optional) True to invalidate the resources after deletion
    :type invalidate: bool
    :return: a list of the public ids for which derived resources were deleted
    :rtype: dict
    """
    ...

def add_related_assets(public_id, assets_to_relate, resource_type=..., type=..., **options):  # -> Response:
    """
    Relates an asset to other assets by public IDs.

    :param public_id: The public ID of the asset to update.
    :type public_id: str
    :param assets_to_relate: The array of up to 10 fully_qualified_public_ids given as resource_type/type/public_id.
    :type assets_to_relate: list[str]
    :param type: The upload type. Defaults to "upload".
    :type type: str
    :param resource_type: The type of the resource. Defaults to "image".
    :type resource_type: str
    :param options: Additional options.
    :type options: dict, optional
    :return: The result of the command.
    :rtype: dict
    """
    ...

def add_related_assets_by_asset_ids(asset_id, assets_to_relate, **options):  # -> Response:
    """
    Relates an asset to other assets by asset IDs.

    :param asset_id: The asset ID of the asset to update.
    :type asset_id: str
    :param assets_to_relate: The array of up to 10 asset IDs.
    :type assets_to_relate: list[str]
    :param options: Additional options.
    :type options: dict, optional
    :return: The result of the command.
    :rtype: dict
    """
    ...

def delete_related_assets(public_id, assets_to_unrelate, resource_type=..., type=..., **options):  # -> Response:
    """
    Unrelates an asset from other assets by public IDs.

    :param public_id: The public ID of the asset to update.
    :type public_id: str
    :param assets_to_unrelate: The array of up to 10 fully_qualified_public_ids given as resource_type/type/public_id.
    :type assets_to_unrelate: list[str]
    :param type: The upload type.
    :type type: str
    :param resource_type: The type of the resource: defaults to "image".
    :type resource_type: str
    :param options: Additional options.
    :type options: dict, optional
    :return: The result of the command.
    :rtype: dict
    """
    ...

def delete_related_assets_by_asset_ids(asset_id, assets_to_unrelate, **options):  # -> Response:
    """
    Unrelates an asset from other assets by asset IDs.

    :param asset_id: The asset ID of the asset to update.
    :type asset_id: str
    :param assets_to_unrelate: The array of up to 10 asset IDs.
    :type assets_to_unrelate: list[str]
    :param options: Additional options.
    :type options: dict, optional
    :return: The result of the command.
    :rtype: dict
    """
    ...

def tags(**options):  # -> Response:
    ...
def transformations(**options):  # -> Response:
    ...
def transformation(transformation, **options):  # -> Response:
    ...
def delete_transformation(transformation, **options):  # -> Response:
    ...
def update_transformation(transformation, **options):  # -> Response:
    ...
def create_transformation(name, definition, **options):  # -> Response:
    ...
def publish_by_ids(public_ids, **options):  # -> Response:
    ...
def publish_by_prefix(prefix, **options):  # -> Response:
    ...
def publish_by_tag(tag, **options):  # -> Response:
    ...
def upload_presets(**options):  # -> Response:
    ...
def upload_preset(name, **options):  # -> Response:
    ...
def delete_upload_preset(name, **options):  # -> Response:
    ...
def update_upload_preset(name, **options):  # -> Response:
    ...
def create_upload_preset(**options):  # -> Response:
    ...
def root_folders(**options):  # -> Response:
    ...
def subfolders(of_folder_path, **options):  # -> Response:
    ...
def create_folder(path, **options):  # -> Response:
    ...
def rename_folder(from_path, to_path, **options):  # -> Response:
    """
    Renames folder

    :param from_path: The full path of an existing asset folder.
    :param to_path:   The full path of the new asset folder.
    :param options:   Additional options

    :rtype: Response
    """
    ...

def delete_folder(path, **options):  # -> Response:
    """Deletes folder

    Deleted folder must be empty, but can have descendant empty sub folders

    :param path: The folder to delete
    :param options: Additional options

    :rtype: Response
    """
    ...

def restore(public_ids, **options):  # -> Response:
    ...
def upload_mappings(**options):  # -> Response:
    ...
def upload_mapping(name, **options):  # -> Response:
    ...
def delete_upload_mapping(name, **options):  # -> Response:
    ...
def update_upload_mapping(name, **options):  # -> Response:
    ...
def create_upload_mapping(name, **options):  # -> Response:
    ...
def list_streaming_profiles(**options):  # -> Response:
    ...
def get_streaming_profile(name, **options):  # -> Response:
    ...
def delete_streaming_profile(name, **options):  # -> Response:
    ...
def create_streaming_profile(name, **options):  # -> Response:
    ...
def update_streaming_profile(name, **options):  # -> Response:
    ...
def only(source, *keys):  # -> dict[Any, Any]:
    ...
def transformation_string(transformation):  # -> str | LiteralString:
    ...
def list_metadata_fields(**options):  # -> Response:
    """Returns a list of all metadata field definitions

    See: `Get metadata fields API reference <https://cloudinary.com/documentation/admin_api#get_metadata_fields>`_

    :param options: Additional options

    :rtype: Response
    """
    ...

def metadata_field_by_field_id(field_external_id, **options):  # -> Response:
    """Gets a metadata field by external id

    See: `Get metadata field by external ID API reference
    <https://cloudinary.com/documentation/admin_api#get_a_metadata_field_by_external_id>`_

    :param field_external_id: The ID of the metadata field to retrieve
    :param options: Additional options

    :rtype: Response
    """
    ...

def add_metadata_field(field, **options):  # -> Response:
    """Creates a new metadata field definition

    See: `Create metadata field API reference <https://cloudinary.com/documentation/admin_api#create_a_metadata_field>`_

    :param field: The field to add
    :param options: Additional options

    :rtype: Response
    """
    ...

def update_metadata_field(field_external_id, field, **options):  # -> Response:
    """Updates a metadata field by external id

    Updates a metadata field definition (partially, no need to pass the entire
    object) passed as JSON data.

    See `Generic structure of a metadata field
    <https://cloudinary.com/documentation/admin_api#generic_structure_of_a_metadata_field>`_ for details.

    :param field_external_id: The id of the metadata field to update
    :param field: The field definition
    :param options: Additional options

    :rtype: Response
    """
    ...

def delete_metadata_field(field_external_id, **options):  # -> Response:
    """Deletes a metadata field definition.
    The field should no longer be considered a valid candidate for all other endpoints

    See: `Delete metadata field API reference
    <https://cloudinary.com/documentation/admin_api#delete_a_metadata_field_by_external_id>`_

    :param field_external_id: The external id of the field to delete
    :param options: Additional options

    :return: An array with a "message" key. "ok" value indicates a successful deletion.
    :rtype: Response
    """
    ...

def delete_datasource_entries(field_external_id, entries_external_id, **options):  # -> Response:
    """Deletes entries in a metadata field datasource

    Deletes (blocks) the datasource entries for a specified metadata field
    definition. Sets the state of the entries to inactive. This is a soft delete,
    the entries still exist under the hood and can be activated again with the
    restore datasource entries method.

    See: `Delete entries in a metadata field datasource API reference
    <https://cloudinary.com/documentation/admin_api#delete_entries_in_a_metadata_field_datasource>`_

    :param field_external_id: The id of the field to update
    :param  entries_external_id: The ids of all the entries to delete from the
                                 datasource
    :param options: Additional options

    :rtype: Response
    """
    ...

def update_metadata_field_datasource(field_external_id, entries_external_id, **options):  # -> Response:
    """Updates a metadata field datasource

    Updates the datasource of a supported field type (currently only enum and set),
    passed as JSON data. The update is partial: datasource entries with an
    existing external_id will be updated and entries with new external_id's (or
    without external_id's) will be appended.

    See: `Update a metadata field datasource API reference
    <https://cloudinary.com/documentation/admin_api#update_a_metadata_field_datasource>`_

    :param field_external_id: The external id of the field to update
    :param entries_external_id:
    :param options: Additional options

    :rtype: Response
    """
    ...

def restore_metadata_field_datasource(field_external_id, entries_external_ids, **options):  # -> Response:
    """Restores entries in a metadata field datasource

    Restores (unblocks) any previously deleted datasource entries for a specified
    metadata field definition.
    Sets the state of the entries to active.

    See: `Restore entries in a metadata field datasource API reference
    <https://cloudinary.com/documentation/admin_api#restore_entries_in_a_metadata_field_datasource>`_

    :param field_external_id: The ID of the metadata field
    :param entries_external_ids: An array of IDs of datasource entries to restore
                                 (unblock)
    :param options: Additional options

    :rtype: Response
    """
    ...

def reorder_metadata_field_datasource(field_external_id, order_by, direction=..., **options):  # -> Response:
    """Reorders metadata field datasource. Currently, supports only value.

    :param field_external_id: The ID of the metadata field.
    :param order_by: Criteria for the order. Currently, supports only value.
    :param direction: Optional (gets either asc or desc).
    :param options: Additional options.

    :rtype: Response
    """
    ...

def reorder_metadata_fields(order_by, direction=..., **options):  # -> Response:
    """Reorders metadata fields.

    :param order_by: Criteria for the order (one of the fields 'label', 'external_id', 'created_at').
    :param direction: Optional (gets either asc or desc).
    :param options: Additional options.

    :rtype: Response
    """
    ...

def analyze(input_type, analysis_type, uri=..., **options):  # -> Response:
    """Analyzes an asset with the requested analysis type.

    :param input_type: The type of input for the asset to analyze ('uri').
    :param analysis_type: The type of analysis to run ('google_tagging', 'captioning', 'fashion').
    :param uri: The URI of the asset to analyze.
    :param options: Additional options.

    :rtype: Response
    """
    ...
