$(document).ready(function () {
    $("#seacrh").on("keyup", function () {
        var value = $(this).val().toLowerCase();
        $("#myTable tr").filter(function () {
            $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
        });
    });
});


// $(document).ready(function () {
//
//     $(".searchKey").keyup(function () {
//         let searchTerm = $(".searchKey").val().replace(/["']/g, "");
//         let arr = searchTerm.split(/(AND|OR)/);
//         let exprs = createExpr(arr);
//         let searchSplit = searchTerm.replace(/AND/g, "'):containsiAND('").replace(/OR/g, "'):containsiOR('");
//
//         $.extend($.expr[':'], {
//             'containsiAND': function (element, i, match, array) {
//                 return (element.textContent || element.innerText || '').toLowerCase().indexOf((match[3] || "").toLowerCase()) >= 0;
//             }
//         });
//
//         $('.results tbody tr').attr('visible', 'false');
//         for (var expr in exprs) {
//             $(".results tbody tr" + exprs[expr]).each(function (e) {
//                 $(this).attr('visible', 'true');
//             });
//         }
//
//         var searchCount = $('.results tbody tr[visible="true"]').length;
//
//         $('.searchCount').text('найдено ' + searchCount + ' человек');
//         if (searchCount == '0') {
//             $('.no-result').show();
//         } else {
//             $('.no-result').hide();
//         }
//         if ($('.searchKey').val().length == 0) {
//             $('.searchCount').hide();
//         } else {
//             $('.searchCount').show();
//         }
//     });
// });