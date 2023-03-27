from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, re_path
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q

from scuba.accounts.models import User
from scuba.content.models import (
    FAQEntry, FAQSection, FAQEntry, Image, Page, EmailTemplate, NewsArticle)
from scuba.content.forms.admin import ImageForm


class PageAdmin(admin.ModelAdmin):
    change_form_template = 'admin/content/change_page_form.html'

class EmailTemplateAdmin(admin.ModelAdmin):
    change_form_template = 'admin/content/change_email_template_form.html'

    def get_urls(self):
        """ get_urls

        adding some extra urls to the user model
        """
        urls = super().get_urls()

        my_urls = [
            re_path(r'^send_test_email/(?P<id>[0-9A-Fa-f-]{1,36})/send_test',
                self.send_test_email, name='send_test_email'),
        ]

        return my_urls + urls

    def send_test_email(modeladmin, request, id):
        """ send_test_email

        send test emails to the staff
        """
        email_template = get_object_or_404(EmailTemplate, pk=id)

        for user in User.objects.filter(
                Q(is_superuser=True) |
                Q(is_admin=True)):

            to_send_email = {
                2: user.send_confirmation_code_email
            }

            to_send_email[email_template.template_type](email_template)
            #user.send_confirmation_code_email(email_template, '123456')

        messages.add_message(
            request,
            messages.INFO,
            'Test message successfully sent'
        )

        # change appropriately
        return redirect('admin:content_emailtemplate_change', object_id=email_template.id)
        #f"/admin/content/emailtemplate/{str(email_template.id)}")


class ImageAdmin(admin.ModelAdmin):
    form = ImageForm

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['filename', 'title',]
        else: # This is an addition
            return []


    def get_urls(self):
        """ get_urls

        Add a couple of urls to the program admin. These will mostly
        be used to handle all ajax / api requests
        """
        urls = super().get_urls()
        my_urls = [
            path('list',admin.site.admin_view(self.get_image_list),
                name='get_image_list'),
        ]

        # add the new url strings to the program stuff
        return my_urls + urls

    def get_image_list(self, request):
        """ get_image_list

        Get a list of images from the server
        """
        retval = []
        # now circle over all of the images and get their
        # values
        for img in Image.objects.all().order_by('title'):
            retval.append({
                'title': img.title,
                'value': img.url,
            })

        return JsonResponse({'images': retval})

    list_display = ('title',)
    change_form_template = 'admin/content/change_image_form.html'


class FAQEntryAdmin(admin.ModelAdmin):
    """ FAQEntryAdmin

    Override some of the display elements for the admin display
    """
    list_display = ('title', 'position', 'faq_section',)
    #exclude = ('position',)
    change_form_template = 'sales/admin/change_faq_form.html'
    model = FAQEntry


class FAQEntryAdminInline(admin.StackedInline):
    """ HomeCategoryInline

    Class representation of the home category inline pages necessary for
    the category admin
    """
    model = FAQEntry
    extra = 0


class FAQSectionAdmin(admin.ModelAdmin):
    inlines = (FAQEntryAdminInline,)


class NewsArticleAdmin(admin.ModelAdmin):
    change_form_template = 'admin/content/change_news_admin_form.html'


admin.site.register(Page, PageAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(FAQSection)
admin.site.register(EmailTemplate, EmailTemplateAdmin)
admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(FAQEntry, FAQEntryAdmin)
