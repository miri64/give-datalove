$(document).ready(function() {
    // AJAX Login
    $("#login_box").submit(function(event) {
        var form = $(this);
        var data = form.serialize();
        var action = form.find("input[name=ajax_action]").val();
        var next = form.find("input[name=next]").val();

        $.post(action, data, function(errors) {
            if (errors) {
                form.find("* :input").each(function(i) {
                    var selector = "ul#"+$(this).attr("name")+"-errors"
                    form.find("ul#"+$(this).attr("name")+"-errors").remove();
                })
                form.find("ul#login-all-errors").remove();
                for (var field in errors) {
                    var errorlist = '<ul id="login-' + field + 
                            '-errors" class="errorlist"></ul>';
                    if (field == 'all') {
                        form.append(errorlist);
                    } else {
                        form.find("input#id_login-"+field+"+br")
                                .after(errorlist);
                    }
                    for (var i in errors[field]) {
                        var selector = "ul#login-"+field+"-errors"
                        form.find(
                                "ul#login-"+field+"-errors"
                            ).append('<li>'+errors[field][i]+'</li>')
                    } 
                }
            } else {
                window.location.replace(next);
            }
        }).error(function(response) {
            $('html').html(response.responseText);
        });

        return false;
    })
})
