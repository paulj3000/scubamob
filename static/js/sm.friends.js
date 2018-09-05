"use strict";
SM.friends  = { 'index': {} };

SM.friends.index.friendresponse                = function(obj, mode)
{
    var fid = obj.getAttribute('data-id'); 
    cr.doAjaxPut('/friends/ajax/acceptrequest/', { fid: fid, mode: mode }, 
                function(data)
                {
//                    var tmpl    = $('#friendrequested').html();
//                   $('.frnd.ctr').html(tmpl);
                });
}

SM.friends.index.init                 = function()
{
    $('.friend.accept').click(function()   { SM.friends.index.friendresponse(this, 'add') });
    $('.friend.ignore').click(function()   { SM.friends.index.friendresponse(this, 'ignore') });
    $('.friend.unblock').click(function()   { SM.friends.index.friendresponse(this, 'unblock') });
}
