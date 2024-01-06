from django.shortcuts import render
from django.core.context_processors import csrf
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from diveshops.forms import DiveShopAddressForm


@login_required
def packages(us_request):
    # render the appropriate template
    context = {}
    return render(us_request, 'diveshops/packages.html', context)


@login_required
def editshop(us_request):
    # render the appropriate template

    shop_form = None
    if us_request.method == 'POST':
        shop_form = DiveShopAddressForm(us_request.POST, user_id=us_request.user.id)

        if shop_form.is_valid():
            messages.add_message(us_request, messages.INFO, 'Shop successfully saved')
            shop_form.save()
    else:
        shop_form = DiveShopAddressForm(user_id=us_request.user.id)

    context = {'shop_form': shop_form}

    context.update(csrf(us_request))
    return render(us_request, 'diveshops/createshop.html', context)
