$('#load').on('click', function () {
    var $this = $(this);
    $this.button('loading');
});

$(document).ready(function () {
    $('#preview-tweet').popover({trigger: "hover"});
});