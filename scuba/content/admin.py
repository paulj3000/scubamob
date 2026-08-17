from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from scuba.content.models import (
    FAQEntry, FAQSection, Image, Page, Article, ArticleVersion, NewsArticle)
from scuba.content.forms.admin import ImageForm


class PageAdmin(admin.ModelAdmin):
    change_form_template = 'admin/content/change_page_form.html'


class ImageAdmin(admin.ModelAdmin):
    form = ImageForm

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ['filename', 'title']
        else:
            return []

    def get_urls(self):
        """ get_urls

        Add a couple of urls to the program admin. These will mostly
        be used to handle all ajax / api requests
        """
        urls = super().get_urls()
        my_urls = [
            path(
                'list', admin.site.admin_view(self.get_image_list),
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


class ArticleVersionInline(admin.StackedInline):
    """ HomeCategoryInline

    Class representation of the home category inline pages necessary for
    the category admin
    """
    model = ArticleVersion
    extra = 0


class ArticleAdmin(admin.ModelAdmin):
    inlines = (ArticleVersionInline,)
    list_display = ('title', 'user', 'url',)
    exclude = ('url',)


class NewsArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'is_published', 'published_date')
    exclude = ('url',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user = request.user

        super().save_model(request, obj, form, change)


admin.site.register(Article, ArticleAdmin)
admin.site.register(NewsArticle, NewsArticleAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(FAQSection)
admin.site.register(FAQEntry, FAQEntryAdmin)
