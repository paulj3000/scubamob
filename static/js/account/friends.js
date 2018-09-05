function getId(elem)
{
    return $(elem).attr('id').replace('friend_request_', '');
}

function moveElement(elem, fid)
{
    $(elem).clone().appendTo('#friend_list');
    $(elem).remove();
    console.log($('#f_menu_' + fid));

    $('#f_menu_' + fid).remove();
}

function removeElement(elem, fid)
{
    $(elem).fadeOut();
}

function comm(t, fid, opt)
{
    //elem    = $(t).closest('li');
    //fid  = getId(elem);
    opt['fid']  = fid;

    console.log(opt);
    $.ajax({
        url: '/account/friends/request/accept',
        type: "POST",
        data: opt,
        }).done(function(data) {
            location.href   = '/account/friends';
           // fn(elem, fid);
        }).fail(function() { console.log("error"); });
}

function init_friends_index()
{
    $('.ignore').click(function()
    {
        id  = $(this).attr('id');
        comm(this, id, { 'delete': true });
    });

    $('.accept').click(function()
    {
        id  = $(this).attr('id');
        comm(this, id, {});
    });
}
