function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


var csrfToken = getCookie('csrftoken');

$('#check_pincode').click(function() {
    var pincode = $('#pincode').val();
    console.log(pincode);
    $.ajax({
        url: '/pincode_details/',
        type: "POST",
        data: {
            'pincode': pincode,
        },
        dataType: 'json',
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function(response) {
            var dist = response.dist;
            var state = response.state;
            console.log(dist, state);
            $('#district').val(dist);
            $('#state').val(state);

        },
        error: function(error) {
            alert('Error fetching city:', error);
        }
    });
});