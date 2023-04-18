# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path, re_path
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

import scuba.divesites.models as divesites_models
from scuba.divesites.models import Divesite
from scuba.divesites.serializers import DivesiteSerializer


class DivesiteAdmin(admin.ModelAdmin):
    list_display = ('name', 'lat', 'long', 'difficulty', 'query_weather')
    change_list_template = 'admin/divesites/change_divesite_list.html'
    change_form_template = 'admin/divesites/change_divesite_form.html'
    readonly_fields = ['url']

    def get_urls(self):
        """ get_urls

        Add a couple of urls to the program admin. These will mostly
        be used to handle all ajax / api requests
        """
        urls = super().get_urls()
        my_urls = [
            path('all', self.get_all_divesites),
            re_path(r'^(?P<divesiteid>[0-9A-Fa-f-]{1,36})/addbanner/$',
                self.admin_site.admin_view(self.upload_banner),
                name='ajax_upload_banner'),
            ]

        # add the new url strings to the program stuff
        return my_urls + urls

    def get_all_divesites(self, request):
        """ updateprogramtime

        Set the program time of a poraticular file
        """
        retval = DivesiteSerializer(divesites_models.Divesite.objects.all(), many=True)
        return JsonResponse({'sites': retval.data})

    @csrf_exempt
    def upload_banner(self, request, divesiteid):
        """ updateprogramtime

        Set the program time of a poraticular file
        """
        divesite = get_object_or_404(Divesite, id=divesiteid)
        divesite.upload_banner(request.FILES['newbanner'])
        return JsonResponse({'images': 'program.get_active_banner()'})


class DivesiteDailyStatsAdmin(admin.ModelAdmin):
    list_display = ('divesite', 'temp_c', 'visibility', 'stats_date')


admin.site.register(divesites_models.Divesite, DivesiteAdmin)
admin.site.register(divesites_models.DivesiteReview)
admin.site.register(divesites_models.DivesiteDailyStats, DivesiteDailyStatsAdmin)
