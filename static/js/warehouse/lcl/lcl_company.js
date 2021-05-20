// function add_company(){
//     console.log('begin add ...')
//     let $form = $('#add_company_form');
//     $.ajax({
//         //几个参数需要注意一下
//         cache:false,             //设置为false将不会从浏览器缓存中加载请求信息
//         type: "POST",            //方法类型
//         dataType: "json",        //预期服务器返回的数据类型
//         url: "add/" ,            //url
//         data: $form.serialize(), //将模态框的form表单数据序列化，以便提交到后台
//         async:false,             //必须要为false, 要求为Boolean类型的参数，默认设置为true，所有请求均为异步请求。
//                                  // 如果需要发送同步请求，请将此选项设置为false。注意，同步请求将锁住浏览器，
//                                  // 用户其他操作必须等待请求完成才可以执行。
//
//         success: function (data) {
//             console.log(data);  //打印服务端返回的数据(调试用)
//             console.log(data.status);  //打印服务端返回的数据(调试用)
//             console.log('============================');  //打印服务端返回的数据(调试用)
//             if(data.status==="success"){
//                 // 关闭模态框并清除框内数据，否则下次打开还是上次的数据
//                 document.getElementById("add_company_form").reset();
//
//                 // 正确提示
//                 toastr.success('Data Save Successfully...');
//
//                 // 刷新表格数据
//                 document.getElementById("btn_search").click();
//              }else if(data.status === "fail"){
//                 console.log("#################"+data.msg.code[0]);
//
//                 $('#code_fail').html(data.msg.code[0]);
//                 console.log('error ============== 0000000000000000000000000')
//                 document.getElementById("add_new_Company").click()
//                 console.log('error ============== clicked')
//
//             }
//          },
//         error : function(error) {
//             //toastr.warning("Some data need to be input....");
//          },
//     })
// }

//如果有输入， 清除错误提示
$("#myModal-company").on("keyup", "#code", function () {
    console.log("code coming in ")
    $('#code_fail').html('')
})

//如果有输入， 清除错误提示
$("#myModal-company").on("keyup", "#name", function () {
    console.log("name coming in ")
    $('#name_fail').html('')
})


// $("#name").bind('input propertychange', function () {
//     console.log("name coming in ")
//     $('#name_fail').html('')
// })


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
        console.log('load Company Form modal ...')
        console.log(btn.attr("data-url"))
        $.ajax({
            url: btn.attr("data-url"),
            type: 'get',
            dataType: 'json',
            beforeSend: function () {
                $("#myModal-company").modal("show");
            },
            success: function (data) {
                $("#myModal-company .modal-content").html(data.html_form);
            }
        })
    };

    let saveForm = function () {
        let form = $(this);
        console.log('save Company Form modal ...')
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
                  $("#myModal-company").modal("hide");  // <-- Close the modal

                  // 刷新表格数据
                  $('#company-table tbody').html(data.html_company_list);
                  // 正确提示
                  toastr.success('Data Save Successfully...');

              } else {
                  // 正确提示
                  toastr.warning('Data have some error ...');
                  //console.log('Submit Button Success and form is no valid ...')
                  $("#myModal-company .modal-content").html(data.html_form);
              }
          },
        });
        return false
    };
    // 建立新的公司
    $(".js_create_company").click(loadForm);
    $("#myModal-company").on("submit", ".js-company-create-form", saveForm);

    // 编辑公司
    $("#company-table").on("click", ".js-update-company", loadForm);
    $("#myModal-company").on("submit", ".js-company-update-form", saveForm);

});
    // $(".js_create_company").click(function () {
    //     //console.log('display company modal ...')
    //     $.ajax({
    //         url: '/lcl/company/create/',
    //         type: 'get',
    //         dataType: 'json',
    //         beforeSend: function () {
    //             $("#myModal-company").modal("show");
    //         },
    //
    //         success: function (data) {
    //             $("#myModal-company .modal-content").html(data.html_form);
    //         }
    //     });
    //     //console.log('display company modal finished...')
    // });

  // $("#myModal-company").on("click", ".js_save_btn", function() {
  //     //console.log('submit button as Button ...')
  //     let form = $("#create_company_form")
  //
  //     $.ajax({
  //         url: form.attr("action"),
  //         data: form.serialize(),
  //         type: form.attr("method"),
  //         dataType: 'json',
  //         cache: false,
  //         async: false,
  //         success: function (data) {
  //             if (data.form_is_valid) {
  //                 //console.log('Submit Button Success and form is valid ...')
  //                 $("#myModal-company").modal("hide");  // <-- Close the modal
  //                 // 刷新表格数据
  //                 $('#company-table tbody').html(data.html_company_list);
  //                 // 正确提示
  //                 toastr.success('Data Save Successfully...');
  //             } else {
  //                 // 正确提示
  //                 toastr.warning('Data have some error ...');
  //                 //console.log('Submit Button Success and form is no valid ...')
  //                 $("#myModal-company .modal-content").html(data.html_form);
  //             }
  //         },
  //     });
  //     return false;
  //  });


  // $("#myModal-company").on("submit",".js-company-create-form", function() {
  //     console.log('Submit Button ...')
  //     let form = $(this)
  //     $.ajax({
  //         url: form.attr("action"),
  //         data: form.serialize(),
  //         type: form.attr("method"),
  //         dataType: 'json',
  //         cache: false,
  //         async: false,
  //         success: function (data) {
  //             if (data.form_is_valid) {
  //                 console.log('Submit Button Success and form is valid ...')
  //                 // $("#myModal-company").modal("hide");  // <-- Close the modal
  //                 document.getElementById("btn-cancel").click();
  //                 // 刷新表格数据
  //                 $('#company-table tbody').html(data.html_company_list);
  //                 // 正确提示
  //                 // toastr.success('Data Save Successfully...');
  //             } else {
  //                 console.log('Submit Button Success and form is no valid ...')
  //                 $("#myModal-company .modal-content").html(data.html_form);
  //             }
  //         },
  //     });
  //     return false;
  //  });
