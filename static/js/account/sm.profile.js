"use strict";
SM.account  = { 'profile': {} };

SM.account.profile.addfriend                = function(obj)
{
    var fid = obj.getAttribute('data-id'); 
    console.log(fid);
    $.doAjaxPut('/friends/ajax/addfriend/', { fid: fid }, 
                function(data)
                {
                    var tmpl    = $('#friendrequested').html();
                    $('.frnd.ctr').html(tmpl);
                    $('.friend.cancel').click(function()    { SM.account.profile.cancelRequest(this) });
                });
}

SM.account.profile.blockfriend             = function(obj)
{
    if (! confirm("Are you sure you want to block this person?"))
    {
        return;
    }
    var fid = obj.getAttribute('data-id'); 
    $.doAjaxPut('/friends/ajax/blockfriend/', { fid: fid }, 
                function(data)
                {
                    location.href='/home';
                });
}

SM.account.profile.cancelRequest             = function(obj)
{
    if (! confirm("Are you sure you want to cancel this request?"))
    {
        return;
    }

    var fid = obj.getAttribute('data-id'); 
    $.doAjaxDelete('/friends/ajax/cancelrequest/', { fid: fid }, 
                function(data)
                {
                    location.href='/home';
                });
}

SM.account.profile.init                 = function()
{
    var tmpl    = '';
    if (requestId)
        tmpl    = $('#friendrequested').html();
    else if (friendId)
        tmpl    = $('#isfriend').html();
    else
        tmpl    = $('#requestfriendship').html();
       // tmpl    = $('#friendrequest').html();

    console.log(tmpl);

    $('.frnd.ctr').html(tmpl);

    $('.friend.add').click(function()       { SM.account.profile.addfriend(this) });
    $('.friend.block').click(function()     { SM.account.profile.blockfriend(this) });
    $('.friend.cancel').click(function()    { SM.account.profile.cancelRequest(this) });
}
