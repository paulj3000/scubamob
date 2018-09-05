createAlbum = function()
{
    serializedData  = $('#f_createalbum').serialize();

    $.post('/gallery/json/createalbum', serializedData, function(data)
    {
        html    = $('#album_template').html();
        $('#album').append(Mustache.render(html, data));
    });

    $("#dialog-form").dialog( "close" );
}
