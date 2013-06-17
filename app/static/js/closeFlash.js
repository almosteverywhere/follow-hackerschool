;(function () {
    window.onload = function () {
        var flash = document.getElementById('flash');
        window.setTimeout(function () {
            flash.parentNode.removeChild(flash);
        }, 2000);
    }
})();