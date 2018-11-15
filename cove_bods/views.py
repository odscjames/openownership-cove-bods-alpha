import json
import logging
import os
import re
import functools
from dateutil import parser
from strict_rfc3339 import validate_rfc3339
from decimal import Decimal

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.utils import translation
from django.utils.html import format_html

from libcovebods.common_checks import common_checks_bods
from libcovebods.schema import SchemaBODS
from libcovebods.config import LibCoveBODSConfig
from libcove.lib.common import get_spreadsheet_meta_data
from libcove.lib.converters import convert_spreadsheet, convert_json
from libcove.lib.exceptions import CoveInputDataError
from cove.views import explore_data_context


logger = logging.getLogger(__name__)


def cove_web_input_error(func):
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        try:
            return func(request, *args, **kwargs)
        except CoveInputDataError as err:
            return render(request, 'error.html', context=err.context)
    return wrapper


@cove_web_input_error
def explore_bods(request, pk):
    context, db_data, error = explore_data_context(request, pk)
    if error:
        return error

    lib_cove_bods_config = LibCoveBODSConfig()

    upload_dir = db_data.upload_dir()
    upload_url = db_data.upload_url()
    file_name = db_data.original_file.file.name
    file_type = context['file_type']

    replace = False
    validation_errors_path = os.path.join(upload_dir, 'validation_errors-3.json')

    if file_type == 'json':
        # open the data first so we can inspect for record package
        with open(file_name, encoding='utf-8') as fp:
            try:
                json_data = json.load(fp, parse_float=Decimal)
            except ValueError as err:
                raise CoveInputDataError(context={
                    'sub_title': _("Sorry, we can't process that data"),
                    'link': 'index',
                    'link_text': _('Try Again'),
                    'msg': _(format_html('We think you tried to upload a JSON file, but it is not well formed JSON.'
                             '\n\n<span class="glyphicon glyphicon-exclamation-sign" aria-hidden="true">'
                             '</span> <strong>Error message:</strong> {}', err)),
                    'error': format(err)
                })

            if not isinstance(json_data, list):
                raise CoveInputDataError(context={
                    'sub_title': _("Sorry, we can't process that data"),
                    'link': 'index',
                    'link_text': _('Try Again'),
                    'msg': _('BODS JSON should have an list as the top level, the JSON you supplied does not.'),
                })

            schema_bods = SchemaBODS(lib_cove_bods_config=lib_cove_bods_config)

    else:
        raise CoveInputDataError(context={
            'sub_title': _("Sorry, we can't process that data"),
            'link': 'index',
            'link_text': _('Try Again'),
            'msg': _('We only do JSON so far'),
        })

    context = common_checks_bods(context, upload_dir, json_data, schema_bods)

    template = 'cove_bods/explore.html'

    return render(request, template, context)
