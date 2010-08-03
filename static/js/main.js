jQuery(document).ready(function($) {
    $('a[rel*=facebox]').facebox({
        loadingImage : '/static/i/loading.gif',
        closeImage   : '/static/i/closelabel.gif'
    });

    $('#bikes').masonry({ singleMode: true });
});


