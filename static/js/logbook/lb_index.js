SM.logbook.folders  = {};

SM.logbook.folders.create                   = function()
{
    dlg = $('#filterdlgtempl').html();
    showDialog('New Folder', [{ text: dlg }], 
        { 'fnok': function(dlg) {
                var foldername  = $('#filterdlg').find('#foldername').val();

                // get the foldername.  if a foldername was not set, return false
                if (! foldername)   return false;

                $.ajax({
                    type: 'POST',
                    contentType: 'application/json; charset=utf-8',
                    url: "/logbook/json/logbookfolders", 
                    data: JSON.stringify({ foldername: foldername}), 
                    dataType: 'json',
                    success: function(data)
                    {
                        SM.logbook.displayFolders(data.folders);
                        $(dlg).dialog('destroy').remove();
                    }
                });
            }
        })
}

SM.logbook.clearResults    = function()
{
    $('#lb-results').empty();
}

SM.logbook.openFolder        = function(id)
{
    $.get('/logbook/json/logbookfolderlogs', { id: id }, function(data)
    {
        SM.logbook.clearResults();
        var ftl = $('#subfoldertempl').html(); 
        $(Mustache.render(ftl, data )).appendTo('#lb-results');
    });
}

SM.logbook.displayFolders    = function(folders)
{
    // let's clear out the old results
    SM.logbook.clearResults();

    var ftl = $('#foldertempl').html(); 
    $(Mustache.render(ftl, { folders: folders })).appendTo('#lb-results');
}

SM.logbook.headers.refreshAssets    = function()
{
    SM.logbook.getAssets(function(data)
    {
        SM.logbook.displayFolders(data.folders);
    });
}


SM.logbook.headers.toggleFolders    = function()
{
    var fhm = $('#foldersHeaderMenu');
    if ( fhm.is(":visible") ) 
    {
        fhm.empty().hide();
    }
    else
    {
        SM.logbook.getAssets(function(data)
        {
            filtertempl = $('#filtertempl').html();
            console.log(filtertempl);

            $(Mustache.render(filtertempl)).appendTo('#foldersHeaderMenu');
            fhm.show();
        });
    }
}

SM.logbook.getAssets    = function(fn)
{
    $.get('/logbook/json/logbookfolders', fn);
}


SM.logbook.headers.toggleTags    = function()
{
    alert("hello");
}
