# -*- coding: utf-8 -*-
from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

import scuba.divesites.models as divesites_models
from scuba.divesites.serializers import DivesiteSerializer


class DivesiteAdmin(admin.ModelAdmin):
    change_list_template = 'admin/divesites/change_list.html'
    readonly_fields = ['url']

    def get_urls(self):
        """ get_urls

        Add a couple of urls to the program admin. These will mostly
        be used to handle all ajax / api requests
        """
        urls = super().get_urls()
        my_urls = [
            path('all',
                self.get_all_divesites),
            ]

        # add the new url strings to the program stuff
        return my_urls + urls

    def get_all_divesites(self, request):
        """ updateprogramtime

        Set the program time of a poraticular file
        """
        retval = DivesiteSerializer(divesites_models.Divesite.objects.all(), many=True)
        return JsonResponse({'sites': retval.data})


admin.site.register(divesites_models.Divesite, DivesiteAdmin)
