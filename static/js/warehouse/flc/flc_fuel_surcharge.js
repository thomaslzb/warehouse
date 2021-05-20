//如果有输入， 清除错误提示
$("#myModal-fuel-surcharge").on("keyup", "#code", function () {
    console.log("code coming in ")
    $('#code_fail').html('')
})

//如果有输入， 清除错误提示
$("#myModal-fuel-surcharge").on("keyup", "#name", function () {
    console.log("name coming in ")
    $('#name_fail').html('')
})

$(function () {
    // 设置弹出提示框属性
    toastr.options = {
        closeButton: true,
        debug: true,
        progressBar: true,
        positionClass: "toast-top-center",
        onclick: null,
        showDuration: "1000",
        hideDuration: "5000",
        timeOut: "2000",
        extendedTimeOut: "1000",
        showEasing: "swing",
        hideEasing: "linear",
        showMethod: "fadeIn",
        hideMethod: "fadeOut"
    };

    let loadForm = function() {
        let btn = $(this);
        console.log('load fuel Form modal ...')
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#myModal-fuel-surcharge").modal("show");
            },
            success: function (data) {
                $("#myModal-fuel-surcharge .modal-content").html(data.html_form);
            }
        })
    };

    let saveForm = function () {
        let form = $(this);
        console.log('save fuel Form modal ...')
        console.log('url ...'+form.attr("action"))
        $.ajax({
          url: form.attr("action"),
          data: form.serialize(),
          type: form.attr("method"),
          dataType: 'json',
          cache: false,
          async: false,
          success: function (data) {
              if (data.form_is_valid) {
                  //console.log('Submit Button Success and form is valid ...')
                  $("#myModal-fuel-surcharge").modal("hide");  // <-- Close the modal

                  // 刷新表格数据
                  $('#fuel-surcharge-table tbody').html(data.html_fuel_list);
                  // 正确提示
                  toastr.success('Data Save Successfully...');

              } else {
                  // 正确提示
                  toastr.warning('Data have some error ...');
                  //console.log('Submit Button Success and form is no valid ...')
                  $("#myModal-fuel-surcharge .modal-content").html(data.html_form);
              }
          },
        });
        return false
    };
    // 建立新的燃油费
    $(".js_create_fuel_surcharge").click(loadForm);
    $("#myModal-fuel-surcharge").on("submit", ".js-fuel-create-form", saveForm);

    // 编辑燃油费
    $("#fuel-surcharge-table").on("click", ".js-update-fuel-surcharge", loadForm);
    $("#myModal-fuel-surcharge").on("submit", ".js-fuel-update-form", saveForm);

});
