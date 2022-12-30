function update_favourite(element){
    let productID = element.data("product"),
        star = element.find("img.star"),
        noStar = element.find("img.no-star");

        if (star.hasClass("d-none")) {
            action = "add"
        } else {
            action = "remove"
        }

        func_data = {
            "product": productID,
            "action": action
        }

    $(function () {
        $.ajaxSetup({
            headers: { "X-CSRFToken": getCookie("csrftoken") }
        });
    });
    $.post(
        `/products/ajax-${action}-favorite/`,
        data=func_data,
        function (data) {
            if (data.form_valid == true) {
                if (data.action == "add") {
                    star.removeClass("d-none")
                    noStar.addClass("d-none")
                } else {
                    star.addClass("d-none")
                    noStar.removeClass("d-none")
                }
            }
        }
    ).fail(function (error) {
        console.log(error);
    });
}