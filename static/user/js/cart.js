function calculateRowTotal() {
    $(".invoicerow").each(function() {
        console.log('in in');
        var row = $(this);
        var quantity = parseFloat(row.find(".quantity").val()) || 0;
        var price = parseFloat(row.find(".price").val()) || 0;
        var total = quantity * price;
        row.find(".total").val(total);
    });
}

$(document).ready(function(){
    calculateRowTotal();
});

