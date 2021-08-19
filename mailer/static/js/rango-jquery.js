$(function()
{
    $(document).on('click', '.btn-add-mail', function(e)
    {
        e.preventDefault();

        var controlForm = $('#mails'),
            currentEntry = $(this).parents('.entry:first'),
            newEntry = $(currentEntry.clone()).appendTo(controlForm);

        newEntry.find('input').val('');
        controlForm.find('.entry:not(:last) .btn-add-mail')
            .removeClass('btn-add-mail').addClass('btn-remove-mail')
            .removeClass('btn-success').addClass('btn-danger')
            .html('<span class="glyphicon glyphicon-minus">Убрать</span>');
    }).on('click', '.btn-remove-mail', function(e)
    {
		$(this).parents('.entry:first').remove();

		e.preventDefault();
		return false;
	});
});

$(function()
{
    $(document).on('click', '.btn-add-file', function(e)
    {
        e.preventDefault();

        var controlForm = $('#files'),
            currentEntry = $(this).parents('.form-file:first'),
            newEntry = $(currentEntry.clone()).appendTo(controlForm);

        newEntry.find('input').val('');
        controlForm.find('.form-file:not(:last) .btn-add-file')
            .removeClass('btn-add-file').addClass('btn-remove-file')
            .removeClass('btn-success').addClass('btn-danger')
            .html('<span class="glyphicon glyphicon-minus">Убрать</span>');
    }).on('click', '.btn-remove-file', function(e)
    {
		$(this).parents('.form-file:first').remove();

		e.preventDefault();
		return false;
	});
});

let msg_box = { "msg": '#msg',
                "type": "alert-danger",
                change_type: function(newtype){
                    $( this.msg ).removeClass(this.type);
                    $( this.msg ).addClass(newtype);
                    this.type = newtype },
                change_text: function(newmgs){
                    $( this.msg ).text(newmgs);
                    console.log(this.msg);
                    console.log("text changed");
                },
                show: function(){
                    $( this.msg ).removeAttr("style");
                },
                hide: function(){
                    $( this.msg ).setAtt("style", "display: none");
                }

            };
$(document).on('click', '#sendbutton', function(e)
    {
        let sendbutton = document.getElementById('sendbutton');
        let sendform = document.getElementById('sendform');
        //let email_choice = document.getElementsByClassName('select2-selection__rendered')[0].children;
        // msg_box = document.getElementById("msg")

        if (sendform.selectmail.value && sendform.title.value) {
            //let reg = new RegExp('[\^:;\\?*"\']+')
            //[.!:;"&/*+?^${}()|[\]\\]
            // let reg = /[.*+?^${}[\]\\/:*?<>"]/g
            // if (reg.test(sendform.title.value)) {
            //     console.log('error!')
            //     msg_box.change_text("у темі присутні недопустимі символи: \\/:*?\"<>|");
            //     msg_box.show()
            // }
            // else {
                console.log('ready_to_send');
                sendbutton.setAttribute('disabled', 'true');
                console.log('submit button disabled');
                msg_box.change_type("alert-success"); //"alert-danger"
                msg_box.change_text("Відправка повідомлення");
                msg_box.show()
                sendform.submit();
              }

            // }}
        else if(!sendform.selectmail.value) {
            msg_box.show();
            msg_box.change_text("Не вибрана адреса");
            console.log("email and title not valid");
        } else if(sendform.title.value == "") {
            msg_box.show();
            msg_box.change_text("Пуста тема");
            console.log("email and title not valid");}
	});

$(document).on('click', '#reload', function(e)
    {
        msg_box = document.getElementById("msg")
        msg_box.setAttribute("style", "display: none")
        let sendbutton = document.getElementById('sendbutton');
        sendbutton.removeAttribute('disabled');
        console.log('enabled');
	// sendform.submit();
	});


$(document).ready(function() {
    $('select').select2({
    placeholder: "Натисніть для вибору адреси"
    });
});


//$(document).ready(function(){
//
//    $(".table-body-mail-list").click(function(){
//        window.location=$(this).find(".row-hover-info").attr("href"); return false;
//    });
//});

$(".table-body-mail-list").click(function(){
        window.location=$(this).find(".row-hover-info").removeClass('.row-hover-info');
        $(this).toggleClass("active");
        });

console.log('ready')


function dragenterfunc(e){
console.log(e)};

function setupmodal(data) {
    statuss = {"1": "Відправленно",
               "2": "Не відправленно",
               "3": "Помилка",
               "4": "У черзі",}

    let modalview = document.querySelector("#modalview")

    $(".button-flex-box #resend").click(function (e) {
      e.preventDefault();
      $(".button-flex-box #resend").addClass("disabled")
      $.ajax({
          type: "GET",
          url: modalview.querySelector(".button-flex-box #resend").href,
          data: "",
          dataType: "json",
          success: function (response) {


              $(".msg").addClass(response.type)
              modalview.querySelector(".msg").innerHTML = response.text
              modalview.querySelector(".msg").style = 'display:block'
              $(".button-flex-box #resend").removeClass("disabled")
          }
      });
    })

    let to = ""
    for(x of data.mails.to) {
        to += " " + x.addres
    };

    let files = "<p>Файли:</p>"
    if(data.mails.files){
      for(file of data.mails.files.files) {
        files += `<p><a href="${ file.url }">${ file.name }</a></p> `
      };

    }

    logs = "";
    for(log of data.mails.logs) {
      let date = new Date(log.when_attempted);
      logs += `
      <tr class="table-body-mail-list">
        <th scope="row"/>${ log.message_id}</th>
        <td>${ date.toLocaleString()} </td>
        <td>${ statuss[log.result]} </td>
        <td>${ log.log_message} </td>
        </tr>
      `
    };

    modalview.querySelector(".log_message tbody").innerHTML = logs;

    $('#modalview').modal("show");

    $('#modalview').on("hide.bs.modal", function (e) {

      $(".msg").removeClass("alert-danger");
      $(".msg").removeClass('alert-success');

      modalview.querySelector(".msg").innerHTML = "";
      modalview.querySelector(".msg").style = 'display:none';
    });

    url = `/mails/resends/${data.mails.id}/`
    modalview.querySelector(".button-flex-box #resend").href = `/mails/resends/${data.mails.id}/`
    modalview.querySelector(".button-flex-box #recreate").href = `/mails/re_create_mail/${data.mails.id}/`

    modalview.querySelector(".card-header").innerHTML = "Отримувачі:" + to;
    modalview.querySelector(".card-title").innerHTML = "Тема: " + data.mails.title;
    modalview.querySelector(".modal-title").innerHTML = `id: ${data.mails.id} ${data.mails.title}`
    modalview.querySelector(".massage").innerHTML = data.mails.body;
    modalview.querySelector(".status").innerHTML = `Статус: ${statuss[data.mails.status]}`;
    modalview.querySelector(".files").innerHTML = files;
    modalview.querySelector(".card-footer").innerHTML = `відправник: ${data.mails.sender.username}`;
};


$(document).on('dragenter', '#drop-area', dragenterfunc);
$(document).on('dragleave', '#drop-area', function(e){
console.log("leave")});
$(document).on('drop', '#drop-area', function(e){
console.log("droped")});


let restapi_ulr = "localhost:8000"
let test = 10;

console.log(test + 10);
let array = [1,2,3,4,5,6];
let data_request = new XMLHttpRequest()
data_request.open("GET", `${restapi_ulr}/api/mails/`, true)


console.log(document.getElementsByClassName("content"));


$(document).ready(function(){
    if(location.pathname != "/mails/allmails/"){
      // что бы скрипт срабатывал на конкретной странице - "/mails/allmails/"
      console.log("не на той странице")
      return
    }
    let input_new_intem = document.getElementById("input_new_intem");
    let menu = document.getElementsByClassName("menu");
    let modalview = document.querySelector("#modalview")

    $("#start").click(function (e) {
      // вставка элемета
        e.preventDefault();
        console.log(input_new_intem.value);
        $(".menu").append(`<li>${input_new_intem.value} <button class="remove_li">remove item</button></li>`);
        $(".remove_li").click(function (e) {
            console.log(this.parentElement.remove());});

        console.log(this.innerHTML)
    });
    $(".remove_li").click(function (e) {
      // удаление html элемента
        console.log(this.parentElement.remove());

    });
    $(".getid").click(function (e) {
        e.preventDefault();
        console.log(`${restapi_ulr}/api/mails/` + this.innerHTML)
        console.log(this.innerHTML);
        $.ajax({
            type: "GET",
            url: `${restapi_ulr}/api/mails/${this.innerHTML.trim()}`,
            data: this.innerHTML,
            dataType: "json",
            success: function (response) {
                setupmodal(response)
                console.log(response)

            }
        });

    });

    $(".resend_from_list").click(function (e) {
        e.preventDefault();
        $(".resend_from_list").addClass("disabled");

        $.ajax({
            type: "GET",
            url: this.href,
            data: this.innerHTML,
            dataType: "json",
            success: function (response) {
                let email_list_msg = document.querySelector("#email_list_msg")

                $("#email_list_msg").removeClass("alert-danger");
                $("#email_list_msg").removeClass('alert-success');

                $("#email_list_msg").addClass(response.type);
                email_list_msg.innerHTML = response.text;
                email_list_msg.style = 'display:block';
                $(".resend_from_list").removeClass("disabled");


                // setupmodal(response)
                // console.log(response)
            }
        });
    });
});

$(document).ready(function () {
     // sidebar все для работы с сайдбаром
    $('#sidebarCollapse').on('click', function () {
        $('#sidebar').toggleClass('active');
    });
    $('#nav-localsave-post').on('click', function() {
       if(localStorage.getItem('postmenu') != "show") {
         localStorage.setItem('postmenu', "show")
       }
       else {
         localStorage.removeItem('postmenu')
       }
    });

    $('#nav-localsave-admin').on('click', function() {
       if(localStorage.getItem('adminmenu') != "show") {
         localStorage.setItem('adminmenu', "show")
       }
       else {
         localStorage.removeItem('adminmenu')
       }
    });



    $('#nav-localsave-blog').on('click', function() {
       if(localStorage.getItem('blogmenu') != "show") {
         localStorage.setItem('blogmenu', "show")
       }
       else {
         localStorage.removeItem('blogmenu')
       }
    })

    if(localStorage.getItem('postmenu') == "show") {
      $("#postmenu").addClass("show")
    }
    if(localStorage.getItem('blogmenu') == "show") {
      $("#blogmenu").addClass("show")
    }
    if(localStorage.getItem('adminmenu') == "show") {
      $("#adminmenu").addClass("show")
    }


    $('li a').each(function(index) {
      let elem = $( this )[0]
      //console.log(elem);
      //console.log($( this ));
      if(elem.href  === location.href){
        $( this ).addClass("urlactive")
      }
    })

    console.log(localStorage.getItem('postmenu'));




});
