"""
This type stub file was generated by pyright.
"""

from urllib3.contrib.appengine import is_appengine_sandbox

if is_appengine_sandbox():
    _http = ...
else:
    _http = ...
upload_options = ...
UPLOAD_LARGE_CHUNK_SIZE = ...

def upload(file, **options):  # -> Any:
    ...
def unsigned_upload(file, upload_preset, **options):  # -> Any:
    ...
def upload_image(file, **options):  # -> CloudinaryImage:
    ...
def upload_resource(file, **options):  # -> CloudinaryResource:
    ...
def upload_large(file, **options):  # -> Any | None:
    """Upload large files."""
    ...

def upload_large_part(file, **options):  # -> Any:
    """Upload large files."""
    ...

def destroy(public_id, **options):  # -> Any:
    ...
def rename(from_public_id, to_public_id, **options):  # -> Any:
    ...
def update_metadata(metadata, public_ids, **options):  # -> Any:
    """
    Populates metadata fields with the given values. Existing values will be overwritten.

    Any metadata-value pairs given are merged with any existing metadata-value pairs
    (an empty value for an existing metadata field clears the value)

    :param metadata: A list of custom metadata fields (by external_id) and the values to assign to each
                     of them.
    :param public_ids: An array of Public IDs of assets uploaded to Cloudinary.
    :param options: Options such as
            *resource_type* (the type of file. Default: image. Valid values: image, raw, or video) and
            *type* (The storage type. Default: upload. Valid values: upload, private, or authenticated.)

    :return: A list of public IDs that were updated
    :rtype: mixed
    """
    ...

def explicit(public_id, **options):  # -> Any:
    ...
def create_archive(**options):  # -> Any:
    ...
def create_zip(**options):  # -> Any:
    ...
def generate_sprite(tag=..., urls=..., **options):  # -> Any:
    """
    Generates sprites by merging multiple images into a single large image.

    See: `Sprite method API reference
    <https://cloudinary.com/documentation/image_upload_api_reference#sprite_method>`_

    :param tag:     The sprite is created from all images with this tag. If not set - `urls` parameter is required
    :type tag:      str
    :param urls:    List of URLs to create a sprite from. Can only be used if `tag` is not set
    :type urls:     list
    :param options: Additional options
    :type options:  dict, optional
    :return:        Dictionary with meta information URLs of generated sprite resources
    :rtype:         dict
    """
    ...

def download_generated_sprite(tag=..., urls=..., **options):  # -> str:
    """
    Returns signed URL for the sprite endpoint with `mode=download`

    :param tag:     The sprite is created from all images with this tag. If not set - `urls` parameter is required
    :type tag:      str
    :param urls:    List of URLs to create a sprite from. Can only be used if `tag` is not set
    :type urls:     list
    :param options: Additional options
    :type options:  dict, optional
    :return:        The signed URL to download sprite
    :rtype:         str
    """
    ...

def multi(tag=..., urls=..., **options):  # -> Any:
    """
    Creates either a single animated image, video or a PDF.

    See: `Upload method API reference
    <https://cloudinary.com/documentation/image_upload_api_reference#multi_method>`_

    :param tag:     The animated image, video or PDF is created from all images with this tag.
                    If not set - `urls` parameter is required
    :type tag:      str
    :param urls:    List of URLs to create an animated image, video or PDF from. Can only be used if `tag` is not set
    :type urls:     list
    :param options: Additional options
    :type options:  dict, optional
    :return:        Dictionary with meta information URLs of the generated file
    :rtype:         dict
    """
    ...

def download_multi(tag=..., urls=..., **options):  # -> str:
    """
    Returns signed URL for the multi endpoint with `mode=download`

    :param tag:     The sprite is created from all images with this tag. If not set - `urls` parameter is required
    :type tag:      str
    :param urls:    List of URLs to create a sprite from. Can only be used if `tag` is not set
    :type urls:     list
    :param options: Additional options
    :type options:  dict, optional
    :return:        The signed URL to download multi
    :rtype:         str
    """
    ...

def explode(public_id, **options):  # -> Any:
    ...
def add_tag(tag, public_ids=..., **options):  # -> Any:
    """
    Adds a single tag or a list of tags or a comma-separated tags to the assets.

    :param tag:         The tag or tags to assign. Can specify multiple tags in a single string,
                        separated by commas - "t1,t2,t3" or list of tags - ["t1","t2","t3"].
    :param public_ids:  A list of public IDs (up to 1000).
    :param options:     Configuration options may include 'exclusive' (boolean) which causes
                        clearing this tag from all other assets.

    :return:            Dictionary with a list of public IDs that were updated.
    """
    ...

def remove_tag(tag, public_ids=..., **options):  # -> Any:
    """
    Removes a single tag or a list of tags or a comma-separated tags from the assets.

    :param tag:         The tag or tags to assign. Can specify multiple tags in a single string,
                        separated by commas - "t1,t2,t3" or list of tags - ["t1","t2","t3"].
    :param public_ids:  A list of public IDs (up to 1000).
    :param options:     Additional options.

    :return:            Dictionary with a list of public IDs that were updated.
    """
    ...

def replace_tag(tag, public_ids=..., **options):  # -> Any:
    """
    Replaces all existing tags with a single tag or a list of tags or a comma-separated tags of the assets.

    :param tag:         The tag or tags to assign. Can specify multiple tags in a single string,
                        separated by commas - "t1,t2,t3" or list of tags - ["t1","t2","t3"].
    :param public_ids:  A list of public IDs (up to 1000).
    :param options:     Additional options.

    :return:            Dictionary with a list of public IDs that were updated.
    """
    ...

def remove_all_tags(public_ids, **options):  # -> Any:
    """
    Remove all tags from the specified public IDs.

    :param public_ids: the public IDs of the resources to update
    :param options: additional options passed to the request

    :return: dictionary with a list of public IDs that were updated
    """
    ...

def add_context(context, public_ids, **options):  # -> Any:
    """
    Add a context keys and values. If a particular key already exists, the value associated with the key is updated.

    :param context: dictionary of context
    :param public_ids: the public IDs of the resources to update
    :param options: additional options passed to the request

    :return: dictionary with a list of public IDs that were updated
    """
    ...

def remove_all_context(public_ids, **options):  # -> Any:
    """
    Remove all custom context from the specified public IDs.

    :param public_ids: the public IDs of the resources to update
    :param options: additional options passed to the request

    :return: dictionary with a list of public IDs that were updated
    """
    ...

def call_tags_api(tag, command, public_ids=..., **options):  # -> Any:
    ...
def call_context_api(context, command, public_ids=..., **options):  # -> Any:
    ...

TEXT_PARAMS = ...

def text(text, **options):  # -> Any:
    ...

_SLIDESHOW_PARAMS = ...

def create_slideshow(**options):  # -> Any:
    """
    Creates auto-generated video slideshows.

    :param options: The optional parameters.  See the upload API documentation.

    :return: a dictionary with details about created slideshow
    """
    ...

def call_cacheable_api(action, params, http_headers=..., return_error=..., unsigned=..., file=..., timeout=..., **options):  # -> Any:
    """
    Calls Upload API and saves results to cache (if enabled)
    """
    ...

def call_api(action, params, http_headers=..., return_error=..., unsigned=..., file=..., timeout=..., extra_headers=..., **options):  # -> Any:
    ...