$(function () {
  $(".purchase-button").on("click", function (e) {
    e.preventDefault();
    ModalWorkflow({
      url: this.getAttribute("href"),

      onload: {
        chooser: function (modal, jsonData) {
          /* When the new purchase order form is submmited  */
          $("form.purchase-order-create", modal.body).on("submit", function (
            e
          ) {
            e.preventDefault();
            var formdata = new FormData(this);
            $.ajax({
              url: this.action,
              data: formdata,
              processData: false,
              contentType: false,
              type: "POST",
              dataType: "text",
              success: modal.loadResponseText,
            });
            return false;
          });

          $("form.purchase-order-add", modal.body).on("submit", function (e) {
            e.preventDefault();
            console.log($(this));
            var formdata = new FormData();
            formdata.append(
              "csrfmiddlewaretoken",
              $('meta[name="csrftoken"]').attr("content")
            );
            formdata.append("purchase_order", this.id);
            formdata.append("add_type", "to_existing");
            $.ajax({
              url: this.action,
              data: formdata,
              processData: false,
              contentType: false,
              type: "POST",
              dataType: "text",
              success: modal.loadResponseText,
            });
            return false;
          });
        },

        choosen: function (modal, jsonData) {
          /* When the purchase order form submition is succuful  */
          addMessage("success", "Added to Purchase Order");
          modal.close();
        },

        choosen_already: function (modal, jsonData) {
          /* If a purchase already is already associated with this item  */
          addMessage("warning", "Purchase Order already exist for this item");
          modal.close();
        },
      },
    });
  });
});
