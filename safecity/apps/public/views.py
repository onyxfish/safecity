import json
import logging
log = logging.getLogger("safecity.public.views")

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template.loader import render_to_string

from safecity.apps.danger.models import Report

def index(request):
    """
    Render the index page that displays anonymized data for public
    consumption.
    """
    map_center = ('41.88', '-87.76')
    
    reports = []
    
    for report in Report.objects.all()[:2]:
        reports.append({
            'lat': report.location.y,
            'lon': report.location.x,
            'desc': report.text
        })
        
    print reports
    
    context = {
        'settings': settings,
        'index_js': render_to_string('public/index.js'),
        'map_center': map_center,
        'reports_json': json.dumps(reports),
    }
    
    return render_to_response(
        'public/index.html',
        context)